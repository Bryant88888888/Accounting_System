from sqlalchemy import Column, Integer, Text
from database import Base


class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(Integer, primary_key=True, autoincrement=True)
    account = Column(Text, unique=True, nullable=False)
    name = Column(Text, nullable=False)
    hashed_password = Column(Text, nullable=False)
    email = Column(Text, nullable=True)
    phone = Column(Text, nullable=True)
    note = Column(Text, nullable=True)
    status = Column(Text, default="active")   # active | inactive
    created_at = Column(Text)
