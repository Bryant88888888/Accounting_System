from pydantic import BaseModel
from typing import Optional


class TenantCreate(BaseModel):
    account: str
    name: str
    password: str
    email: Optional[str] = None
    phone: Optional[str] = None
    note: Optional[str] = None


class TenantUpdate(BaseModel):
    account: Optional[str] = None
    name: Optional[str] = None
    password: Optional[str] = None   # 空白不修改
    email: Optional[str] = None
    phone: Optional[str] = None
    note: Optional[str] = None
    status: Optional[str] = None


class TenantResponse(BaseModel):
    id: int
    account: str
    name: str
    email: Optional[str]
    phone: Optional[str]
    note: Optional[str]
    status: str
    created_at: Optional[str]

    class Config:
        from_attributes = True
