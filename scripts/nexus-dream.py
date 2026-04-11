"""
nexus-dream.py (v3.2) — TR Time + TURN TRACKER + Context Alert
Scans Nexus memory index, detects patterns, and alerts on context bloat.
"""
import argparse, json, sys, os, time, re, urllib.request, urllib.error
from pathlib import Path
from datetime import datetime, timezone, timedelta

# ── config ────────────────────────────────────────────────────────────────────
NEXUS_URL    = "http://192.168.1.186:8900"
TR_TZ        = timezone(timedelta(hours=3))
SYNC_DIR     = Path("data/memory/sync")
STATE_FILE   = Path(".nexus-session-state")
TURN_LIMIT   = 5  # 5 soruda bir mola uyarısı

_parser = argparse.ArgumentParser(description="Nexus autodream v3.2")
_parser.add_argument("--light", action="store_true", help="Last 4 hours only")
_parser.add_argument("--increment", action="store_true", help="Increment turn counter")
_args = _parser.parse_args()
LIGHT_MODE = _args.light

def get_session_state():
    if not STATE_FILE.exists():
        return {"turns": 0, "start_time": datetime.now(TR_TZ).isoformat()}
    try:
        return json.loads(STATE_FILE.read_text())
    except:
        return {"turns": 0, "start_time": datetime.now(TR_TZ).isoformat()}

def save_session_state(state):
    STATE_FILE.write_text(json.dumps(state))

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

state = get_session_state()
if _args.increment:
    state["turns"] += 1
    save_session_state(state)

turns_count = state["turns"]
print(f"🚀 Nexus Dream v3.2 [{mode.upper()}] (Turns: {turns_count}/{TURN_LIMIT})")

alert_triggered = turns_count >= TURN_LIMIT
report_content = f"""# Nexus Dream Report - {today} {hour}:00
Mode: {mode}
Session Turns: {turns_count} / {TURN_LIMIT}
Status: {"⚠️ NEARING BLOAT" if alert_triggered else "Healthy"}
"""

if alert_triggered:
    report_content += "\n⚠️ **CRITICAL BLOAT ALERT:** Turn limit reached (5+). WRITE HANDOFF AND START NEW SESSION NOW."
    print(f"\n[!!!] CONTEXT BLOAT ALERT: {turns_count} turns reached. Please write memory and restart session.")

metadata = {
    "id": f"dream-{mode}-{today}-{hour}",
    "type": "sync_report",
    "context": "global",
    "generated_at": now_tr.isoformat(),
    "turns": turns_count,
    "tags": f"dream, {mode}, context-alert, turn-tracker"
}

key = f"dream--{mode}--{today}--{hour}"
if nexus_put(key, report_content, metadata):
    print(f"✅ Rapor yüklendi: {key}")
    (SYNC_DIR / f"{key}.md").write_text(report_content, encoding="utf-8")

if alert_triggered:
    sys.exit(5) # Özel exit code: Bloat detected
