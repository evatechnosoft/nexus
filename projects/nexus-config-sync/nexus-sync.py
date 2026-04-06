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
            fm = _yaml_loads(parts[1])
            body = parts[2].lstrip("\n")
            return fm, body
    return {}, content


def add_yaml_frontmatter(body: str, frontmatter: dict) -> str:
    """Add YAML frontmatter to markdown body."""
    if not frontmatter:
        return body
    fm_str = _yaml_dumps(frontmatter)
    return f"---\n{fm_str}\n---\n\n{body}"


# ---------------------------------------------------------------------------
# INIT command
# ---------------------------------------------------------------------------

def cmd_init(args):
    """Initialize .ai/ canonical structure."""
    root = Path.cwd()
    ai_dir = root / ".ai"

    if ai_dir.exists():
        print("⚠️  .ai/ zaten mevcut. Mevcut dosyalar korunacak.")
    else:
        print("📁 .ai/ dizin yapısı oluşturuluyor...")

    # Create directories
    for d in ["skills", "guides", "contracts", "memory", "templates"]:
        (ai_dir / d).mkdir(parents=True, exist_ok=True)

    project_name = getattr(args, "project_name", None) or root.name

    # Create manifest.yaml if not exists
    manifest_path = ai_dir / "manifest.yaml"
    if not manifest_path.exists():
        manifest_content = textwrap.dedent(f"""\
        version: "1.0"

        project:
          name: "{project_name}"
          description: "Project description"

        targets:
          claude:
            enabled: true
            strategy: merged
            max_lines: 200
          gemini:
            enabled: true
            strategy: merged
            imports: true
          agents:
            enabled: false

        distribution:
          - source: "skills/*"
            targets: [claude, gemini]
            scope: project
          - source: "guides/*"
            targets: [claude, gemini]
            scope: project
          - source: "contracts/*"
            targets: [claude, gemini]
            scope: project
          - source: "memory/project-context.md"
            targets: [claude, gemini]
            scope: project
          - source: "memory/preferences.md"
            targets: [claude, gemini]
            scope: global
        """)
        manifest_path.write_text(manifest_content, encoding="utf-8")
        print(f"  ✅ {manifest_path.relative_to(root)}")

    # Create sample project-context
    ctx_path = ai_dir / "memory" / "project-context.md"
    if not ctx_path.exists():
        ctx_path.write_text(textwrap.dedent(f"""\
        # Project: {project_name}

        ## Overview
        <!-- Projenin kısa açıklaması -->

        ## Architecture
        <!-- Temel mimari kararlar -->

        ## Key Directories
        <!-- Önemli dizin yapısı -->

        ## Common Commands
        ```bash
        # build
        # test
        # lint
        ```
        """), encoding="utf-8")
        print(f"  ✅ {ctx_path.relative_to(root)}")

    # Create sample preferences
    pref_path = ai_dir / "memory" / "preferences.md"
    if not pref_path.exists():
        pref_path.write_text(textwrap.dedent("""\
        # Personal Preferences

        ## Code Style
        - 2 space indentation
        - Strict typing everywhere
        - Prefer functional patterns

        ## Communication
        - Türkçe tercih edilir
        - Kısa ve direkt cevaplar
        - Gereksiz açıklama yapma
        """), encoding="utf-8")
        print(f"  ✅ {pref_path.relative_to(root)}")

    # Create .gitattributes entry
    gitattr_path = root / ".gitattributes"
    marker = "# nexus-sync generated files"
    existing = gitattr_path.read_text() if gitattr_path.exists() else ""
    if marker not in existing:
        with open(gitattr_path, "a", encoding="utf-8") as f:
            f.write(f"\n{marker}\n")
            f.write("CLAUDE.md linguist-generated=true merge=ours\n")
            f.write("GEMINI.md linguist-generated=true merge=ours\n")
            f.write("AGENTS.md linguist-generated=true merge=ours\n")
            f.write(".claude/rules/** linguist-generated=true merge=ours\n")
        print(f"  ✅ .gitattributes güncellendi")

    print(f"\n🎉 Başlatma tamamlandı. Sonraki adımlar:")
    print(f"   1. .ai/manifest.yaml dosyasını düzenle")
    print(f"   2. .ai/skills/ ve .ai/guides/ altına içerik ekle")
    print(f"   3. nexus-sync build çalıştır")


# ---------------------------------------------------------------------------
# BUILD command — the core transpiler
# ---------------------------------------------------------------------------

def cmd_build(args):
    """Transpile canonical .ai/ → target config files."""
    root = find_project_root()
    ai_dir = root / ".ai"

    if not ai_dir.exists():
        print("❌ .ai/ dizini bulunamadı. Önce 'nexus-sync init' çalıştır.")
        sys.exit(1)

    manifest_path = ai_dir / "manifest.yaml"
    if not manifest_path.exists():
        print("❌ .ai/manifest.yaml bulunamadı.")
        sys.exit(1)

    manifest = load_yaml(manifest_path)
    targets = manifest.get("targets", {})
    distributions = manifest.get("distribution", [])

    target_filter = getattr(args, "target", None)
    dry_run = getattr(args, "dry_run", False)
    lock_data: dict[str, str] = {}

    # Collect source files per target
    target_sources: dict[str, list[tuple[Path, dict]]] = {}

    for dist in distributions:
        if not isinstance(dist, dict):
            continue
        source_glob = dist.get("source", "")
        dist_targets = dist.get("targets", [])
        if isinstance(dist_targets, str):
            dist_targets = [dist_targets]

        scope = dist.get("scope", "project")

        # Resolve source files
        source_files = []
        if "*" in str(source_glob):
            base_dir = ai_dir / str(source_glob).rsplit("/*", 1)[0] if "/*" in str(source_glob) else ai_dir
            if base_dir.is_dir():
                for f in sorted(base_dir.rglob("*.md")):
                    source_files.append(f)
        else:
            src_path = ai_dir / str(source_glob)
            if src_path.exists():
                if src_path.is_dir():
                    source_files.extend(sorted(src_path.rglob("*.md")))
                else:
                    source_files.append(src_path)

        for t in dist_targets:
            t_str = str(t)
            if target_filter and t_str != target_filter:
                continue
            if t_str not in target_sources:
                target_sources[t_str] = []
            for sf in source_files:
                target_sources[t_str].append((sf, {
                    "scope": scope,
                    "claude_rule_path": dist.get("claude_rule_path"),
                    "claude_rule_paths": dist.get("claude_rule_paths"),
                }))

    # Build each target
    for target_name, sources in target_sources.items():
        target_config = targets.get(target_name, {})
        if not target_config:
            continue
        enabled = target_config.get("enabled", False)
        if not enabled:
            print(f"⏭️  {target_name}: disabled, skipping")
            continue

        print(f"\n🔨 Building target: {target_name}")
        strategy = target_config.get("strategy", "merged")

        if target_name == "claude":
            _build_claude(root, ai_dir, sources, target_config, dry_run, lock_data)
        elif target_name == "gemini":
            _build_gemini(root, ai_dir, sources, target_config, dry_run, lock_data)
        elif target_name == "agents":
            _build_agents(root, ai_dir, sources, target_config, dry_run, lock_data)

    # Write lock file
    if not dry_run:
        lock_path = root / ".nexus-sync.lock"
        lock_content = json.dumps({
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "files": lock_data,
        }, indent=2, ensure_ascii=False)
        lock_path.write_text(lock_content, encoding="utf-8")
        print(f"\n🔒 Lock dosyası güncellendi: .nexus-sync.lock")

    print("\n✅ Build tamamlandı.")


