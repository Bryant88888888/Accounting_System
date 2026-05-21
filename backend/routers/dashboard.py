from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models.report import SettlementProduct, SettlementReport
from utils.security import Principal, get_current_principal

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


def scoped_report_query(db: Session, principal: Principal):
    q = db.query(SettlementReport)
    if principal.is_tenant:
        return q.filter(SettlementReport.tenant_id == principal.id)
    if not principal.is_super_admin:
        return q.filter(SettlementReport.tenant_id.is_(None))
    return q


@router.get("/today")
def today_summary(
    db: Session = Depends(get_db),
    principal: Principal = Depends(get_current_principal),
):
    report = scoped_report_query(db, principal).order_by(SettlementReport.id.desc()).first()
    if not report:
        return {"raw_win_loss": 0, "settlement": 0, "bet_amount": 0, "bet_count": 0}

    products = db.query(SettlementProduct).filter(
        SettlementProduct.report_id == report.id
    ).all()

    return {
        "raw_win_loss": sum(p.raw_win_loss or 0 for p in products),
        "settlement": sum(p.settlement or 0 for p in products),
        "bet_amount": sum(p.bet_amount or 0 for p in products),
        "bet_count": sum(p.bet_count or 0 for p in products),
    }
