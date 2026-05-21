import requests
import re
from bs4 import BeautifulSoup


class Tz98Crawler:
    def __init__(self):
        self.session = requests.Session()
        self.base_url = "https://ag.tz98.net"

        # 設定 headers 模擬瀏覽器
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        })

    def _get_verification_token(self) -> str:
        """
        從登入頁面取得 __RequestVerificationToken
        """
        response = self.session.get(f"{self.base_url}/")
        soup = BeautifulSoup(response.text, 'html.parser')

        # 找到隱藏的 token 欄位
        token_input = soup.find('input', {'name': '__RequestVerificationToken'})
        if token_input:
            return token_input.get('value', '')
        return ''

    def login(self, username: str, password: str) -> bool:
        """
        登入系統

        Args:
            username: 帳號
            password: 密碼

        Returns:
            bool: 登入是否成功
        """
        # 先取得 CSRF token
        token = self._get_verification_token()
        if not token:
            print("[錯誤] 無法取得 verification token")
            return False

        login_url = f"{self.base_url}/Home/Authenticate"

        login_data = {
            '__RequestVerificationToken': token,
            'txtac': username,
            'txtpd': password,
        }

        try:
            response = self.session.post(login_url, data=login_data, allow_redirects=True)
            response.raise_for_status()

            # 登入後可能會重定向，再取得首頁確認狀態
            home_response = self.session.get(f"{self.base_url}/")

            # 如果還在登入頁面，代表登入失敗
            if 'loginform' in home_response.text.lower() or '請輸入帳號' in home_response.text:
                print("[失敗] 登入失敗，請檢查帳號密碼")
                return False

            # 登入成功會包含登出連結
            if 'logout' in home_response.text.lower() or '登出' in home_response.text:
                print("[成功] 登入成功")
                return True

            # 其他情況
            print("[警告] 無法確認登入狀態")
            return False

        except requests.RequestException as e:
            print(f"[錯誤] 請求錯誤: {e}")
            return False

    def get_page(self, path: str) -> str:
        """
        取得登入後的頁面內容

        Args:
            path: 相對路徑，例如 '/Report/Index'

        Returns:
            str: 頁面 HTML 內容
        """
        url = f"{self.base_url}{path}"
        response = self.session.get(url)
        return response.text

    def get_bill_summary(self) -> list:
        """
        取得查詢報表首頁摘要 (三天的已過帳/未過帳)

        Returns:
            list: 三天的報表資料
        """
        url = f"{self.base_url}/Bill/billQ"
        response = self.session.post(url, data={})
        return response.json()

    def get_date_range(self, date_type: str, ticket_time: str = "acctime") -> dict:
        """
        取得日期範圍 (點擊日期按鈕)

        Args:
            date_type: 日期類型
                - 'DB': 前一日
                - 'N': 今日
                - 'DA': 後一日
                - 'W': 本週
                - 'LW': 上週
                - 'M': 本月
                - 'LM': 上月
            ticket_time: 'acctime' (帳務日期) 或 'bettime' (投注時間)

        Returns:
            dict: {'s': 開始時間, 'e': 結束時間}
        """
        url = f"{self.base_url}/Bill/GetDate"
        response = self.session.post(url, data={
            'DType': date_type,
            'Date': ticket_time
        })
        return response.json()

    def query_bill_all(self, date_start: str, date_end: str, mem_id: str = "-1") -> dict:
        """
        查詢總帳 (點擊「查詢」按鈕)

        Args:
            date_start: 開始日期 (yyyy-mm-dd)
            date_end: 結束日期 (yyyy-mm-dd)
            mem_id: 會員ID (可選，'-1' 表示全部)

        Returns:
            dict: {
                'Data': [...],  # 包含 RetAmt (返水), BetSum (下注), MemResult (結果) 等
                'MemLv': 層級,
                'category': [...]
            }
        """
        url = f"{self.base_url}/Bill/billAllQ"
        response = self.session.post(url, data={
            'ticketTime': 'acctime',    # 帳務日期
            'ballType': -1,             # 球種 (全部)
            'acqType': -1,              # 賽程時段 (全部)
            'dateS': date_start,
            'dateE': date_end,
            'rpt': 'All',               # 報表類型: 總帳
            'wagerType': -1,            # 投注種類 (全部)
            'memAID': mem_id,           # 帳號 (-1=全部)
            'memID': '-1',
            'finished': '-1',
            'ticketid': '',
            'numType': 0,               # 整數格式
            'RowNum': 0,
            'Span': 100,
        })
        return response.json()

    def query_week_bill_all(self, mem_id: str = "-1") -> dict:
        """
        Query this week's all-game bill report.
        """
        date_range = self.get_date_range('W', 'acctime')
        if not date_range or not date_range.get('s') or not date_range.get('e'):
            return {}
        date_start = date_range['s'].split(' ')[0]
        date_end = date_range['e'].split(' ')[0]
        result = self.query_bill_all(date_start, date_end, mem_id)
        result["_date_range"] = date_range
        return result

    def query_bill_type(self, date_start: str, date_end: str, mem_id: str = "-1") -> dict:
        """
        查詢分類帳 (依下注方式分類)

        Args:
            date_start: 開始日期
            date_end: 結束日期
            mem_id: 會員ID (可選，'-1' 表示全部)

        Returns:
            dict: {'Data': [...], 'MemLv': 層級}
        """
        url = f"{self.base_url}/Bill/billTypeQ"
        response = self.session.post(url, data={
            'ticketTime': 'acctime',
            'ballType': -1,
            'acqType': -1,
            'dateS': date_start,
            'dateE': date_end,
            'rpt': 'Type',
            'wagerType': -1,
            'memAID': mem_id,
            'memID': '-1',
            'finished': '-1',
            'ticketid': '',
            'numType': 0,
            'RowNum': 0,
            'Span': 100,
        })
        return response.json()

    def query_bill_ticket(self, date_start: str, date_end: str, mem_id: str = "-1",
                          row_num: int = 0, span: int = 100) -> dict:
        """
        查詢注單明細

        Args:
            date_start: 開始日期
            date_end: 結束日期
            mem_id: 會員ID (可選，'-1' 表示全部)
            row_num: 起始行號 (分頁用)
            span: 每頁筆數

        Returns:
            dict: {'Data': [...], 'MemLv': 層級, 'totalRows': 總筆數}
        """
        url = f"{self.base_url}/Bill/billTicketQ"
        response = self.session.post(url, data={
            'ticketTime': 'acctime',
            'ballType': -1,
            'acqType': -1,
            'dateS': date_start,
            'dateE': date_end,
            'rpt': 'Ticket',
            'wagerType': -1,
            'memAID': mem_id,
            'memID': '-1',
            'finished': '-1',
            'ticketid': '',
            'numType': 0,
            'RowNum': row_num,
            'Span': span,
        })
        return response.json()


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')

    crawler = Tz98Crawler()

    USERNAME = "ddaa129"
    PASSWORD = "ddaa129"

    if crawler.login(USERNAME, PASSWORD):
        # 取得本週日期
        date_range = crawler.get_date_range('W', 'acctime')
        date_start = date_range['s'].split(' ')[0]
        date_end = date_range['e'].split(' ')[0]

        # 查詢總帳
        result = crawler.query_bill_all(date_start, date_end)

        if result.get('Data'):
            for item in result['Data']:
                if item.get('Ball') == 'ALL':
                    data_list = item.get('Data', [])
                    if data_list:
                        d = data_list[0]
                        member_id = d.get('memberID')
                        l5hyqt = d.get('l5hyqt')
                        print(f"帳號: {member_id}")
                        print(f"日期: {date_start} ~ {date_end}")
                        print(f"未拆帳: {l5hyqt:,.2f}")
                    break
        else:
            print("無資料")
    else:
        print("登入失敗")
