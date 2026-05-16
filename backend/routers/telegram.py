from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date
from database import get_db
from models.telegram import TelegramConfig
from schemas.telegram import TelegramConfigUpdate, TelegramConfigResponse

router = APIRouter(prefix="/api/telegram", tags=["telegram"])


def _get_or_create(db: Session) -> TelegramConfig:
    cfg = db.query(TelegramConfig).first()
    if not cfg:
        cfg = TelegramConfig(created_at=str(date.today()))
        db.add(cfg)
        db.commit()
        db.refresh(cfg)
    return cfg


@router.get("/config", response_model=TelegramConfigResponse)
def get_config(db: Session = Depends(get_db)):
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
def update_config(data: TelegramConfigUpdate, db: Session = Depends(get_db)):
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
def send_test(db: Session = Depends(get_db)):
    cfg = _get_or_create(db)
    if not cfg.bot_token or not cfg.chat_id:
        raise HTTPException(status_code=400, detail="請先設定 bot_token 與 chat_id")
    # 實際發送留給後續整合
    return {"success": True, "message": "測試訊息已排程（尚未整合實際發送）"}
