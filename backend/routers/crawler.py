from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models.product import Product
from utils.crawler_runner import fetch_player_metrics, fetch_report, test_connection
from utils.crypto import decrypt_secret, encrypt_secret
from utils.security import Principal, get_current_principal

router = APIRouter(prefix="/api/products", tags=["crawler"])


def _get_product_password(product: Product, db: Session) -> str | None:
    password = decrypt_secret(product.encrypted_password)
    if password:
        return password
    if product.plain_password:
        product.encrypted_password = encrypt_secret(product.plain_password)
        product.plain_password = None
        db.commit()
        return decrypt_secret(product.encrypted_password)
    return None


def _get_product_or_raise(product_id: int, db: Session, principal: Principal) -> Product:
    query = db.query(Product).filter(Product.id == product_id)
    if principal.is_tenant:
        query = query.filter(Product.tenant_id == principal.id)
    elif not principal.is_super_admin:
        query = query.filter(Product.tenant_id.is_(None))

    product = query.first()
    if not product:
        raise HTTPException(status_code=404, detail="產品不存在")
    if not product.crawler_type:
        raise HTTPException(status_code=400, detail="尚未設定查帳平台")
    if not product.account or not _get_product_password(product, db):
        raise HTTPException(status_code=400, detail="帳號或密碼未設定")
    return product


@router.post("/{product_id}/test-connection")
def api_test_connection(
    product_id: int,
    db: Session = Depends(get_db),
    principal: Principal = Depends(get_current_principal),
):
    product = _get_product_or_raise(product_id, db, principal)
    password = _get_product_password(product, db)
    return test_connection(
        product.crawler_type,
        product.account,
        password,
        product.crawler_agent_id,
    )


@router.post("/{product_id}/fetch-report")
def api_fetch_report(
    product_id: int,
    db: Session = Depends(get_db),
    principal: Principal = Depends(get_current_principal),
):
    product = _get_product_or_raise(product_id, db, principal)
    password = _get_product_password(product, db)
    return fetch_report(
        product.crawler_type,
        product.account,
        password,
        product.crawler_agent_id,
    )


@router.post("/{product_id}/player-metrics")
def api_fetch_player_metrics(
    product_id: int,
    db: Session = Depends(get_db),
    principal: Principal = Depends(get_current_principal),
):
    product = _get_product_or_raise(product_id, db, principal)
    password = _get_product_password(product, db)
    return fetch_player_metrics(
        product.crawler_type,
        product.account,
        password,
        product.crawler_agent_id,
    )
