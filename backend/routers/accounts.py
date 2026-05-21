from datetime import date
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models.account import Account
from schemas.account import AccountCreate, AccountResponse, AccountUpdate
from utils.password import hash_password
from utils.security import Principal, require_super_admin

router = APIRouter(prefix="/api/accounts", tags=["accounts"])


@router.get("", response_model=List[AccountResponse])
def list_accounts(
    db: Session = Depends(get_db),
    _: Principal = Depends(require_super_admin),
):
    return db.query(Account).all()


@router.get("/{account_id}", response_model=AccountResponse)
def get_account(
    account_id: int,
    db: Session = Depends(get_db),
    _: Principal = Depends(require_super_admin),
):
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="帳號不存在")
    return account


@router.post("", response_model=AccountResponse, status_code=201)
def create_account(
    data: AccountCreate,
    db: Session = Depends(get_db),
    _: Principal = Depends(require_super_admin),
):
    if db.query(Account).filter(Account.account == data.account).first():
        raise HTTPException(status_code=400, detail="帳號已存在")
    if db.query(Account).filter(Account.nickname == data.nickname).first():
        raise HTTPException(status_code=400, detail="暱稱已存在")

    account = Account(
        account=data.account,
        nickname=data.nickname,
        hashed_password=hash_password(data.password),
        role=data.role,
        status="active",
        created_at=str(date.today()),
    )
    db.add(account)
    db.commit()
    db.refresh(account)
    return account


@router.put("/{account_id}", response_model=AccountResponse)
def update_account(
    account_id: int,
    data: AccountUpdate,
    db: Session = Depends(get_db),
    _: Principal = Depends(require_super_admin),
):
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="帳號不存在")

    if data.account and data.account != account.account:
        if db.query(Account).filter(Account.account == data.account).first():
            raise HTTPException(status_code=400, detail="帳號已存在")
        account.account = data.account

    if data.nickname and data.nickname != account.nickname:
        if db.query(Account).filter(Account.nickname == data.nickname).first():
            raise HTTPException(status_code=400, detail="暱稱已存在")
        account.nickname = data.nickname

    if data.password:
        account.hashed_password = hash_password(data.password)
    if data.role is not None:
        account.role = data.role
    if data.status is not None:
        account.status = data.status

    db.commit()
    db.refresh(account)
    return account


@router.delete("/{account_id}")
def delete_account(
    account_id: int,
    db: Session = Depends(get_db),
    _: Principal = Depends(require_super_admin),
):
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="帳號不存在")
    if account.role == "super_admin":
        raise HTTPException(status_code=400, detail="不可刪除超級管理員")
    db.delete(account)
    db.commit()
    return {"success": True}


@router.put("/{account_id}/toggle-status", response_model=AccountResponse)
def toggle_status(
    account_id: int,
    db: Session = Depends(get_db),
    _: Principal = Depends(require_super_admin),
):
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="帳號不存在")
    if account.role == "super_admin":
        raise HTTPException(status_code=400, detail="不可停用超級管理員")
    account.status = "inactive" if account.status == "active" else "active"
    db.commit()
    db.refresh(account)
    return account
