from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import date
from database import get_db
from models.partner import Partner
from schemas.partner import PartnerCreate, PartnerUpdate, PartnerResponse

router = APIRouter(prefix="/api/partners", tags=["partners"])


@router.get("", response_model=List[PartnerResponse])
def list_partners(db: Session = Depends(get_db)):
    return db.query(Partner).all()


@router.post("", response_model=PartnerResponse, status_code=201)
def create_partner(data: PartnerCreate, db: Session = Depends(get_db)):
    if db.query(Partner).filter(Partner.name == data.name).first():
        raise HTTPException(status_code=400, detail="夥伴名稱已存在")
    p = Partner(name=data.name, created_at=str(date.today()))
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


@router.put("/{partner_id}", response_model=PartnerResponse)
def update_partner(partner_id: int, data: PartnerUpdate, db: Session = Depends(get_db)):
    p = db.query(Partner).filter(Partner.id == partner_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="夥伴不存在")
    if data.name:
        p.name = data.name
    db.commit()
    db.refresh(p)
    return p


@router.delete("/{partner_id}")
def delete_partner(partner_id: int, db: Session = Depends(get_db)):
    p = db.query(Partner).filter(Partner.id == partner_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="夥伴不存在")
    db.delete(p)
    db.commit()
    return {"success": True}
