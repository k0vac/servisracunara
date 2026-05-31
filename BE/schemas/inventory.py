from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class CategoryItem(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


class PartListItem(BaseModel):
    id: int
    name: str
    category_id: int | None
    category_name: str | None
    unit_price: Decimal
    quantity_on_hand: int
    low_stock_threshold: int | None
    is_active: bool
    is_low_stock: bool
    created_at: datetime


class PartDetailResponse(BaseModel):
    id: int
    name: str
    category_id: int | None
    category_name: str | None
    unit_price: Decimal
    quantity_on_hand: int
    low_stock_threshold: int | None
    notes: str | None
    is_active: bool
    is_low_stock: bool
    created_at: datetime


class PartListResponse(BaseModel):
    items: list[PartListItem]
    total: int


class CreatePartRequest(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    category_name: str | None = Field(default=None, max_length=64)
    unit_price: Decimal = Field(ge=0)
    quantity_on_hand: int = Field(ge=0, default=0)
    low_stock_threshold: int | None = Field(default=None, ge=0)
    notes: str | None = None


class UpdatePartRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=128)
    category_name: str | None = Field(default=None, max_length=64)
    unit_price: Decimal | None = Field(default=None, ge=0)
    low_stock_threshold: int | None = Field(default=None, ge=0)
    notes: str | None = None
    is_active: bool | None = None


class AdjustStockRequest(BaseModel):
    delta: int
