from sqlalchemy import Column, Integer, Text
from database import Base


class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    account = Column(Text, unique=True, nullable=False)
    nickname = Column(Text, unique=True, nullable=False)
    hashed_password = Column(Text, nullable=False)
    role = Column(Text, default="user")        # 'super_admin' | 'user'
    status = Column(Text, default="active")    # 'active' | 'inactive'
    created_at = Column(Text)
