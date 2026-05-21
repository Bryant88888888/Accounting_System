"""
ag.dg18.vip 靜態爬蟲
使用 requests 進行登入操作
使用 ddddocr 自動識別驗證碼
"""

import requests
import base64
from datetime import datetime, timedelta
import ddddocr


class AGCrawler:
    BASE_URL = "https://ag.dg18.vip"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            "Origin": self.BASE_URL,
            "Referer": f"{self.BASE_URL}/",
            "Sec-Ch-Ua": '"Chromium";v="143", "Google Chrome";v="143"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
        })
        self.token = None
        self.user_info = None
        # 初始化 OCR
        self.ocr = ddddocr.DdddOcr(show_ad=False)

    def get_captcha(self):
        """取得驗證碼圖片和 captchaKey"""
        url = f"{self.BASE_URL}/tscms/rpc-api/unlimited/agent/captcha"

        # 注意：這是 POST 請求，不是 GET
        response = self.session.post(url)
        data = response.json()

        if data.get("code") == 10000:
            captcha_key = data["body"]["captchaKey"]
            base64_img = data["body"]["base64"]
            return captcha_key, base64_img
        else:
            raise Exception(f"取得驗證碼失敗: {data.get('message')}")

    def decode_base64_image(self, base64_img):
        """將 base64 圖片解碼為 bytes"""
        if "," in base64_img:
            base64_img = base64_img.split(",")[1]
        return base64.b64decode(base64_img)

    def save_captcha_image(self, base64_img, filename="captcha.png"):
        """將 base64 圖片儲存為檔案"""
        img_data = self.decode_base64_image(base64_img)
        with open(filename, "wb") as f:
            f.write(img_data)
        return filename

    def recognize_captcha(self, base64_img):
        """使用 ddddocr 識別驗證碼"""
        img_bytes = self.decode_base64_image(base64_img)
        result = self.ocr.classification(img_bytes)
        return result

    def login(self, username, password, code, captcha_key, language="CN"):
        """執行登入"""
        url = f"{self.BASE_URL}/tscms/rpc-api/unlimited/agent/login"

        payload = {
            "username": username,
            "password": password,
            "code": code,
            "captchaKey": captcha_key,
            "language": language
        }

        # 登入需要 Content-Type
        headers = {"Content-Type": "application/json"}
        response = self.session.post(url, json=payload, headers=headers)
        data = response.json()

        if data.get("code") == 10000:
            self.user_info = data["body"]
            self.token = data["body"]["token"]
            # 設定 Authorization header 供後續請求使用
            self.session.headers.update({
                "Authorization": f"Bearer {self.token}"
            })
            return True, data["body"]
        else:
            return False, data.get("message", "登入失敗")

    def auto_login(self, username, password, max_retries=5):
        """自動登入（包含驗證碼識別和重試機制）"""
        for attempt in range(1, max_retries + 1):
            print(f"[嘗試 {attempt}/{max_retries}] 正在取得驗證碼...")

            # 取得驗證碼
            captcha_key, base64_img = self.get_captcha()

            # 識別驗證碼
            code = self.recognize_captcha(base64_img)
            print(f"[嘗試 {attempt}/{max_retries}] 識別結果: {code}")

            # 執行登入
            success, result = self.login(username, password, code, captcha_key)

            if success:
                print(f"[成功] 登入成功!")
                return True, result
            else:
                print(f"[失敗] {result}")
                if attempt < max_retries:
                    print("重新嘗試...")

        return False, "已達最大重試次數"

    def is_logged_in(self):
        """檢查是否已登入"""
        return self.token is not None

    def get_week_range(self):
        """
        Return this week's Monday 00:00:00 to Sunday 23:59:59 for DG reports.
        """
        today = datetime.now()
        monday = today - timedelta(days=today.weekday())
        monday = monday.replace(hour=0, minute=0, second=0, microsecond=0)
        sunday = monday + timedelta(days=6, hours=23, minutes=59, seconds=59)
        return (
            monday.strftime("%Y-%m-%d %H:%M:%S"),
            sunday.strftime("%Y-%m-%d %H:%M:%S"),
        )

    def get_week_statistics(self):
        start_date, end_date = self.get_week_range()
        return self.get_statistics(
            date_unit="Week",
            start_date=start_date,
            end_date=end_date,
        )

    def get_week_statistics_list(self, level_type="Agent", page_no=1, page_size=10):
        start_date, end_date = self.get_week_range()
        return self.get_statistics_list(
            date_unit="Week",
            start_date=start_date,
            end_date=end_date,
            level_type=level_type,
            page_no=page_no,
            page_size=page_size,
        )

    def get_statistics(self, date_unit="Today", start_date=None, end_date=None):
        """
        取得輸贏報表統計總覽

        Args:
            date_unit: 日期單位 ("Today", "Yesterday", "Week", "LastWeek", "Month", "LastMonth")
            start_date: 開始日期 (格式: "2026-01-31 00:00:00")
            end_date: 結束日期 (格式: "2026-01-31 23:59:59")
        """
        if not self.is_logged_in():
            raise Exception("請先登入")

        url = f"{self.BASE_URL}/tscms/rpc-api/unlimited/countAgent/statistics"

        # 如果沒有指定日期，使用今天
        if start_date is None or end_date is None:
            today = datetime.now().strftime("%Y-%m-%d")
            start_date = f"{today} 00:00:00"
            end_date = f"{today} 23:59:59"

        payload = {
            "parentId": self.user_info["parentId"],
            "dateUnit": date_unit,
            "from": start_date,
            "to": end_date
        }

        headers = {"Content-Type": "application/json"}
        response = self.session.post(url, json=payload, headers=headers)
        data = response.json()

        if data.get("code") == 10000:
            return True, data["body"]
        else:
            return False, data.get("message", "取得統計失敗")

    def get_statistics_list(self, date_unit="Today", start_date=None, end_date=None,
                            level_type="Agent", page_no=1, page_size=10):
        """
        取得輸贏報表統計列表

        Args:
            date_unit: 日期單位 ("Today", "Yesterday", "Week", "LastWeek", "Month", "LastMonth")
            start_date: 開始日期 (格式: "2026-01-31 00:00:00")
            end_date: 結束日期 (格式: "2026-01-31 23:59:59")
            level_type: 層級類型 ("Agent", "Member")
            page_no: 頁碼
            page_size: 每頁筆數
        """
        if not self.is_logged_in():
            raise Exception("請先登入")

        url = f"{self.BASE_URL}/tscms/rpc-api/unlimited/countAgent/statisticsList"

        # 如果沒有指定日期，使用今天
        if start_date is None or end_date is None:
            today = datetime.now().strftime("%Y-%m-%d")
            start_date = f"{today} 00:00:00"
            end_date = f"{today} 23:59:59"

        payload = {
            "dateUnit": date_unit,
            "from": start_date,
            "to": end_date,
            "pageParam": {
                "pageNo": page_no,
                "pageSize": page_size
            },
            "parentId": self.user_info["parentId"],
            "levelType": level_type
        }

        headers = {"Content-Type": "application/json"}
        response = self.session.post(url, json=payload, headers=headers)
        data = response.json()

        if data.get("code") == 10000:
            return True, data["body"]
        else:
            return False, data.get("message", "取得統計列表失敗")


