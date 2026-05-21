# 代理分帳系統

Next.js 前端搭配 FastAPI 後端，用來管理租戶產品帳密、查詢平台帳務、設定 Telegram 推播與定時查帳。

## 本地啟動

前端：

```bash
npm install
npm run dev
```

後端：

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

前端預設網址為 `http://127.0.0.1:3000`，後端預設網址為 `http://127.0.0.1:8000`。

## Render 手動部署

本專案不使用 Render Blueprint。請在 Render 後台手動建立三個服務：PostgreSQL、FastAPI Web Service、Next.js Web Service，定時查帳再另外建立 Cron Job。

### 1. PostgreSQL

建立一個 Render PostgreSQL 資料庫，完成後複製 Internal Database URL，填到後端與 Cron Job 的 `DATABASE_URL`。

### 2. 後端 Web Service

設定：

```text
Root Directory: backend
Build Command: pip install -r requirements.txt
Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
```

環境變數：

```text
DATABASE_URL=<Render PostgreSQL Internal Database URL>
SECRET_KEY=<自訂長隨機字串>
PRODUCT_PASSWORD_SECRET=<自訂 Fernet key，API 與 Cron Job 必須相同>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
TELEGRAM_BOT_TOKEN=<Telegram bot token>
TELEGRAM_BOT_USERNAME=pal_crawler_bot
TELEGRAM_WEBHOOK_SECRET=<自訂長隨機字串>
CORS_ORIGINS=<前端 Render 網址，例如 https://xxx.onrender.com>
```

`PRODUCT_PASSWORD_SECRET` 必須固定保存；如果換掉，既有產品密碼會無法解密。

### 3. 前端 Web Service

設定：

```text
Root Directory: .
Build Command: npm ci && npm run build
Start Command: npm run start -- -p $PORT
```

環境變數：

```text
NEXT_PUBLIC_API_URL=<後端 Render 網址，例如 https://xxx.onrender.com>
```

### 4. 定時查帳 Cron Job

設定：

```text
Root Directory: backend
Build Command: pip install -r requirements.txt
Start Command: python -m jobs.run_auto_queries
Schedule: 0 * * * *
```

環境變數請放：

```text
DATABASE_URL=<同後端>
SECRET_KEY=<同後端>
PRODUCT_PASSWORD_SECRET=<同後端>
TELEGRAM_BOT_TOKEN=<同後端>
TELEGRAM_BOT_USERNAME=pal_crawler_bot
```

Cron Job 每小時執行一次，實際是否推播會依每個租戶在「定時任務」頁面設定的頻率與啟用狀態判斷。

### 5. Telegram Webhook

後端部署完成後，可設定 Telegram webhook，讓使用者傳 `/start` 或 `/id` 時取得自己的 Chat ID。

```bash
curl "https://api.telegram.org/bot<TELEGRAM_BOT_TOKEN>/setWebhook" \
  -d "url=<後端 Render 網址>/api/telegram/webhook" \
  -d "secret_token=<TELEGRAM_WEBHOOK_SECRET>"
```

不要把 `.env`、bot token、資料庫密碼或任何正式密鑰提交到 GitHub。
