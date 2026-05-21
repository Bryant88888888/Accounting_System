from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db
from models.partner import Partner
from models.product import Product, ProductDownstream
from schemas.product import (
    DownstreamResponse,
    PartnerRef,
    ProductCreate,
    ProductResponse,
    ProductUpdate,
)
from utils.crypto import encrypt_secret
from utils.security import Principal, get_current_principal

router = APIRouter(prefix="/api/products", tags=["products"])


def scoped_product_query(db: Session, principal: Principal):
    q = db.query(Product)
    if principal.is_tenant:
        return q.filter(Product.tenant_id == principal.id)
    if not principal.is_super_admin:
        return q.filter(Product.tenant_id.is_(None))
    return q


def get_scoped_product_or_404(product_id: int, db: Session, principal: Principal) -> Product:
    product = scoped_product_query(db, principal).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="產品不存在")
    return product


def build_product_response(p: Product, db: Session) -> ProductResponse:
    upstream = None
    if p.upstream_partner_id:
        partner = db.query(Partner).filter(Partner.id == p.upstream_partner_id).first()
        if partner:
            upstream = PartnerRef(
                id=str(partner.id),
                name=partner.name,
                percentage=p.upstream_percentage or 0,
            )

    downstreams_raw = db.query(ProductDownstream).filter(ProductDownstream.product_id == p.id).all()
    downstreams = [
        DownstreamResponse(id=str(d.id), name=d.name or "", percentage=d.percentage or 0)
        for d in downstreams_raw
    ]

    return ProductResponse(
        id=p.id,
        name=p.name,
        series=p.series,
        code=p.code,
        description=p.description,
        platform_type=p.platform_type,
        platform_url=p.platform_url,
        account=p.account,
        crawler_type=p.crawler_type,
        crawler_agent_id=p.crawler_agent_id,
        status=p.status,
        upstream=upstream,
        my_percentage=p.my_percentage,
        downstreams=downstreams,
        rebate_rate=p.rebate_rate,
        discount_rate=p.discount_rate,
        created_at=p.created_at,
    )


@router.get("/series", response_model=List[str])
def get_series(
    db: Session = Depends(get_db),
    principal: Principal = Depends(get_current_principal),
):
    rows = scoped_product_query(db, principal).with_entities(Product.series).distinct().all()
    return [r[0] for r in rows if r[0]]


@router.get("", response_model=List[ProductResponse])
def list_products(
    series: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    principal: Principal = Depends(get_current_principal),
):
    q = scoped_product_query(db, principal)
    if series and series != "all":
        q = q.filter(Product.series == series)
    return [build_product_response(p, db) for p in q.all()]


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    principal: Principal = Depends(get_current_principal),
):
    return build_product_response(get_scoped_product_or_404(product_id, db, principal), db)


@router.post("", response_model=ProductResponse, status_code=201)
def create_product(
    data: ProductCreate,
    db: Session = Depends(get_db),
    principal: Principal = Depends(get_current_principal),
):
    p = Product(
        tenant_id=principal.id if principal.is_tenant else None,
        name=data.name,
        series=data.series,
        code=data.code,
        description=data.description,
        platform_type=data.platform_type,
        platform_url=data.platform_url,
        account=data.account,
        hashed_password=None,
        encrypted_password=encrypt_secret(data.password),
        plain_password=None,
        crawler_type=data.crawler_type,
        crawler_agent_id=data.crawler_agent_id,
        status="active",
        upstream_partner_id=data.upstream_partner_id,
        upstream_percentage=data.upstream_percentage,
        my_percentage=data.my_percentage,
        rebate_rate=data.rebate_rate,
        discount_rate=data.discount_rate,
        created_at=str(date.today()),
    )
    db.add(p)
    db.flush()

    for ds in data.downstreams or []:
        db.add(ProductDownstream(product_id=p.id, name=ds.name, percentage=ds.percentage))

    db.commit()
    db.refresh(p)
    return build_product_response(p, db)


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    data: ProductUpdate,
    db: Session = Depends(get_db),
    principal: Principal = Depends(get_current_principal),
):
    p = get_scoped_product_or_404(product_id, db, principal)

    for field in [
        "name",
        "series",
        "code",
        "description",
        "platform_type",
        "platform_url",
        "account",
        "upstream_partner_id",
        "upstream_percentage",
        "my_percentage",
        "rebate_rate",
        "discount_rate",
        "crawler_type",
        "crawler_agent_id",
    ]:
        val = getattr(data, field, None)
        if val is not None:
            setattr(p, field, val)

    if data.password:
        p.hashed_password = None
        p.encrypted_password = encrypt_secret(data.password)
        p.plain_password = None

    if data.downstreams is not None:
        db.query(ProductDownstream).filter(ProductDownstream.product_id == p.id).delete()
        for ds in data.downstreams:
            db.add(ProductDownstream(product_id=p.id, name=ds.name, percentage=ds.percentage))

    db.commit()
    db.refresh(p)
    return build_product_response(p, db)


@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    principal: Principal = Depends(get_current_principal),
):
    p = get_scoped_product_or_404(product_id, db, principal)
    db.query(ProductDownstream).filter(ProductDownstream.product_id == p.id).delete()
    db.delete(p)
    db.commit()
    return {"success": True}
