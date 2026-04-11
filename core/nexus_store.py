"""
Nexus store module: Merge fetched + embedded skills into skill-index.json.
Handles atomic writes and schema validation.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from nexus_utils import atomic_write_json, logger
from pydantic import BaseModel, Field

# ============================================================================
# SCHEMA: Extended Skill Entry (with vectors)
# ============================================================================


class SkillEntry(BaseModel):
    """Extended skill entry schema (Phase 2)."""

    name: str
    description: str = ""
    category: str = "general"
    triggers: List[str] = Field(default_factory=list)
    source: str = "local"  # local, ddgs, brave, ...
    path: Optional[str] = None
    url: Optional[str] = None  # For fetched skills
    fetched_at: Optional[str] = None

    # Phase 2: Vector fields
    vector: List[float] = Field(default_factory=list)  # 384-dim aggregate
    chunks: List[Dict[str, Any]] = Field(default_factory=list)
    embedding_model: Optional[str] = None
    embedding_cached: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for JSON serialization."""
        return self.dict(exclude_unset=False)


# ============================================================================
# INDEX MERGE LOGIC
# ============================================================================


async def merge_fetched_skills(
    new_embeds: List[Dict[str, Any]],
    current_index: Dict[str, Any],
    deduplicate: bool = True,
) -> int:
    """
    Merge embedded skills into current index.

    Flow:
      1. Load current index
      2. For each embedded_skill:
         a. Validate schema (Pydantic)
         b. Check dedup cache
         c. Add or update in index
         d. Increment fetched_at for tracking
      3. Atomic write to disk
      4. Update metadata

    Args:
        new_embeds: List of embedded skill dicts from nexus_embed
        current_index: Current skill-index.json dict
        deduplicate: Skip if URL/name already in index

    Returns:
        Count of new skills added
    """
    if not new_embeds:
        logger.warning("No embedded skills to merge")
        return 0

    if "skills" not in current_index:
        current_index["skills"] = []

    # Track existing URLs/names
    existing_urls = {s.get("url", ""): s for s in current_index.get("skills", [])}
    existing_names = {s.get("name", ""): s for s in current_index.get("skills", [])}

    added = 0

    for embed_dict in new_embeds:
        try:
            # Validate schema
            skill = SkillEntry(**embed_dict)
        except Exception as e:
            logger.warning(f"Invalid skill schema: {e}")
            continue

        # Dedup check
        if deduplicate:
            if skill.url and skill.url in existing_urls:
                logger.debug(f"Skill URL already exists: {skill.url}")
                continue
            if skill.name and skill.name in existing_names:
                logger.debug(f"Skill name already exists: {skill.name}")
                continue

        # Add or update
        existing_names[skill.name] = skill
        if skill.url:
            existing_urls[skill.url] = skill

        added += 1
        logger.debug(f"Added skill: {skill.name} (source: {skill.source})")

    # Rebuild skills list
    current_index["skills"] = list(existing_names.values())

    # Update metadata
    current_index["version"] = "2.0"
    current_index["total"] = len(current_index["skills"])
    current_index["last_update"] = datetime.utcnow().isoformat() + "Z"

    # Recount categories
    categories = {}
    for skill in current_index["skills"]:
        cat = skill.get("category", "general") if isinstance(skill, dict) else skill.category
        categories[cat] = categories.get(cat, 0) + 1
    current_index["categories"] = categories

    logger.info(f"Merged {added} new skills; index now has {current_index['total']} total")

    return added


async def save_index(
    index: Dict[str, Any],
    output_path: Path,
) -> bool:
    """
    Atomically save index to disk.

    Args:
        index: Skill index dict
        output_path: Path to skill-index.json

    Returns:
        True if successful
    """
    try:
        # Convert Pydantic models to dicts
        skills_list = []
        for skill in index.get("skills", []):
            if isinstance(skill, SkillEntry):
                skills_list.append(skill.dict())
            else:
                skills_list.append(skill)

        index["skills"] = skills_list

        # Atomic write
        atomic_write_json(output_path, index)
        logger.info(f"Index saved: {output_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to save index: {e}")
        return False


async def load_index(index_path: Path) -> Dict[str, Any]:
    """Load skill index from disk."""
    try:
        if not index_path.exists():
            logger.warning(f"Index not found: {index_path}")
            return {"version": "2.0", "skills": [], "categories": {}}

        data = json.loads(index_path.read_text(encoding="utf-8"))
        logger.debug(f"Index loaded: {len(data.get('skills', []))} skills")
        return data
    except Exception as e:
        logger.error(f"Failed to load index: {e}")
        return {"version": "2.0", "skills": [], "categories": {}}


# ============================================================================
# FETCH-STATE TRACKING
# ============================================================================


class FetchState(BaseModel):
    """Metadata for fetch pipeline."""

    version: str = "1.0"
    last_full_fetch: Optional[str] = None
    categories_completed: List[str] = Field(default_factory=list)
    categories_pending: List[str] = Field(default_factory=list)
    dedup_cache_size: int = 0
    skills_added_in_last_run: int = 0
    last_errors: List[Dict[str, str]] = Field(default_factory=list)


async def save_fetch_state(
    state: FetchState,
    output_path: Path,
) -> bool:
    """Save fetch metadata."""
    try:
        atomic_write_json(output_path, state.dict())
        return True
    except Exception as e:
        logger.error(f"Failed to save fetch state: {e}")
        return False


async def load_fetch_state(state_path: Path) -> FetchState:
    """Load fetch metadata."""
    try:
        if state_path.exists():
            data = json.loads(state_path.read_text(encoding="utf-8"))
            return FetchState(**data)
        return FetchState()
    except Exception as e:
        logger.warning(f"Failed to load fetch state: {e}")
        return FetchState()


# ============================================================================
# MAIN (for testing)
# ============================================================================


async def main():
    """Test merging."""
    print("Testing merge...")

    # Create mock embedded skills
    mock_embeds = [
        {
            "name": "dockerfile-advanced",
            "description": "Advanced Dockerfile patterns",
            "category": "devops",
            "source": "ddgs",
            "url": "https://example.com/dockerfile",
            "vector": [0.1, 0.2, 0.3] * 128,  # Mock 384-dim
            "chunks": [{"text": "chunk 0", "vector": [0.1] * 384}],
            "embedding_model": "BAAI/bge-small-en-v1.5",
        }
    ]

    # Load or create index
    index_path = Path.home() / ".ai" / "skill-index.json"
    index = await load_index(index_path)

    # Merge
    added = await merge_fetched_skills(mock_embeds, index, deduplicate=True)
    print(f"Merged {added} skills")

    # Save
    success = await save_index(index, index_path)
    print(f"Save: {'OK' if success else 'FAILED'}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
