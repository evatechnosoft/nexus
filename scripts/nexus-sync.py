#!/usr/bin/env python3
"""
nexus-sync: Universal AI Config Sync Tool
Canonical .ai/ source → Claude, Gemini, Copilot, Cursor targets

Usage:
    python nexus-sync.py init [--project-name NAME]
    python nexus-sync.py build [--target TARGET] [--dry-run]
    python nexus-sync.py diff
    python nexus-sync.py status
    python nexus-sync.py validate
    python nexus-sync.py add skill <name>
    python nexus-sync.py add guide <name>
    python nexus-sync.py import claude|gemini
    python nexus-sync.py install-hooks
"""

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import textwrap
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# YAML‑lite parser/emitter (zero‑dependency – stdlib only)
# Handles the subset used by manifest.yaml: scalars, lists, nested dicts.
# ---------------------------------------------------------------------------

def _yaml_loads(text: str) -> dict:
    """Minimal YAML‑like loader for manifest.yaml format."""
    result: dict[str, Any] = {}
    stack: list[tuple[int, dict]] = [(-1, result)]
    list_key: str | None = None

    lines = text.splitlines()
    i = 0
    while i < len(lines):
        raw_line = lines[i]
        stripped = raw_line.rstrip()
        if not stripped or stripped.lstrip().startswith("#"):
            i += 1
            continue

        indent = len(raw_line) - len(raw_line.lstrip())

        # Pop stack to correct depth
        while len(stack) > 1 and indent <= stack[-1][0]:
            stack.pop()
            list_key = None

        current = stack[-1][1]
        line = stripped.lstrip()

        # List item
        if line.startswith("- "):
            item_text = line[2:].strip()
            if list_key and list_key in current:
                # Ensure the value is a list
                if not isinstance(current[list_key], list):
                    current[list_key] = []
                # Multi-line dict list item: collect subsequent indented key:val lines
                if ":" in item_text and not item_text.startswith('"'):
                    k, v = item_text.split(":", 1)
                    entry = {k.strip(): _yaml_scalar(v.strip())}
                    # Peek ahead for continuation lines at deeper indent
                    item_indent = indent + 2 + (len(line) - len(line.lstrip()))
                    j = i + 1
                    while j < len(lines):
                        next_raw = lines[j]
                        next_stripped = next_raw.rstrip()
                        if not next_stripped or next_stripped.lstrip().startswith("#"):
                            j += 1
                            continue
                        next_indent = len(next_raw) - len(next_raw.lstrip())
                        next_line = next_stripped.lstrip()
                        if next_indent > indent and not next_line.startswith("- ") and ":" in next_line:
                            nk, nv = next_line.split(":", 1)
                            nk = nk.strip()
                            nv = nv.strip()
                            if nv.startswith("[") and nv.endswith("]"):
                                entry[nk] = [_yaml_scalar(x.strip()) for x in nv[1:-1].split(",") if x.strip()]
                            else:
                                entry[nk] = _yaml_scalar(nv)
                            j += 1
                        else:
                            break
                    current[list_key].append(entry)
                    i = j
                    continue
                else:
                    current[list_key].append(_yaml_scalar(item_text))
            i += 1
            continue

        # Key: value
        if ":" in line:
            key, _, val = line.partition(":")
            key = key.strip().strip('"').strip("'")
            val = val.strip()

            if val == "":
                # Peek ahead: if next non-empty line starts with "- ", it's a list
                j = i + 1
                is_list = False
                while j < len(lines):
                    peek = lines[j].rstrip()
                    if not peek or peek.lstrip().startswith("#"):
                        j += 1
                        continue
                    peek_indent = len(lines[j]) - len(lines[j].lstrip())
                    if peek_indent > indent and peek.lstrip().startswith("- "):
                        is_list = True
                    break

                if is_list:
                    current[key] = []
                    list_key = key
                else:
                    new_dict: dict[str, Any] = {}
                    current[key] = new_dict
                    stack.append((indent, new_dict))
                    list_key = None
            elif val.startswith("[") and val.endswith("]"):
                items = [_yaml_scalar(x.strip()) for x in val[1:-1].split(",") if x.strip()]
                current[key] = items
                list_key = key
            else:
                current[key] = _yaml_scalar(val)
                list_key = key

        i += 1

    return result


def _yaml_scalar(val: str):
    """Convert a YAML scalar string to Python type."""
    if val.startswith('"') and val.endswith('"'):
        return val[1:-1]
    if val.startswith("'") and val.endswith("'"):
        return val[1:-1]
    if val.lower() in ("true", "yes"):
        return True
    if val.lower() in ("false", "no"):
        return False
    if val.lower() in ("null", "~", ""):
        return None
    try:
        return int(val)
    except ValueError:
        pass
    try:
        return float(val)
    except ValueError:
        pass
    return val


