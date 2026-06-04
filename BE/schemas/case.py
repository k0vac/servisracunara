from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, model_validator

from models.enums import CaseEventType, CasePriority


class CaseListItem(BaseModel):
    id: int
    ticket_number: str
    customer_name: str
    customer_phone: str
    device_type: str
    device_brand: str
    device_model: str
    status: str
    priority: str
    assigned_to_username: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class CaseEventPartItem(BaseModel):
    part_name: str
    quantity: int
    unit_price_at_time: Decimal
    line_total: Decimal


class CaseEventLaborItem(BaseModel):
    labor_type_name: str
    hours: Decimal
    rate_at_time: Decimal
    line_total: Decimal


class CaseEventItem(BaseModel):
    id: int
    event_type: str
    description: str
    is_public: bool
    created_by_username: str | None
    created_at: datetime
    parts_used: list[CaseEventPartItem] = []
    labor: list[CaseEventLaborItem] = []


class CaseDetailResponse(BaseModel):
    id: int
    ticket_number: str
    customer_name: str
    customer_phone: str
    device_type: str
    device_brand: str
    device_model: str
    reported_issue: str
    status: str
    priority: str
    assigned_to_username: str | None
    estimated_completion: str | None
    created_at: datetime
    closed_at: datetime | None
    events: list[CaseEventItem]


class CaseListResponse(BaseModel):
    items: list[CaseListItem]
    total: int


class CreateCaseRequest(BaseModel):
    customer_name: str = Field(min_length=1, max_length=128)
    customer_phone: str = Field(min_length=1, max_length=32)
    device_type: str = Field(min_length=1, max_length=64)
    device_brand: str = Field(min_length=1, max_length=64)
    device_model: str = Field(min_length=1, max_length=64)
    reported_issue: str = Field(min_length=1)
    priority: CasePriority = CasePriority.NORMAL


class RepairPartInput(BaseModel):
    part_id: int
    quantity: int = Field(ge=1)


class RepairLaborInput(BaseModel):
    labor_type_id: int
    hours: Decimal = Field(gt=0)


class CreateCaseEventRequest(BaseModel):
    event_type: CaseEventType
    description: str = Field(min_length=1)
    is_public: bool = False
    parts_used: list[RepairPartInput] = Field(default_factory=list)
    labor: list[RepairLaborInput] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_repair_extras(self) -> "CreateCaseEventRequest":
        has_extras = bool(self.parts_used or self.labor)
        if has_extras and self.event_type != CaseEventType.REPAIR:
            raise ValueError("Parts and labor can only be added on repair updates")
        return self
