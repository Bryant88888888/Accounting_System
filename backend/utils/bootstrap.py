import os
from datetime import datetime

from sqlalchemy.orm import Session

from models.account import Account
from utils.password import hash_password


def ensure_initial_super_admin(db: Session) -> None:
    if db.query(Account).filter(Account.role == "super_admin").first():
        return

    account = os.getenv("INITIAL_ADMIN_ACCOUNT")
    password = os.getenv("INITIAL_ADMIN_PASSWORD")
    nickname = os.getenv("INITIAL_ADMIN_NICKNAME", "超級管理員")

    if not account or not password:
        return

    db.add(Account(
        account=account,
        nickname=nickname,
        hashed_password=hash_password(password),
        role="super_admin",
        status="active",
        created_at=datetime.now().strftime("%Y-%m-%d"),
    ))
    db.commit()
