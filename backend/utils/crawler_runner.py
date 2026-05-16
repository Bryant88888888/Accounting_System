"""
統一爬蟲執行介面
封裝 5 個平台爬蟲的差異，提供 test_connection / fetch_report 兩個公開函式
"""

import sys
import os

# 確保 crawlers/ 目錄在 import 路徑內
_BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)

CRAWLER_TYPES = ["ag_dg18", "cali358", "kim_tae_ji_888", "t9live1", "tz98"]


def _get_crawler(crawler_type: str):
    """動態載入對應爬蟲類別"""
    if crawler_type == "ag_dg18":
        from crawlers.ag_dg18_login_crawler import AGCrawler
        return AGCrawler()
    elif crawler_type == "cali358":
        from crawlers.cali358_login_crawler import Cali358Crawler
        return Cali358Crawler()
    elif crawler_type == "kim_tae_ji_888":
        from crawlers.Kim_Tae_ji_888_login_crawler import Crawler
        return Crawler()
    elif crawler_type == "t9live1":
        from crawlers.t9live1_login_crawler import T9live1Crawler
        return T9live1Crawler()
    elif crawler_type == "tz98":
        from crawlers.tz98_login_crawler import Tz98Crawler
        return Tz98Crawler()
    else:
        raise ValueError(f"不支援的 crawler_type: {crawler_type}")


def _login(crawler, crawler_type: str, account: str, password: str) -> tuple[bool, str]:
    """
    執行登入，回傳 (success: bool, message: str)
    """
    if crawler_type == "ag_dg18":
        success, result = crawler.auto_login(account, password, max_retries=3)
        if success:
            return True, "登入成功"
        return False, str(result)

    elif crawler_type in ("cali358", "kim_tae_ji_888", "tz98"):
        ok = crawler.login(account, password)
        if ok:
            return True, "登入成功"
        return False, "登入失敗（帳號或密碼錯誤）"

    elif crawler_type == "t9live1":
        ok = crawler.login(account, password)
        if ok:
            return True, "登入成功"
        return False, "登入失敗（帳號或密碼錯誤）"

    return False, "未知的 crawler_type"


def test_connection(crawler_type: str, account: str, password: str) -> dict:
    """
    測試平台連線（僅登入，不抓資料）

    Returns:
        {"success": bool, "message": str}
    """
    try:
        crawler = _get_crawler(crawler_type)
        success, message = _login(crawler, crawler_type, account, password)
        return {"success": success, "message": message}
    except Exception as e:
        return {"success": False, "message": f"連線錯誤：{str(e)}"}


def fetch_report(crawler_type: str, account: str, password: str) -> dict:
    """
    登入後抓取輸贏報表（不儲存 DB）

    Returns:
        {"success": bool, "data": dict|None, "error": str|None}
    """
    try:
        crawler = _get_crawler(crawler_type)
        success, message = _login(crawler, crawler_type, account, password)

        if not success:
            return {"success": False, "data": None, "error": message}

        data = {}

        if crawler_type == "ag_dg18":
            ok1, stat = crawler.get_statistics(date_unit="Today")
            ok2, stat_list = crawler.get_statistics_list(date_unit="Today")
            if ok1:
                data["statistics"] = stat
            if ok2:
                data["statistics_list"] = stat_list

        elif crawler_type == "cali358":
            profit = crawler.get_profit_summary()
            subagents = crawler.get_subagents_report()
            data["profit_summary"] = profit
            data["subagents_report"] = subagents

        elif crawler_type == "kim_tae_ji_888":
            from datetime import date
            today = str(date.today())
            # 先進入歷史總帳頁面（設定 uid），再查詢本週資料
            crawler.get_history_report()
            html = crawler.query_history(today, today)
            data["history_report_html"] = html

        elif crawler_type == "t9live1":
            report = crawler.get_win_loss_report()
            data["win_loss_report"] = report

        elif crawler_type == "tz98":
            summary = crawler.get_bill_summary()
            data["bill_summary"] = summary
            # "N" = 今日
            date_range = crawler.get_date_range("N")
            if date_range and date_range.get("s") and date_range.get("e"):
                bill_all = crawler.query_bill_all(
                    date_range["s"],
                    date_range["e"],
                )
                data["bill_all"] = bill_all

        return {"success": True, "data": data, "error": None}

    except Exception as e:
        return {"success": False, "data": None, "error": str(e)}
