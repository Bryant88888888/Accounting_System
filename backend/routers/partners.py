from datetime import date
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models.partner import Partner
from schemas.partner import PartnerCreate, PartnerResponse, PartnerUpdate
from utils.security import Principal, get_current_principal

router = APIRouter(prefix="/api/partners", tags=["partners"])


def scoped_partner_query(db: Session, principal: Principal):
    q = db.query(Partner)
    if principal.is_tenant:
        return q.filter(Partner.tenant_id == principal.id)
    if not principal.is_super_admin:
        return q.filter(Partner.tenant_id.is_(None))
    return q


def get_scoped_partner_or_404(partner_id: int, db: Session, principal: Principal) -> Partner:
    partner = scoped_partner_query(db, principal).filter(Partner.id == partner_id).first()
    if not partner:
        raise HTTPException(status_code=404, detail="夥伴不存在")
    return partner


@router.get("", response_model=List[PartnerResponse])
def list_partners(
    db: Session = Depends(get_db),
    principal: Principal = Depends(get_current_principal),
):
    return scoped_partner_query(db, principal).all()


@router.post("", response_model=PartnerResponse, status_code=201)
def create_partner(
    data: PartnerCreate,
    db: Session = Depends(get_db),
    principal: Principal = Depends(get_current_principal),
):
    existing = scoped_partner_query(db, principal).filter(Partner.name == data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="夥伴名稱已存在")

    partner = Partner(
        tenant_id=principal.id if principal.is_tenant else None,
        name=data.name,
        created_at=str(date.today()),
    )
    db.add(partner)
    db.commit()
    db.refresh(partner)
    return partner


@router.put("/{partner_id}", response_model=PartnerResponse)
def update_partner(
    partner_id: int,
    data: PartnerUpdate,
    db: Session = Depends(get_db),
    principal: Principal = Depends(get_current_principal),
):
    partner = get_scoped_partner_or_404(partner_id, db, principal)
    if data.name:
        existing = scoped_partner_query(db, principal).filter(
            Partner.name == data.name,
            Partner.id != partner.id,
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="夥伴名稱已存在")
        partner.name = data.name
    db.commit()
    db.refresh(partner)
    return partner


@router.delete("/{partner_id}")
def delete_partner(
    partner_id: int,
    db: Session = Depends(get_db),
    principal: Principal = Depends(get_current_principal),
):
    partner = get_scoped_partner_or_404(partner_id, db, principal)
    db.delete(partner)
    db.commit()
    return {"success": True}
