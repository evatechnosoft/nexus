import os
import logging
from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import engine, get_db
import models

# Veritabanı tablolarını oluştur
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Nexus Inventory Satellite v1.0")

# Statik ve Template ayarları
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
templates.env.globals.update({"APP_ENV": os.getenv("APP_ENV", "PROD")})

# Router Entegrasyonu
from routers import inventory, requests, assignments, departments
app.include_router(inventory.router)
app.include_router(requests.router)
app.include_router(assignments.router)
app.include_router(departments.router)

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    """Fiziksel Envanter Dashboard'u"""
    devices = db.query(models.Device).all()
    reqs = db.query(models.Request).all()
    
    stats = {
        "total_devices": len(devices),
        "in_stock": sum(1 for d in devices if d.status == models.DeviceStatus.in_stock),
        "assigned": sum(1 for d in devices if d.status == models.DeviceStatus.assigned),
        "pending_requests": sum(1 for r in reqs if r.status == models.RequestStatus.pending)
    }
    
    # Son talepleri getir
    recent_requests = db.query(models.Request).order_by(models.Request.created_at.desc()).limit(10).all()
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "stats": stats,
        "recent_requests": recent_requests
    })

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("APP_PORT", 4800))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
