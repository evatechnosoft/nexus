from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import or_
from sqlalchemy.orm import Session

from database import get_db
from email_parser import parse_email
import models
import email_watcher

router = APIRouter(prefix="/requests", tags=["requests"])
templates = Jinja2Templates(directory="templates")


def _get_or_create_person(
    db: Session, name: str, email: str, phone: str, address: str
) -> models.Person:
    """Email ile kişiyi bul; yoksa yeni oluştur ve KSI kodu ata."""
    person = db.query(models.Person).filter_by(email=email.lower().strip()).first()
    if not person:
        person = models.Person(
            name=name.strip(),
            email=email.lower().strip(),
            phone=phone.strip() or None,
            address=address.strip() or None,
        )
        db.add(person)
        db.flush()
        person.person_code = f"KSI-{person.id:04d}"
    else:
        # Bilgileri güncelle (telefon/adres değişmiş olabilir)
        person.name = name.strip()
        if phone:
            person.phone = phone.strip()
        if address:
            person.address = address.strip()
    return person


@router.get("/", response_class=HTMLResponse)
def request_list(
    request: Request,
    q: str = "",
    status: str = "",
    dept: str = "",
    db: Session = Depends(get_db),
):
    query = db.query(models.Request).join(models.Department)

    if q:
        search = f"%{q}%"
        query = query.outerjoin(models.Person).filter(
            or_(
                models.Request.requester_name.ilike(search),
                models.Request.requester_email.ilike(search),
                models.Request.requester_phone.ilike(search),
                models.Person.person_code.ilike(search),
            )
        )
    if status:
        query = query.filter(models.Request.status == status)
    if dept:
        query = query.filter(models.Department.name == dept)

    reqs = query.order_by(models.Request.created_at.desc()).all()
    departments = db.query(models.Department).all()

    return templates.TemplateResponse(
        "requests.html",
        {
            "request": request,
            "requests": reqs,
            "departments": departments,
            "device_types": [e.value for e in models.DeviceType],
            "statuses": [e.value for e in models.RequestStatus],
            "q": q,
            "filter_status": status,
            "filter_dept": dept,
        },
    )


@router.post("/parse-email")
async def parse_email_endpoint(request: Request):
    """Ham email metnini parse edip kişisel bilgileri döndürür."""
    body = await request.json()
    raw = body.get("raw_email", "")
    if not raw.strip():
        return JSONResponse({"error": "Metin boş"}, status_code=400)
    result = parse_email(raw)
    return JSONResponse(result)


@router.post("/add")
def add_request(
    requester_name: str = Form(...),
    requester_email: str = Form(...),
    requester_phone: str = Form(""),
    requester_address: str = Form(""),
    department_id: int = Form(...),
    device_type: str = Form(...),
    notes: str = Form(""),
    db: Session = Depends(get_db),
):
    person = _get_or_create_person(
        db, requester_name, requester_email, requester_phone, requester_address
    )

    req = models.Request(
        person_id=person.id,
        requester_name=requester_name,
        requester_email=requester_email,
        requester_phone=requester_phone or None,
        requester_address=requester_address or None,
        department_id=department_id,
        device_type=device_type,
        notes=notes or None,
        status=models.RequestStatus.pending,
    )
    db.add(req)
    db.commit()
    return RedirectResponse("/requests/", status_code=303)


@router.post("/update-status/{req_id}")
def update_request_status(
    req_id: int,
    status: str = Form(...),
    db: Session = Depends(get_db),
):
    req = db.query(models.Request).filter_by(id=req_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Talep bulunamadı")
    req.status = status
    db.commit()
    return RedirectResponse("/requests/", status_code=303)


@router.get("/delete/{req_id}")
def delete_request(req_id: int, db: Session = Depends(get_db)):
    req = db.query(models.Request).filter_by(id=req_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Talep bulunamadı")

    # Cascade'ler modelde tanımlıysa otomatik silinecektir
    db.delete(req)
    db.commit()
    return RedirectResponse("/requests/", status_code=303)


@router.get("/{req_id}/detail", response_class=HTMLResponse)
def request_detail(req_id: int, request: Request, db: Session = Depends(get_db)):
    req = db.query(models.Request).filter_by(id=req_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Talep bulunamadı")
    config_items = (
        db.query(models.ConfigItem).filter_by(department_id=req.department_id).all()
    )
    available_devices = (
        db.query(models.Device)
        .filter_by(status=models.DeviceStatus.in_stock, device_type=req.device_type)
        .all()
    )
    # Kişinin önceki talepleri
    person_requests = []
    if req.person_id:
        person_requests = (
            db.query(models.Request)
            .filter(
                models.Request.person_id == req.person_id, models.Request.id != req_id
            )
            .order_by(models.Request.created_at.desc())
            .all()
        )
    return templates.TemplateResponse(
        "request_detail.html",
        {
            "request": request,
            "req": req,
            "config_items": config_items,
            "available_devices": available_devices,
            "person_requests": person_requests,
        },
    )


@router.get("/email-queue", response_class=HTMLResponse)
def email_queue_list(request: Request, db: Session = Depends(get_db)):
    """E-posta kuyruğunu listeler."""
    items = (
        db.query(models.EmailQueue).order_by(models.EmailQueue.received_at.desc()).all()
    )
    return templates.TemplateResponse(
        "email_queue.html",
        {
            "request": request,
            "items": items,
        },
    )


@router.post("/email-queue/retry/{item_id}")
def retry_email_item(item_id: int, db: Session = Depends(get_db)):
    """Kuyruktaki bir öğeyi manuel olarak tekrar işlemeye çalışır."""
    item = db.query(models.EmailQueue).filter_by(id=item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Öğe bulunamadı")

    # Durumu beklemeye al ve işlemeyi dene
    item.status = "pending"
    db.commit()

    success = email_watcher._process_email_item(item, db)
    return RedirectResponse("/requests/email-queue", status_code=303)


@router.post("/email-queue/delete/{item_id}")
def delete_email_item(item_id: int, db: Session = Depends(get_db)):
    """Kuyruktaki bir öğeyi siler."""
    item = db.query(models.EmailQueue).filter_by(id=item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Öğe bulunamadı")

    db.delete(item)
    db.commit()
    return RedirectResponse("/requests/email-queue", status_code=303)