def _build_claude(root: Path, ai_dir: Path, sources: list, config: dict, dry_run: bool, lock: dict):
    """Build Claude Code target files."""
    max_lines = config.get("max_lines", 200)
    sections: list[str] = []
    rules: list[tuple[str, str, str | None]] = []  # (name, content, paths_glob)

    header = "<!-- Generated by nexus-sync. DO NOT EDIT. Modify .ai/ sources instead. -->\n\n"

    for src_path, dist_meta in sources:
        raw = src_path.read_text(encoding="utf-8")
        fm, body = strip_yaml_frontmatter(raw)
        body = body.strip()
        if not body:
            continue

        scope = dist_meta.get("scope", "project")
        rule_path = dist_meta.get("claude_rule_path")
        rule_paths_glob = dist_meta.get("claude_rule_paths")

        # Determine if this should be a separate rule file
        rel = src_path.relative_to(ai_dir)
        section_name = fm.get("name", rel.stem)

        if rule_path or rule_paths_glob:
            # Write as .claude/rules/ file
            rules.append((str(rule_path or section_name), body, rule_paths_glob))
        else:
            # Add to main CLAUDE.md
            sections.append(f"## {section_name}\n\n{body}")

    # Write CLAUDE.md
    claude_md_content = header + "\n\n".join(sections)
    claude_md_path = root / "CLAUDE.md"

    if dry_run:
        line_count = claude_md_content.count("\n")
        print(f"  [DRY] CLAUDE.md → {line_count} satır")
    else:
        claude_md_path.write_text(claude_md_content, encoding="utf-8")
        lock["CLAUDE.md"] = sha256_of(claude_md_content)
        line_count = claude_md_content.count("\n")
        status = "⚠️ UZUN" if line_count > max_lines else "✅"
        print(f"  {status} CLAUDE.md → {line_count} satır")

    # Write .claude/rules/ files
    if rules:
        rules_dir = root / ".claude" / "rules"
        rules_dir.mkdir(parents=True, exist_ok=True)
        for rule_name, rule_body, paths_glob in rules:
            rule_file = rules_dir / f"{rule_name}.md"
            content = rule_body
            if paths_glob:
                content = add_yaml_frontmatter(rule_body, {"paths": [paths_glob]})
            content = header + content

            if dry_run:
                print(f"  [DRY] .claude/rules/{rule_name}.md")
            else:
                rule_file.write_text(content, encoding="utf-8")
                rel_path = str(rule_file.relative_to(root))
                lock[rel_path] = sha256_of(content)
                print(f"  ✅ .claude/rules/{rule_name}.md")


def _build_gemini(root: Path, ai_dir: Path, sources: list, config: dict, dry_run: bool, lock: dict):
    """Build Gemini CLI target files."""
    use_imports = config.get("imports", False)
    sections: list[str] = []

    header = "<!-- Generated by nexus-sync. DO NOT EDIT. Modify .ai/ sources instead. -->\n\n"

    for src_path, dist_meta in sources:
        raw = src_path.read_text(encoding="utf-8")
        fm, body = strip_yaml_frontmatter(raw)
        body = body.strip()
        if not body:
            continue

        rel = src_path.relative_to(ai_dir)
        section_name = fm.get("name", rel.stem)

        if use_imports:
            # Gemini supports @./path imports — reference the canonical file
            canonical_rel = f".ai/{rel}"
            sections.append(f"## {section_name}\n\n@./{canonical_rel}")
        else:
            sections.append(f"## {section_name}\n\n{body}")

    gemini_md_content = header + "\n\n".join(sections)
    gemini_md_path = root / "GEMINI.md"

    if dry_run:
        print(f"  [DRY] GEMINI.md → {gemini_md_content.count(chr(10))} satır")
    else:
        gemini_md_path.write_text(gemini_md_content, encoding="utf-8")
        lock["GEMINI.md"] = sha256_of(gemini_md_content)
        print(f"  ✅ GEMINI.md → {gemini_md_content.count(chr(10))} satır")


def _build_agents(root: Path, ai_dir: Path, sources: list, config: dict, dry_run: bool, lock: dict):
    """Build AGENTS.md (cross-tool)."""
    sections: list[str] = []
    header = "<!-- Generated by nexus-sync. DO NOT EDIT. Modify .ai/ sources instead. -->\n\n"

    for src_path, dist_meta in sources:
        raw = src_path.read_text(encoding="utf-8")
        fm, body = strip_yaml_frontmatter(raw)
        body = body.strip()
        if not body:
            continue
        rel = src_path.relative_to(ai_dir)
        section_name = fm.get("name", rel.stem)
        sections.append(f"## {section_name}\n\n{body}")

    agents_content = header + "\n\n".join(sections)
    agents_path = root / "AGENTS.md"

    if dry_run:
        print(f"  [DRY] AGENTS.md → {agents_content.count(chr(10))} satır")
    else:
        agents_path.write_text(agents_content, encoding="utf-8")
        lock["AGENTS.md"] = sha256_of(agents_content)
        print(f"  ✅ AGENTS.md → {agents_content.count(chr(10))} satır")