def _yaml_dumps(data: dict, indent: int = 0) -> str:
    """Minimal YAML emitter."""
    lines: list[str] = []
    prefix = "  " * indent
    for key, val in data.items():
        if isinstance(val, dict):
            lines.append(f"{prefix}{key}:")
            lines.append(_yaml_dumps(val, indent + 1))
        elif isinstance(val, list):
            lines.append(f"{prefix}{key}:")
            for item in val:
                if isinstance(item, dict):
                    first = True
                    for k2, v2 in item.items():
                        if first:
                            lines.append(f"{prefix}  - {k2}: {_format_scalar(v2)}")
                            first = False
                        else:
                            lines.append(f"{prefix}    {k2}: {_format_scalar(v2)}")
                else:
                    lines.append(f"{prefix}  - {_format_scalar(item)}")
        else:
            lines.append(f"{prefix}{key}: {_format_scalar(val)}")
    return "\n".join(lines)


def _format_scalar(val) -> str:
    if val is None:
        return "null"
    if isinstance(val, bool):
        return "true" if val else "false"
    if isinstance(val, str) and (":" in val or "#" in val or val.startswith("{")):
        return f'"{val}"'
    return str(val)


def load_yaml(path: Path) -> dict:
    return _yaml_loads(path.read_text(encoding="utf-8"))


