#!/usr/bin/env python3
"""
ai-discovery: Bilgisayardaki tüm AI config dosyalarını tarar.
Çıktıyı Claude'a yapıştırarak mevcut durumu analiz ettirebilirsin.

Kullanım:
    python ai-discovery.py                          # Varsayılan: mevcut dizin
    python ai-discovery.py C:\ D:\projects          # Belirli dizinler
    python ai-discovery.py --output report.json     # JSON'a kaydet
    python ai-discovery.py --max-depth 5            # Derinlik limiti

Windows:  python ai-discovery.py C:\ D:\
Linux:    python3 ai-discovery.py /home /projects
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Taranan dosya/dizin pattern'leri
AI_CONFIG_PATTERNS = {
    # Claude
    "CLAUDE.md": "claude",
    ".claude": "claude",

    # Gemini
    "GEMINI.md": "gemini",
    ".gemini": "gemini",

    # Copilot
    "copilot-instructions.md": "copilot",

    # Cursor
    ".cursorrules": "cursor",
    ".cursor": "cursor",

    # Cross-tool
    "AGENTS.md": "agents",

    # Universal (bizim sistem)
    ".ai": "ai-sync",
}

# Atlanacak dizinler
SKIP_DIRS = {
    "node_modules", ".git", "__pycache__", ".venv", "venv",
    "env", ".env", "dist", "build", ".next", ".nuxt",
    ".dart_tool", ".pub-cache", "vendor", "Pods",
    ".gradle", ".idea", ".vs", "bin", "obj",
    "AppData", "Windows", "Program Files", "Program Files (x86)",
    "$Recycle.Bin", "System Volume Information",
    ".Trash", "Library",
}

MAX_FILE_READ_SIZE = 50_000  # 50KB per file max


def scan_directories(roots: list[str], max_depth: int = 6) -> dict:
    """Tüm AI config dosyalarını tara."""

    inventory = {
        "scan_date": datetime.now().isoformat(),
        "scan_roots": roots,
        "projects": [],
        "global_configs": [],
        "summary": {
            "total_projects": 0,
            "by_tool": {},
            "files_found": 0,
        }
    }

    seen_projects: dict[str, dict] = {}  # project_root -> project_data
    files_found = 0

    for root_dir in roots:
        root_path = Path(root_dir).resolve()
        if not root_path.exists():
            print(f"⚠️  Dizin bulunamadı: {root_dir}", file=sys.stderr)
            continue

        print(f"🔍 Taranıyor: {root_path}", file=sys.stderr)

        for dirpath, dirnames, filenames in os.walk(root_path):
            current = Path(dirpath)

            # Depth check
            try:
                depth = len(current.relative_to(root_path).parts)
            except ValueError:
                continue
            if depth > max_depth:
                dirnames.clear()
                continue

            # Skip known irrelevant directories
            dirnames[:] = [
                d for d in dirnames
                if d not in SKIP_DIRS and not d.startswith(".")
                or d in (".claude", ".gemini", ".cursor", ".github", ".ai")
            ]

            # Check for AI config files/dirs
            for name in list(filenames) + list(dirnames):
                tool = None

                # Direct match
                if name in AI_CONFIG_PATTERNS:
                    tool = AI_CONFIG_PATTERNS[name]
                # .github/copilot-instructions.md
                elif name == ".github" and name in dirnames:
                    copilot_file = current / ".github" / "copilot-instructions.md"
                    if copilot_file.exists():
                        tool = "copilot"
                # *.instructions.md pattern
                elif name.endswith(".instructions.md"):
                    tool = "copilot"

                if not tool:
                    continue

                full_path = current / name

                # Determine project root (walk up to find .git or use parent)
                project_root = _find_project_root(current)
                project_key = str(project_root)

                # Is this a global config? (home directory level)
                home = Path.home()
                is_global = False
                try:
                    current.relative_to(home)
                    if current == home or current.parent == home:
                        is_global = True
                except ValueError:
                    pass

                # Collect file info
                file_info = _collect_file_info(full_path, tool)
                if file_info:
                    files_found += len(file_info) if isinstance(file_info, list) else 1

                    if is_global:
                        if isinstance(file_info, list):
                            inventory["global_configs"].extend(file_info)
                        else:
                            inventory["global_configs"].append(file_info)
                    else:
                        if project_key not in seen_projects:
                            seen_projects[project_key] = {
                                "root": project_key,
                                "name": project_root.name,
                                "tools_detected": set(),
                                "files": [],
                            }
                        proj = seen_projects[project_key]
                        proj["tools_detected"].add(tool)
                        if isinstance(file_info, list):
                            proj["files"].extend(file_info)
                        else:
                            proj["files"].append(file_info)

    # Finalize
    for proj_data in seen_projects.values():
        proj_data["tools_detected"] = sorted(proj_data["tools_detected"])
        inventory["projects"].append(proj_data)

    inventory["summary"]["total_projects"] = len(inventory["projects"])
    inventory["summary"]["files_found"] = files_found

    # Count by tool
    tool_counts: dict[str, int] = {}
    for proj in inventory["projects"]:
        for t in proj["tools_detected"]:
            tool_counts[t] = tool_counts.get(t, 0) + 1
    for gc in inventory["global_configs"]:
        t = gc.get("tool", "unknown")
        tool_counts[t] = tool_counts.get(t, 0) + 1
    inventory["summary"]["by_tool"] = tool_counts

    return inventory


def _find_project_root(current: Path) -> Path:
    """Walk up to find .git directory as project root indicator."""
    for parent in [current, *current.parents]:
        if (parent / ".git").exists():
            return parent
        # Stop at drive root
        if parent == parent.parent:
            break
    return current


def _collect_file_info(path: Path, tool: str) -> list[dict] | dict | None:
    """Collect info about an AI config file or directory."""
    if path.is_file():
        return _read_file_info(path, tool)
    elif path.is_dir():
        results = []
        # Scan directory for .md files
        try:
            for f in sorted(path.rglob("*.md")):
                if f.is_file():
                    info = _read_file_info(f, tool)
                    if info:
                        results.append(info)
            # Also check for JSON config files
            for f in sorted(path.rglob("*.json")):
                if f.is_file() and f.stat().st_size < MAX_FILE_READ_SIZE:
                    info = _read_file_info(f, tool)
                    if info:
                        results.append(info)
        except PermissionError:
            pass
        return results if results else None
    return None


def _read_file_info(path: Path, tool: str) -> dict | None:
    """Read a single file and return its metadata + content."""
    try:
        stat = path.stat()
        size = stat.st_size

        info = {
            "path": str(path),
            "tool": tool,
            "filename": path.name,
            "size_bytes": size,
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
        }

        # Read content if small enough
        if size <= MAX_FILE_READ_SIZE:
            try:
                content = path.read_text(encoding="utf-8", errors="replace")
                info["content"] = content
                info["line_count"] = content.count("\n") + 1
            except Exception:
                info["content"] = "[READ ERROR]"
        else:
            info["content"] = f"[TOO LARGE: {size} bytes]"
            # Read first 200 lines as preview
            try:
                with open(path, "r", encoding="utf-8", errors="replace") as f:
                    preview_lines = []
                    for i, line in enumerate(f):
                        if i >= 200:
                            break
                        preview_lines.append(line)
                    info["content_preview"] = "".join(preview_lines)
            except Exception:
                pass

        return info
    except (PermissionError, OSError):
        return None


def print_summary(inventory: dict):
    """Print human-readable summary to stderr."""
    s = inventory["summary"]
    print(f"\n📊 Tarama Sonucu:", file=sys.stderr)
    print(f"   Toplam proje: {s['total_projects']}", file=sys.stderr)
    print(f"   Toplam dosya: {s['files_found']}", file=sys.stderr)
    print(f"   Global config: {len(inventory['global_configs'])}", file=sys.stderr)
    print(f"\n   Araç dağılımı:", file=sys.stderr)
    for tool, count in sorted(s.get("by_tool", {}).items()):
        print(f"     {tool}: {count} proje/dosya", file=sys.stderr)

    if inventory["projects"]:
        print(f"\n   Projeler:", file=sys.stderr)
        for proj in inventory["projects"][:20]:
            tools = ", ".join(proj["tools_detected"])
            fcount = len(proj["files"])
            print(f"     📁 {proj['name']} [{tools}] — {fcount} dosya", file=sys.stderr)
        if len(inventory["projects"]) > 20:
            remaining = len(inventory["projects"]) - 20
            print(f"     ... ve {remaining} proje daha", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(
        prog="ai-discovery",
        description="Bilgisayardaki tüm AI config dosyalarını tarar",
    )
    parser.add_argument(
        "roots", nargs="*",
        default=[str(Path.cwd())],
        help="Taranacak dizinler (varsayılan: mevcut dizin)"
    )
    parser.add_argument("--output", "-o", default=None, help="JSON çıktı dosyası")
    parser.add_argument("--max-depth", type=int, default=6, help="Max dizin derinliği")
    parser.add_argument("--no-content", action="store_true", help="Dosya içeriklerini dahil etme")
    parser.add_argument("--compact", action="store_true", help="Sadece özet, content yok")

    args = parser.parse_args()

    inventory = scan_directories(args.roots, args.max_depth)

    # Strip content if requested
    if args.no_content or args.compact:
        for proj in inventory["projects"]:
            for f in proj["files"]:
                f.pop("content", None)
                f.pop("content_preview", None)
        for gc in inventory["global_configs"]:
            gc.pop("content", None)
            gc.pop("content_preview", None)

    print_summary(inventory)

    output_json = json.dumps(inventory, indent=2, ensure_ascii=False, default=str)

    if args.output:
        Path(args.output).write_text(output_json, encoding="utf-8")
        print(f"\n💾 Çıktı kaydedildi: {args.output}", file=sys.stderr)
    else:
        # Print to stdout (pipe-friendly)
        print(output_json)

    print(f"\n💡 Sonraki adım: çıktıyı Claude'a yapıştır veya dosyayı yükle.", file=sys.stderr)


if __name__ == "__main__":
    main()
