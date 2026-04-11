"""
Nexus Satellite Agent v1.0
==========================
Bu script, 'D:/mainprojects/nexus-hub' veya herhangi bir bağımsız proje dizinine yerleştirilir.
Hub API'sine (it.evaitec.com veya yerel IP) periyodik olarak durum bildirir.
"""

import os
import time
import httpx
import logging
import socket
from datetime import datetime

# --- YAPILANDIRMA ---
HUB_URL = "http://192.168.1.186:4500/ops/satellite/report"
SATELLITE_NAME = f"Nexus-Hub-Satellite-{socket.gethostname()}"
CHECK_INTERVAL = 30  # Saniye

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
log = logging.getLogger("satellite")

def get_current_action():
    """
    Uydunun şu an ne yaptığını tespit eden mantık.
    Örnek: Belirli bir log dosyasının son satırını oku veya dizin değişikliğini kontrol et.
    """
    # Örnek: 'fetch_results.log' varsa son satırını al
    log_file = "fetch_results.log"
    if os.path.exists(log_file):
        with open(log_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
            if lines:
                return f"Last Log: {lines[-1].strip()[:50]}..."
    
    return "Monitoring directory..."

def scan_directory():
    """Dizin istatistiklerini topla."""
    files = os.listdir(".")
    return {
        "file_count": len(files),
        "last_file": files[-1] if files else None,
        "size_mb": sum(os.path.getsize(f) for f in files if os.path.isfile(f)) / (1024*1024)
    }

async def report():
    log.info(f"Satellite {SATELLITE_NAME} başlatıldı. Hub: {HUB_URL}")
    
    async with httpx.AsyncClient() as client:
        while True:
            try:
                action = get_current_action()
                meta = scan_directory()
                
                payload = {
                    "name": SATELLITE_NAME,
                    "status": "online",
                    "action": action,
                    "meta": meta
                }
                
                r = await client.post(HUB_URL, json=payload, timeout=10)
                if r.status_code == 200:
                    log.info(f"Rapor gönderildi: {action}")
                else:
                    log.error(f"Hub hatası: {r.status_code}")
                    
            except Exception as e:
                log.error(f"Bağlantı hatası: {e}")
            
            time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    import asyncio
    try:
        asyncio.run(report())
    except KeyboardInterrupt:
        log.info("Satellite durduruldu.")
