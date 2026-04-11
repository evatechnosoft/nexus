import os
import logging
import httpx
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv

import processor

# .env yükle
load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
log = logging.getLogger("nexus-curator")

app = FastAPI(title="Nexus Curator Satellite")

# Statik ve Template ayarları
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

HUB_URL = os.getenv("NEXUS_HUB_URL")

@app.on_event("startup")
async def startup_event():
    scheduler = AsyncIOScheduler()
    # TODO: Scout görevlerini buraya ekleyeceğiz (Aşama 1.2)
    scheduler.start()
    app.state.scheduler = scheduler
    log.info("Nexus Curator started. Hub: %s", HUB_URL)

@app.get("/", response_class=HTMLResponse)
async def read_curator_dashboard(request: Request):
    """Zekâ Taslakları ve Onay Paneli (The Curator)"""
    return templates.TemplateResponse("brain_dashboard.html", {"request": request})

@app.get("/api/drafts")
async def list_drafts():
    """İşlenmeyi bekleyen ham scout verileri."""
    draft_path = "./drafts"
    if not os.path.exists(draft_path): return []
    return [f for f in os.listdir(draft_path) if f.endswith(".json")]

@app.get("/api/processed")
async def list_processed():
    """Ollama tarafından Nexus formatına getirilmiş, onay bekleyen taslaklar."""
    processed_path = "./processed"
    if not os.path.exists(processed_path): return []
    return [f for f in os.listdir(processed_path) if f.endswith(".md")]

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
