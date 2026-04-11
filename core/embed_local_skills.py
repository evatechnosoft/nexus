"""
Batch embed existing skills in skill-index.json.
Reads index, embeds skills without vectors, writes back atomically.

Usage (inside nexus-mcp container):
    docker exec nexus-mcp python /app/src/embed_local_skills.py [--dry-run] [--limit N]
"""

import asyncio
import json
import sys
import time
from pathlib import Path
from typing import Any

# ── Path setup ────────────────────────────────────────────────────────────────
_SRC_DIR = Path(__file__).parent
sys.path.insert(0, str(_SRC_DIR))

INDEX_PATH = Path("/app/data/skill-index.json")
EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"


# ── Helpers ───────────────────────────────────────────────────────────────────


def _skill_content(skill: dict[str, Any]) -> str:
    """Build embeddable text from available skill fields."""
    parts: list[str] = []

    name = skill.get("name") or ""
    if name:
        parts.append(name.replace("-", " ").replace("_", " "))

    description = skill.get("description") or ""
    if description:
        parts.append(description)

    triggers = skill.get("triggers") or []
    if triggers:
        parts.append(" ".join(str(t) for t in triggers))

    # Snippet/snippet from fetched skills
    snippet = skill.get("snippet") or ""
    if snippet:
        parts.append(snippet)

    return " ".join(parts).strip()


def _needs_embedding(skill: dict[str, Any]) -> bool:
    """Return True if skill has no usable vector."""
    v = skill.get("vector")
    return not v or not isinstance(v, list) or len(v) == 0


def _print_progress(idx: int, total: int, name: str, elapsed: float) -> None:
    pct = int(idx / total * 100)
    bar = "#" * (pct // 5) + "-" * (20 - pct // 5)
    print(
        f"\r[{bar}] {pct:3d}% ({idx}/{total}) {name[:40]:<40} {elapsed:.1f}s",
        end="",
        flush=True,
    )


# ── Main ──────────────────────────────────────────────────────────────────────


async def run(dry_run: bool = False, limit: int = 0) -> None:
    from nexus_embed import EmbeddingEngine, embed_skill
    from nexus_store import save_index
    from nexus_utils import logger

    # Load index
    if not INDEX_PATH.exists():
        print(f"ERROR: Index not found at {INDEX_PATH}", file=sys.stderr)
        sys.exit(1)

    index: dict[str, Any] = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    skills: list[dict[str, Any]] = index.get("skills", [])

    pending = [s for s in skills if _needs_embedding(s)]
    if limit > 0:
        pending = pending[:limit]

    total_skills = len(skills)
    total_pending = len(pending)

    print(f"skill-index.json: {total_skills} total, {total_pending} need embedding")

    if total_pending == 0:
        print("All skills already have vectors. Nothing to do.")
        return

    if dry_run:
        print(f"[DRY-RUN] Would embed {total_pending} skills. Exiting.")
        return

    # Init embedding engine (singleton)
    engine = EmbeddingEngine(model_name=EMBEDDING_MODEL)
    engine._load_model()

    if engine.model is None:
        print(
            "ERROR: FastEmbed model failed to load. Check fastembed install.",
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"Model loaded: {EMBEDDING_MODEL}")

    # Build name → skill lookup for in-place update
    skill_by_name: dict[str, dict[str, Any]] = {s.get("name", ""): s for s in skills}

    embedded_count = 0
    failed_count = 0
    start_total = time.time()

    for i, skill in enumerate(pending, start=1):
        name = skill.get("name") or f"skill_{i}"
        content = _skill_content(skill)

        _print_progress(i - 1, total_pending, name, time.time() - start_total)

        if not content:
            logger.warning(f"No content for skill '{name}', skipping")
            failed_count += 1
            continue

        try:
            result = await embed_skill(
                skill_name=name,
                content=content,
                title=name,
                embedding_engine=engine,
            )

            if result.get("vector"):
                # Update skill in-place
                target = skill_by_name.get(name)
                if target is not None:
                    target["vector"] = result["vector"]
                    target["chunks"] = result["chunks"]
                    target["embedding_model"] = result["embedding_model"]
                    target["embedding_cached"] = False
                embedded_count += 1
            else:
                logger.warning(f"Empty vector for '{name}'")
                failed_count += 1

        except Exception as exc:
            logger.error(f"embed_skill failed for '{name}': {exc}")
            failed_count += 1

        elapsed = time.time() - start_total
        _print_progress(i, total_pending, name, elapsed)

    print()  # newline after progress bar

    # Update index metadata
    index["skills"] = list(skill_by_name.values())
    index["total"] = len(index["skills"])

    # Re-count vectors
    with_vector = sum(1 for s in index["skills"] if s.get("vector"))
    index["vectors_count"] = with_vector

    # Save
    ok = await save_index(index, INDEX_PATH)
    elapsed_total = time.time() - start_total

    print(f"\n{'=' * 60}")
    print(f"Done in {elapsed_total:.1f}s")
    print(f"  Embedded : {embedded_count}")
    print(f"  Failed   : {failed_count}")
    print(f"  Total w/ vectors: {with_vector}/{len(index['skills'])}")
    print(f"  Saved    : {'OK' if ok else 'FAILED'}")


def main() -> None:
    dry_run = "--dry-run" in sys.argv
    limit = 0
    if "--limit" in sys.argv:
        idx = sys.argv.index("--limit")
        try:
            limit = int(sys.argv[idx + 1])
        except (IndexError, ValueError):
            print("Usage: embed_local_skills.py [--dry-run] [--limit N]")
            sys.exit(1)

    asyncio.run(run(dry_run=dry_run, limit=limit))


if __name__ == "__main__":
    main()
