from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models.report import SettlementReport, SettlementProduct

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/today")
def today_summary(db: Session = Depends(get_db)):
    report = db.query(SettlementReport).order_by(SettlementReport.id.desc()).first()
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
