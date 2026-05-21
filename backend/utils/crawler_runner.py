"""
統一爬蟲執行介面
封裝 5 個平台爬蟲的差異，提供 test_connection / fetch_report 兩個公開函式
"""

import sys
import os
import re

# 確保 crawlers/ 目錄在 import 路徑內
_BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)

CRAWLER_TYPES = ["ag_dg18", "cali358", "kim_tae_ji_888", "t9live1", "tz98"]


def _get_crawler(crawler_type: str, agent_id: int | None = None):
    """動態載入對應爬蟲類別"""
    if crawler_type == "ag_dg18":
        from crawlers.ag_dg18_login_crawler import AGCrawler
        return AGCrawler()
    elif crawler_type == "cali358":
        from crawlers.cali358_login_crawler import Cali358Crawler
        return Cali358Crawler(agent_id=agent_id)
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


def test_connection(
    crawler_type: str,
    account: str,
    password: str,
    agent_id: int | None = None,
) -> dict:
    """
    測試平台連線（僅登入，不抓資料）

    Returns:
        {"success": bool, "message": str}
    """
    try:
        crawler = _get_crawler(crawler_type, agent_id)
        success, message = _login(crawler, crawler_type, account, password)
        return {"success": success, "message": message}
    except Exception as e:
        return {"success": False, "message": f"連線錯誤：{str(e)}"}


def _extract_cali_player_metrics(simple_profit: dict) -> dict:
    """
    Extract the two Cali report fields that match the simple profit page.
    """
    total = (simple_profit.get("data") or {}).get("total") or {}
    summary = total.get("summary") or {}
    inferior = summary.get("INFERIOR") or {}
    date_info = (simple_profit.get("data") or {}).get("date") or {}

    return {
        "player_valid_bet": total.get("totalValidBetAmount", 0),
        "player_win_loss": inferior.get("winLose", 0),
        "source": {
            "api": "/service/reports/profit/simple/{agent_id}",
            "player_valid_bet": "data.total.totalValidBetAmount",
            "player_win_loss": "data.total.summary.INFERIOR.winLose",
        },
        "date": date_info,
    }


def _extract_dg_player_metrics(statistics: dict) -> dict:
    """
    Extract the two DG report fields needed by the settlement report.
    """
    member = statistics.get("Member") or {}
    return {
        "player_valid_bet": member.get("availableBet", 0),
        "player_win_loss": member.get("winOrLoss", 0),
        "source": {
            "api": "/tscms/rpc-api/unlimited/countAgent/statistics",
            "player_valid_bet": "body.Member.availableBet",
            "player_win_loss": "body.Member.winOrLoss",
        },
    }


def _extract_tz98_player_metrics(bill_all: dict) -> dict:
    """
    Extract player metrics from TZ98 weekly all-game report.
    Use Ball=ALL to avoid double-counting category rows.

    The TZ98 page flow is:
    1. Check 代理
    2. Click 上級返水
    3. Read 未拆帳

    In BillDG.js, that displayed cell is:
    data-v=3 / w3 / w3s1 -> row.l5hyqt
    """
    rows = []
    for group in bill_all.get("Data") or []:
        if group.get("Ball") == "ALL":
            rows = group.get("Data") or []
            break

    player_valid_bet = sum(float(row.get("EffectiveSum") or 0) for row in rows)
    player_win_loss = sum(float(row.get("l5hyqt") or 0) for row in rows)

    return {
        "player_valid_bet": player_valid_bet,
        "player_win_loss": player_win_loss,
        "source": {
            "api": "/Bill/billAllQ",
            "player_valid_bet": "Data[Ball=ALL].Data[].EffectiveSum",
            "player_win_loss": "Data[Ball=ALL].Data[].l5hyqt",
            "ui_path": "代理 -> 上級返水 -> 未拆帳",
        },
        "date": bill_all.get("_date_range"),
    }


def _extract_t9_player_metrics(report: dict) -> dict:
    """
    Extract player metrics from T9 weekly win/loss report.
    """
    total = (((report.get("agentInfo") or {}).get("member") or {}).get("total") or {})
    return {
        "player_valid_bet": float(total.get("validBetAmount") or 0),
        "player_win_loss": float(total.get("winLoss") or 0),
        "source": {
            "api": "/api/agent/winLoss",
            "player_valid_bet": "agentInfo.member.total.validBetAmount",
            "player_win_loss": "agentInfo.member.total.winLoss",
        },
    }


def _parse_amount(value: str) -> float:
    cleaned = re.sub(r"[^\d\-.]", "", value or "")
    if cleaned in ("", "-", ".", "-."):
        return 0
    return float(cleaned)


