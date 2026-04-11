import os
import subprocess
import sys
from pathlib import Path

def run_cmd(cmd):
    print(f"Executing: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout

def compress_session():
    print("\n🛡️ NEXUS MASTER SEAL & COMPRESS BAŞLATILIYOR...")
    
    # 1. Cleanup (Cache temizliği)
    print("🧹 Cleanup: Gereksiz dosyalar temizleniyor...")
    run_cmd("rmdir /s /q .pytest_cache .ruff_cache 2>nul")
    run_cmd("for /d /r . %d in (__pycache__) do @if exist \"%d\" rmdir /s /q \"%d\"")
    
    # 2. Sync Build
    print("💾 Sync: Kurallar güncelleniyor...")
    run_cmd("python scripts/nexus-sync.py build")
    
    # 3. Index & Dream
    print("📊 Index: Hafıza tazeleniyor...")
    run_cmd("python core/build_skill_index.py")
    run_cmd("python scripts/nexus-dream.py --light")
    
    # 4. Seans Sıfırla
    if Path(".nexus-session-state").exists():
        Path(".nexus-session-state").unlink()
    
    print("\n✅ MÜHÜRLENDİ VE SIKIŞTIRILDI.")
    print("-" * 40)
    print("🚀 BİR SONRAKİ OTURUM İÇİN DEVAM KOMUTU:")
    print("   git checkout dev ; . .\\scripts\\shortcuts.ps1 ; n-doctor")
    print("-" * 40)

if __name__ == "__main__":
    compress_session()
