"""
初始化資料庫並匯入 mock 資料
執行：python seed.py
"""
from database import engine, SessionLocal, Base
import models  # noqa: F401 — 確保所有 model 被載入
from models.account import Account
from models.partner import Partner
from models.product import Product, ProductDownstream
from models.report import SettlementReport, SettlementProduct, SettlementMember
from utils.password import hash_password

Base.metadata.create_all(bind=engine)

db = SessionLocal()


def seed_accounts():
    if db.query(Account).count() > 0:
        print("accounts 已有資料，跳過")
        return
    accounts = [
        Account(account="admin",  nickname="超級管理員", hashed_password=hash_password("ilovetaiwan"), role="super_admin", status="active", created_at="2026-01-01"),
        Account(account="user01", nickname="張三",       hashed_password=hash_password("user1234"),  role="user",        status="active", created_at="2026-01-15"),
        Account(account="user02", nickname="李四",       hashed_password=hash_password("user5678"),  role="user",        status="active", created_at="2026-02-01"),
    ]
    db.add_all(accounts)
    db.commit()
    print(f"已新增 {len(accounts)} 個帳號")


def seed_partners():
    if db.query(Partner).count() > 0:
        print("partners 已有資料，跳過")
        return
    partners = [
        Partner(name="肖",  created_at="2026-01-01"),
        Partner(name="邓",  created_at="2026-01-01"),
        Partner(name="自營", created_at="2026-01-01"),
    ]
    db.add_all(partners)
    db.commit()
    print(f"已新增 {len(partners)} 個夥伴")


def seed_products():
    if db.query(Product).count() > 0:
        print("products 已有資料，跳過")
        return

    # 取得夥伴 ID
    xiao = db.query(Partner).filter(Partner.name == "肖").first()
    deng = db.query(Partner).filter(Partner.name == "邓").first()
    self_op = db.query(Partner).filter(Partner.name == "自營").first()

    products_data = [
        dict(name="泰8",   series="體育·36588", code="A693023",    platform_type="體育", platform_url="https://36588.com",  account="A693023",    upstream_partner_id=xiao.id,    upstream_percentage=50,  my_percentage=50,  rebate_rate=0.5, discount_rate=0, created_at="2026-01-31", downstreams=[("下手1", 10)]),
        dict(name="贏9",   series="體育·36588", code="mmnn123",    platform_type="體育", platform_url="https://36588.com",  account="mmnn123",    upstream_partner_id=deng.id,    upstream_percentage=60,  my_percentage=40,  rebate_rate=0.5, discount_rate=0, created_at="2026-01-31", downstreams=[("下手1", 5)]),
        dict(name="博金",  series="體育·36588", code="52445RR",    platform_type="體育", platform_url="https://36588.com",  account="52445RR",    upstream_partner_id=xiao.id,    upstream_percentage=20,  my_percentage=80,  rebate_rate=0.5, discount_rate=0, created_at="2026-01-31", downstreams=[("下手1", 10)]),
        dict(name="太子",  series="體育·super", code="deng1111",   platform_type="體育", platform_url="https://super.com",  account="deng1111",   upstream_partner_id=xiao.id,    upstream_percentage=60,  my_percentage=40,  rebate_rate=0.5, discount_rate=0, created_at="2026-01-31", downstreams=[("下手1", 5)]),
        dict(name="泰金999", series="體育·super", code="facebook111", platform_type="體育", platform_url="https://super.com", account="facebook111", upstream_partner_id=xiao.id, upstream_percentage=40, my_percentage=60, rebate_rate=0.5, discount_rate=0, created_at="2026-01-31", downstreams=[("下手1", 10)]),
        dict(name="無雙體育鑫寶系列(無雙/禾康)", series="體育·xinbao", code="App9557", platform_type="體育", platform_url="https://xinbao.com", account="App9557", upstream_partner_id=self_op.id, upstream_percentage=100, my_percentage=100, rebate_rate=0.5, discount_rate=0, created_at="2026-02-01", downstreams=[]),
    ]

    for pd in products_data:
        downstreams = pd.pop("downstreams")
        p = Product(**pd, status="active", hashed_password=None)
        db.add(p)
        db.flush()
        for name, pct in downstreams:
            db.add(ProductDownstream(product_id=p.id, name=name, percentage=pct))

    db.commit()
    print(f"已新增 {len(products_data)} 個產品")


