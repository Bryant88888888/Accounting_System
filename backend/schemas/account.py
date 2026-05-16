from pydantic import BaseModel
from typing import Optional, Literal


class AccountCreate(BaseModel):
    account: str
    nickname: str
    password: str
    role: Literal["super_admin", "user"] = "user"


class AccountUpdate(BaseModel):
    account: Optional[str] = None
    nickname: Optional[str] = None
    password: Optional[str] = None   # 空白不修改
    role: Optional[Literal["super_admin", "user"]] = None
    status: Optional[Literal["active", "inactive"]] = None


class AccountResponse(BaseModel):
    id: int
    account: str
    nickname: str
    role: str
    status: str
    created_at: Optional[str]

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    account: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    account: AccountResponse
