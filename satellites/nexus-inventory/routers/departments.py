from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from database import get_db
import models

router = APIRouter(prefix="/departments", tags=["departments"])
templates = Jinja2Templates(directory="templates")

CONFIG_CATEGORIES = ["Yazılım", "Donanım", "Ağ", "MDM", "Diğer"]


@router.get("/", response_class=HTMLResponse)
def department_list(request: Request, db: Session = Depends(get_db)):
    departments = db.query(models.Department).all()
    return templates.TemplateResponse(
        "departments.html",
        {
            "request": request,
            "departments": departments,
            "categories": CONFIG_CATEGORIES,
        },
    )


@router.post("/add-config")
def add_config(
    department_id: int = Form(...),
    category: str = Form(...),
    name: str = Form(...),
    description: str = Form(""),
    db: Session = Depends(get_db),
):
    dept = db.query(models.Department).filter_by(id=department_id).first()
    if not dept:
        raise HTTPException(status_code=404, detail="Departman bulunamadı")
    item = models.ConfigItem(
        department_id=department_id,
        category=category,
        name=name,
        description=description,
    )
    db.add(item)
    db.commit()
    return RedirectResponse("/departments/", status_code=303)


@router.post("/delete-config/{item_id}")
def delete_config(item_id: int, db: Session = Depends(get_db)):
    item = db.query(models.ConfigItem).filter_by(id=item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Config öğesi bulunamadı")
    db.delete(item)
    db.commit()
    return RedirectResponse("/departments/", status_code=303)
