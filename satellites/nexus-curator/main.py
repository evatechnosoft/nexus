import os
import logging
import httpx
import json
from fastapi import FastAPI, Request, HTTPException, Body
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv

import processor

# .env yÃ¼kle
load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
log = logging.getLogger("nexus-curator")

app = FastAPI(title="Nexus Curator Satellite")

# Statik ve Template ayarlarÄ± - Mutlak Yollar
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(CURRENT_DIR, "static")
TEMPLATES_DIR = os.path.join(CURRENT_DIR, "templates")

if not os.path.exists(STATIC_DIR): os.makedirs(STATIC_DIR)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

HUB_URL = os.getenv("NEXUS_HUB_URL")
# Projenin kök dizinine erişim (satellites/nexus-curator'dan yukarı)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REGISTRY_PATH = os.path.join(BASE_DIR, "data", "memory", "projects", "satellites.json")

@app.on_event("startup")
async def startup_event():
    scheduler = AsyncIOScheduler()
    scheduler.start()
    app.state.scheduler = scheduler
    log.info("Nexus Curator started. Hub: %s", HUB_URL)

@app.get("/", response_class=HTMLResponse)
async def read_curator_dashboard(request: Request):
    """ZekÃ¢ TaslaklarÄ± ve Onay Paneli (The Curator)"""
    return templates.TemplateResponse("brain_dashboard.html", {"request": request})

# --- SATELLITE CONTROL API ---

@app.get("/api/satellites")
async def get_satellites():
    """Tüm uyduların durumunu döner."""
    if not os.path.exists(REGISTRY_PATH):
        raise HTTPException(status_code=404, detail="Registry not found")
    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        return json.load(f).get("satellites", {})

@app.post("/api/satellites/toggle/{name}")
async def toggle_satellite(name: str, enabled: bool = Body(..., embed=True)):
    """Bir uydunun aktif/pasif durumunu değiştirir."""
    if not os.path.exists(REGISTRY_PATH):
        raise HTTPException(status_code=404, detail="Registry not found")

    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    if name not in data["satellites"]:
        raise HTTPException(status_code=404, detail="Satellite not found")

    data["satellites"][name]["enabled"] = enabled

    with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    log.info(f"Satellite {name} status updated to: {enabled}")
    return {"status": "success", "name": name, "enabled": enabled}

# --- EXISTING API ENDPOINTS ---


@app.post("/api/process/{filename}")
async def process_with_ollama(filename: str):
    """Belirli bir ham taslağı Ollama ile işle ve Nexus formatına sok."""
    processed_file = await processor.process_draft(filename)
    if not processed_file:
        raise HTTPException(status_code=500, detail="Ollama processing failed")
    return {"status": "processed", "file": processed_file}

@app.get("/api/processed-view/{filename}")
async def view_processed(filename: str):
    """İşlenmiş taslağın içeriğini döner."""
    path = os.path.join("./processed", filename)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File not found")
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    return {"content": content}

@app.post("/api/approve/{filename}")
async def approve_to_nexus(filename: str):
    """Onaylanan bilgiyi Nexus Hub'a (MCP) gönder."""
    path = os.path.join("./processed", filename)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Processed file not found")
    
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    
    async with httpx.AsyncClient() as client:
        # Hub'a (MCP) bilgiyi mühürle
        response = await client.post(f"{HUB_URL}/brain/update", json={
            "name": filename,
            "content": content,
            "category": "skills" 
        })
        
        if response.status_code == 200:
            # Başarılıysa yerel dosyayı temizle/arşivle
            # os.remove(path)
            pass
            
        return response.json()

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("APP_PORT", 4700))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
