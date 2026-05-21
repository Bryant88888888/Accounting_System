from sqlalchemy import Column, Integer, Text, ForeignKey
from database import Base


class Partner(Base):
    __tablename__ = "partners"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=True)
    name = Column(Text, unique=True, nullable=False)
    created_at = Column(Text)