# ---------------------------------------------------------------------------
# DIFF command
# ---------------------------------------------------------------------------

def cmd_diff(args):
    """Show drift between canonical and generated files."""
    if getattr(args, "global_mode", False):
        _cmd_diff_global(args)
        return

    root = find_project_root()
    lock_path = root / ".nexus-sync.lock"

    if not lock_path.exists():
        print("❌ .nexus-sync.lock bulunamadı. Önce 'nexus-sync build' çalıştır.")
        sys.exit(1)

    lock_data = json.loads(lock_path.read_text(encoding="utf-8"))
    files = lock_data.get("files", {})
    has_drift = False

    for filepath, expected_hash in files.items():
        full_path = root / filepath
        if not full_path.exists():
            print(f"  ❌ MISSING: {filepath}")
            has_drift = True
            continue

        actual_hash = sha256_of(full_path.read_text(encoding="utf-8"))
        if actual_hash != expected_hash:
            print(f"  ⚠️  DRIFT: {filepath} (expected={expected_hash}, actual={actual_hash})")
            has_drift = True
        else:
            print(f"  ✅ OK: {filepath}")

    if has_drift:
        print("\n⚠️  Drift tespit edildi. 'nexus-sync build' ile yeniden oluştur.")
        if getattr(args, "exit_code", False):
            sys.exit(1)
    else:
        print("\n✅ Tüm generated dosyalar canonical ile uyumlu.")


def _cmd_diff_global(args):
    """Compare ~/.ai/memory/ vs currently built outputs."""
    ai_dir = GLOBAL_AI_DIR
    manifest_path = ai_dir / "manifest.yaml"
    if not manifest_path.exists():
        print("❌ ~/.ai/manifest.yaml bulunamadı.")
        sys.exit(1)

    manifest = load_yaml(manifest_path)
    distributions = manifest.get("distribution", [])
    has_drift = False

    print("📊 Global diff: ~/.ai/ → built outputs\n")

    # Build expected content per rule file and check each
    claude_cfg = manifest.get("targets", {}).get("claude", {})
    out_cfg = claude_cfg.get("output", {})
    rules_dir = Path(str(out_cfg.get("rules_dir", str(Path.home() / ".claude" / "rules"))))
    global_claude = Path(str(out_cfg.get("global_path", str(Path.home() / ".claude" / "CLAUDE.md"))))

    gemini_cfg = manifest.get("targets", {}).get("gemini", {})
    gemini_out = gemini_cfg.get("output", {})
    global_gemini = Path(str(gemini_out.get("global_path", str(Path.home() / ".gemini" / "GEMINI.md"))))

    header = "<!-- Generated by nexus-sync global-build. DO NOT EDIT. Edit ~/.ai/memory/ instead. -->\n\n"

    for dist in distributions:
        if not isinstance(dist, dict):
            continue
        source_str = dist.get("source", "")
        dist_targets = dist.get("targets", [])
        if isinstance(dist_targets, str):
            dist_targets = [dist_targets]
        dist_targets = [str(t) for t in dist_targets]
        rule_path = dist.get("claude_rule_path")

        src_path = ai_dir / source_str
        if not src_path.exists():
            print(f"  ❌ SOURCE MISSING: {source_str}")
            has_drift = True
            continue

        canonical_content = src_path.read_text(encoding="utf-8")
        _, canonical_body = strip_yaml_frontmatter(canonical_content)
        canonical_body = canonical_body.strip()

        # Check rule file if applicable
        if "claude" in dist_targets and rule_path:
            rule_file = rules_dir / f"{rule_path}.md"
            expected = header + canonical_body
            if not rule_file.exists():
                print(f"  ❌ MISSING:  rules/{rule_path}.md")
                has_drift = True
            else:
                actual = rule_file.read_text(encoding="utf-8")
                if sha256_of(actual) != sha256_of(expected):
                    print(f"  ⚠️  DRIFT:   rules/{rule_path}.md")
                    has_drift = True
                else:
                    print(f"  ✅ OK:      rules/{rule_path}.md")

    # Check CLAUDE.md contains generated section
    if global_claude.exists():
        claude_content = global_claude.read_text(encoding="utf-8")
        if _CLAUDE_GENERATED_START in claude_content and _CLAUDE_GENERATED_END in claude_content:
            print(f"  ✅ OK:      {global_claude.name} (generated section present)")
        else:
            print(f"  ⚠️  DRIFT:   {global_claude.name} (generated section missing — run global-build)")
            has_drift = True
        if not claude_content.splitlines()[0].startswith("@"):
            print(f"  ⚠️  WARN:    {global_claude.name} — first line is not an @import")
    else:
        print(f"  ❌ MISSING: {global_claude}")
        has_drift = True

    # Check GEMINI.md contains generated section
    if global_gemini.exists():
        gemini_content = global_gemini.read_text(encoding="utf-8")
        if _GEMINI_GENERATED_START in gemini_content and _GEMINI_GENERATED_END in gemini_content:
            print(f"  ✅ OK:      {global_gemini.name} (generated section present)")
        else:
            print(f"  ⚠️  DRIFT:   {global_gemini.name} (generated section missing — run global-build)")
            has_drift = True
    else:
        print(f"  ❌ MISSING: {global_gemini}")
        has_drift = True

    if has_drift:
        print("\n⚠️  Drift tespit edildi. 'nexus-sync global-build' ile yeniden oluştur.")
        if getattr(args, "exit_code", False):
            sys.exit(1)
    else:
        print("\n✅ Tüm global outputs canonical ile uyumlu.")


# ---------------------------------------------------------------------------
# STATUS command
# ---------------------------------------------------------------------------

