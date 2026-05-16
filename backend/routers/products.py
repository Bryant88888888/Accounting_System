from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from database import get_db
from models.product import Product, ProductDownstream
from models.partner import Partner
from schemas.product import ProductCreate, ProductUpdate, ProductResponse, PartnerRef, DownstreamResponse
from utils.password import hash_password

router = APIRouter(prefix="/api/products", tags=["products"])


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
        status=p.status,
        upstream=upstream,
        my_percentage=p.my_percentage,
        downstreams=downstreams,
        rebate_rate=p.rebate_rate,
        discount_rate=p.discount_rate,
        created_at=p.created_at,
    )


@router.get("/series", response_model=List[str])
def get_series(db: Session = Depends(get_db)):
    rows = db.query(Product.series).distinct().all()
    return [r[0] for r in rows if r[0]]


@router.get("", response_model=List[ProductResponse])
def list_products(series: Optional[str] = Query(None), db: Session = Depends(get_db)):
    q = db.query(Product)
    if series and series != "all":
        q = q.filter(Product.series == series)
    products = q.all()
    return [build_product_response(p, db) for p in products]


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    p = db.query(Product).filter(Product.id == product_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="產品不存在")
    return build_product_response(p, db)


@router.post("", response_model=ProductResponse, status_code=201)
def create_product(data: ProductCreate, db: Session = Depends(get_db)):
    hashed_pw = hash_password(data.password) if data.password else None
    p = Product(
        name=data.name,
        series=data.series,
        code=data.code,
        description=data.description,
        platform_type=data.platform_type,
        platform_url=data.platform_url,
        account=data.account,
        hashed_password=hashed_pw,
        plain_password=data.password,
        crawler_type=data.crawler_type,
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

    for ds in (data.downstreams or []):
        db.add(ProductDownstream(product_id=p.id, name=ds.name, percentage=ds.percentage))

    db.commit()
    db.refresh(p)
    return build_product_response(p, db)


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(product_id: int, data: ProductUpdate, db: Session = Depends(get_db)):
    p = db.query(Product).filter(Product.id == product_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="產品不存在")

    for field in ["name", "series", "code", "description", "platform_type",
                  "platform_url", "account", "upstream_partner_id",
                  "upstream_percentage", "my_percentage", "rebate_rate", "discount_rate",
                  "crawler_type"]:
        val = getattr(data, field, None)
        if val is not None:
            setattr(p, field, val)

    if data.password:
        p.hashed_password = hash_password(data.password)
        p.plain_password = data.password

    if data.downstreams is not None:
        db.query(ProductDownstream).filter(ProductDownstream.product_id == p.id).delete()
        for ds in data.downstreams:
            db.add(ProductDownstream(product_id=p.id, name=ds.name, percentage=ds.percentage))

    db.commit()
    db.refresh(p)
    return build_product_response(p, db)


@router.delete("/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    p = db.query(Product).filter(Product.id == product_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="產品不存在")
    db.query(ProductDownstream).filter(ProductDownstream.product_id == p.id).delete()
    db.delete(p)
    db.commit()
    return {"success": True}
