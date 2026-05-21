import requests
import re
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

class Crawler:
    def __init__(self):
        self.session = requests.Session()
        self.base_url = "https://xg.tg8888.in/app"
        self.uid = None  # 登入後的 uid
        self.alvl = "ag"  # 帳號等級

        # 設定 headers 模擬瀏覽器
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'Referer': f'{self.base_url}/',
        })

    def _get_login_params(self) -> dict:
        """
        從登入頁面取得動態參數 (uid, encode_num)
        """
        response = self.session.get(f"{self.base_url}/")
        html = response.text

        # 解析隱藏欄位
        uid_match = re.search(r'name="uid"\s+value="([^"]+)"', html)
        encode_match = re.search(r'name="encode_num"\s+value="([^"]+)"', html)

        uid = uid_match.group(1) if uid_match else ''
        encode_num = encode_match.group(1) if encode_match else ''

        return {'uid': uid, 'encode_num': encode_num}

    def login(self, username: str, password: str) -> bool:
        """
        登入系統

        Args:
            username: 管理帳號
            password: 管理密碼

        Returns:
            bool: 登入是否成功
        """
        # 先取得動態參數
        params = self._get_login_params()

        login_url = f"{self.base_url}/login.php"

        # 表單資料（包含動態隱藏欄位）
        login_data = {
            'username': username,
            'passwd': password,
            'active': '1',
            'uid': params['uid'],
            'langx': 'zh-tw',
            'encode_num': params['encode_num'],
            'l_type': 'ag',
        }

        try:
            response = self.session.post(login_url, data=login_data)
            response.raise_for_status()

            # 檢查是否登入成功
            if 'frameset' in response.text.lower() or 'members' in response.text:
                # 解析登入後的 uid
                uid_match = re.search(r'uid=([a-f0-9]+)', response.text)
                if uid_match:
                    self.uid = uid_match.group(1)
                return True

            if '錯誤' in response.text or '失敗' in response.text or 'LoginForm' in response.text:
                print("[失敗] 登入失敗")
                return False

            return True

        except requests.RequestException as e:
            print(f"請求錯誤: {e}")
            return False

    def get_page(self, path: str) -> str:
        """
        取得登入後的頁面內容

        Args:
            path: 相對路徑，例如 'dashboard.php'

        Returns:
            str: 頁面 HTML 內容
        """
        url = f"{self.base_url}/{path}"
        response = self.session.get(url)
        return response.text

    def get_report_page(self) -> str:
        """
        取得查詢報表頁面

        Returns:
            str: 查詢報表頁面 HTML 內容
        """
        if not self.uid:
            print("錯誤: 尚未登入或無法取得 uid")
            return ""

        url = f"{self.base_url}/report/rpt_group.php?uid={self.uid}&alvl={self.alvl}"
        print(f"請求查詢報表: {url}")
        response = self.session.get(url)
        return response.text

    def get_history_report(self) -> str:
        """
        取得歷史總帳頁面

        Returns:
            str: 歷史總帳頁面 HTML 內容
        """
        if not self.uid:
            print("錯誤: 尚未登入或無法取得 uid")
            return ""

        url = f"{self.base_url}/report/report_history_smarty.php?uid={self.uid}&alvl={self.alvl}"
        response = self.session.get(url)
        return response.text

    def query_history(self, date_start: str, date_end: str) -> str:
        """
        查詢歷史總帳資料 (點擊查找)

        Args:
            date_start: 開始日期 (yyyy-mm-dd)
            date_end: 結束日期 (yyyy-mm-dd)

        Returns:
            str: 查詢結果 HTML 內容
        """
        if not self.uid:
            print("錯誤: 尚未登入或無法取得 uid")
            return ""

        url = f"{self.base_url}/report/report_agent_smarty.php"

        form_data = {
            'uid': self.uid,
            'alvl': self.alvl,
            'img': 'himg',
            'gtype': '',       # 全部
            'ms': '',          # 賽程時段全部
            'date_start': date_start,
            'date_end': date_end,
            'wtype': '',       # 下注方式全部
            'report_kind': 'A',  # 總帳
            'result_type': '0',  # 全部
            'SUBMIT': '查找',
        }

        response = self.session.post(url, data=form_data)
        return response.text

    def query_week_history(self) -> str:
        """
        Query this week's history report.
        """
        today = datetime.now()
        monday = today - timedelta(days=today.weekday())
        sunday = monday + timedelta(days=6)
        return self.query_history(
            monday.strftime('%Y-%m-%d'),
            sunday.strftime('%Y-%m-%d'),
        )

    def parse_report(self, html: str, date_start: str, date_end: str):
        """
        解析報表 HTML，提取未拆帳總計

        Args:
            html: 查詢結果 HTML
            date_start: 開始日期
            date_end: 結束日期
        """
        soup = BeautifulSoup(html, 'html.parser')

        # 找到代理商名稱
        agent_text = soup.find('font', string=re.compile(r'^a\d+'))
        agent_name = agent_text.get_text() if agent_text else "未知"

        # 找到總計那一列 (class="m_rig_to")
        total_row = soup.find('tr', class_='m_rig_to')

        if total_row:
            cells = total_row.find_all('td')
            # 未拆帳在第 8 個 td (index 7)
            if len(cells) >= 8:
                unsplit = cells[7].get_text(strip=True)
                # 移除 font 標籤的內容
                unsplit_value = re.sub(r'[^\d\-.]', '', unsplit)

                print("=" * 40)
                print(f"會員名稱: {agent_name}")
                print(f"查詢日期: {date_start} ~ {date_end}")
                print(f"未拆帳金額: {unsplit}")
                print("=" * 40)
            else:
                print("無法解析未拆帳資料")
        else:
            print("查無資料或無法找到總計列")


if __name__ == "__main__":
    crawler = Crawler()

    # 請填入你的帳號密碼
    USERNAME = "mi7"
    PASSWORD = "mi7"

    if crawler.login(USERNAME, PASSWORD):
        # 先進入歷史總帳頁面
        crawler.get_history_report()

        # 點擊「本週」+ 點擊「查找」
        date_start = "2026-01-26"
        date_end = "2026-02-01"
        result_html = crawler.query_history(date_start, date_end)

        # 解析並顯示結果
        crawler.parse_report(result_html, date_start, date_end)
    else:
        print("\n登入失敗，請檢查帳密或回應內容")
