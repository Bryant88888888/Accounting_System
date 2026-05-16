from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.product import Product
from utils.crawler_runner import test_connection, fetch_report

router = APIRouter(prefix="/api/products", tags=["crawler"])


@router.post("/{product_id}/test-connection")
def api_test_connection(product_id: int, db: Session = Depends(get_db)):
    p = db.query(Product).filter(Product.id == product_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="產品不存在")
    if not p.crawler_type:
        raise HTTPException(status_code=400, detail="尚未設定爬蟲類型")
    if not p.account or not p.plain_password:
        raise HTTPException(status_code=400, detail="帳號或密碼未設定")

    result = test_connection(p.crawler_type, p.account, p.plain_password)
    return result


@router.post("/{product_id}/fetch-report")
def api_fetch_report(product_id: int, db: Session = Depends(get_db)):
    p = db.query(Product).filter(Product.id == product_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="產品不存在")
    if not p.crawler_type:
        raise HTTPException(status_code=400, detail="尚未設定爬蟲類型")
    if not p.account or not p.plain_password:
        raise HTTPException(status_code=400, detail="帳號或密碼未設定")

    result = fetch_report(p.crawler_type, p.account, p.plain_password)
    return result
