import argparse
import os
import sys

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

import models  # noqa: E402,F401
from database import Base, SessionLocal, engine  # noqa: E402
from models.auto_query import AutoQuerySetting  # noqa: E402
from utils.auto_query import due_settings, execute_auto_query_for_setting  # noqa: E402


def main() -> int:
    Base.metadata.create_all(bind=engine)
    parser = argparse.ArgumentParser(description="Run due auto query jobs.")
    parser.add_argument(
        "--frequency",
        type=int,
        default=None,
        help="Optional frequency filter in minutes. Render hourly cron can omit this.",
    )
    parser.add_argument(
        "--tenant-id",
        type=int,
        default=None,
        help="Optional tenant id filter for debugging.",
    )
    args = parser.parse_args()

    db = SessionLocal()
    try:
        settings = due_settings(db)
        if args.frequency is not None:
            settings = [s for s in settings if s.frequency_minutes == args.frequency]
        if args.tenant_id is not None:
            settings = [s for s in settings if s.tenant_id == args.tenant_id]

        print(f"Found {len(settings)} due auto-query setting(s).")
        for setting in settings:
            setting = db.query(AutoQuerySetting).filter(AutoQuerySetting.id == setting.id).first()
            if not setting:
                continue
            log = execute_auto_query_for_setting(db, setting, send_telegram=True)
            print(
                f"tenant={log.tenant_id} log={log.id} status={log.status} "
                f"success={log.success_count} failed={log.failed_count}"
            )
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
