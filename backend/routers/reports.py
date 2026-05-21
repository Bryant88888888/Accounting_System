from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db
from models.report import SettlementMember, SettlementProduct, SettlementReport
from schemas.report import (
    MemberResponse,
    ProductResponse,
    ReportCreate,
    ReportResponse,
    ReportTotals,
)
from utils.security import Principal, get_current_principal

router = APIRouter(prefix="/api/reports", tags=["reports"])


def scoped_report_query(db: Session, principal: Principal):
    q = db.query(SettlementReport)
    if principal.is_tenant:
        return q.filter(SettlementReport.tenant_id == principal.id)
    if not principal.is_super_admin:
        return q.filter(SettlementReport.tenant_id.is_(None))
    return q


def build_report_response(report: SettlementReport, db: Session) -> ReportResponse:
    products_raw = db.query(SettlementProduct).filter(
        SettlementProduct.report_id == report.id
    ).all()

    products = []
    totals = ReportTotals(
        bet_count=0,
        bet_amount=0,
        valid_bet=0,
        raw_win_loss=0,
        rebate_amount=0,
        discount_amount=0,
        settlement=0,
    )

    for sp in products_raw:
        members_raw = db.query(SettlementMember).filter(
            SettlementMember.settlement_product_id == sp.id
        ).all()
        members = [MemberResponse.model_validate(m) for m in members_raw]

        products.append(ProductResponse(
            id=sp.id,
            product_name=sp.product_name or "",
            product_code=sp.product_code,
            member_count=sp.member_count or 0,
            bet_count=sp.bet_count or 0,
            bet_amount=sp.bet_amount or 0,
            valid_bet=sp.valid_bet or 0,
            raw_win_loss=sp.raw_win_loss or 0,
            rebate_rate=sp.rebate_rate or 0,
            rebate_amount=sp.rebate_amount or 0,
            discount_rate=sp.discount_rate or 0,
            discount_amount=sp.discount_amount or 0,
            share_rate=sp.share_rate or 0,
            settlement=sp.settlement or 0,
            members=members,
        ))

        totals.bet_count += sp.bet_count or 0
        totals.bet_amount += sp.bet_amount or 0
        totals.valid_bet += sp.valid_bet or 0
        totals.raw_win_loss += sp.raw_win_loss or 0
        totals.rebate_amount += sp.rebate_amount or 0
        totals.discount_amount += sp.discount_amount or 0
        totals.settlement += sp.settlement or 0

    return ReportResponse(
        id=report.id,
        start_date=report.start_date,
        end_date=report.end_date,
        products=products,
        totals=totals,
    )


@router.get("/settlement", response_model=ReportResponse)
def get_settlement(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    principal: Principal = Depends(get_current_principal),
):
    q = scoped_report_query(db, principal)
    if start_date:
        q = q.filter(SettlementReport.start_date == start_date)
    if end_date:
        q = q.filter(SettlementReport.end_date == end_date)
    report = q.order_by(SettlementReport.id.desc()).first()

    if not report:
        report = scoped_report_query(db, principal).order_by(SettlementReport.id.desc()).first()

    if not report:
        raise HTTPException(status_code=404, detail="尚無報表資料")
    return build_report_response(report, db)


@router.post("/settlement", response_model=ReportResponse, status_code=201)
def create_report(
    data: ReportCreate,
    db: Session = Depends(get_db),
    principal: Principal = Depends(get_current_principal),
):
    report = SettlementReport(
        tenant_id=principal.id if principal.is_tenant else None,
        start_date=data.start_date,
        end_date=data.end_date,
        created_at=str(date.today()),
    )
    db.add(report)
    db.flush()

    for pd in data.products:
        sp = SettlementProduct(
            report_id=report.id,
            product_id=pd.product_id,
            product_name=pd.product_name,
            product_code=pd.product_code,
            member_count=pd.member_count,
            bet_count=pd.bet_count,
            bet_amount=pd.bet_amount,
            valid_bet=pd.valid_bet,
            raw_win_loss=pd.raw_win_loss,
            rebate_rate=pd.rebate_rate,
            rebate_amount=pd.rebate_amount,
            discount_rate=pd.discount_rate,
            discount_amount=pd.discount_amount,
            share_rate=pd.share_rate,
            settlement=pd.settlement,
        )
        db.add(sp)
        db.flush()

        for m in pd.members:
            db.add(SettlementMember(
                settlement_product_id=sp.id,
                name=m.name,
                bet_count=m.bet_count,
                bet_amount=m.bet_amount,
                valid_bet=m.valid_bet,
                raw_win_loss=m.raw_win_loss,
                rebate_rate=m.rebate_rate,
                rebate_amount=m.rebate_amount,
                discount_rate=m.discount_rate,
                discount_amount=m.discount_amount,
                share_rate=m.share_rate,
                settlement=m.settlement,
            ))

    db.commit()
    db.refresh(report)
    return build_report_response(report, db)