def seed_reports():
    if db.query(SettlementReport).count() > 0:
        print("settlement_reports 已有資料，跳過")
        return

    products = db.query(Product).all()
    prod_map = {p.code: p.id for p in products}

    report = SettlementReport(start_date="2026-01-01", end_date="2026-02-01", created_at="2026-02-01")
    db.add(report)
    db.flush()

    report_products = [
        dict(product_code="A693023",    product_name="泰8",   member_count=1, bet_count=215,  bet_amount=920500.00,  valid_bet=885230.00,  raw_win_loss=-23450.50, rebate_rate=0.5, rebate_amount=4426.15,  discount_rate=0, discount_amount=0, share_rate=50,  settlement=-23450.50,
             members=[dict(name="player001", bet_count=215, bet_amount=920500.00,  valid_bet=885230.00,  raw_win_loss=-23450.50, rebate_rate=0.5, rebate_amount=4426.15,  discount_rate=0, discount_amount=0, share_rate=50,  settlement=-23450.50)]),
        dict(product_code="mmnn123",    product_name="贏9",   member_count=1, bet_count=328,  bet_amount=1450200.00, valid_bet=1392680.00, raw_win_loss=18920.30,  rebate_rate=0.5, rebate_amount=6963.40,  discount_rate=0, discount_amount=0, share_rate=40,  settlement=18920.30,
             members=[dict(name="player002", bet_count=328, bet_amount=1450200.00, valid_bet=1392680.00, raw_win_loss=18920.30,  rebate_rate=0.5, rebate_amount=6963.40,  discount_rate=0, discount_amount=0, share_rate=40,  settlement=18920.30)]),
        dict(product_code="52445RR",    product_name="博金",  member_count=0, bet_count=0,    bet_amount=0,          valid_bet=0,          raw_win_loss=0,         rebate_rate=0.5, rebate_amount=0,        discount_rate=0, discount_amount=0, share_rate=80,  settlement=0, members=[]),
        dict(product_code="deng1111",   product_name="太子",  member_count=3, bet_count=687,  bet_amount=2890107.00, valid_bet=2745824.00, raw_win_loss=-98230.42, rebate_rate=0.5, rebate_amount=13729.12, discount_rate=0, discount_amount=0, share_rate=40,  settlement=-98230.42,
             members=[
                 dict(name="player003", bet_count=245, bet_amount=1050000.00, valid_bet=1008500.00, raw_win_loss=-35200.10, rebate_rate=0.5, rebate_amount=5042.50, discount_rate=0, discount_amount=0, share_rate=40, settlement=-35200.10),
                 dict(name="player004", bet_count=198, bet_amount=890107.00,  valid_bet=845324.00,  raw_win_loss=-41530.32, rebate_rate=0.5, rebate_amount=4226.62, discount_rate=0, discount_amount=0, share_rate=40, settlement=-41530.32),
                 dict(name="player005", bet_count=244, bet_amount=950000.00,  valid_bet=892000.00,  raw_win_loss=-21500.00, rebate_rate=0.5, rebate_amount=4460.00, discount_rate=0, discount_amount=0, share_rate=40, settlement=-21500.00),
             ]),
        dict(product_code="facebook111", product_name="泰金999", member_count=1, bet_count=369, bet_amount=1499600.00, valid_bet=1460000.00, raw_win_loss=-44151.50, rebate_rate=0.5, rebate_amount=7300.00, discount_rate=0, discount_amount=0, share_rate=60, settlement=-44151.50,
             members=[dict(name="player006", bet_count=369, bet_amount=1499600.00, valid_bet=1460000.00, raw_win_loss=-44151.50, rebate_rate=0.5, rebate_amount=7300.00, discount_rate=0, discount_amount=0, share_rate=60, settlement=-44151.50)]),
        dict(product_code="App9557",    product_name="無雙體育鑫寶系列(無雙/禾康)", member_count=0, bet_count=0, bet_amount=0, valid_bet=0, raw_win_loss=0, rebate_rate=0.5, rebate_amount=0, discount_rate=0, discount_amount=0, share_rate=100, settlement=0, members=[]),
    ]

    for rp in report_products:
        members = rp.pop("members")
        sp = SettlementProduct(
            report_id=report.id,
            product_id=prod_map.get(rp["product_code"]),
            **rp,
        )
        db.add(sp)
        db.flush()
        for m in members:
            db.add(SettlementMember(settlement_product_id=sp.id, **m))

    db.commit()
    print(f"已新增 1 份結算報表，含 {len(report_products)} 個產品記錄")


if __name__ == "__main__":
    print("開始初始化資料庫...")
    seed_accounts()
    seed_partners()
    seed_products()
    seed_reports()
    db.close()
    print("資料庫初始化完成！")