def _extract_kim_player_metrics(html: str) -> dict:
    """
    Extract player metrics from Kim/Tae8 weekly history report.
    """
    from bs4 import BeautifulSoup

    source = {
        "api": "/app/report/report_agent_smarty.php",
        "player_valid_bet": "total row td[2] 金額",
        "player_win_loss": "total row td[7] 未拆帳",
    }
    soup = BeautifulSoup(html or "", "html.parser")
    total_row = soup.find("tr", class_="m_rig_to")
    if not total_row:
        return {"player_valid_bet": 0, "player_win_loss": 0, "source": source}

    cells = [cell.get_text(" ", strip=True) for cell in total_row.find_all("td")]
    return {
        "player_valid_bet": _parse_amount(cells[2] if len(cells) > 2 else ""),
        "player_win_loss": _parse_amount(cells[7] if len(cells) > 7 else ""),
        "source": source,
    }


def fetch_report(
    crawler_type: str,
    account: str,
    password: str,
    agent_id: int | None = None,
) -> dict:
    """
    登入後抓取輸贏報表（不儲存 DB）

    Returns:
        {"success": bool, "data": dict|None, "error": str|None}
    """
    try:
        crawler = _get_crawler(crawler_type, agent_id)
        success, message = _login(crawler, crawler_type, account, password)

        if not success:
            return {"success": False, "data": None, "error": message}

        data = {}

        if crawler_type == "ag_dg18":
            ok1, stat = crawler.get_week_statistics()
            ok2, stat_list = crawler.get_week_statistics_list()
            if ok1:
                data["player_metrics"] = _extract_dg_player_metrics(stat)
                data["statistics"] = stat
            if ok2:
                data["statistics_list"] = stat_list

        elif crawler_type == "cali358":
            if not getattr(crawler, "agent_id", None):
                return {
                    "success": False,
                    "data": None,
                    "error": "cali358 查報表需要設定 agent_id",
                }
            simple_profit = crawler.get_week_simple_profit_report()
            profit = crawler.get_week_report()
            subagents = crawler.get_week_subagents_report()
            for name, result in (
                ("simple_profit", simple_profit),
                ("profit_summary", profit),
                ("subagents_report", subagents),
            ):
                if isinstance(result, dict) and result.get("resultCode") not in (None, 0):
                    return {
                        "success": False,
                        "data": None,
                        "error": f"cali358 {name} 查詢失敗：{result.get('messages')}",
                    }
            if not simple_profit and not profit and not subagents:
                return {
                    "success": False,
                    "data": None,
                    "error": "cali358 查詢成功但報表為空，請確認 agent_id 或查詢權限",
                }
            data["player_metrics"] = _extract_cali_player_metrics(simple_profit)
            data["simple_profit"] = simple_profit
            data["profit_summary"] = profit
            data["subagents_report"] = subagents

        elif crawler_type == "kim_tae_ji_888":
            # 先進入歷史總帳頁面（設定 uid），再查詢本週資料
            crawler.get_history_report()
            html = crawler.query_week_history()
            data["player_metrics"] = _extract_kim_player_metrics(html)
            data["history_report_html"] = html

        elif crawler_type == "t9live1":
            report = crawler.get_week_report()
            data["player_metrics"] = _extract_t9_player_metrics(report)
            data["win_loss_report"] = report

        elif crawler_type == "tz98":
            summary = crawler.get_bill_summary()
            data["bill_summary"] = summary
            # "N" = 今日
            bill_all = crawler.query_week_bill_all()
            if bill_all:
                data["player_metrics"] = _extract_tz98_player_metrics(bill_all)
                data["bill_all"] = bill_all

        return {"success": True, "data": data, "error": None}

    except Exception as e:
        return {"success": False, "data": None, "error": str(e)}


def fetch_player_metrics(
    crawler_type: str,
    account: str,
    password: str,
    agent_id: int | None = None,
) -> dict:
    """
    Login and fetch only the two report fields needed by the settlement report:
    player_valid_bet and player_win_loss.
    """
    result = fetch_report(crawler_type, account, password, agent_id)
    if not result.get("success"):
        return {
            "success": False,
            "data": None,
            "error": result.get("error"),
        }

    metrics = (result.get("data") or {}).get("player_metrics")
    if not metrics:
        return {
            "success": False,
            "data": None,
            "error": f"{crawler_type} 尚未整理玩家有效投注與玩家輸贏欄位",
        }

    return {
        "success": True,
        "data": {
            "player_valid_bet": metrics.get("player_valid_bet", 0),
            "player_win_loss": metrics.get("player_win_loss", 0),
            "source": metrics.get("source"),
        },
        "error": None,
    }