def cmd_status(args):
    """Show current sync status."""
    root = find_project_root()
    ai_dir = root / ".ai"

    if not ai_dir.exists():
        print("❌ .ai/ dizini bulunamadı.")
        sys.exit(1)

    # Count sources
    skills = list((ai_dir / "skills").rglob("*.md")) if (ai_dir / "skills").exists() else []
    guides = list((ai_dir / "guides").rglob("*.md")) if (ai_dir / "guides").exists() else []
    contracts = list((ai_dir / "contracts").rglob("*.md")) if (ai_dir / "contracts").exists() else []
    memory = list((ai_dir / "memory").rglob("*.md")) if (ai_dir / "memory").exists() else []

    print("📊 AI Config Sync Status")
    print(f"   Project root: {root}")
    print(f"   Skills:    {len(skills)}")
    print(f"   Guides:    {len(guides)}")
    print(f"   Contracts: {len(contracts)}")
    print(f"   Memory:    {len(memory)}")

    # Check targets
    manifest_path = ai_dir / "manifest.yaml"
    if manifest_path.exists():
        manifest = load_yaml(manifest_path)
        targets = manifest.get("targets", {})
        print(f"\n   Targets:")
        for t, cfg in targets.items():
            if isinstance(cfg, dict):
                enabled = cfg.get("enabled", False)
                symbol = "✅" if enabled else "⏭️"
                print(f"     {symbol} {t}")

    # Check lock
    lock_path = root / ".nexus-sync.lock"
    if lock_path.exists():
        lock_data = json.loads(lock_path.read_text(encoding="utf-8"))
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
    ai_dir = GLOBAL_AI_DIR
    errors: list[str] = []
    warnings: list[str] = []

    print("🔍 Global validation: ~/.ai/manifest.yaml\n")

    # 1. manifest.yaml var mı?
    manifest_path = ai_dir / "manifest.yaml"
    if not manifest_path.exists():
        print("❌ ~/.ai/manifest.yaml bulunamadı. Önce 'nexus-sync global-init' çalıştır.")
        sys.exit(1)

    manifest = load_yaml(manifest_path)

    # 2. Zorunlu alanlar
    for field in ("version", "targets", "distribution"):
        if field not in manifest:
            errors.append(f"manifest.yaml: '{field}' alanı eksik")

    # 3. Target output paths kontrol
    targets = manifest.get("targets", {})
    for t_name, t_cfg in targets.items():
        if not isinstance(t_cfg, dict):
            continue
        if not t_cfg.get("enabled", False):
            warnings.append(f"targets.{t_name}: disabled")
            continue
        out = t_cfg.get("output", {})
        if isinstance(out, dict):
            gp = out.get("global_path")
            if gp:
                parent = Path(str(gp)).parent
                if not parent.exists():
                    warnings.append(f"targets.{t_name}.output.global_path parent dizin yok: {parent}")
            if t_name == "claude":
                rd = out.get("rules_dir")
                if rd and not Path(str(rd)).exists():
                    warnings.append(f"targets.claude.output.rules_dir yok (build sonrası oluşur): {rd}")

    # 4. Distribution source dosyaları var mı?
    distributions = manifest.get("distribution", [])
    referenced: set[str] = set()
    for dist in distributions:
        if not isinstance(dist, dict):
            continue
        source = dist.get("source", "")
        if not source:
            errors.append("distribution entry: 'source' alanı eksik")
            continue
        referenced.add(str(source))
        src_path = ai_dir / str(source)
        if not src_path.exists():
            errors.append(f"source bulunamadı: {source}")
        else:
            content = src_path.read_text(encoding="utf-8").strip()
            if content.endswith("-->"):
                warnings.append(f"placeholder (henüz doldurulmamış): {source}")
            elif len(content.splitlines()) < 3:
                warnings.append(f"çok kısa (placeholder olabilir): {source}")

        dist_targets = dist.get("targets", [])
        if isinstance(dist_targets, str):
            dist_targets = [dist_targets]
        for t in dist_targets:
            if str(t) not in targets:
                errors.append(f"distribution '{source}': bilinmeyen target '{t}'")

    # 5. ~/.ai/memory/'de referenced olmayan dosyalar
    memory_dir = ai_dir / "memory"
    if memory_dir.exists():
        for f in sorted(memory_dir.rglob("*.md")):
            rel = "memory/" + f.name
            if rel not in referenced:
                warnings.append(f"distribution'da referans yok (orphan): {rel}")

    # Çıktı
    if errors:
        print("❌ Validation FAILED:")
        for e in errors:
            print(f"   • {e}")
    if warnings:
        print("⚠️  Warnings:")
        for w in warnings:
            print(f"   • {w}")
    if not errors and not warnings:
        print("✅ Global validation passed.")
    elif not errors:
        print("\n✅ Validation passed (warnings var ama kritik hata yok).")

    if errors:
        sys.exit(1)


# ---------------------------------------------------------------------------
# ADD command
# ---------------------------------------------------------------------------

def cmd_add(args):
    """Scaffold a new skill or guide."""
    root = find_project_root()
    ai_dir = root / ".ai"
    kind = args.kind  # "skill" or "guide"
    name = args.name

    if kind == "skill":
        skill_dir = ai_dir / "skills" / name
        skill_dir.mkdir(parents=True, exist_ok=True)
        skill_file = skill_dir / "skill.md"
        if not skill_file.exists():
            skill_file.write_text(textwrap.dedent(f"""\
            ---
            name: {name}
            description: "{name} skill açıklaması"
            ---

            ## Genel Bakış
            <!-- Bu skill ne yapar -->

            ## Temel Talimatlar
            <!-- Kurallar ve yönergeler -->

            ## Örnek Kullanım
            <!-- Girdi/çıktı örnekleri -->
            """), encoding="utf-8")
        print(f"✅ Skill oluşturuldu: .ai/skills/{name}/skill.md")

    elif kind == "guide":
        guide_file = ai_dir / "guides" / f"{name}.md"
        guide_file.parent.mkdir(parents=True, exist_ok=True)
        if not guide_file.exists():
            guide_file.write_text(textwrap.dedent(f"""\
            # {name.replace('-', ' ').title()}

            ## Kurallar
            <!-- Coding standartları -->

            ## Örnekler
            <!-- Doğru/yanlış örnekler -->
            """), encoding="utf-8")
        print(f"✅ Guide oluşturuldu: .ai/guides/{name}.md")


# ---------------------------------------------------------------------------
# IMPORT command — reverse-engineer existing configs
# ---------------------------------------------------------------------------

