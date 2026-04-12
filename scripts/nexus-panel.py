import os
import sys
import json
import subprocess
import time

REGISTRY_PATH = "data/memory/projects/satellites.json"
LOG_DIR = "logs/satellites"
PYTHON_EXE = os.path.join(".venv", "Scripts", "python.exe") if os.name == "nt" else os.path.join(".venv", "bin", "python")

if not os.path.exists(PYTHON_EXE):
    PYTHON_EXE = sys.executable

def load_satellites():
    if not os.path.exists(REGISTRY_PATH):
        return {}
    with open(REGISTRY_PATH, "r") as f:
        return json.load(f).get("satellites", {})

def start_satellites():
    satellites = load_satellites()
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
        
    print(f"\n🚀 IGNITION: Aktif uydular ateşleniyor...\n")
    
    processes = []
    for name, info in satellites.items():
        if info["enabled"]:
            entry_path = info["entry"]
            if not os.path.exists(entry_path):
                print(f"❌ HATA: {name} için giriş dosyası bulunamadı: {entry_path}")
                continue
                
            log_file = os.path.join(LOG_DIR, f"{name}.log")
            with open(log_file, "a") as log:
                # Bağımsız süreç olarak başlat
                process = subprocess.Popen(
                    [PYTHON_EXE, entry_path],
                    stdout=log,
                    stderr=log,
                    creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == "nt" else 0
                )
                print(f"🟢 {name:<20} | BAŞLATILDI (PID: {process.pid}) | LOG: {log_file}")
                processes.append(process)
    
    if not processes:
        print("ℹ️  Aktif edilecek uydu bulunamadı. Lütfen /enable komutunu kullanın.")
    else:
        print(f"\n✅ Toplam {len(processes)} uydu devrede.")

def show_panel():
    satellites = load_satellites()
    
    print("\n" + "="*50)
    print("      🛰️  NEXUS HUB - SATELLITE CONTROL PANEL")
    print("="*50)
    
    print(f"{'UYDU ADI':<20} | {'DURUM':<8} | {'PORT':<6} | {'ROL'}")
    print("-" * 70)
    
    for name, info in satellites.items():
        status = "🟢 ON" if info["enabled"] else "⚪ OFF"
        port = info["port"] if info["port"] else "N/A"
        print(f"{name:<20} | {status:<8} | {port:<6} | {info['role']}")
    
    print("\n" + "="*50)
    print("KOMUTLAR:")
    print("1. /start         - Aktif uyduları BAŞLAT (Ignition)")
    print("2. /enable <ad>   - Uyduyu aktif et")
    print("3. /disable <ad>  - Uyduyu pasif et")
    print("4. /doctor        - Sağlık taraması")
    print("5. /exit          - Paneli kapat")
    print("="*50)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--start":
        start_satellites()
    else:
        show_panel()

