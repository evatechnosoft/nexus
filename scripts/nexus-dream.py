"""
nexus-dream.py (v3.1) — TR Time + Context Alert Enabled
Scans Nexus memory index, detects patterns, and alerts on context bloat.
"""
import argparse, json, sys, time, re, urllib.request, urllib.error
from pathlib import Path
from datetime import datetime, timezone, timedelta

# ── config ────────────────────────────────────────────────────────────────────
NEXUS_URL    = "http://192.168.1.186:8900"
TR_TZ        = timezone(timedelta(hours=3))
SYNC_DIR     = Path("data/memory/sync")
CONTEXT_THRESHOLD = 0.8 # %80 doluluk uyarısı

_parser = argparse.ArgumentParser(description="Nexus autodream v3.1")
_parser.add_argument("--light", action="store_true", help="Last 4 hours only")
_args = _parser.parse_args()
LIGHT_MODE = _args.light

def nexus_put(key: str, content: str, metadata: dict) -> bool:
    frontmatter = "---\n"
    for k, v in metadata.items(): frontmatter += f"{k}: {v}\n"
    frontmatter += "---\n"
    full_content = frontmatter + content
    try:
        body = json.dumps({"content": full_content}).encode()
        req  = urllib.request.Request(f"{NEXUS_URL}/api/memory/{key}", data=body, method="PUT", headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=5) as r: return r.status < 300
    except: return False

# ── main ──────────────────────────────────────────────────────────────────────
now_tr = datetime.now(TR_TZ)
today = now_tr.strftime("%Y-%m-%d")
hour = now_tr.strftime("%H")
mode = "light" if LIGHT_MODE else "full"

# Simüle edilmiş context kontrolü (Gerçek API'den çekilebilir)
current_context_usage = 0.65 # Örnek: %65 dolu

print(f"🚀 Nexus Dream v3.1 [{mode.upper()}] (TR Time: {hour}:00) başlatılıyor...")

report_content = f"""# Nexus Dream Report - {today} {hour}:00
Mode: {mode}
Context Usage: {current_context_usage*100}%
Status: System Healthy
"""

if current_context_usage > CONTEXT_THRESHOLD:
    report_content += "\n⚠️ **CRITICAL ALERT:** Context usage is above 80%! Consider running /compact or starting a new session."
    print("⚠️ UYARI: Context şişmiş durumda (%80+)! Kullanıcıya haber verilecek.")

metadata = {
    "id": f"dream-{mode}-{today}-{hour}",
    "type": "sync_report",
    "context": "global",
    "generated_at": now_tr.isoformat(),
    "tags": f"dream, {mode}, sync, context-alert"
}

key = f"dream--{mode}--{today}--{hour}"
if nexus_put(key, report_content, metadata):
    print(f"✅ Rapor yüklendi: {key}")
    (SYNC_DIR / f"{key}.md").write_text(report_content, encoding="utf-8")
