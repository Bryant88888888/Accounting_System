from sqlalchemy import Column, Integer, Text
from database import Base


class TelegramConfig(Base):
    __tablename__ = "telegram_configs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    bot_token = Column(Text)
    chat_id = Column(Text)
    is_active = Column(Integer, default=0)     # 0 / 1
    push_interval_minutes = Column(Integer, default=60)
    created_at = Column(Text)
