from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .db import SessionLocal
from . import models, schemas
from .utils import generate_code

router = APIRouter(prefix="/api/v1")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/merchant/register_public", response_model=schemas.RegisterPublicOut, status_code=201)
def register_public(inp: schemas.RegisterPublicIn, db: Session = Depends(get_db)):
    if not inp.phone and not inp.email:
        raise HTTPException(status_code=422, detail="phone or email is required")

    # minimal dedupe: by phone/email
    q = db.query(models.Merchant)
    if inp.phone:
        existing = q.filter(models.Merchant.phone == inp.phone).first()
        if existing:
            # regenerate link_code if absent
            if not existing.link_code:
                existing.link_code = generate_code()
                db.add(existing); db.commit(); db.refresh(existing)
            return {"merchant_id": existing.id, "link_code": existing.link_code}
    if inp.email:
        existing = q.filter(models.Merchant.email == inp.email).first()
        if existing:
            if not existing.link_code:
                existing.link_code = generate_code()
                db.add(existing); db.commit(); db.refresh(existing)
            return {"merchant_id": existing.id, "link_code": existing.link_code}

    m = models.Merchant(phone=inp.phone, email=inp.email, password_hash=None, link_code=generate_code())
    db.add(m); db.commit(); db.refresh(m)
    return {"merchant_id": m.id, "link_code": m.link_code}

@router.post("/telegram/link")
def telegram_link(inp: schemas.TelegramLinkIn, db: Session = Depends(get_db)):
    m = db.query(models.Merchant).filter(models.Merchant.link_code == inp.code).first()
    if not m:
        raise HTTPException(status_code=404, detail="code not found")
    m.telegram_chat_id = inp.chat_id
    db.add(m); db.commit()
    return {"ok": True, "merchant_id": m.id}
