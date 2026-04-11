import json
from datetime import datetime

from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from database import get_db
import models

router = APIRouter(prefix="/assignments", tags=["assignments"])
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
def assignment_list(request: Request, db: Session = Depends(get_db)):
    assignments = (
        db.query(models.Assignment).order_by(models.Assignment.assigned_at.desc()).all()
    )
    return templates.TemplateResponse(
        "assignments.html",
        {
            "request": request,
            "assignments": assignments,
        },
    )


@router.post("/create")
def create_assignment(
    request_id: int = Form(...),
    device_id: int = Form(...),
    checklist: str = Form("[]"),  # JSON list of completed config item ids
    notes: str = Form(""),
    db: Session = Depends(get_db),
):
    req = db.query(models.Request).filter_by(id=request_id).first()
    device = db.query(models.Device).filter_by(id=device_id).first()

    if not req or not device:
        raise HTTPException(status_code=404, detail="Talep veya cihaz bulunamadı")
    if device.status != models.DeviceStatus.in_stock:
        raise HTTPException(status_code=400, detail="Cihaz depoda değil")
    if req.assignment:
        raise HTTPException(
            status_code=400, detail="Bu talep için zaten atama yapılmış"
        )

    assignment = models.Assignment(
        request_id=request_id,
        device_id=device_id,
        config_checklist=checklist,
        notes=notes,
    )
    db.add(assignment)

    device.status = models.DeviceStatus.assigned
    req.status = models.RequestStatus.approved
    db.commit()

    return RedirectResponse(f"/assignments/{assignment.id}/shipment", status_code=303)


@router.get("/{assignment_id}/shipment", response_class=HTMLResponse)
def shipment_view(assignment_id: int, request: Request, db: Session = Depends(get_db)):
    assignment = db.query(models.Assignment).filter_by(id=assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Atama bulunamadı")
    config_items = (
        db.query(models.ConfigItem)
        .filter_by(department_id=assignment.request.department_id)
        .all()
    )
    try:
        checked_ids = json.loads(assignment.config_checklist or "[]")
    except Exception:
        checked_ids = []
    return templates.TemplateResponse(
        "shipment.html",
        {
            "request": request,
            "assignment": assignment,
            "config_items": config_items,
            "checked_ids": checked_ids,
        },
    )


@router.post("/{assignment_id}/mark-shipped")
def mark_shipped(
    assignment_id: int,
    tracking_no: str = Form(""),
    db: Session = Depends(get_db),
):
    assignment = db.query(models.Assignment).filter_by(id=assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Atama bulunamadı")
    assignment.shipped_at = datetime.utcnow()
    assignment.tracking_no = tracking_no
    assignment.request.status = models.RequestStatus.shipped
    db.commit()
    return RedirectResponse("/assignments/", status_code=303)
