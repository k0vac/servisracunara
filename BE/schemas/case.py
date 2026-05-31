from datetime import datetime

from pydantic import BaseModel, Field

from models.enums import CasePriority


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


class CaseEventItem(BaseModel):
    id: int
    event_type: str
    description: str
    is_public: bool
    created_by_username: str | None
    created_at: datetime


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
