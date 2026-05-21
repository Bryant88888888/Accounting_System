from sqlalchemy import Column, Integer, Text, Float, ForeignKey
from database import Base


class SettlementReport(Base):
    __tablename__ = "settlement_reports"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=True)
    start_date = Column(Text)
    end_date = Column(Text)
    created_at = Column(Text)


class SettlementProduct(Base):
    __tablename__ = "settlement_products"

    id = Column(Integer, primary_key=True, autoincrement=True)
    report_id = Column(Integer, ForeignKey("settlement_reports.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    product_name = Column(Text)
    product_code = Column(Text)
    member_count = Column(Integer, default=0)
    bet_count = Column(Integer, default=0)
    bet_amount = Column(Float, default=0)
    valid_bet = Column(Float, default=0)
    raw_win_loss = Column(Float, default=0)
    rebate_rate = Column(Float, default=0)
    rebate_amount = Column(Float, default=0)
    discount_rate = Column(Float, default=0)
    discount_amount = Column(Float, default=0)
    share_rate = Column(Float, default=0)
    settlement = Column(Float, default=0)


class SettlementMember(Base):
    __tablename__ = "settlement_members"

    id = Column(Integer, primary_key=True, autoincrement=True)
    settlement_product_id = Column(Integer, ForeignKey("settlement_products.id"), nullable=False)
    name = Column(Text)
    bet_count = Column(Integer, default=0)
    bet_amount = Column(Float, default=0)
    valid_bet = Column(Float, default=0)
    raw_win_loss = Column(Float, default=0)
    rebate_rate = Column(Float, default=0)
    rebate_amount = Column(Float, default=0)
    discount_rate = Column(Float, default=0)
    discount_amount = Column(Float, default=0)
    share_rate = Column(Float, default=0)
    settlement = Column(Float, default=0)
