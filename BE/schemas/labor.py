from decimal import Decimal

from pydantic import BaseModel, Field


class LaborTypeItem(BaseModel):
    id: int
    name: str
    hourly_rate: Decimal
    is_active: bool

    model_config = {"from_attributes": True}
