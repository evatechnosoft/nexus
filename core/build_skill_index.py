"""
Nexus Master Index Builder (v3.0)
Scans skills and global memory (rules, handoffs, projects).
Supports Metadata/Frontmatter and Vault Pointers.
"""

import json
import os
import re
import sys
from pathlib import Path
from typing import Optional, Any, Dict, List

# Target directories for indexing
SKILLS_DIRS = [
    Path(os.path.expanduser("~/.claude/skills")),
    Path("data/memory/rules"),
    Path("data/memory/handoffs"),
    Path("data/memory/projects"),
]

# Output path for the unified index
OUTPUT_PATH = Path(os.path.expanduser("~/.ai/skill-index.json"))
NEXUS_URL = "http://192.168.1.186:8900"

CATEGORY_MAP = {
    "rule--": "rules",
    "handoff--": "handoffs",
    "project--": "projects",
    "ansible-": "devops",
    "dockerfile-": "devops",
    "k8s-": "devops",
}

CORE_SKILLS = {"best-practices", "commit-smart", "context-prep", "nexus-discover", "nexus-sync"}

def detect_category(name: str, path: str) -> str:
    for prefix, category in CATEGORY_MAP.items():
        if name.startswith(prefix):
            return category
    if name in CORE_SKILLS:
        return "core"
    if "data/memory/rules" in path: return "rules"
    if "data/memory/handoffs" in path: return "handoffs"
    if "data/memory/projects" in path: return "projects"
    return "general"

def parse_frontmatter(content: str) -> Dict[str, str]:
    match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return {}
    frontmatter = {}
    for line in match.group(1).strip().split("\n"):
        if ":" in line:
            key, _, value = line.partition(":")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and value:
                frontmatter[key] = value
    return frontmatter

def extract_triggers(content: str) -> List[str]:
    triggers = []
    trigger_section = re.search(r"(?:trigger|triggers|when to use)[:\s]*\n((?:[-*]\s+.+\n?)+)", content, re.IGNORECASE)
    if trigger_section:
        for line in trigger_section.group(1).strip().split("\n"):
            line = line.strip().lstrip("-*").strip()
            if line and len(line) < 100:
                triggers.append(line)
    return triggers[:10]

def scan_skill_file(md_file: Path) -> Optional[Dict[str, Any]]:
    if not md_file.exists():
        return None
    try:
        content = md_file.read_text(encoding="utf-8")
    except Exception:
        return None

    frontmatter = parse_frontmatter(content)
    # Metadata hiyerarşisi: id > name > filename
    name = frontmatter.get("id", frontmatter.get("name", md_file.stem))
    description = frontmatter.get("description", "")
    type_ = frontmatter.get("type", "rule" if name.startswith("rule--") else "general")
    context = frontmatter.get("context", "global")
    extends = frontmatter.get("extends", "")
    
    triggers = extract_triggers(content)
    category = detect_category(name, str(md_file))

    return {
        "name": name,
        "description": description[:300],
        "category": category,
        "type": type_,
        "context": context,
        "extends": extends,
        "triggers": triggers,
        "source": "local",
        "path": str(md_file),
        "metadata": frontmatter,
        "lines": len(content.split("\n"))
    }

def build_index() -> List[Dict[str, Any]]:
    index = []
    seen_names = set()
    for d in SKILLS_DIRS:
        if not d.exists(): continue
        for md in sorted(d.rglob("*.md")):
            data = scan_skill_file(md)
            if data and data["name"] not in seen_names:
                index.append(data)
                seen_names.add(data["name"])
    return index

def main():
    print("🚀 Building Nexus Master Index...")
    index = build_index()
    
    categories = {}
    for s in index:
        cat = s["category"]
        categories[cat] = categories.get(cat, 0) + 1

    output = {
        "version": "3.0",
        "generated_at": __import__("datetime").datetime.now().isoformat(),
        "total": len(index),
        "categories": categories,
        "skills": index,
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n✅ Index written to: {OUTPUT_PATH}")
    print(f"📊 Stats: {len(index)} total entries in {len(categories)} categories.")

if __name__ == "__main__":
    main()
