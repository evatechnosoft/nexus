"""
Nexus fetch module: DDGS web search with deduplication and retry logic.
Fetches new skills from web to enrich skill registry.
"""

import asyncio
import json
import re
import time
from pathlib import Path
from typing import Dict, List, Optional

from nexus_utils import (
    FetchReport,
    FetchResult,
    RetryPolicy,
    fuzzy_match,
    log_fetch_complete,
    log_fetch_result,
    log_fetch_start,
    logger,
)

# ============================================================================
# CONSTANTS
# ============================================================================

DDGS_MAX_RETRIES = 3
DDGS_RETRY_DELAY = 1.5  # seconds between retries on rate-limit

CATEGORY_QUERIES = {
    "devops": [
        "dockerfile best practices 2026",
        "kubernetes deployment patterns",
        "terraform infrastructure",
        "CI/CD pipeline tutorial",
        "github actions workflow",
        "helm chart examples",
    ],
    "general": [
        "python programming tutorials",
        "git workflow best practices",
        "code review checklist",
        "software design patterns",
        "REST API design",
    ],
    "bmad": [
        "brainstorming techniques",
        "sprint planning methodology",
        "agile retrospective",
        "user story writing",
    ],
    "security": [
        "cybersecurity best practices",
        "OWASP top 10",
        "encryption algorithms",
        "secure coding",
    ],
}


# ============================================================================
# DDGS SEARCH
# ============================================================================


class DDGSFetcher:
    """DDGS search using duckduckgo-search package (stable API)."""

    def __init__(self, retry_policy: Optional[RetryPolicy] = None):
        self.retry_policy = retry_policy or RetryPolicy(
            max_retries=DDGS_MAX_RETRIES, base_delay=DDGS_RETRY_DELAY
        )

    async def search(self, query: str, max_results: int = 10) -> List[FetchResult]:
        """
        Search via duckduckgo_search package.
        Runs sync DDGS().text() in a thread to avoid blocking the event loop.
        """

        def _sync_search() -> List[FetchResult]:
            try:
                from duckduckgo_search import DDGS

                raw = DDGS().text(query, max_results=max_results) or []
                return [
                    FetchResult(
                        title=r.get("title", ""),
                        url=r.get("href", ""),
                        snippet=(r.get("body", "") or "")[:200],
                        source="ddgs",
                    )
                    for r in raw
                    if r.get("href")
                ]
            except Exception as e:
                logger.error(f"DDGS search failed for '{query}': {e}")
                return []

        try:
            results = await asyncio.to_thread(_sync_search)
            logger.debug(f"DDGS '{query}': {len(results)} results")
            return results
        except Exception as e:
            logger.error(f"DDGS thread error for '{query}': {e}")
            return []


# ============================================================================
# DEDUPLICATION
# ============================================================================


async def is_duplicate(url: str, title: str, current_index: dict, threshold: float = 0.85) -> bool:
    """
    Check if URL or similar title already in skill-index.json.

    Logic:
      1. Exact URL match in existing skills
      2. Fuzzy title match (>0.85 similarity)
      3. Domain-based check (same domain, similar title)

    Returns: True if should skip (is duplicate).
    """
    if not current_index or "skills" not in current_index:
        return False

    # Extract domain
    try:
        domain = re.match(r"https?://([^/]+)", url)
        url_domain = domain.group(1) if domain else ""
    except Exception:
        url_domain = ""

    for skill in current_index.get("skills", []):
        # Check 1: Exact URL match
        if skill.get("url") == url:
            return True

        # Check 2: Fuzzy title match
        skill_title = skill.get("title") or skill.get("name", "")
        if fuzzy_match(title, skill_title, threshold=threshold):
            return True

        # Check 3: Domain-based (same domain + similar title)
        if url_domain:
            skill_url = skill.get("url") or skill.get("path", "")
            try:
                skill_domain = re.match(r"https?://([^/]+)", skill_url)
                skill_domain = skill_domain.group(1) if skill_domain else ""
                if url_domain == skill_domain and skill_title:
                    # Same domain; check title similarity (lower threshold)
                    if fuzzy_match(title, skill_title, threshold=0.7):
                        return True
            except Exception:
                pass

    return False


# ============================================================================
# FETCH ORCHESTRATION
# ============================================================================


async def fetch_by_category(
    category: str,
    skill_index: dict,
    limit_per_query: int = 5,
    max_new_skills: int = 50,
) -> FetchReport:
    """
    Fetch new skills for a category.

    Flow:
      1. Generate queries for category
      2. Fetch from DDGS (with retry)
      3. Deduplicate against current index
      4. Return candidates for embedding

    Args:
        category: Skill category (e.g., "devops", "general")
        skill_index: Current skill-index.json dict
        limit_per_query: Max results per query
        max_new_skills: Stop after finding this many new skills

    Returns:
        FetchReport with candidates and errors
    """
    start_time = time.time()
    log_fetch_start(category, "ddgs")

    queries = CATEGORY_QUERIES.get(category, [])
    if not queries:
        logger.warning(f"No queries defined for category: {category}")
        return FetchReport(category=category, total_fetched=0, total_deduped=0, candidates=[])

    candidates = []
    all_fetched = 0
    total_deduped = 0
    errors = []

    fetcher = DDGSFetcher()

    for query in queries:
        if len(candidates) >= max_new_skills:
            break

        try:
            logger.debug(f"  Fetching: {query}")
            results = await fetcher.search(query, max_results=limit_per_query)
            all_fetched += len(results)

            for result in results:
                if len(candidates) >= max_new_skills:
                    break

                is_dup = await is_duplicate(result.url, result.title, skill_index)
                if is_dup:
                    log_fetch_result(result.title, result.url, is_dedup=True)
                    total_deduped += 1
                else:
                    log_fetch_result(result.title, result.url, is_dedup=False)
                    candidates.append(result)

        except Exception as e:
            error_msg = f"Query '{query}': {str(e)}"
            logger.error(f"  Error: {error_msg}")
            errors.append(error_msg)

        # Rate limit: small delay between queries
        await asyncio.sleep(0.5)

    elapsed = time.time() - start_time
    report = FetchReport(
        category=category,
        total_fetched=all_fetched,
        total_deduped=total_deduped,
        candidates=candidates,
        errors=errors,
        elapsed_seconds=elapsed,
    )

    log_fetch_complete(report)
    return report


async def fetch_all_categories(
    skill_index: dict,
    categories: Optional[List[str]] = None,
    max_per_category: int = 50,
) -> Dict[str, FetchReport]:
    """
    Fetch for all or specified categories.

    Returns:
        Dict of category → FetchReport
    """
    if categories is None:
        categories = list(CATEGORY_QUERIES.keys())

    reports = {}
    for category in categories:
        report = await fetch_by_category(category, skill_index, max_new_skills=max_per_category)
        reports[category] = report

    return reports


# ============================================================================
# MAIN (for testing)
# ============================================================================


async def main():
    """Test DDGS fetch locally."""
    print("Testing DDGS fetch...")

    # Load current skill index
    index_path = Path.home() / ".ai" / "skill-index.json"
    if index_path.exists():
        skill_index = json.loads(index_path.read_text(encoding="utf-8"))
    else:
        skill_index = {"skills": []}

    # Fetch devops category
    report = await fetch_by_category("devops", skill_index, limit_per_query=3, max_new_skills=5)
    print(f"\nReport: {report.to_dict()}")


if __name__ == "__main__":
    asyncio.run(main())