def cmd_import(args):
    """Import from existing CLAUDE.md or GEMINI.md into canonical .ai/"""
    root = find_project_root()
    ai_dir = root / ".ai"
    source_tool = args.source_tool  # "claude" or "gemini"

    if source_tool == "claude":
        source_file = root / "CLAUDE.md"
    elif source_tool == "gemini":
        source_file = root / "GEMINI.md"
    else:
        print(f"❌ Bilinmeyen kaynak: {source_tool}")
        sys.exit(1)

    if not source_file.exists():
        print(f"❌ {source_file.name} bulunamadı.")
        sys.exit(1)

    content = source_file.read_text(encoding="utf-8")
    fm, body = strip_yaml_frontmatter(content)

    # Parse sections by ## headers
    sections = re.split(r'^## ', body, flags=re.MULTILINE)
    imported_count = 0

    for section in sections:
        section = section.strip()
        if not section:
            continue

        # First line is the section title
        lines = section.split("\n", 1)
        title = lines[0].strip()
        body_text = lines[1].strip() if len(lines) > 1 else ""

        if not body_text:
            continue

        # Determine category based on keywords
        title_lower = title.lower()
        if any(kw in title_lower for kw in ["skill", "beceri", "capability"]):
            category = "skills"
            dest = ai_dir / category / _slugify(title) / "skill.md"
        elif any(kw in title_lower for kw in ["style", "code", "lint", "format", "test", "security"]):
            category = "guides"
            dest = ai_dir / category / f"{_slugify(title)}.md"
        elif any(kw in title_lower for kw in ["project", "overview", "about", "context"]):
            category = "memory"
            dest = ai_dir / category / f"{_slugify(title)}.md"
        elif any(kw in title_lower for kw in ["api", "contract", "architecture", "decision"]):
            category = "contracts"
            dest = ai_dir / category / f"{_slugify(title)}.md"
        else:
            category = "guides"
            dest = ai_dir / category / f"{_slugify(title)}.md"

        dest.parent.mkdir(parents=True, exist_ok=True)
        if not dest.exists():
            full_content = f"## {title}\n\n{body_text}"
            dest.write_text(full_content, encoding="utf-8")
            print(f"  ✅ {category}/{dest.name}")
            imported_count += 1
        else:
            print(f"  ⏭️  Zaten mevcut: {category}/{dest.name}")

    print(f"\n📥 {imported_count} section import edildi.")
    print(f"   Sonra: manifest.yaml'ı kontrol et ve 'nexus-sync build' çalıştır.")


def _slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s]+', '-', text)
    return text[:50]


# ---------------------------------------------------------------------------
# INSTALL-HOOKS command
# ---------------------------------------------------------------------------

def cmd_install_hooks(args):
    """Install git pre-commit hook for auto-sync."""
    root = find_project_root()
    hooks_dir = root / ".git" / "hooks"

    if not hooks_dir.exists():
        print("❌ .git/hooks dizini bulunamadı. Git repo'su mu bu?")
        sys.exit(1)

    hook_path = hooks_dir / "pre-commit"
    hook_content = textwrap.dedent("""\
    #!/bin/sh
    # nexus-sync: Auto-build AI config files before commit
    # Installed by: nexus-sync install-hooks

    if [ -d ".ai" ]; then
        echo "🔄 nexus-sync: Building AI configs..."
        python3 nexus-sync.py build 2>/dev/null || python nexus-sync.py build 2>/dev/null
        if [ $? -eq 0 ]; then
            git add CLAUDE.md GEMINI.md AGENTS.md .claude/rules/ .nexus-sync.lock 2>/dev/null
            echo "✅ nexus-sync: Config files updated and staged."
        else
            echo "⚠️  nexus-sync: Build failed, committing without update."
        fi
    fi
    """)

    # Preserve existing hook content
    if hook_path.exists():
        existing = hook_path.read_text(encoding="utf-8")
        if "nexus-sync" in existing:
            print("⏭️  Git hook zaten kurulu.")
            return
        # Append to existing
        hook_content = existing.rstrip() + "\n\n" + hook_content

    hook_path.write_text(hook_content, encoding="utf-8")
    hook_path.chmod(0o755)
    print("✅ Git pre-commit hook kuruldu.")
    print("   Her commit'te AI config dosyaları otomatik güncellenecek.")


# ---------------------------------------------------------------------------
# GLOBAL COMMANDS — ~/.ai/ canonical source for all AI tools
# ---------------------------------------------------------------------------

GLOBAL_AI_DIR = Path.home() / ".ai"
_CLAUDE_GENERATED_START = "<!-- nexus-sync: BEGIN generated memory section -->"
_CLAUDE_GENERATED_END   = "<!-- nexus-sync: END generated memory section -->"
_GEMINI_GENERATED_START = "<!-- BEGIN nexus-sync generated section -->"
_GEMINI_GENERATED_END   = "<!-- END nexus-sync generated section -->"


