import json
from datetime import datetime, timedelta, timezone
from typing import Optional
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session

from models.auto_query import AutoQueryLog, AutoQuerySetting
from models.product import Product
from schemas.auto_query import ALLOWED_FREQUENCIES
from utils.crawler_runner import fetch_player_metrics
from utils.crypto import decrypt_secret
from utils.telegram import send_telegram_message


def utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def to_iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).replace(microsecond=0).isoformat()


def parse_iso(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def calculate_next_run(frequency_minutes: int, from_time: Optional[datetime] = None) -> str:
    base = from_time or utc_now()
    return to_iso(base + timedelta(minutes=frequency_minutes))


def format_display_time(value: str) -> str:
    parsed = parse_iso(value) or utc_now()
    taipei = parsed.astimezone(ZoneInfo("Asia/Taipei"))
    return taipei.strftime("%Y-%m-%d %H:%M:%S")


def format_amount(value: float | int) -> str:
    amount = float(value or 0)
    if amount.is_integer():
        return f"{int(amount):,}"
    return f"{amount:,.2f}".rstrip("0").rstrip(".")


def ensure_setting(db: Session, tenant_id: int) -> AutoQuerySetting:
    setting = db.query(AutoQuerySetting).filter(AutoQuerySetting.tenant_id == tenant_id).first()
    now = to_iso(utc_now())
    if setting:
        return setting
    setting = AutoQuerySetting(
        tenant_id=tenant_id,
        telegram_enabled=0,
        auto_query_enabled=0,
        frequency_minutes=180,
        created_at=now,
        updated_at=now,
    )
    db.add(setting)
    db.commit()
    db.refresh(setting)
    return setting


def update_setting(
    db: Session,
    tenant_id: int,
    telegram_enabled: bool,
    telegram_chat_id: Optional[str],
    auto_query_enabled: bool,
    frequency_minutes: int,
) -> AutoQuerySetting:
    if frequency_minutes not in ALLOWED_FREQUENCIES:
        raise ValueError("不支援的查詢頻率")

    setting = ensure_setting(db, tenant_id)
    setting.telegram_enabled = 1 if telegram_enabled else 0
    setting.telegram_chat_id = telegram_chat_id or None
    setting.auto_query_enabled = 1 if auto_query_enabled else 0
    setting.frequency_minutes = frequency_minutes
    setting.updated_at = to_iso(utc_now())

    if auto_query_enabled:
        setting.next_run_at = calculate_next_run(frequency_minutes)
    if not auto_query_enabled:
        setting.next_run_at = None

    db.commit()
    db.refresh(setting)
    return setting


def get_product_password(product: Product) -> Optional[str]:
    return decrypt_secret(product.encrypted_password) or product.plain_password


def build_message(started_at: str, results: list[dict], success_count: int, failed_count: int) -> str:
    lines = [
        "自動查帳結果",
        f"時間：{format_display_time(started_at)}",
        "範圍：本週",
        "",
    ]
    for item in results:
        lines.append(str(item["name"]))
        if item["status"] == "success":
            lines.append(f"玩家有效投注：{format_amount(item['player_valid_bet'])}")
            lines.append(f"玩家輸贏/未拆帳：{format_amount(item['player_win_loss'])}")
        else:
            lines.append(f"查詢失敗：{item['error']}")
        lines.append("")
    lines.append(f"本次成功：{success_count}")
    lines.append(f"本次失敗：{failed_count}")
    return "\n".join(lines).strip()


def execute_auto_query_for_setting(db: Session, setting: AutoQuerySetting, send_telegram: bool = True) -> AutoQueryLog:
    started = utc_now()
    started_at = to_iso(started)
    log = AutoQueryLog(
        tenant_id=setting.tenant_id,
        frequency_minutes=setting.frequency_minutes,
        started_at=started_at,
        status="running",
        success_count=0,
        failed_count=0,
    )
    db.add(log)
    db.commit()
    db.refresh(log)

    results: list[dict] = []
    success_count = 0
    failed_count = 0
    error_message = None

    try:
        products = db.query(Product).filter(
            Product.tenant_id == setting.tenant_id,
            Product.status == "active",
        ).all()

        for product in products:
            password = get_product_password(product)
            if not product.crawler_type or not product.account or not password:
                failed_count += 1
                results.append({
                    "product_id": product.id,
                    "name": product.name,
                    "status": "failed",
                    "error": "尚未設定查帳平台、帳號或密碼",
                })
                continue

            result = fetch_player_metrics(
                product.crawler_type,
                product.account,
                password,
                product.crawler_agent_id,
            )
            if result.get("success") and result.get("data"):
                data = result["data"]
                success_count += 1
                results.append({
                    "product_id": product.id,
                    "name": product.name,
                    "status": "success",
                    "player_valid_bet": float(data.get("player_valid_bet") or 0),
                    "player_win_loss": float(data.get("player_win_loss") or 0),
                })
            else:
                failed_count += 1
                results.append({
                    "product_id": product.id,
                    "name": product.name,
                    "status": "failed",
                    "error": result.get("error") or "查詢失敗",
                })

        if not results:
            failed_count = 1
            results.append({
                "product_id": None,
                "name": "系統",
                "status": "failed",
                "error": "沒有可查詢的啟用產品",
            })

        message = build_message(started_at, results, success_count, failed_count)
        if send_telegram and setting.telegram_enabled:
            if not setting.telegram_chat_id:
                error_message = "Telegram Chat ID 未設定"
            else:
                ok, telegram_message = send_telegram_message(setting.telegram_chat_id, message)
                if not ok:
                    error_message = telegram_message

        status = "success" if failed_count == 0 and not error_message else "partial_failed" if success_count else "failed"
        finished_at = to_iso(utc_now())
        log.status = status
        log.success_count = success_count
        log.failed_count = failed_count
        log.message_text = message
        log.result_json = json.dumps(results, ensure_ascii=False)
        log.error_message = error_message
        log.finished_at = finished_at

        setting.last_run_at = finished_at
        setting.next_run_at = calculate_next_run(setting.frequency_minutes, utc_now()) if setting.auto_query_enabled else None
        setting.last_status = status
        setting.updated_at = finished_at
        db.commit()
        db.refresh(log)
        return log

    except Exception as exc:
        finished_at = to_iso(utc_now())
        log.status = "failed"
        log.failed_count = failed_count or 1
        log.success_count = success_count
        log.result_json = json.dumps(results, ensure_ascii=False)
        log.error_message = str(exc)
        log.finished_at = finished_at
        setting.last_run_at = finished_at
        setting.next_run_at = calculate_next_run(setting.frequency_minutes, utc_now()) if setting.auto_query_enabled else None
        setting.last_status = "failed"
        setting.updated_at = finished_at
        db.commit()
        db.refresh(log)
        return log


def due_settings(db: Session) -> list[AutoQuerySetting]:
    now = utc_now()
    settings = db.query(AutoQuerySetting).filter(AutoQuerySetting.auto_query_enabled == 1).all()
    return [
        setting for setting in settings
        if parse_iso(setting.next_run_at) is None or parse_iso(setting.next_run_at) <= now
    ]
