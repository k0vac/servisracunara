from datetime import datetime

from pydantic import BaseModel


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


class CaseListResponse(BaseModel):
    items: list[CaseListItem]
    total: int
