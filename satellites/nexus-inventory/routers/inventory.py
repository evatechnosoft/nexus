from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import or_
from sqlalchemy.orm import Session

from database import get_db
import models

router = APIRouter(prefix="/inventory", tags=["inventory"])
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
def inventory_list(
    request: Request,
    q: str = "",
    status: str = "",
    device_type: str = "",
    imported: int = 0,
    skipped: int = 0,
    db: Session = Depends(get_db),
):
    query = db.query(models.Device)

    if q:
        search = f"%{q}%"
        query = query.filter(
            or_(
                models.Device.inventory_code.ilike(search),
                models.Device.serial_no.ilike(search),
                models.Device.imei.ilike(search),
                models.Device.brand.ilike(search),
                models.Device.model.ilike(search),
            )
        )
    if status:
        query = query.filter(models.Device.status == status)
    if device_type:
        query = query.filter(models.Device.device_type == device_type)

    devices = query.order_by(models.Device.created_at.desc()).all()

    all_devices = db.query(models.Device).all()
    stats = {
        "total": len(all_devices),
        "in_stock": sum(
            1 for d in all_devices if d.status == models.DeviceStatus.in_stock
        ),
        "assigned": sum(
            1 for d in all_devices if d.status == models.DeviceStatus.assigned
        ),
        "service": sum(
            1 for d in all_devices if d.status == models.DeviceStatus.service
        ),
    }

    return templates.TemplateResponse(
        "inventory.html",
        {
            "request": request,
            "devices": devices,
            "stats": stats,
            "device_types": [e.value for e in models.DeviceType],
            "device_statuses": [e.value for e in models.DeviceStatus],
            "q": q,
            "filter_status": status,
            "filter_type": device_type,
            "imported": imported,
            "skipped": skipped,
        },
    )


@router.post("/add")
def add_device(
    device_type: str = Form(...),
    brand: str = Form(...),
    model: str = Form(...),
    serial_no: str = Form(...),
    imei: str = Form(""),
    notes: str = Form(""),
    db: Session = Depends(get_db),
):
    if db.query(models.Device).filter_by(serial_no=serial_no).first():
        raise HTTPException(status_code=400, detail="Bu seri numarası zaten kayıtlı")
    if imei and db.query(models.Device).filter_by(imei=imei).first():
        raise HTTPException(status_code=400, detail="Bu IMEI zaten kayıtlı")

    device = models.Device(
        device_type=device_type,
        brand=brand,
        model=model,
        serial_no=serial_no,
        imei=imei.strip() or None,
        notes=notes or None,
        status=models.DeviceStatus.in_stock,
    )
    db.add(device)
    db.flush()
    device.inventory_code = f"ENV-{device.id:04d}"
    db.commit()
    return RedirectResponse("/inventory/", status_code=303)


@router.post("/update-status/{device_id}")
def update_status(
    device_id: int,
    status: str = Form(...),
    db: Session = Depends(get_db),
):
    device = db.query(models.Device).filter_by(id=device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Cihaz bulunamadı")
    device.status = status
    db.commit()
    return RedirectResponse("/inventory/", status_code=303)


@router.post("/delete/{device_id}")
def delete_device(device_id: int, db: Session = Depends(get_db)):
    device = db.query(models.Device).filter_by(id=device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Cihaz bulunamadı")
    if device.status == models.DeviceStatus.assigned:
        raise HTTPException(status_code=400, detail="Dağıtılmış cihaz silinemez")
    db.delete(device)
    db.commit()
    return RedirectResponse("/inventory/", status_code=303)
