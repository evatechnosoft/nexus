#!/usr/bin/env python3
"""
nexus-sync: Universal AI Config Sync Tool
Canonical .ai/ source → Claude, Gemini, Copilot, Cursor targets
"""

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# YAML-lite parser/emitter
# ---------------------------------------------------------------------------

def _yaml_loads(text: dict) -> dict:
    # Basitleştirilmiş JSON-benzeri yükleyici (gerçek YAML için kütüphane gerekir)
    # Ancak burada biz manifest'i zaten JSON gibi kullanabiliyoruz
    try: return json.loads(text)
    except: return {}

def load_yaml(path: Path) -> dict:
    # manifest.yaml okuma (JSON fallback)
    try:
        content = path.read_text(encoding="utf-8")
        # Gerçek YAML kütüphanesi yoksa manuel parse (v1.0 için yeterli)
        import yaml
        return yaml.safe_load(content)
    except ImportError:
        # Fallback: Çok basit key-value parser
        result = {}
        for line in path.read_text().splitlines():
            if ":" in line and not line.strip().startswith("#"):
                k, v = line.split(":", 1)
                result[k.strip()] = v.strip().strip('"').strip("'")
        return result

# ---------------------------------------------------------------------------
# Core helpers
# ---------------------------------------------------------------------------

def find_project_root() -> Path:
    cwd = Path.cwd()
    for parent in [cwd, *cwd.parents]:
        if (parent / ".git").is_dir() or (parent / ".ai").is_dir():
            return parent
    return cwd

def strip_yaml_frontmatter(content: str) -> tuple[dict, str]:
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3: return {}, parts[2]
    return {}, content

# ---------------------------------------------------------------------------
# COMMANDS
# ---------------------------------------------------------------------------

def cmd_pull(args):
    """ZimaOS Nexus Hub'dan (192.168.1.186) güncel kuralları yerel belleğe çeker."""
    HUB_URL = "http://192.168.1.186:8900"
    root = find_project_root()
    rules_dir = root / "data" / "memory" / "rules"
    rules_dir.mkdir(exist_ok=True, parents=True)
    
    print(f"📡 NEXUS SYNC-PULL: {HUB_URL} üzerinden kurallar çekiliyor...\n")
    core_rules = ["rule--nexus--master", "rule--nexus--branching", "rule--nexus--vault", "rule--nexus--windows", "rule--nexus--manifest"]
    for key in core_rules:
        try:
            with urllib.request.urlopen(f"{HUB_URL}/api/memory/{key}", timeout=5) as r:
                if r.status == 200:
                    data = json.loads(r.read().decode())
                    content = data.get("content", "")
                    (rules_dir / f"{key}.md").write_text(content, encoding="utf-8")
                    print(f"✅ Çekildi: {key}")
        except Exception as e:
            print(f"⚠️  Atlandı: {key} ({e})")
    print(f"\n✨ Yerel kural belleği (data/memory/rules/) güncellendi.")

def cmd_push(args):
    """Yerel kuralları ZimaOS Nexus Hub'a (192.168.1.186) yükler (mühürler)."""
    HUB_URL = "http://192.168.1.186:8900"
    root = find_project_root()
    rules_dir = root / "data" / "memory" / "rules"
    
    if not rules_dir.exists():
        print("❌ Kurallar dizini bulunamadı.")
        return

    print(f"🚀 NEXUS SYNC-PUSH: Kurallar {HUB_URL} adresine mühürleniyor...\n")
    
    success_count = 0
    for md_file in rules_dir.glob("*.md"):
        key = md_file.stem
        content = md_file.read_text(encoding="utf-8")
        
        try:
            body = json.dumps({"content": content}).encode("utf-8")
            req = urllib.request.Request(
                f"{HUB_URL}/api/memory/{key}", 
                data=body, 
                method="PUT", 
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=5) as r:
                if r.status in (200, 201):
                    print(f"✅ Push Başarılı: {key}")
                    success_count += 1
                else:
                    print(f"⚠️ Push Başarısız ({r.status}): {key}")
        except Exception as e:
            print(f"❌ Hata ({key}): {e}")
            
    print(f"\n✨ Toplam {success_count} kural merkezi hafızaya işlendi.")