def save_yaml(path: Path, data: dict):
    path.write_text(_yaml_dumps(data) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# Core helpers
# ---------------------------------------------------------------------------

def sha256_of(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]


def find_project_root() -> Path:
    """Walk up to find .ai/ or .git/"""
    cwd = Path.cwd()
    for parent in [cwd, *cwd.parents]:
        if (parent / ".ai").is_dir() or (parent / ".git").is_dir():
            return parent
    return cwd


def strip_yaml_frontmatter(content: str) -> tuple[dict, str]:
    """Strip YAML frontmatter from markdown, return (frontmatter_dict, body)."""
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            try:
                fm = _yaml_loads(parts[1])
                return fm, parts[2]
            except Exception:
                pass
    return {}, content


# ---------------------------------------------------------------------------
# INIT command
# ---------------------------------------------------------------------------

def cmd_init(args):
    """Initialize canonical .ai/ structure."""
    root = find_project_root()
    ai_dir = root / ".ai"
    ai_dir.mkdir(exist_ok=True)
    
    for subdir in ["skills", "guides", "contracts", "memory"]:
        (ai_dir / subdir).mkdir(exist_ok=True)
        
    manifest_path = ai_dir / "manifest.yaml"
    if not manifest_path.exists():
        project_name = args.project_name or root.name
        manifest = {
            "version": "1.0",
            "project": project_name,
            "targets": {
                "claude": {"enabled": True, "output": "CLAUDE.md"},
                "gemini": {"enabled": True, "output": "GEMINI.md"}
            },
            "distribution": [
                {"source": "memory/overview.md", "targets": ["claude", "gemini"]},
                {"source": "guides/standards.md", "targets": ["claude"]}
            ]
        }
        save_yaml(manifest_path, manifest)
        
    # Placeholders
    (ai_dir / "memory" / "overview.md").write_text("# Project Overview\n\nGenerated by nexus-sync.\n", encoding="utf-8")
    (ai_dir / "guides" / "standards.md").write_text("# Coding Standards\n\n- Use clean code\n- Write tests\n", encoding="utf-8")
    
    print(f"✅ Nexus init completed at {ai_dir}")


# ---------------------------------------------------------------------------
# BUILD command
# ---------------------------------------------------------------------------

def cmd_build(args):
    """Build target config files from .ai/ canonical source."""
    root = find_project_root()
    ai_dir = root / ".ai"
    manifest_path = ai_dir / "manifest.yaml"
    
    if not manifest_path.exists():
        print("❌ manifest.yaml not found. Run 'init' first.")
        sys.exit(1)
        
    manifest = load_yaml(manifest_path)
    targets = manifest.get("targets", {})
    distribution = manifest.get("distribution", [])
    
    # Collect content per target
    target_content: dict[str, list[str]] = {t: [] for t in targets}
    
    for entry in distribution:
        source = entry.get("source")
        dist_targets = entry.get("targets", [])
        
        src_path = ai_dir / source
        if not src_path.exists():
            print(f"⚠️  Source not found: {source}")
            continue
            
        content = src_path.read_text(encoding="utf-8")
        _, body = strip_yaml_frontmatter(content)
        
        for t in dist_targets:
            if t in target_content:
                target_content[t].append(body.strip())
                
    # Write to target files
    for t_name, t_cfg in targets.items():
        if not t_cfg.get("enabled", False):
            continue
            
        output_file = root / t_cfg.get("output", f"{t_name.upper()}.md")
        combined = "\n\n---\n\n".join(target_content[t_name])
        
        if args.dry_run:
            print(f"[DRY RUN] Would write to {output_file}")
        else:
            output_file.write_text(combined, encoding="utf-8")
            print(f"✅ Generated {output_file}")


# ---------------------------------------------------------------------------
# DIFF / STATUS commands
# ---------------------------------------------------------------------------

def cmd_diff(args):
    """Check for drift between .ai/ and generated files."""
    print("🔍 Checking for drift... (Not fully implemented)")


def cmd_status(args):
    """Show current sync status."""
    root = find_project_root()
    ai_dir = root / ".ai"
    print(f"Nexus Sync Status:")
    print(f"  Root: {root}")
    print(f"  Canonical: {ai_dir}")
    
    lock_file = root / ".nexus-sync.lock"
    if lock_file.exists():
        lock_data = json.loads(lock_file.read_text())
        gen_at = lock_data.get("generated_at", "bilinmiyor")
        print(f"\n   Son build: {gen_at}")
    else:
        print(f"\n   ⚠️  Henüz build yapılmamış")


# ---------------------------------------------------------------------------
# VALIDATE command
# ---------------------------------------------------------------------------

def cmd_validate(args):
    """Validate manifest.yaml and source files."""
    if getattr(args, "global_mode", False):
        _cmd_validate_global(args)
        return

    root = find_project_root()
    ai_dir = root / ".ai"
    errors: list[str] = []
    warnings: list[str] = []

    manifest_path = ai_dir / "manifest.yaml"
    if not manifest_path.exists():
        errors.append("manifest.yaml bulunamadı")
    else:
        manifest = load_yaml(manifest_path)

        # Check required fields
        if "targets" not in manifest:
            errors.append("manifest.yaml: 'targets' alanı eksik")
        if "distribution" not in manifest:
            errors.append("manifest.yaml: 'distribution' alanı eksik")

        # Check distributions reference existing files
        for dist in manifest.get("distribution", []):
            if not isinstance(dist, dict):
                continue
            source = dist.get("source", "")
            if "*" not in str(source):
                src_path = ai_dir / str(source)
                if not src_path.exists():
                    warnings.append(f"Kaynak bulunamadı: {source}")

    # Check for orphan files (not referenced in any distribution)
    all_sources = set()
    for subdir in ["skills", "guides", "contracts", "memory"]:
        d = ai_dir / subdir
        if d.exists():
            for f in d.rglob("*.md"):
                all_sources.add(str(f.relative_to(ai_dir)))

    if errors:
        print("❌ Validation FAILED:")
        for e in errors:
            print(f"   • {e}")
    if warnings:
        print("⚠️  Warnings:")
        for w in warnings:
            print(f"   • {w}")
    if not errors and not warnings:
        print("✅ Validation passed. Tüm dosyalar geçerli.")

    if errors:
        sys.exit(1)


def _cmd_validate_global(args):
    """Validate ~/.ai/manifest.yaml and all referenced sources."""
    ai_dir = Path.home() / ".ai"
    errors: list[str] = []
    warnings: list[str] = []

    print("🔍 Global validation: ~/.ai/manifest.yaml\n")

    # 1. manifest.yaml var mı?
    manifest_path = ai_dir / "manifest.yaml"
    if not manifest_path.exists():
        print("❌ ~/.ai/manifest.yaml bulunamadı.")
        sys.exit(1)

    manifest = load_yaml(manifest_path)

# ---------------------------------------------------------------------------
# Main CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        prog="nexus-sync",
        description="Universal AI Config Sync — tek kaynak, tüm AI araçlara dağıtım",
    )
    sub = parser.add_subparsers(dest="command")

    # init, build, diff, status, validate, add, import, install-hooks
    p_init = sub.add_parser("init", help="Canonical .ai/ yapısını başlat")
    p_init.add_argument("--project-name", default=None)

    p_build = sub.add_parser("build", help="Canonical → target dosyalara transpile et")
    p_build.add_argument("--target", choices=["claude", "gemini", "agents"], default=None)
    p_build.add_argument("--dry-run", action="store_true")

    sub.add_parser("diff", help="Canonical vs generated fark analizi")
    sub.add_parser("status", help="Sync durumu")
    p_validate = sub.add_parser("validate", help="manifest.yaml doğrulama")
    p_validate.add_argument("--global", dest="global_mode", action="store_true")

    args = parser.parse_args()

    commands = {
        "init": cmd_init,
        "build": cmd_build,
        "diff": cmd_diff,
        "status": cmd_status,
        "validate": cmd_validate,
    }

    if args.command in commands:
        commands[args.command](args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
