from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db
from models.account import Account
from models.tenant import Tenant
from schemas.account import AccountResponse, LoginRequest, TokenResponse
from utils.auth import create_access_token, decode_token
from utils.password import verify_password

router = APIRouter(prefix="/api/auth", tags=["auth"])


def tenant_to_account_response(tenant: Tenant) -> AccountResponse:
    return AccountResponse(
        id=tenant.id,
        account=tenant.account,
        nickname=tenant.name,
        role="user",
        status=tenant.status,
        created_at=tenant.created_at,
    )


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(Account).filter(Account.account == data.account).first()
    if user and verify_password(data.password, user.hashed_password):
        if user.status == "inactive":
            raise HTTPException(status_code=403, detail="帳號已停用")

        token = create_access_token({
            "sub": str(user.id),
            "account": user.account,
            "role": user.role,
            "kind": "account",
        })
        return TokenResponse(
            access_token=token,
            account=AccountResponse.model_validate(user),
        )

    tenant = db.query(Tenant).filter(Tenant.account == data.account).first()
    if tenant and verify_password(data.password, tenant.hashed_password):
        if tenant.status == "inactive":
            raise HTTPException(status_code=403, detail="租戶已停用")

        token = create_access_token({
            "sub": str(tenant.id),
            "account": tenant.account,
            "role": "user",
            "kind": "tenant",
        })
        return TokenResponse(
            access_token=token,
            account=tenant_to_account_response(tenant),
        )

    raise HTTPException(status_code=401, detail="帳號或密碼錯誤")


@router.get("/me", response_model=AccountResponse)
def me(
    authorization: Optional[str] = Header(default=None),
    db: Session = Depends(get_db),
):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="缺少 Token")

    token = authorization.removeprefix("Bearer ").strip()
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Token 無效或已過期")

    user_id = payload.get("sub")
    kind = payload.get("kind", "account")
    if not user_id:
        raise HTTPException(status_code=401, detail="Token 缺少使用者資訊")

    if kind == "tenant":
        tenant = db.query(Tenant).filter(Tenant.id == int(user_id)).first()
        if not tenant or tenant.status == "inactive":
            raise HTTPException(status_code=403, detail="租戶不存在或已停用")
        return tenant_to_account_response(tenant)

    user = db.query(Account).filter(Account.id == int(user_id)).first()
    if not user or user.status == "inactive":
        raise HTTPException(status_code=403, detail="帳號不存在或已停用")
    return user
