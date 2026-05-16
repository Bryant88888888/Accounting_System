from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models.risk import RiskRecord

router = APIRouter(prefix="/api/risk", tags=["risk"])


@router.get("/members")
def list_members(db: Session = Depends(get_db)):
    records = db.query(RiskRecord).order_by(RiskRecord.id.desc()).all()
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
def member_history(name: str, db: Session = Depends(get_db)):
    records = db.query(RiskRecord).filter(RiskRecord.member_name == name).all()
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
