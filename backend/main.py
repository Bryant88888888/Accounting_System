import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect, text

from database import Base, engine
from utils.crypto import encrypt_secret

# Import all models so Base.metadata sees them
import models  # noqa: F401

from routers import accounts, auth, auto_query, crawler, dashboard, partners, products, reports, risk, telegram, tenant

# Create all tables
Base.metadata.create_all(bind=engine)


def ensure_runtime_columns():
    inspector = inspect(engine)
    product_columns = {col["name"] for col in inspector.get_columns("products")}
    partner_columns = {col["name"] for col in inspector.get_columns("partners")}
    report_columns = {col["name"] for col in inspector.get_columns("settlement_reports")}
    with engine.begin() as conn:
        if "crawler_agent_id" not in product_columns:
            conn.execute(text("ALTER TABLE products ADD COLUMN crawler_agent_id INTEGER"))
        if "encrypted_password" not in product_columns:
            conn.execute(text("ALTER TABLE products ADD COLUMN encrypted_password TEXT"))
        if "tenant_id" not in product_columns:
            conn.execute(text("ALTER TABLE products ADD COLUMN tenant_id INTEGER"))
        if "plain_password" in product_columns:
            rows = conn.execute(text(
                "SELECT id, plain_password FROM products "
                "WHERE plain_password IS NOT NULL AND plain_password != '' "
                "AND (encrypted_password IS NULL OR encrypted_password = '')"
            )).mappings().all()
            for row in rows:
                conn.execute(
                    text("UPDATE products SET encrypted_password = :encrypted, plain_password = NULL WHERE id = :id"),
                    {"encrypted": encrypt_secret(row["plain_password"]), "id": row["id"]},
                )
        if "tenant_id" not in partner_columns:
            conn.execute(text("ALTER TABLE partners ADD COLUMN tenant_id INTEGER"))
        if "tenant_id" not in report_columns:
            conn.execute(text("ALTER TABLE settlement_reports ADD COLUMN tenant_id INTEGER"))


def get_cors_origins():
    origins = ["http://localhost:3000", "http://127.0.0.1:3000"]
    frontend_url = os.getenv("FRONTEND_URL")
    if frontend_url:
        origins.append(frontend_url.rstrip("/"))
    cors_origins = os.getenv("CORS_ORIGINS")
    if cors_origins:
        origins.extend(origin.strip().rstrip("/") for origin in cors_origins.split(",") if origin.strip())
    return list(dict.fromkeys(origins))


ensure_runtime_columns()

app = FastAPI(title="代理分帳系統 API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(accounts.router)
app.include_router(auto_query.router)
app.include_router(partners.router)
app.include_router(products.router)
app.include_router(reports.router)
app.include_router(dashboard.router)
app.include_router(risk.router)
app.include_router(telegram.router)
app.include_router(tenant.router)
app.include_router(crawler.router)


@app.get("/")
def root():
    return {"message": "代理分帳系統 API 正常運作", "docs": "/docs"}
