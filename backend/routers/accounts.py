from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import date
from database import get_db
from models.account import Account
from schemas.account import AccountCreate, AccountUpdate, AccountResponse
from utils.password import hash_password

router = APIRouter(prefix="/api/accounts", tags=["accounts"])


@router.get("", response_model=List[AccountResponse])
def list_accounts(db: Session = Depends(get_db)):
    return db.query(Account).all()


@router.get("/{account_id}", response_model=AccountResponse)
def get_account(account_id: int, db: Session = Depends(get_db)):
    acc = db.query(Account).filter(Account.id == account_id).first()
    if not acc:
        raise HTTPException(status_code=404, detail="帳號不存在")
    return acc


@router.post("", response_model=AccountResponse, status_code=201)
def create_account(data: AccountCreate, db: Session = Depends(get_db)):
    if db.query(Account).filter(Account.account == data.account).first():
        raise HTTPException(status_code=400, detail="帳號已存在，請使用其他帳號")
    if db.query(Account).filter(Account.nickname == data.nickname).first():
        raise HTTPException(status_code=400, detail="暱稱已存在，請使用其他暱稱")

    acc = Account(
        account=data.account,
        nickname=data.nickname,
        hashed_password=hash_password(data.password),
        role=data.role,
        status="active",
        created_at=str(date.today()),
    )
    db.add(acc)
    db.commit()
    db.refresh(acc)
    return acc


@router.put("/{account_id}", response_model=AccountResponse)
def update_account(account_id: int, data: AccountUpdate, db: Session = Depends(get_db)):
    acc = db.query(Account).filter(Account.id == account_id).first()
    if not acc:
        raise HTTPException(status_code=404, detail="帳號不存在")

    if data.account and data.account != acc.account:
        if db.query(Account).filter(Account.account == data.account).first():
            raise HTTPException(status_code=400, detail="帳號已存在，請使用其他帳號")
        acc.account = data.account

    if data.nickname and data.nickname != acc.nickname:
        if db.query(Account).filter(Account.nickname == data.nickname).first():
            raise HTTPException(status_code=400, detail="暱稱已存在，請使用其他暱稱")
        acc.nickname = data.nickname

    if data.password:
        acc.hashed_password = hash_password(data.password)

    if data.role is not None:
        acc.role = data.role
    if data.status is not None:
        acc.status = data.status

    db.commit()
    db.refresh(acc)
    return acc


@router.delete("/{account_id}")
def delete_account(account_id: int, db: Session = Depends(get_db)):
    acc = db.query(Account).filter(Account.id == account_id).first()
    if not acc:
        raise HTTPException(status_code=404, detail="帳號不存在")
    if acc.role == "super_admin":
        raise HTTPException(status_code=400, detail="無法刪除超級管理者帳號")
    db.delete(acc)
    db.commit()
    return {"success": True}


@router.put("/{account_id}/toggle-status", response_model=AccountResponse)
def toggle_status(account_id: int, db: Session = Depends(get_db)):
    acc = db.query(Account).filter(Account.id == account_id).first()
    if not acc:
        raise HTTPException(status_code=404, detail="帳號不存在")
    if acc.role == "super_admin":
        raise HTTPException(status_code=400, detail="無法停用超級管理者")
    acc.status = "inactive" if acc.status == "active" else "active"
    db.commit()
    db.refresh(acc)
    return acc
