from pydantic import BaseModel
from typing import List, Optional


class MemberInput(BaseModel):
    name: str
    bet_count: int = 0
    bet_amount: float = 0
    valid_bet: float = 0
    raw_win_loss: float = 0
    rebate_rate: float = 0
    rebate_amount: float = 0
    discount_rate: float = 0
    discount_amount: float = 0
    share_rate: float = 0
    settlement: float = 0


class ProductInput(BaseModel):
    product_id: Optional[int] = None
    product_name: str
    product_code: Optional[str] = None
    member_count: int = 0
    bet_count: int = 0
    bet_amount: float = 0
    valid_bet: float = 0
    raw_win_loss: float = 0
    rebate_rate: float = 0
    rebate_amount: float = 0
    discount_rate: float = 0
    discount_amount: float = 0
    share_rate: float = 0
    settlement: float = 0
    members: List[MemberInput] = []


class ReportCreate(BaseModel):
    start_date: str
    end_date: str
    products: List[ProductInput]


class MemberResponse(BaseModel):
    id: int
    name: str
    bet_count: int
    bet_amount: float
    valid_bet: float
    raw_win_loss: float
    rebate_rate: float
    rebate_amount: float
    discount_rate: float
    discount_amount: float
    share_rate: float
    settlement: float

    class Config:
        from_attributes = True


class ProductResponse(BaseModel):
    id: int
    product_name: str
    product_code: Optional[str]
    member_count: int
    bet_count: int
    bet_amount: float
    valid_bet: float
    raw_win_loss: float
    rebate_rate: float
    rebate_amount: float
    discount_rate: float
    discount_amount: float
    share_rate: float
    settlement: float
    members: List[MemberResponse]

    class Config:
        from_attributes = True


class ReportTotals(BaseModel):
    bet_count: int
    bet_amount: float
    valid_bet: float
    raw_win_loss: float
    rebate_amount: float
    discount_amount: float
    settlement: float


class ReportResponse(BaseModel):
    id: int
    start_date: str
    end_date: str
    products: List[ProductResponse]
    totals: ReportTotals
