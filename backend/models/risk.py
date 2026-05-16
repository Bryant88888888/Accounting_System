from sqlalchemy import Column, Integer, Text, Float, ForeignKey
from database import Base


class RiskRecord(Base):
    __tablename__ = "risk_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    member_name = Column(Text, nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    record_date = Column(Text)
    bet_count = Column(Float)
    bet_amount = Column(Float)
    win_loss = Column(Float)
    risk_level = Column(Text)   # 'low' | 'medium' | 'high'
    notes = Column(Text)
    created_at = Column(Text)
