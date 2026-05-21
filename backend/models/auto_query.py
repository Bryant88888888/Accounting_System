from sqlalchemy import Column, Integer, Text, ForeignKey
from database import Base


class AutoQuerySetting(Base):
    __tablename__ = "auto_query_settings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), unique=True, nullable=False)
    telegram_enabled = Column(Integer, default=0)
    telegram_bot_token_encrypted = Column(Text, nullable=True)
    telegram_chat_id = Column(Text, nullable=True)
    auto_query_enabled = Column(Integer, default=0)
    frequency_minutes = Column(Integer, default=180)
    last_run_at = Column(Text, nullable=True)
    next_run_at = Column(Text, nullable=True)
    last_status = Column(Text, nullable=True)
    created_at = Column(Text)
    updated_at = Column(Text)


class AutoQueryLog(Base):
    __tablename__ = "auto_query_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    frequency_minutes = Column(Integer, nullable=False)
    started_at = Column(Text, nullable=False)
    finished_at = Column(Text, nullable=True)
    status = Column(Text, nullable=False)
    success_count = Column(Integer, default=0)
    failed_count = Column(Integer, default=0)
    message_text = Column(Text, nullable=True)
    result_json = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
