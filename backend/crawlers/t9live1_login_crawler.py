import requests
import json
import base64
from datetime import datetime, timedelta
from Crypto.Cipher import AES


class T9live1Crawler:
    """
    T9 代理商管理系統爬蟲
    網址: https://i.t9live1.vip
    """

    def __init__(self):
        self.session = requests.Session()
        self.base_url = "https://i.t9live1.vip"
        self.api_url = f"{self.base_url}/api"
        self.token = None
        self.user_info = None
        self.agent_id = None

        # 設定 headers 模擬瀏覽器
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-TW,zh;q=0.9',
            'Content-Type': 'application/json',
            'Origin': self.base_url,
            'Referer': f'{self.base_url}/',
        })

    def _decrypt_data(self, encrypted_b64: str) -> dict:
        """
        解密 T9 系統的加密資料

        加密格式:
        1. 整體是 Base64 編碼
        2. 解碼後前 16 bytes 為 IV
        3. 剩餘部分是另一個 Base64 字串
        4. 再次解碼得到實際密文
        5. Key = IV + 16 個 0x00 (共 32 bytes)
        6. 使用 AES-256-CBC + PKCS7 解密
        """
        # 第一次 Base64 解碼
        decoded = base64.b64decode(encrypted_b64)

        # 前 16 bytes 為 IV
        iv = decoded[:16]

        # 剩餘部分是 Base64 編碼的密文
        remaining = decoded[16:]
        ciphertext = base64.b64decode(remaining.decode('latin-1'))

        # Key = IV + 16 個零字節
        key = iv + bytes(16)

        # AES CBC 解密
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted = cipher.decrypt(ciphertext)

        # PKCS7 去除填充
        pad_len = decrypted[-1]
        if 1 <= pad_len <= 16:
            decrypted = decrypted[:-pad_len]

        return json.loads(decrypted.decode('utf-8'))

    def _process_response(self, result: dict) -> dict:
        """處理 API 回應，自動解密加密資料"""
        if result.get('cifrado') and result.get('data'):
            return self._decrypt_data(result['data'])
        return result.get('data', {})

    def login(self, account: str, password: str) -> bool:
        """
        登入系統

        Args:
            account: 帳號
            password: 密碼

        Returns:
            bool: 登入是否成功
        """
        # 訪問首頁取得 cookies
        self.session.get(self.base_url)

        # 登入資料
        login_data = {
            'account': account,
            'password': password,
            'Merchant': '_T9',
        }

        try:
            response = self.session.post(
                f"{self.api_url}/user/login",
                json=login_data
            )
            result = response.json()

            if result.get('code') == 200:
                self.token = result.get('access_token')

                # 更新 headers 加入 token
                self.session.headers.update({
                    'Authorization': f'Bearer {self.token}'
                })

                # 解密用戶資料
                if result.get('cifrado') and result.get('data'):
                    self.user_info = self._decrypt_data(result['data'])
                    user = self.user_info.get('user', {})
                    self.agent_id = user.get('agent_id')

                    print(f"[成功] 登入成功")
                    print(f"  帳號: {user.get('account', 'N/A')}")
                    print(f"  暱稱: {user.get('nickname', 'N/A')}")
                    print(f"  代理商: {user.get('agentName', 'N/A')}")
                    print(f"  AgentID: {self.agent_id}")
                else:
                    print("[成功] 登入成功 (無加密資料)")

                return True
            else:
                print(f"[失敗] 登入失敗: {result.get('message', '未知錯誤')}")
                return False

        except requests.RequestException as e:
            print(f"[錯誤] 請求錯誤: {e}")
            return False

    def get_win_loss_report(self, start_date: str = None, end_date: str = None) -> dict:
        """
        取得輸贏報表

        Args:
            start_date: 開始日期 (yyyy-mm-dd)，預設為本週一
            end_date: 結束日期 (yyyy-mm-dd)，預設為本週日

        Returns:
            dict: 報表資料
        """
        if not self.token:
            print("[錯誤] 尚未登入")
            return {}

        # 預設時間範圍：本週
        if start_date is None or end_date is None:
            today = datetime.now()
            monday = today - timedelta(days=today.weekday())
            sunday = monday + timedelta(days=6)
            start_date = monday.strftime('%Y-%m-%d')
            end_date = sunday.strftime('%Y-%m-%d')

        report_data = {
            'betTime': [start_date, end_date],
            'page': 1,
            'rowsCount': 100,
        }

        try:
            response = self.session.post(
                f"{self.api_url}/agent/winLoss",
                json=report_data
            )
            result = response.json()

            if result.get('code') == 200:
                return self._process_response(result)
            else:
                print(f"[錯誤] 取得報表失敗: {result.get('message', '未知錯誤')}")
                return {}

        except requests.RequestException as e:
            print(f"[錯誤] 請求錯誤: {e}")
            return {}

    def get_week_report(self) -> dict:
        """
        取得本週輸贏報表

        Returns:
            dict: 本週報表資料
        """
        today = datetime.now()
        monday = today - timedelta(days=today.weekday())
        sunday = monday + timedelta(days=6)

        return self.get_win_loss_report(
            monday.strftime('%Y-%m-%d'),
            sunday.strftime('%Y-%m-%d')
        )

    def logout(self):
        """登出系統"""
        if self.token:
            try:
                self.session.post(f"{self.api_url}/user/logout")
            except:
                pass
            self.token = None
            self.user_info = None
            print("[成功] 已登出")


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')

    # 設定帳號密碼
    USERNAME = "goodday"
    PASSWORD = "TI9VXP&iab"

    crawler = T9live1Crawler()

    if crawler.login(USERNAME, PASSWORD):
        print("\n" + "=" * 50)
        print("本週輸贏報表:")
        print("=" * 50)

        report = crawler.get_week_report()

        if report:
            agent_info = report.get('agentInfo', {})
            title = agent_info.get('title', 'N/A')

            # 顯示代理總計
            agent_data = agent_info.get('agent', {})
            total = agent_data.get('total', {})

            print(f"\n代理商: {title}")
            print(f"  投注金額: {float(total.get('betAmount', 0)):,.2f}")
            print(f"  有效投注: {float(total.get('validBetAmount', 0)):,.2f}")
            print(f"  輸贏: {float(total.get('winLoss', 0)):,.2f}")
            print(f"  退水: {float(total.get('rollingCommission', 0)):,.2f}")
            print(f"  淨盈虧: {float(total.get('netPL', 0)):,.2f}")

            # 顯示會員明細
            member = agent_info.get('member', {})
            rows = member.get('rows', {})

            if rows:
                print(f"\n{'-' * 40}")
                print("遊戲類別明細:")
                for game_id, data in rows.items():
                    game_type = data.get('gameType', game_id)
                    print(f"\n  [{game_type}]")
                    print(f"    投注人數: {data.get('betMemberCount', 0)}")
                    print(f"    投注金額: {float(data.get('betAmount', 0)):,.2f}")
                    print(f"    有效投注: {float(data.get('validBetAmount', 0)):,.2f}")
                    print(f"    輸贏: {float(data.get('winLoss', 0)):,.2f}")
                    print(f"    輸贏率: {data.get('winLossRate', '0')}%")
        else:
            print("無法取得報表")

        # 登出
        crawler.logout()
    else:
        print("\n登入失敗，請檢查帳號密碼")
