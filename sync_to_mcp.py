import os
import json
import urllib.request
from pathlib import Path

# MCP Sunucusu (ZimaOS veya Localhost)
# Kullanıcının "mcp kurduk ya orda herşey" dediği evrensel adres.
MCP_URL = "http://localhost:8900/sync"
SYNC_TOKEN = "changeme"  # mcp_server.py içindeki varsayılan token

# Gönderilecek zeka (kurallar) dizini
RULES_DIR = Path("brain/shared/rules")

def sync_rules():
    if not RULES_DIR.exists():
        print(f"Hata: {RULES_DIR} dizini bulunamadı.")
        return

    files_payload = {}
    
    # Dizindeki tüm markdown dosyalarını oku
    for md_file in RULES_DIR.glob("*.md"):
        content = md_file.read_text(encoding="utf-8")
        files_payload[md_file.name] = content
        print(f"[Okundu] {md_file.name} ({len(content)} karakter)")

    if not files_payload:
        print("Gönderilecek kural bulunamadı.")
        return

    # Payload'u hazırla
    data = json.dumps({"files": files_payload}).encode('utf-8')
    req = urllib.request.Request(MCP_URL, data=data, method='POST')
    req.add_header('Content-Type', 'application/json')
    req.add_header('X-Sync-Token', SYNC_TOKEN)

    print(f"\n[MCP Sync] {MCP_URL} adresine {len(files_payload)} dosya gönderiliyor...")

    # İsteği at
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            res_body = response.read().decode('utf-8')
            res_json = json.loads(res_body)
            print("\n[Başarılı] Nexus Brain (MCP) Güncellendi!")
            print(f"Güncellenen Dosyalar: {res_json.get('updated', [])}")
            print(f"Toplam İndekslenen (ChromaDB): {res_json.get('indexed', 0)}")
            
            if res_json.get('errors'):
                print(f"Hatalar: {res_json.get('errors')}")
                
    except urllib.error.URLError as e:
        print(f"\n[Bağlantı Hatası] MCP sunucusuna ulaşılamadı: {e}")
        print("Lütfen MCP sunucusunun (192.168.1.186:8900) çalıştığından emin olun.")
    except Exception as e:
        print(f"\n[Beklenmeyen Hata] {e}")

if __name__ == "__main__":
    sync_rules()
