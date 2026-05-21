from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models.product import Product
from models.risk import RiskRecord
from utils.security import Principal, get_current_principal

router = APIRouter(prefix="/api/risk", tags=["risk"])


def scoped_risk_query(db: Session, principal: Principal):
    q = db.query(RiskRecord)
    if principal.is_super_admin:
        return q
    if principal.is_tenant:
        return q.join(Product, RiskRecord.product_id == Product.id).filter(Product.tenant_id == principal.id)
    return q.join(Product, RiskRecord.product_id == Product.id).filter(Product.tenant_id.is_(None))


@router.get("/members")
def list_members(
    db: Session = Depends(get_db),
    principal: Principal = Depends(get_current_principal),
):
    records = scoped_risk_query(db, principal).order_by(RiskRecord.id.desc()).all()
    return [
        {
            "id": r.id,
            "member_name": r.member_name,
            "product_id": r.product_id,
            "record_date": r.record_date,
            "bet_count": r.bet_count,
            "bet_amount": r.bet_amount,
            "win_loss": r.win_loss,
            "risk_level": r.risk_level,
            "notes": r.notes,
        }
        for r in records
    ]


@router.get("/members/{name}/history")
def member_history(
    name: str,
    db: Session = Depends(get_db),
    principal: Principal = Depends(get_current_principal),
):
    records = scoped_risk_query(db, principal).filter(RiskRecord.member_name == name).all()
    return [
        {
            "id": r.id,
            "record_date": r.record_date,
            "bet_count": r.bet_count,
            "bet_amount": r.bet_amount,
            "win_loss": r.win_loss,
            "risk_level": r.risk_level,
            "notes": r.notes,
        }
        for r in records
    ]
