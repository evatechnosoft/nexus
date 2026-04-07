"""
Skill Index Builder for Nexus Registry
Scans skill directories, parses SKILL.md frontmatter, produces skill-index.json
Usage: python build-skill-index.py [--upload]
"""

import json
import os
import re
import sys
from pathlib import Path
from typing import Optional

SKILLS_DIRS = [
    Path(os.path.expanduser("~/.claude/skills")),
    Path(os.path.expanduser("~/.claude/skills/_archived")),
    Path(os.path.expanduser("~/.claude/skills/_registry")),
]

OUTPUT_PATH = Path(os.path.expanduser("~/.ai/skill-index.json"))
NEXUS_URL = "http://192.168.1.186:8900"

# Category detection by prefix/path
CATEGORY_MAP = {
    "bmad-": "bmad",
    "tob-": "security",
    "kdense-": "scientific",
    "ansible-": "devops",
    "azure-pipelines-": "devops",
    "bash-script-": "devops",
    "dockerfile-": "devops",
    "fluentbit-": "devops",
    "github-actions-": "devops",
    "gitlab-ci-": "devops",
    "helm-": "devops",
    "jenkinsfile-": "devops",
    "k8s-": "devops",
    "logql-": "devops",
    "loki-": "devops",
    "makefile-": "devops",
    "promql-": "devops",
    "terraform-": "devops",
    "terragrunt-": "devops",
}

CORE_SKILLS = {
    "best-practices",
    "commit-smart",
    "context-prep",
    "nexus-discover",
    "nexus-sync",
}


def detect_category(name: str, path: str) -> str:
    """Detect skill category from name prefix or path."""
    if "_archived" in path:
        return "archived"
    for prefix, category in CATEGORY_MAP.items():
        if name.startswith(prefix):
            return category
    if name in CORE_SKILLS:
        return "core"
    return "general"


def parse_frontmatter(content: str) -> dict[str, str]:
    """Parse YAML frontmatter from SKILL.md content."""
    match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return {}

    frontmatter: dict[str, str] = {}
    for line in match.group(1).strip().split("\n"):
        if ":" in line:
            key, _, value = line.partition(":")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and value:
                frontmatter[key] = value
    return frontmatter


def extract_triggers(content: str) -> list[str]:
    """Extract trigger phrases from SKILL.md body."""
    triggers: list[str] = []

    # Look for trigger sections
    trigger_section = re.search(
        r"(?:trigger|triggers|when to use)[:\s]*\n((?:[-*]\s+.+\n?)+)",
        content,
        re.IGNORECASE,
    )
    if trigger_section:
        for line in trigger_section.group(1).strip().split("\n"):
            line = line.strip().lstrip("-*").strip()
            if line and len(line) < 100:
                triggers.append(line)

    return triggers[:10]  # Max 10 triggers


def count_lines(content: str) -> int:
    """Count non-empty lines."""
    return len([line for line in content.split("\n") if line.strip()])


def scan_skill_dir(skill_path: Path, max_depth: int = 0) -> Optional[dict[str, object]]:
    """Scan a single skill directory and return index entry. Recurse into subdirs if no SKILL.md found."""
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        # If no SKILL.md and we haven't recursed too deep, try subdirectories
        if max_depth < 2:
            for subdir in sorted(skill_path.iterdir()):
                if subdir.is_dir() and not subdir.name.startswith("."):
                    result = scan_skill_dir(subdir, max_depth + 1)
                    if result:
                        return result
        return None

    try:
        content = skill_md.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None

    frontmatter = parse_frontmatter(content)
    name = frontmatter.get("name", skill_path.name)
    description = frontmatter.get("description", "")
    triggers = extract_triggers(content)
    lines = count_lines(content)
    category = detect_category(name, str(skill_path))

    # Check if it's a symlink
    is_symlink = skill_path.is_symlink()

    return {
        "name": name,
        "description": description[:200],  # Truncate long descriptions
        "category": category,
        "triggers": triggers,
        "lines": lines,
        "source": "local",
        "path": str(skill_path),
        "symlink": is_symlink,
    }


def build_index() -> list[dict[str, object]]:
    """Build the complete skill index."""
    index: list[dict[str, object]] = []
    seen_names: set[str] = set()

    for skills_dir in SKILLS_DIRS:
        if not skills_dir.exists():
            continue

        # Recursively find all SKILL.md files
        for skill_md in sorted(skills_dir.rglob("SKILL.md")):
            skill_path = skill_md.parent
            skill_data = scan_skill_dir(skill_path)
            if skill_data and skill_data["name"] not in seen_names:
                index.append(skill_data)
                seen_names.add(skill_data["name"])

    return index


def upload_to_nexus(index: list[dict[str, object]]) -> bool:
    """Upload index to Nexus server."""
    try:
        import urllib.request

        data = json.dumps({"skills": index}).encode("utf-8")
        req = urllib.request.Request(
            f"{NEXUS_URL}/api/skills/upload",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            print(f"Upload response: {resp.status}")
            return resp.status == 200
    except Exception as e:
        print(f"Upload failed: {e}")
        return False


def main() -> None:
    """Main entry point."""
    print("Building skill index...")
    index = build_index()

    # Stats
    categories: dict[str, int] = {}
    for skill in index:
        cat = str(skill["category"])
        categories[cat] = categories.get(cat, 0) + 1

    print(f"\nTotal skills: {len(index)}")
    for cat, count in sorted(categories.items()):
        print(f"  {cat}: {count}")

    # Write to file
    output = {
        "version": "1.0",
        "generated_at": __import__("datetime").datetime.now().isoformat(),
        "total": len(index),
        "categories": categories,
        "skills": index,
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nIndex written to: {OUTPUT_PATH}")

    # Upload if requested
    if "--upload" in sys.argv:
        print("\nUploading to Nexus...")
        upload_to_nexus(index)


if __name__ == "__main__":
    main()
