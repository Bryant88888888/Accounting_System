from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import date
from database import get_db
from models.tenant import Tenant
from schemas.tenant import TenantCreate, TenantUpdate, TenantResponse
from utils.password import hash_password

router = APIRouter(prefix="/api/tenants", tags=["tenants"])


@router.get("", response_model=List[TenantResponse])
def list_tenants(db: Session = Depends(get_db)):
    return db.query(Tenant).all()


@router.get("/{tenant_id}", response_model=TenantResponse)
def get_tenant(tenant_id: int, db: Session = Depends(get_db)):
    t = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="租戶不存在")
    return t


@router.post("", response_model=TenantResponse, status_code=201)
def create_tenant(data: TenantCreate, db: Session = Depends(get_db)):
    if db.query(Tenant).filter(Tenant.account == data.account).first():
        raise HTTPException(status_code=400, detail="帳號已存在，請使用其他帳號")

    t = Tenant(
        account=data.account,
        name=data.name,
        hashed_password=hash_password(data.password),
        email=data.email,
        phone=data.phone,
        note=data.note,
        status="active",
        created_at=str(date.today()),
    )
    db.add(t)
    db.commit()
    db.refresh(t)
    return t


@router.put("/{tenant_id}", response_model=TenantResponse)
def update_tenant(tenant_id: int, data: TenantUpdate, db: Session = Depends(get_db)):
    t = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="租戶不存在")

    if data.account and data.account != t.account:
        if db.query(Tenant).filter(Tenant.account == data.account).first():
            raise HTTPException(status_code=400, detail="帳號已存在，請使用其他帳號")
        t.account = data.account

    if data.name:
        t.name = data.name
    if data.password:
        t.hashed_password = hash_password(data.password)
    if data.email is not None:
        t.email = data.email
    if data.phone is not None:
        t.phone = data.phone
    if data.note is not None:
        t.note = data.note
    if data.status is not None:
        t.status = data.status

    db.commit()
    db.refresh(t)
    return t


@router.delete("/{tenant_id}")
def delete_tenant(tenant_id: int, db: Session = Depends(get_db)):
    t = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="租戶不存在")
    db.delete(t)
    db.commit()
    return {"success": True}


@router.put("/{tenant_id}/toggle-status", response_model=TenantResponse)
def toggle_status(tenant_id: int, db: Session = Depends(get_db)):
    t = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="租戶不存在")
    t.status = "inactive" if t.status == "active" else "active"
    db.commit()
    db.refresh(t)
    return t
