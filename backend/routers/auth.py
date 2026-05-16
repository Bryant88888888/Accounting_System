from fastapi import APIRouter, Depends, HTTPException, Header
from typing import Optional
from sqlalchemy.orm import Session
from database import get_db
from models.account import Account
from schemas.account import LoginRequest, TokenResponse, AccountResponse
from utils.password import verify_password
from utils.auth import create_access_token, decode_token

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(Account).filter(Account.account == data.account).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="帳號或密碼錯誤")
    if user.status == "inactive":
        raise HTTPException(status_code=403, detail="帳號已停用")

    token = create_access_token({"sub": str(user.id), "account": user.account, "role": user.role})
    return TokenResponse(
        access_token=token,
        account=AccountResponse.model_validate(user),
    )


@router.get("/me", response_model=AccountResponse)
def me(
    authorization: Optional[str] = Header(default=None),
    db: Session = Depends(get_db),
):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未提供認證 Token")
    token = authorization.removeprefix("Bearer ").strip()
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Token 無效或已過期")
    user_id = payload.get("sub")
    user = db.query(Account).filter(Account.id == int(user_id)).first()
    if not user or user.status == "inactive":
        raise HTTPException(status_code=403, detail="帳號無效或已停用")
    return user
