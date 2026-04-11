"""
Nexus utilities: types, retry logic, helpers.
Shared by nexus_fetch, nexus_embed, nexus_store modules.
"""

import asyncio
import hashlib
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

# Logging setup (async-safe)
logger = logging.getLogger("nexus")
logger.setLevel(logging.DEBUG)

if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("[%(levelname)s] %(asctime)s - %(message)s"))
    logger.addHandler(handler)


# ============================================================================
# TYPE DEFINITIONS
# ============================================================================


@dataclass
class FetchResult:
    """Raw result from DDGS search."""

    title: str
    url: str
    snippet: str
    source: str = "ddgs"  # ddgs, brave, local
    fetched_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "url": self.url,
            "snippet": self.snippet,
            "source": self.source,
            "fetched_at": self.fetched_at,
        }


@dataclass
class FetchReport:
    """Report from fetch cycle."""

    category: str
    total_fetched: int
    total_deduped: int
    candidates: List[FetchResult]
    errors: List[str] = field(default_factory=list)
    elapsed_seconds: float = 0.0

    def to_dict(self) -> dict:
        return {
            "category": self.category,
            "total_fetched": self.total_fetched,
            "total_deduped": self.total_deduped,
            "candidates": [c.to_dict() for c in self.candidates],
            "errors": self.errors,
            "elapsed_seconds": self.elapsed_seconds,
        }


@dataclass
class EmbeddedSkill:
    """Skill with vector embeddings."""

    name: str
    vector: List[float]  # 384-dim or empty
    chunks: List[Dict[str, Any]] = field(default_factory=list)
    embedding_model: str = "BAAI/bge-small-en-v1.5"
    embedding_cached: bool = False

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "vector": self.vector,
            "chunks": self.chunks,
            "embedding_model": self.embedding_model,
            "embedding_cached": self.embedding_cached,
        }


# ============================================================================
# RETRY POLICY
# ============================================================================


class RetryPolicy:
    """Exponential backoff retry logic."""

    def __init__(self, max_retries: int = 3, base_delay: float = 1.0, max_delay: float = 30.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay

    async def execute(self, coro_fn, *args, **kwargs):
        """
        Execute async function with exponential backoff.
        Retries on Timeout, RateLimit, or ConnectionError.
        """
        last_error = None
        for attempt in range(self.max_retries):
            try:
                return await coro_fn(*args, **kwargs)
            except (asyncio.TimeoutError, ConnectionError, Exception) as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    delay = min(self.base_delay * (2**attempt), self.max_delay)
                    logger.warning(
                        f"Attempt {attempt + 1}/{self.max_retries} failed: {e}. "
                        f"Retrying in {delay}s..."
                    )
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"All {self.max_retries} attempts failed: {e}")

        raise last_error or Exception("Unknown retry error")


# ============================================================================
# HELPERS
# ============================================================================


def hash_content(content: str) -> str:
    """SHA256 hash of content for caching."""
    return hashlib.sha256(content.encode()).hexdigest()


def atomic_write(path: Path, data: str) -> None:
    """
    Atomic write using temp file + rename (POSIX safe).
    Prevents corruption if write interrupted.
    """
    temp_path = path.with_suffix(".tmp")
    temp_path.write_text(data, encoding="utf-8")
    temp_path.replace(path)
    logger.debug(f"Atomic write: {path}")


def atomic_write_json(path: Path, data: dict) -> None:
    """Atomic write of JSON data."""
    import json

    atomic_write(path, json.dumps(data, indent=2, ensure_ascii=False))


def levenshtein_distance(s1: str, s2: str) -> int:
    """Simple Levenshtein distance (for dedup without Levenshtein import)."""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


def fuzzy_match(s1: str, s2: str, threshold: float = 0.85) -> bool:
    """
    Fuzzy string match using normalized Levenshtein distance.
    Returns True if similarity >= threshold.
    """
    # Normalize
    s1_norm = s1.lower().strip()
    s2_norm = s2.lower().strip()

    # Quick exact match
    if s1_norm == s2_norm:
        return True

    # Length check (if very different, skip expensive computation)
    if abs(len(s1_norm) - len(s2_norm)) > max(len(s1_norm), len(s2_norm)) * 0.3:
        return False

    # Levenshtein
    max_len = max(len(s1_norm), len(s2_norm))
    distance = levenshtein_distance(s1_norm, s2_norm)
    similarity = 1.0 - (distance / max_len)

    return similarity >= threshold


# ============================================================================
# LOGGING HELPERS
# ============================================================================


def log_fetch_start(category: str, source: str):
    """Log fetch cycle start."""
    logger.info(f"[Fetch] Starting {source} search for category: {category}")


def log_fetch_result(title: str, url: str, is_dedup: bool = False):
    """Log individual fetch result."""
    status = "[DEDUP]" if is_dedup else "[NEW]"
    logger.debug(f"  {status} {title[:60]} ({url[:60]}...)")


def log_fetch_complete(report: FetchReport):
    """Log fetch cycle completion."""
    logger.info(
        f"[Fetch] {report.category}: "
        f"{report.total_fetched} fetched, {report.total_deduped} deduped, "
        f"{len(report.candidates)} candidates, "
        f"{report.elapsed_seconds:.2f}s"
    )
    if report.errors:
        for error in report.errors:
            logger.warning(f"  - {error}")
