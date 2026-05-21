from datetime import date
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models.tenant import Tenant
from schemas.tenant import TenantCreate, TenantResponse, TenantUpdate
from utils.password import hash_password
from utils.security import Principal, require_super_admin

router = APIRouter(prefix="/api/tenants", tags=["tenants"])


@router.get("", response_model=List[TenantResponse])
def list_tenants(
    db: Session = Depends(get_db),
    _: Principal = Depends(require_super_admin),
):
    return db.query(Tenant).all()


@router.get("/{tenant_id}", response_model=TenantResponse)
def get_tenant(
    tenant_id: int,
    db: Session = Depends(get_db),
    _: Principal = Depends(require_super_admin),
):
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="租戶不存在")
    return tenant


@router.post("", response_model=TenantResponse, status_code=201)
def create_tenant(
    data: TenantCreate,
    db: Session = Depends(get_db),
    _: Principal = Depends(require_super_admin),
):
    if db.query(Tenant).filter(Tenant.account == data.account).first():
        raise HTTPException(status_code=400, detail="帳號已存在")

    tenant = Tenant(
        account=data.account,
        name=data.name,
        hashed_password=hash_password(data.password),
        email=data.email,
        phone=data.phone,
        note=data.note,
        status="active",
        created_at=str(date.today()),
    )
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    return tenant


@router.put("/{tenant_id}", response_model=TenantResponse)
def update_tenant(
    tenant_id: int,
    data: TenantUpdate,
    db: Session = Depends(get_db),
    _: Principal = Depends(require_super_admin),
):
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="租戶不存在")

    if data.account and data.account != tenant.account:
        if db.query(Tenant).filter(Tenant.account == data.account).first():
            raise HTTPException(status_code=400, detail="帳號已存在")
        tenant.account = data.account

    if data.name:
        tenant.name = data.name
    if data.password:
        tenant.hashed_password = hash_password(data.password)
    if data.email is not None:
        tenant.email = data.email
    if data.phone is not None:
        tenant.phone = data.phone
    if data.note is not None:
        tenant.note = data.note
    if data.status is not None:
        tenant.status = data.status

    db.commit()
    db.refresh(tenant)
    return tenant


@router.delete("/{tenant_id}")
def delete_tenant(
    tenant_id: int,
    db: Session = Depends(get_db),
    _: Principal = Depends(require_super_admin),
):
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="租戶不存在")
    db.delete(tenant)
    db.commit()
    return {"success": True}


@router.put("/{tenant_id}/toggle-status", response_model=TenantResponse)
def toggle_status(
    tenant_id: int,
    db: Session = Depends(get_db),
    _: Principal = Depends(require_super_admin),
):
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="租戶不存在")
    tenant.status = "inactive" if tenant.status == "active" else "active"
    db.commit()
    db.refresh(tenant)
    return tenant
