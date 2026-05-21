import os
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy.orm import Session

from database import get_db
from models.telegram import TelegramConfig
from schemas.telegram import TelegramConfigResponse, TelegramConfigUpdate
from utils.security import Principal, require_super_admin
from utils.telegram import reply_chat_id

router = APIRouter(prefix="/api/telegram", tags=["telegram"])


def _get_or_create(db: Session) -> TelegramConfig:
    cfg = db.query(TelegramConfig).first()
    if not cfg:
        cfg = TelegramConfig(created_at=str(date.today()))
        db.add(cfg)
        db.commit()
        db.refresh(cfg)
    return cfg


@router.post("/webhook")
async def webhook(
    request: Request,
    x_telegram_bot_api_secret_token: Optional[str] = Header(default=None),
):
    expected_secret = os.getenv("TELEGRAM_WEBHOOK_SECRET")
    if expected_secret and x_telegram_bot_api_secret_token != expected_secret:
        raise HTTPException(status_code=403, detail="Invalid Telegram webhook secret")

    update = await request.json()
    ok, message = reply_chat_id(update)
    return {"ok": ok, "message": message}


@router.get("/config", response_model=TelegramConfigResponse)
def get_config(
    db: Session = Depends(get_db),
    _: Principal = Depends(require_super_admin),
):
    cfg = _get_or_create(db)
    return TelegramConfigResponse(
        id=cfg.id,
        bot_token=cfg.bot_token,
        chat_id=cfg.chat_id,
        is_active=bool(cfg.is_active),
        push_interval_minutes=cfg.push_interval_minutes or 60,
        created_at=cfg.created_at,
    )


@router.put("/config", response_model=TelegramConfigResponse)
def update_config(
    data: TelegramConfigUpdate,
    db: Session = Depends(get_db),
    _: Principal = Depends(require_super_admin),
):
    cfg = _get_or_create(db)
    if data.bot_token is not None:
        cfg.bot_token = data.bot_token
    if data.chat_id is not None:
        cfg.chat_id = data.chat_id
    if data.is_active is not None:
        cfg.is_active = 1 if data.is_active else 0
    if data.push_interval_minutes is not None:
        cfg.push_interval_minutes = data.push_interval_minutes
    db.commit()
    db.refresh(cfg)
    return TelegramConfigResponse(
        id=cfg.id,
        bot_token=cfg.bot_token,
        chat_id=cfg.chat_id,
        is_active=bool(cfg.is_active),
        push_interval_minutes=cfg.push_interval_minutes or 60,
        created_at=cfg.created_at,
    )


@router.post("/test")
def send_test(_: Principal = Depends(require_super_admin)):
    return {"success": True, "message": "Telegram 系統設定 API 已保留給管理端使用"}
