import os
import sys
import json
import logging
import subprocess
from fastapi import FastAPI, Request, HTTPException, Body
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
log = logging.getLogger("nexus-admin")

app = FastAPI(title="Nexus Master Portal v3.1")

# Paths
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(CURRENT_DIR, "static")
TEMPLATES_DIR = os.path.join(CURRENT_DIR, "templates")
if not os.path.exists(STATIC_DIR): os.makedirs(STATIC_DIR)
if not os.path.exists(TEMPLATES_DIR): os.makedirs(TEMPLATES_DIR)

# Project Root Paths
BASE_DIR = os.path.dirname(os.path.dirname(CURRENT_DIR))
REGISTRY_PATH = os.path.join(BASE_DIR, "data", "memory", "projects", "satellites.json")
DOCTOR_SCRIPT = os.path.join(BASE_DIR, "scripts", "nexus-doctor.py")

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

@app.get("/", response_class=HTMLResponse)
async def read_admin_dashboard(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# --- SATELLITE MANAGEMENT ---

@app.get("/api/satellites")
async def get_satellites():
    if not os.path.exists(REGISTRY_PATH):
        return {"satellites": {}}
    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        return json.load(f).get("satellites", {})

@app.post("/api/satellites/toggle/{name}")
async def toggle_satellite(name: str, enabled: bool = Body(..., embed=True)):
    with open(REGISTRY_PATH, "r+", encoding="utf-8") as f:
        data = json.load(f)
        if name in data["satellites"]:
            data["satellites"][name]["enabled"] = enabled
            f.seek(0)
            json.dump(data, f, indent=2)
            f.truncate()
            return {"status": "success", "name": name, "enabled": enabled}
    raise HTTPException(status_code=404, detail="Satellite not found")

@app.post("/api/system/ignite")
async def ignite_satellites():
    """Tüm aktif uyduları scripts/nexus-panel.py --start üzerinden ateşle."""
    try:
        cmd = [sys.executable, os.path.join(BASE_DIR, "scripts", "nexus-panel.py"), "--start"]
        subprocess.Popen(cmd, cwd=BASE_DIR)
        return {"status": "Ignition command sent"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# --- SYSTEM MONITORING ---

@app.get("/api/system/doctor")
async def run_doctor():
    """Nexus Doctor raporunu çalıştır ve sonucu dön."""
    try:
        result = subprocess.run([sys.executable, DOCTOR_SCRIPT], capture_output=True, text=True)
        return {"output": result.stdout + result.stderr}
    except Exception as e:
        return {"output": f"Doctor Error: {str(e)}"}

@app.get("/api/system/logs/{name}")
async def get_logs(name: str):
    """Belirli bir uydunun son loglarını döner."""
    log_file = os.path.join(BASE_DIR, "logs", "satellites", f"{name}.log")
    if not os.path.exists(log_file):
        return {"logs": "Log file not found."}
    with open(log_file, "r", encoding="utf-8") as f:
        # Son 100 satırı çek
        lines = f.readlines()
        return {"logs": "".join(lines[-100:])}

# --- ZIMAOS INTEGRATION ---

@app.post("/api/zimaos/exec")
async def exec_zimaos(command: str = Body(..., embed=True)):
    """ZimaOS (192.168.1.186) üzerinde SSH üzerinden komut çalıştırır."""
    try:
        # Nexus Windows Protocol: ssh -i ~/.ssh/zimaos_key dean@192.168.1.186 "command"
        ssh_cmd = f'ssh -i ~/.ssh/zimaos_key -o ConnectTimeout=5 dean@192.168.1.186 "{command}"'
        result = subprocess.run(ssh_cmd, shell=True, capture_output=True, text=True)
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exit_code": result.returncode
        }
    except Exception as e:
        return {"stdout": "", "stderr": str(e), "exit_code": 1}

if __name__ == "__main__":
    import uvicorn
    # Default admin port 4700
    uvicorn.run("main:app", host="0.0.0.0", port=4700, reload=True)
