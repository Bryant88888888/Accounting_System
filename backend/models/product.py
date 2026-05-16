from sqlalchemy import Column, Integer, Text, Float, ForeignKey
from database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text, nullable=False)
    series = Column(Text, nullable=False)
    code = Column(Text)
    description = Column(Text)
    platform_type = Column(Text)
    platform_url = Column(Text)
    account = Column(Text)
    hashed_password = Column(Text)
    plain_password = Column(Text, nullable=True)   # 明文，供爬蟲傳送至外部平台
    crawler_type = Column(Text, nullable=True)      # ag_dg18|cali358|kim_tae_ji_888|t9live1|tz98
    status = Column(Text, default="active")
    upstream_partner_id = Column(Integer, ForeignKey("partners.id"), nullable=True)
    upstream_percentage = Column(Float)
    my_percentage = Column(Float)
    rebate_rate = Column(Float)
    discount_rate = Column(Float)
    created_at = Column(Text)


class ProductDownstream(Base):
    __tablename__ = "product_downstreams"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    partner_id = Column(Integer, ForeignKey("partners.id"), nullable=True)
    name = Column(Text)          # 下手名稱快照（partner 可能被刪）
    percentage = Column(Float)