def cmd_global_init(args):
    """Initialize ~/.ai/ global canonical structure."""
    ai_dir = GLOBAL_AI_DIR

    if ai_dir.exists():
        print("⚠️  ~/.ai/ zaten mevcut. Mevcut dosyalar korunacak.")
    else:
        print("📁 ~/.ai/ dizin yapısı oluşturuluyor...")

    for d in ["memory", "skills", "guides", "commands", "config", "hooks", "plugins"]:
        (ai_dir / d).mkdir(parents=True, exist_ok=True)
        print(f"  ✅ ~/.ai/{d}/")

    manifest_path = ai_dir / "manifest.yaml"
    if not manifest_path.exists():
        home = str(Path.home()).replace("\\", "/")
        manifest_content = textwrap.dedent(f"""\
        version: "1.0"
        mode: global

        targets:
          claude:
            enabled: true
            output:
              global_path: "{home}/.claude/CLAUDE.md"
              rules_dir: "{home}/.claude/rules/"
          gemini:
            enabled: true
            output:
              global_path: "{home}/.gemini/GEMINI.md"

        skill_libraries:
          - id: claude-skills
            path: "{home}/.claude/skills/"
          - id: antigravity-skills
            path: "C:/projects/Antigravity/skills/"

        distribution:
          - source: "memory/profile.md"
            targets: [claude, gemini]
          - source: "memory/preferences.md"
            targets: [claude, gemini]
          - source: "memory/decisions.md"
            targets: [claude]
            claude_rule_path: "memory-decisions"
          - source: "memory/sessions.md"
            targets: [claude]
            claude_rule_path: "memory-sessions"
          - source: "memory/projects.md"
            targets: [claude, gemini]
            claude_rule_path: "projects"
          - source: "memory/best-practices.md"
            targets: [claude, gemini]
            claude_rule_path: "best-practices"
          - source: "memory/security-notes.md"
            targets: [claude, gemini]
            claude_rule_path: "security-mcp-notes"
        """)
        manifest_path.write_text(manifest_content, encoding="utf-8")
        print("  ✅ ~/.ai/manifest.yaml")
    else:
        print("  ⏭️  ~/.ai/manifest.yaml zaten mevcut, korundu")

    placeholders = {
        "profile.md":       "# Kullanıcı Profili\n\n<!-- global-import ile doldurulacak -->\n",
        "preferences.md":   "# Çalışma Tercihleri\n\n<!-- global-import ile doldurulacak -->\n",
        "decisions.md":     "# Geçmiş Kararlar\n\n<!-- global-import ile doldurulacak -->\n",
        "sessions.md":      "# Oturum Özeti\n\n<!-- global-import ile doldurulacak -->\n",
        "projects.md":      "# Projeler\n\n<!-- global-import ile doldurulacak -->\n",
        "best-practices.md":"# Best Practices\n\n<!-- global-import ile doldurulacak -->\n",
        "security-notes.md":"# Güvenlik Notları\n\n<!-- global-import ile doldurulacak -->\n",
    }
    for fname, content in placeholders.items():
        fpath = ai_dir / "memory" / fname
        if not fpath.exists():
            fpath.write_text(content, encoding="utf-8")
            print(f"  ✅ ~/.ai/memory/{fname} (placeholder)")
        else:
            print(f"  ⏭️  ~/.ai/memory/{fname} zaten mevcut")

    print("\n🎉 Global init tamamlandı.")
    print("   Sıradaki: global-import çalıştır → ~/.claude/rules/ kaynaklarını içe aktarır")


def cmd_global_import(args):
    """Copy ~/.claude/rules/*.md → ~/.ai/memory/ (one-time migration)."""
    claude_rules_dir = Path.home() / ".claude" / "rules"
    ai_memory_dir = GLOBAL_AI_DIR / "memory"
    force = getattr(args, "force", False)

    if not claude_rules_dir.exists():
        print("❌ ~/.claude/rules/ dizini bulunamadı.")
        sys.exit(1)
    if not ai_memory_dir.exists():
        print("❌ ~/.ai/memory/ bulunamadı. Önce 'nexus-sync global-init' çalıştır.")
        sys.exit(1)

    memory_map = {
        "memory-profile.md":    "profile.md",
        "memory-preferences.md":"preferences.md",
        "memory-decisions.md":  "decisions.md",
        "memory-sessions.md":   "sessions.md",
        "projects.md":          "projects.md",
        "best-practices.md":    "best-practices.md",
        "security-mcp-notes.md":"security-notes.md",
    }

    imported = skipped = missing = 0

    def _copy_file(src_path: Path, dst_path: Path, label: str) -> None:
        nonlocal imported, skipped, missing
        if not src_path.exists():
            print(f"  ⚠️  Kaynak bulunamadı: {label}")
            missing += 1
            return
        if dst_path.exists() and not force:
            existing = dst_path.read_text(encoding="utf-8").strip()
            is_placeholder = existing.endswith("-->") or len(existing.splitlines()) <= 3
            if not is_placeholder:
                print(f"  ⏭️  {dst_path.name} zaten dolu (--force ile üzerine yaz)")
                skipped += 1
                return
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        dst_path.write_text(src_path.read_text(encoding="utf-8"), encoding="utf-8")
        print(f"  ✅ {label} → ~/.ai/{dst_path.relative_to(GLOBAL_AI_DIR).as_posix()}")
        imported += 1

    def _copy_dir(src_dir: Path, dst_dir: Path, exts: tuple = (".md",), label: str = "") -> None:
        if not src_dir.exists():
            print(f"  ⚠️  Dizin bulunamadı: {src_dir}")
            return
        files = [f for f in sorted(src_dir.iterdir()) if f.is_file() and f.suffix in exts]
        if not files:
            print(f"  ⏭️  {label or src_dir.name}: .md dosya yok")
            return
        dst_dir.mkdir(parents=True, exist_ok=True)
        for f in files:
            _copy_file(f, dst_dir / f.name, f"{label or src_dir.name}/{f.name}")

    # 1. memory/ ← ~/.claude/rules/
    print("\n📂 memory/ ← ~/.claude/rules/")
    for src_name, dst_name in memory_map.items():
        _copy_file(claude_rules_dir / src_name, ai_memory_dir / dst_name,
                   f"~/.claude/rules/{src_name}")

    # 2. commands/ ← ~/.claude/commands/
    print("\n📂 commands/ ← ~/.claude/commands/")
    _copy_dir(Path.home() / ".claude" / "commands",
              GLOBAL_AI_DIR / "commands", exts=(".md",), label="commands")

    # 3. guides/ ← ~/.claude/guides/
    print("\n📂 guides/ ← ~/.claude/guides/")
    _copy_dir(Path.home() / ".claude" / "guides",
              GLOBAL_AI_DIR / "guides", exts=(".md",), label="guides")

    # 4. config/ ← ~/.claude/config/
    print("\n📂 config/ ← ~/.claude/config/")
    _copy_dir(Path.home() / ".claude" / "config",
              GLOBAL_AI_DIR / "config", exts=(".md", ".json"), label="config")

    # 5. hooks/ ← ~/.claude/hooks/ (README + config subdir)
    print("\n📂 hooks/ ← ~/.claude/hooks/")
    hooks_src = Path.home() / ".claude" / "hooks"
    hooks_dst = GLOBAL_AI_DIR / "hooks"
    _copy_dir(hooks_src, hooks_dst, exts=(".md",), label="hooks")
    hooks_config_src = hooks_src / "config"
    if hooks_config_src.exists():
        _copy_dir(hooks_config_src, hooks_dst / "config", exts=(".md", ".json", ".yaml"), label="hooks/config")

    # 6. plugins/ ← ~/.claude/plugins/local/ (just local plugins, not VSCode extensions)
    print("\n📂 plugins/ ← ~/.claude/plugins/local/")
    plugins_src = Path.home() / ".claude" / "plugins" / "local"
    plugins_dst = GLOBAL_AI_DIR / "plugins"
    if plugins_src.exists():
        for plugin_dir in sorted(plugins_src.iterdir()):
            if plugin_dir.is_dir():
                for f in sorted(plugin_dir.glob("*.md")):
                    _copy_file(f, plugins_dst / plugin_dir.name / f.name,
                               f"plugins/local/{plugin_dir.name}/{f.name}")
    else:
        print(f"  ⚠️  ~/.claude/plugins/local/ bulunamadı")

    print(f"\n📥 {imported} dosya import edildi, {skipped} atlandı, {missing} bulunamadı.")
    if imported > 0:
        print("   ~/.ai/ artık canonical kaynak.")
        print("   Sıradaki: nexus-sync global-build çalıştır")


