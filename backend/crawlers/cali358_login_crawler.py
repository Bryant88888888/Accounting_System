import requests
import hashlib
import json
import time
from urllib.parse import unquote
from datetime import datetime, timedelta


class Cali358Crawler:
    def __init__(self, agent_id: int = None):
        """
        初始化爬蟲

        Args:
            agent_id: 代理商 ID (可選，登入後會自動嘗試獲取)
        """
        self.session = requests.Session()
        self.base_url = "https://ams.cali358.net"
        self.api_url = f"{self.base_url}/service"
        self.token = None
        self.agent_id = agent_id
        self.user_info = None

        # 設定 headers 模擬瀏覽器
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'zh-TW,zh;q=0.9',
            'Content-Type': 'application/json',
            'Origin': self.base_url,
            'Referer': f'{self.base_url}/',
        })

    def _md5_password(self, password: str, username: str) -> str:
        """
        生成 MD5 加密密碼
        格式: MD5(password + "{" + username.toLowerCase() + "}")
        """
        raw = f"{password}{{{username.lower()}}}"
        return hashlib.md5(raw.encode()).hexdigest()

    def _parse_user_info_from_cookies(self):
        """
        從 cookies 中解析 userInfo
        """
        cookies = self.session.cookies.get_dict()
        if 'userInfo' in cookies:
            try:
                user_info_str = unquote(cookies['userInfo'])
                self.user_info = json.loads(user_info_str)
                return True
            except json.JSONDecodeError:
                pass
        return False

    def _get_timestamp(self) -> str:
        """
        生成時間戳參數 (防快取)
        """
        return str(int(time.time() * 1000)) + str(int(time.time() * 10000) % 10000)

    def login(self, username: str, password: str) -> bool:
        """
        登入系統

        Args:
            username: 帳號
            password: 密碼

        Returns:
            bool: 登入是否成功
        """
        # 訪問首頁取得 cookies
        self.session.get(self.base_url)

        # 取得 auth preset
        preset_response = self.session.get(f"{self.api_url}/auth/preset")
        preset = preset_response.json()

        if preset.get('resultCode') != 0:
            print(f"[錯誤] 無法取得 auth preset: {preset.get('messages')}")
            return False

        # 檢查是否需要驗證碼
        if preset.get('data', {}).get('captchaOn'):
            print("[錯誤] 需要驗證碼，無法自動登入")
            return False

        # 加密密碼
        encrypted_password = self._md5_password(password, username)

        # 發送登入請求
        login_data = {
            'username': username,
            'password': encrypted_password,
            'refer': f'{self.base_url}/',
        }

        try:
            response = self.session.post(
                f"{self.api_url}/auth",
                json=login_data
            )
            result = response.json()

            if result.get('resultCode') == 0:
                data = result.get('data', {})
                self.token = data.get('token')

                # 檢查是否需要雙重驗證
                if data.get('tfaRequired'):
                    print("[警告] 需要雙重驗證 (TFA)")
                    return False

                # 更新 headers 加入 token
                self.session.headers.update({
                    'x-token': self.token
                })

                # 取得選單
                self.session.get(f"{self.api_url}/menu")

                # 從 cookies 解析 userInfo
                if self._parse_user_info_from_cookies():
                    if not self.agent_id:
                        self.agent_id = self.user_info.get('agentId')
                    print(f"[成功] 登入成功 - 代理商: {self.user_info.get('agentUserName')}, AgentID: {self.agent_id}")
                elif self.agent_id:
                    print(f"[成功] 登入成功 - AgentID: {self.agent_id}")
                else:
                    print("[成功] 登入成功 (請手動提供 agentId)")

                return True
            else:
                print(f"[失敗] 登入失敗: {result.get('messages')}")
                return False

        except requests.RequestException as e:
            print(f"[錯誤] 請求錯誤: {e}")
            return False

    def get_profit_summary(self, start_time: int = None, end_time: int = None) -> dict:
        """
        取得輸贏報表摘要

        Args:
            start_time: 開始時間 (毫秒時間戳，預設為今天 00:00)
            end_time: 結束時間 (毫秒時間戳，預設為明天 00:00)

        Returns:
            dict: 報表資料
        """
        if not self.token:
            print("[錯誤] 尚未登入")
            return {}

        if not self.agent_id:
            print("[錯誤] 無法取得 agentId，請在初始化時提供")
            return {}

        # 預設時間範圍：今天
        if start_time is None:
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            start_time = int(today.timestamp() * 1000)

        if end_time is None:
            tomorrow = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
            end_time = int(tomorrow.timestamp() * 1000)

        params = {
            't': self._get_timestamp(),
            'agentId': self.agent_id,
            'startTime': start_time,
            'endTime': end_time,
            'page.numPerPage': 100,
            'page.pageNum': 1,
        }

        try:
            response = self.session.get(
                f"{self.api_url}/reports/profit/{self.agent_id}/summary",
                params=params
            )
            return response.json()
        except requests.RequestException as e:
            print(f"[錯誤] 請求錯誤: {e}")
            return {}

    def get_subagents_report(self, start_time: int = None, end_time: int = None) -> dict:
        """
        取得子代理報表

        Args:
            start_time: 開始時間 (毫秒時間戳)
            end_time: 結束時間 (毫秒時間戳)

        Returns:
            dict: 報表資料
        """
        if not self.token:
            print("[錯誤] 尚未登入")
            return {}

        if not self.agent_id:
            print("[錯誤] 無法取得 agentId，請在初始化時提供")
            return {}

        # 預設時間範圍：今天
        if start_time is None:
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            start_time = int(today.timestamp() * 1000)

        if end_time is None:
            end_time = int(time.time() * 1000)  # 當前時間

        params = {
            't': self._get_timestamp(),
            'agentId': self.agent_id,
            'startTime': start_time,
            'endTime': end_time,
            'page.numPerPage': 100,
            'page.pageNum': 1,
        }

        try:
            response = self.session.get(
                f"{self.api_url}/v2/reports/profit/{self.agent_id}/subagents",
                params=params
            )
            return response.json()
        except requests.RequestException as e:
            print(f"[錯誤] 請求錯誤: {e}")
            return {}

    def get_week_report(self) -> dict:
        """
        取得本週輸贏報表

        Returns:
            dict: 本週報表資料
        """
        # 計算本週一 00:00
        today = datetime.now()
        monday = today - timedelta(days=today.weekday())
        monday = monday.replace(hour=0, minute=0, second=0, microsecond=0)

        # 計算下週一 00:00
        next_monday = monday + timedelta(days=7)

        start_time = int(monday.timestamp() * 1000)
        end_time = int(next_monday.timestamp() * 1000)

        return self.get_profit_summary(start_time, end_time)

    def logout(self):
        """
        登出系統
        """
        if self.token:
            try:
                self.session.delete(f"{self.api_url}/auth")
            except:
                pass
            self.token = None
            self.user_info = None
            print("[成功] 已登出")


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')

    # 設定帳號密碼和 agentId
    USERNAME = "baba129"
    PASSWORD = "Baba129@@"
    AGENT_ID = 626066  # 從瀏覽器抓取的 agentId

    crawler = Cali358Crawler(agent_id=AGENT_ID)

    if crawler.login(USERNAME, PASSWORD):
        print("\n" + "=" * 50)
        print("用戶資訊:")
        print("=" * 50)
        if crawler.user_info:
            print(f"  帳號: {crawler.user_info.get('userName')}")
            print(f"  代理商: {crawler.user_info.get('agentUserName')}")
            print(f"  AgentID: {crawler.user_info.get('agentId')}")
            print(f"  角色: {crawler.user_info.get('role')}")
            print(f"  貨幣: {crawler.user_info.get('currencyUnit')}")

        print("\n" + "=" * 50)
        print("本週輸贏報表:")
        print("=" * 50)
        report = crawler.get_week_report()
        if report.get('resultCode') == 0:
            data = report.get('data', {})
            print(f"  結果: {json.dumps(data, ensure_ascii=False, indent=2)}")
        else:
            print(f"  錯誤: {report.get('messages')}")

        print("\n" + "=" * 50)
        print("子代理報表:")
        print("=" * 50)
        subagents = crawler.get_subagents_report()
        if subagents.get('resultCode') == 0:
            data = subagents.get('data', {})
            print(f"  結果: {json.dumps(data, ensure_ascii=False, indent=2)}")
        else:
            print(f"  錯誤: {subagents.get('messages')}")

        # 登出
        crawler.logout()
    else:
        print("\n登入失敗")
