from pydantic import BaseModel
from typing import Optional


class TelegramConfigUpdate(BaseModel):
    bot_token: Optional[str] = None
    chat_id: Optional[str] = None
    is_active: Optional[bool] = None
    push_interval_minutes: Optional[int] = None


class TelegramConfigResponse(BaseModel):
    id: int
    bot_token: Optional[str]
    chat_id: Optional[str]
    is_active: bool
    push_interval_minutes: int
    created_at: Optional[str]

    class Config:
        from_attributes = True