def cmd_global_build(args):
    """Build from ~/.ai/ manifest → ~/.claude/ and ~/.gemini/ targets."""
    ai_dir = GLOBAL_AI_DIR
    manifest_path = ai_dir / "manifest.yaml"
    if not manifest_path.exists():
        print("❌ ~/.ai/manifest.yaml bulunamadı. Önce 'nexus-sync global-init' çalıştır.")
        sys.exit(1)

    manifest = load_yaml(manifest_path)
    targets = manifest.get("targets", {})
    distributions = manifest.get("distribution", [])
    dry_run = getattr(args, "dry_run", False)
    target_filter = getattr(args, "target", None)

    # Collect content per target
    claude_inline: list[str] = []
    claude_rules: list[tuple[str, str]] = []   # (rule_name, body)
    gemini_sections: list[str] = []

    for dist in distributions:
        if not isinstance(dist, dict):
            continue
        source_str = dist.get("source", "")
        dist_targets = dist.get("targets", [])
        if isinstance(dist_targets, str):
            dist_targets = [dist_targets]
        dist_targets = [str(t) for t in dist_targets]
        rule_path = dist.get("claude_rule_path")

        src_path = ai_dir / source_str
        if not src_path.exists():
            print(f"  ⚠️  Kaynak bulunamadı: {source_str}")
            continue

        raw = src_path.read_text(encoding="utf-8")
        _fm, body = strip_yaml_frontmatter(raw)
        body = body.strip()
        if not body:
            continue

        if "claude" in dist_targets and (target_filter in (None, "claude")):
            if rule_path:
                claude_rules.append((rule_path, body))
            else:
                claude_inline.append(body)

        if "gemini" in dist_targets and (target_filter in (None, "gemini")):
            gemini_sections.append(body)

    claude_enabled = isinstance(targets.get("claude"), dict) and targets["claude"].get("enabled", False)
    gemini_enabled = isinstance(targets.get("gemini"), dict) and targets["gemini"].get("enabled", False)

    if claude_enabled and target_filter in (None, "claude"):
        _build_global_claude(manifest, claude_inline, claude_rules, dry_run)

    if gemini_enabled and target_filter in (None, "gemini"):
        _build_global_gemini(manifest, gemini_sections, dry_run)

    label = "[DRY] " if dry_run else ""
    print(f"\n{label}✅ Global build tamamlandı.")


def _build_global_claude(manifest: dict, inline_sections: list[str], rules: list[tuple[str, str]], dry_run: bool):
    print("\n🔨 Building target: claude (global)")
    claude_cfg = manifest.get("targets", {}).get("claude", {})
    out_cfg = claude_cfg.get("output", {})
    if isinstance(out_cfg, str):
        global_path = Path(out_cfg)
        rules_dir = global_path.parent / "rules"
    else:
        global_path = Path(str(out_cfg.get("global_path", str(Path.home() / ".claude" / "CLAUDE.md"))))
        rules_dir   = Path(str(out_cfg.get("rules_dir",   str(Path.home() / ".claude" / "rules"))))

    note = "<!-- DO NOT EDIT. Edit ~/.ai/memory/ and run: nexus-sync global-build -->"
    gen_lines = [_CLAUDE_GENERATED_START, note, ""]
    for body in inline_sections:
        gen_lines.append(body)
        gen_lines.append("")
    gen_lines.append(_CLAUDE_GENERATED_END)
    generated_section = "\n".join(gen_lines)

    existing = global_path.read_text(encoding="utf-8") if global_path.exists() else ""

    if _CLAUDE_GENERATED_START in existing:
        before = existing.split(_CLAUDE_GENERATED_START)[0].rstrip()
        after  = ""
        if _CLAUDE_GENERATED_END in existing:
            parts = existing.split(_CLAUDE_GENERATED_END, 1)
            if len(parts) > 1:
                after = parts[1]
        new_content = before + "\n\n" + generated_section + after
    else:
        lines = existing.splitlines()
        first_line = lines[0] if lines else ""
        preserve_first = first_line.startswith("@") and "empirica" in first_line
        if preserve_first:
            rest = "\n".join(lines[1:]).strip()
            new_content = (
                first_line + "\n\n" + rest + "\n\n" + generated_section + "\n"
                if rest else
                first_line + "\n\n" + generated_section + "\n"
            )
        else:
            new_content = (
                existing.rstrip() + "\n\n" + generated_section + "\n"
                if existing.strip() else
                generated_section + "\n"
            )

    if dry_run:
        print(f"  [DRY] {global_path} → {new_content.count(chr(10))} satır")
    else:
        global_path.parent.mkdir(parents=True, exist_ok=True)
        global_path.write_text(new_content, encoding="utf-8")
        print(f"  ✅ {global_path} → {new_content.count(chr(10))} satır")

    header = "<!-- Generated by nexus-sync global-build. DO NOT EDIT. Edit ~/.ai/memory/ instead. -->\n\n"
    for rule_name, rule_body in rules:
        rule_file = rules_dir / f"{rule_name}.md"
        content = header + rule_body
        if dry_run:
            print(f"  [DRY] {rule_file}")
        else:
            rules_dir.mkdir(parents=True, exist_ok=True)
            rule_file.write_text(content, encoding="utf-8")
            print(f"  ✅ {rule_file}")


