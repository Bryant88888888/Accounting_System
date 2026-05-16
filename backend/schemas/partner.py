from pydantic import BaseModel
from typing import Optional


class PartnerCreate(BaseModel):
    name: str


class PartnerUpdate(BaseModel):
    name: Optional[str] = None


class PartnerResponse(BaseModel):
    id: int
    name: str
    created_at: Optional[str]

    class Config:
        from_attributes = True