def main():
    crawler = AGCrawler()

    # 帳號密碼
    username = "bbaa123"
    password = "bbaa123"

    # 自動登入（含驗證碼識別，最多重試 5 次）
    success, result = crawler.auto_login(username, password, max_retries=5)

    if success:
        print("-" * 50)
        print(f"用戶名: {result['username']}")
        print(f"餘額: {result['balance']}")
        print(f"Token: {result['token'][:50]}...")
        print("-" * 50)

        # 取得輸贏報表統計總覽
        print("\n[輸贏報表 - 統計總覽]")
        stat_success, stat_data = crawler.get_statistics(date_unit="Today")
        if stat_success:
            print(f"  總投注額: {stat_data.get('totalBetAmount', 0)}")
            print(f"  總有效投注: {stat_data.get('totalValidBetAmount', 0)}")
            print(f"  總輸贏: {stat_data.get('totalWinOrLoss', 0)}")
            print(f"  總佣金: {stat_data.get('totalCommission', 0)}")
        else:
            print(f"  取得失敗: {stat_data}")

        # 取得輸贏報表統計列表
        print("\n[輸贏報表 - 統計列表]")
        list_success, list_data = crawler.get_statistics_list(date_unit="Today")
        if list_success:
            records = list_data.get("records", [])
            print(f"  共 {len(records)} 筆記錄")
            for i, record in enumerate(records[:5], 1):  # 只顯示前5筆
                print(f"  {i}. {record.get('username', 'N/A')} - 投注: {record.get('totalBetAmount', 0)}, 輸贏: {record.get('totalWinOrLoss', 0)}")
        else:
            print(f"  取得失敗: {list_data}")

    else:
        print(f"登入失敗: {result}")


if __name__ == "__main__":
    main()
