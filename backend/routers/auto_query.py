import json
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models.auto_query import AutoQueryLog
from models.tenant import Tenant
from schemas.auto_query import (
    ALLOWED_FREQUENCIES,
    AutoQueryLogResponse,
    AutoQueryRunResponse,
    AutoQuerySettingResponse,
    AutoQuerySettingUpdate,
    TelegramBotInfoResponse,
)
from utils.auto_query import ensure_setting, execute_auto_query_for_setting, update_setting
from utils.security import Principal, get_current_principal
from utils.telegram import bot_deep_link, get_system_bot_token, get_system_bot_username, send_telegram_message

router = APIRouter(prefix="/api/auto-query", tags=["auto-query"])


def tenant_id_for_principal(principal: Principal) -> int:
    if principal.is_tenant:
        return principal.id
    raise HTTPException(status_code=403, detail="此功能目前僅提供租戶使用")


def setting_response(setting) -> AutoQuerySettingResponse:
    return AutoQuerySettingResponse(
        id=setting.id,
        tenant_id=setting.tenant_id,
        telegram_enabled=bool(setting.telegram_enabled),
        telegram_chat_id=setting.telegram_chat_id,
        auto_query_enabled=bool(setting.auto_query_enabled),
        frequency_minutes=setting.frequency_minutes,
        last_run_at=setting.last_run_at,
        next_run_at=setting.next_run_at,
        last_status=setting.last_status,
        created_at=setting.created_at,
        updated_at=setting.updated_at,
    )


def log_response(log: AutoQueryLog) -> AutoQueryLogResponse:
    result = None
    if log.result_json:
        try:
            result = json.loads(log.result_json)
        except json.JSONDecodeError:
            result = None
    return AutoQueryLogResponse(
        id=log.id,
        tenant_id=log.tenant_id,
        frequency_minutes=log.frequency_minutes,
        started_at=log.started_at,
        finished_at=log.finished_at,
        status=log.status,
        success_count=log.success_count or 0,
        failed_count=log.failed_count or 0,
        message_text=log.message_text,
        result=result,
        error_message=log.error_message,
    )


@router.get("/frequencies")
def frequencies():
    return [
        {"value": 60, "label": "每 1 小時"},
        {"value": 180, "label": "每 3 小時"},
        {"value": 360, "label": "每 6 小時"},
        {"value": 720, "label": "每 12 小時"},
        {"value": 1440, "label": "每日一次"},
    ]


@router.get("/bot-info", response_model=TelegramBotInfoResponse)
def bot_info(_: Principal = Depends(get_current_principal)):
    username = get_system_bot_username()
    return TelegramBotInfoResponse(
        configured=bool(get_system_bot_token()),
        username=f"@{username}" if username else None,
        url=bot_deep_link(),
    )


@router.get("/setting", response_model=AutoQuerySettingResponse)
def get_setting(
    db: Session = Depends(get_db),
    principal: Principal = Depends(get_current_principal),
):
    tenant_id = tenant_id_for_principal(principal)
    if not db.query(Tenant).filter(Tenant.id == tenant_id).first():
        raise HTTPException(status_code=404, detail="租戶不存在")
    return setting_response(ensure_setting(db, tenant_id))


@router.put("/setting", response_model=AutoQuerySettingResponse)
def save_setting(
    data: AutoQuerySettingUpdate,
    db: Session = Depends(get_db),
    principal: Principal = Depends(get_current_principal),
):
    tenant_id = tenant_id_for_principal(principal)
    if data.frequency_minutes not in ALLOWED_FREQUENCIES:
        raise HTTPException(status_code=400, detail="不支援的查詢頻率")
    try:
        setting = update_setting(
            db=db,
            tenant_id=tenant_id,
            telegram_enabled=data.telegram_enabled,
            telegram_chat_id=data.telegram_chat_id,
            auto_query_enabled=data.auto_query_enabled,
            frequency_minutes=data.frequency_minutes,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return setting_response(setting)


@router.post("/test-telegram")
def test_telegram(
    db: Session = Depends(get_db),
    principal: Principal = Depends(get_current_principal),
):
    tenant_id = tenant_id_for_principal(principal)
    setting = ensure_setting(db, tenant_id)
    if not setting.telegram_chat_id:
        raise HTTPException(status_code=400, detail="請先設定 Telegram Chat ID")
    ok, message = send_telegram_message(setting.telegram_chat_id, "Telegram 推播測試成功")
    return {"success": ok, "message": message}


@router.post("/run-now", response_model=AutoQueryRunResponse)
def run_now(
    db: Session = Depends(get_db),
    principal: Principal = Depends(get_current_principal),
):
    tenant_id = tenant_id_for_principal(principal)
    setting = ensure_setting(db, tenant_id)
    log = execute_auto_query_for_setting(db, setting, send_telegram=bool(setting.telegram_enabled))
    return AutoQueryRunResponse(success=log.status in ("success", "partial_failed"), log=log_response(log))


@router.get("/logs", response_model=List[AutoQueryLogResponse])
def list_logs(
    db: Session = Depends(get_db),
    principal: Principal = Depends(get_current_principal),
):
    tenant_id = tenant_id_for_principal(principal)
    logs = db.query(AutoQueryLog).filter(
        AutoQueryLog.tenant_id == tenant_id,
    ).order_by(AutoQueryLog.id.desc()).limit(20).all()
    return [log_response(log) for log in logs]
