from dataclasses import dataclass
from typing import Optional

from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models.account import Account
from models.tenant import Tenant
from utils.auth import decode_token


@dataclass(frozen=True)
class Principal:
    id: int
    account: str
    role: str
    kind: str

    @property
    def is_super_admin(self) -> bool:
        return self.kind == "account" and self.role == "super_admin"

    @property
    def is_tenant(self) -> bool:
        return self.kind == "tenant"


def get_current_principal(
    authorization: Optional[str] = Header(default=None),
    db: Session = Depends(get_db),
) -> Principal:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未登入")

    payload = decode_token(authorization.removeprefix("Bearer ").strip())
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
        return Principal(id=tenant.id, account=tenant.account, role="user", kind="tenant")

    account = db.query(Account).filter(Account.id == int(user_id)).first()
    if not account or account.status == "inactive":
        raise HTTPException(status_code=403, detail="帳號不存在或已停用")
    return Principal(id=account.id, account=account.account, role=account.role, kind="account")


def require_super_admin(
    principal: Principal = Depends(get_current_principal),
) -> Principal:
    if not principal.is_super_admin:
        raise HTTPException(status_code=403, detail="需要超級管理員權限")
    return principal
