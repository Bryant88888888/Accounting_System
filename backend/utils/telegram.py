import os
from typing import Any, Optional

import requests
from dotenv import load_dotenv

load_dotenv()


def get_system_bot_token() -> Optional[str]:
    return os.getenv("TELEGRAM_BOT_TOKEN")


def get_system_bot_username() -> Optional[str]:
    username = os.getenv("TELEGRAM_BOT_USERNAME")
    if username:
        return username.removeprefix("@")
    return None


def bot_deep_link() -> Optional[str]:
    username = get_system_bot_username()
    if not username:
        return None
    return f"https://t.me/{username}"


def send_telegram_message(chat_id: str, text: str, bot_token: Optional[str] = None) -> tuple[bool, str]:
    token = bot_token or get_system_bot_token()
    if not token:
        return False, "系統尚未設定 TELEGRAM_BOT_TOKEN"

    try:
        response = requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": text,
                "disable_web_page_preview": True,
            },
            timeout=20,
        )
        if response.ok:
            return True, "Telegram 推播成功"
        try:
            detail: Any = response.json()
        except Exception:
            detail = response.text
        return False, f"Telegram 推播失敗：{detail}"
    except Exception as exc:
        return False, f"Telegram 推播失敗：{exc}"


def reply_chat_id(update: dict) -> tuple[bool, str]:
    message = update.get("message") or update.get("edited_message") or {}
    text = (message.get("text") or "").strip()
    chat = message.get("chat") or {}
    chat_id = chat.get("id")

    if not chat_id:
        return True, "ignored"

    command = text.split()[0].split("@")[0] if text else ""
    if command not in ("/start", "/id"):
        return True, "ignored"

    chat_type = chat.get("type") or "chat"
    label = "這個群組" if chat_type in ("group", "supergroup") else "你的 Telegram"
    reply = (
        f"{label} Chat ID 是：\n"
        f"{chat_id}\n\n"
        "請回到系統「定時任務」頁，貼到 Telegram Chat ID 欄位後按「測試推播」。"
    )
    return send_telegram_message(str(chat_id), reply)
