from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base

# Import all models so Base.metadata sees them
import models  # noqa: F401

from routers import auth, accounts, partners, products, reports, dashboard, risk, telegram, tenant, crawler

# Create all tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="代理分帳系統 API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(accounts.router)
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
    return {"message": "代理分帳系統 API 正常運行", "docs": "/docs"}