def _build_global_gemini(manifest: dict, sections: list[str], dry_run: bool):
    print("\n🔨 Building target: gemini (global)")
    gemini_cfg = manifest.get("targets", {}).get("gemini", {})
    out_cfg = gemini_cfg.get("output", {})
    if isinstance(out_cfg, str):
        global_path = Path(out_cfg)
    else:
        global_path = Path(str(out_cfg.get("global_path", str(Path.home() / ".gemini" / "GEMINI.md"))))

    note = "<!-- DO NOT EDIT. Edit ~/.ai/memory/ and run: nexus-sync global-build -->"
    gen_lines = [_GEMINI_GENERATED_START, note, ""]
    for body in sections:
        gen_lines.append(body)
        gen_lines.append("")
    gen_lines.append(_GEMINI_GENERATED_END)
    generated_section = "\n".join(gen_lines)

    existing = global_path.read_text(encoding="utf-8") if global_path.exists() else ""

    if _GEMINI_GENERATED_START in existing:
        before = existing.split(_GEMINI_GENERATED_START)[0].rstrip()
        after  = ""
        if _GEMINI_GENERATED_END in existing:
            parts = existing.split(_GEMINI_GENERATED_END, 1)
            if len(parts) > 1:
                after = parts[1]
        new_content = before + "\n\n" + generated_section + after
    else:
        new_content = (
            existing.rstrip() + "\n\n" + generated_section + "\n"
            if existing.strip() else
            generated_section + "\n"
        )

    if dry_run:
        print(f"  [DRY] {global_path} → {new_content.count(chr(10))} satır")
    else:
        global_path.parent.mkdir(parents=True, exist_ok=True)
        global_path.write_text(new_content, encoding="utf-8")
        print(f"  ✅ {global_path} → {new_content.count(chr(10))} satır")


# ---------------------------------------------------------------------------
# Main CLI
# ---------------------------------------------------------------------------

def cmd_global_deploy(args):
    """~/.ai/memory/*.md dosyalarını MCP sunucusuna HTTP POST ile gönder."""
    import urllib.request
    import urllib.error

    memory_dir = Path.home() / ".ai" / "memory"
    if not memory_dir.exists():
        print(f"❌ {memory_dir} bulunamadı. Önce 'global-init' çalıştır.")
        sys.exit(1)

    md_files = sorted(memory_dir.glob("*.md"))
    if not md_files:
        print(f"⚠️  {memory_dir} içinde .md dosyası yok.")
        return

    files: dict[str, str] = {}
    for md in md_files:
        files[md.name] = md.read_text(encoding="utf-8")

    payload = json.dumps({"files": files}).encode("utf-8")
    server = args.server.rstrip("/")
    url = f"{server}/sync"

    print(f"🚀 {len(files)} dosya → {url}")

    req = urllib.request.Request(
        url,
        data=payload,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "X-Sync-Token": args.token,
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            updated = body.get("updated", [])
            errors  = body.get("errors", [])
            print(f"✅ Güncellendi ({len(updated)}): {', '.join(updated) or '-'}")
            if errors:
                print(f"⚠️  Hatalar: {'; '.join(errors)}")
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace")
        print(f"❌ HTTP {e.code}: {detail}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Bağlantı hatası: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        prog="nexus-sync",
        description="Universal AI Config Sync — tek kaynak, tüm AI araçlara dağıtım",
    )
    sub = parser.add_subparsers(dest="command")

    # init
    p_init = sub.add_parser("init", help="Canonical .ai/ yapısını başlat")
    p_init.add_argument("--project-name", default=None)

    # build
    p_build = sub.add_parser("build", help="Canonical → target dosyalara transpile et")
    p_build.add_argument("--target", choices=["claude", "gemini", "agents"], default=None)
    p_build.add_argument("--dry-run", action="store_true")

    # diff
    p_diff = sub.add_parser("diff", help="Canonical vs generated fark analizi")
    p_diff.add_argument("--exit-code", action="store_true", help="Drift varsa exit 1")
    p_diff.add_argument("--global", dest="global_mode", action="store_true",
                        help="~/.ai/ global diff modunu kullan")

    # status
    sub.add_parser("status", help="Sync durumu")

    # validate
    p_validate = sub.add_parser("validate", help="manifest.yaml doğrulama")
    p_validate.add_argument("--global", dest="global_mode", action="store_true",
                            help="~/.ai/ global validate modunu kullan")

    # add
    p_add = sub.add_parser("add", help="Yeni skill veya guide ekle")
    p_add.add_argument("kind", choices=["skill", "guide"])
    p_add.add_argument("name")

    # import
    p_import = sub.add_parser("import", help="Mevcut config'den canonical'a import")
    p_import.add_argument("source_tool", choices=["claude", "gemini"])

    # install-hooks
    sub.add_parser("install-hooks", help="Git pre-commit hook kur")

    # --- global commands ---

    # global-init
    sub.add_parser("global-init", help="~/.ai/ global canonical yapısını oluştur")

    # global-import
    p_gimport = sub.add_parser("global-import", help="~/.claude/rules/ → ~/.ai/memory/ import et")
    p_gimport.add_argument("--force", action="store_true", help="Mevcut dosyaların üzerine yaz")

    # global-build
    p_gbuild = sub.add_parser("global-build", help="~/.ai/ → ~/.claude/ ve ~/.gemini/ build et")
    p_gbuild.add_argument("--target", choices=["claude", "gemini"], default=None)
    p_gbuild.add_argument("--dry-run", action="store_true")

    # global-deploy
    p_gdeploy = sub.add_parser("global-deploy", help="~/.ai/memory/*.md → MCP sunucusuna gönder")
    p_gdeploy.add_argument("--server", required=True, help="http://192.168.1.x:8900")
    p_gdeploy.add_argument("--token", default="changeme", help="X-Sync-Token değeri")

    args = parser.parse_args()

    commands = {
        "init": cmd_init,
        "build": cmd_build,
        "diff": cmd_diff,
        "status": cmd_status,
        "validate": cmd_validate,
        "add": cmd_add,
        "import": cmd_import,
        "install-hooks": cmd_install_hooks,
        "global-init":   cmd_global_init,
        "global-import": cmd_global_import,
        "global-build":  cmd_global_build,
        "global-deploy": cmd_global_deploy,
    }

    if args.command in commands:
        commands[args.command](args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
