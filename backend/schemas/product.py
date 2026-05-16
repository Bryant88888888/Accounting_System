from pydantic import BaseModel
from typing import Optional, List


class DownstreamItem(BaseModel):
    id: Optional[str] = None
    name: str
    percentage: float


class PartnerRef(BaseModel):
    id: str
    name: str
    percentage: float


class ProductCreate(BaseModel):
    name: str
    series: str
    code: Optional[str] = None
    description: Optional[str] = None
    platform_type: Optional[str] = None
    platform_url: Optional[str] = None
    account: Optional[str] = None
    password: Optional[str] = None
    crawler_type: Optional[str] = None
    upstream_partner_id: Optional[int] = None
    upstream_percentage: Optional[float] = None
    my_percentage: Optional[float] = None
    rebate_rate: Optional[float] = None
    discount_rate: Optional[float] = None
    downstreams: Optional[List[DownstreamItem]] = []


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    series: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None
    platform_type: Optional[str] = None
    platform_url: Optional[str] = None
    account: Optional[str] = None
    password: Optional[str] = None
    crawler_type: Optional[str] = None
    upstream_partner_id: Optional[int] = None
    upstream_percentage: Optional[float] = None
    my_percentage: Optional[float] = None
    rebate_rate: Optional[float] = None
    discount_rate: Optional[float] = None
    downstreams: Optional[List[DownstreamItem]] = None


class DownstreamResponse(BaseModel):
    id: str
    name: str
    percentage: float


class ProductResponse(BaseModel):
    id: int
    name: str
    series: str
    code: Optional[str]
    description: Optional[str]
    platform_type: Optional[str]
    platform_url: Optional[str]
    account: Optional[str]
    crawler_type: Optional[str]
    status: str
    upstream: Optional[PartnerRef]
    my_percentage: Optional[float]
    downstreams: List[DownstreamResponse]
    rebate_rate: Optional[float]
    discount_rate: Optional[float]
    created_at: Optional[str]

    class Config:
        from_attributes = True