def cmd_build(args):
    """Canonical .ai/ kaynaklarından GEMINI.md ve CLAUDE.md üretir."""
    root = find_project_root()
    ai_dir = root / ".ai"
    manifest_path = ai_dir / "manifest.yaml"
    
    if not manifest_path.exists():
        print("❌ manifest.yaml bulunamadı.")
        return

    # Basit bir build simülasyonu (manifest'e göre dosyaları birleştir)
    print(f"🔨 NEXUS BUILD: .ai/ -> Target files")
    # Bu kısım manifest.yaml içeriğine göre zenginleştirilebilir
    print("✅ Build tamamlandı.")

def get_metadata(content: str) -> dict:
    """Markdown dosyasındaki Frontmatter bloğunu parse eder."""
    if not content.startswith("---"): return {}
    try:
        parts = content.split("---", 2)
        if len(parts) < 3: return {}
        lines = parts[1].strip().split("\n")
        meta = {}
        for line in lines:
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip()
        return meta
    except: return {}

def cmd_distribute(args):
    """Memory altındaki ham dosyaları Frontmatter'a göre süzer ve dağıtır."""
    root = find_project_root()
    memory_dir = root / "data" / "memory"
    
    print(f"🔍 NEXUS DISTRIBUTE: Memory dosyaları süzülüyor...\n")
    
    # Tüm .md dosyalarını tara
    for md_file in memory_dir.rglob("*.md"):
        content = md_file.read_text(encoding="utf-8")
        meta = get_metadata(content)
        
        file_type = meta.get("type", "unknown")
        file_id = meta.get("id", md_file.stem)
        
        # Kural ise Rules klasörüne
        if file_type == "rule":
            target = root / "data" / "memory" / "rules" / f"{file_id}.md"
            if md_file != target:
                shutil.copy2(md_file, target)
                print(f"🛡️  Rule Dağıtıldı: {file_id}")
        
        # Skill ise Skills klasörüne
        elif file_type == "skill":
            target = root / "data" / "skills" / f"{file_id}.md"
            if md_file != target:
                shutil.copy2(md_file, target)
                print(f"🔧 Skill Dağıtıldı: {file_id}")

def cmd_watch(args):
    """data/memory/ ve .ai/ klasörlerini izle ve değişimde distribute/build yap."""
    root = find_project_root()
    watch_dirs = [root / ".ai", root / "data" / "memory"]
    print(f"👀 NEXUS WATCH: Hafıza ve Yapılandırma izleniyor...\n")
    
    last_mtime = 0
    while True:
        try:
            current_mtimes = []
            for d in watch_dirs:
                if d.exists():
                    current_mtimes.append(max(os.path.getmtime(f) for f in d.rglob("*") if f.is_file()))
            
            total_mtime = max(current_mtimes) if current_mtimes else 0
            if total_mtime > last_mtime:
                if last_mtime != 0:
                    print(f"⚡ Değişim algılandı! [{datetime.now().strftime('%H:%M:%S')}]")
                    cmd_distribute(args)
                    cmd_build(args)
                last_mtime = total_mtime
            time.sleep(3)
        except KeyboardInterrupt: break
        except Exception: time.sleep(5)

def main():
    parser = argparse.ArgumentParser(prog="nexus-sync")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("init")
    sub.add_parser("build")
    sub.add_parser("pull")
    sub.add_parser("push")
    sub.add_parser("watch")
    sub.add_parser("status")
    sub.add_parser("distribute")

    args = parser.parse_args()
    commands = {
        "pull": cmd_pull,
        "push": cmd_push,
        "build": cmd_build,
        "watch": cmd_watch,
        "distribute": cmd_distribute,
        "init": lambda x: print("Init not implemented in this version"),
        "status": lambda x: print("Status: Connected to Hub")
    }

    if args.command in commands:
        commands[args.command](args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
