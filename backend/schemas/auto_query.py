from typing import Any, Optional

from pydantic import BaseModel, Field


ALLOWED_FREQUENCIES = [60, 180, 360, 720, 1440]


class AutoQuerySettingUpdate(BaseModel):
    telegram_enabled: bool = False
    telegram_chat_id: Optional[str] = None
    auto_query_enabled: bool = False
    frequency_minutes: int = Field(default=180)


class AutoQuerySettingResponse(BaseModel):
    id: int
    tenant_id: int
    telegram_enabled: bool
    telegram_chat_id: Optional[str]
    auto_query_enabled: bool
    frequency_minutes: int
    last_run_at: Optional[str]
    next_run_at: Optional[str]
    last_status: Optional[str]
    created_at: Optional[str]
    updated_at: Optional[str]


class TelegramBotInfoResponse(BaseModel):
    configured: bool
    username: Optional[str]
    url: Optional[str]


class AutoQueryLogResponse(BaseModel):
    id: int
    tenant_id: int
    frequency_minutes: int
    started_at: str
    finished_at: Optional[str]
    status: str
    success_count: int
    failed_count: int
    message_text: Optional[str]
    result: Optional[Any]
    error_message: Optional[str]


class AutoQueryRunResponse(BaseModel):
    success: bool
    log: Optional[AutoQueryLogResponse] = None
    error: Optional[str] = None
