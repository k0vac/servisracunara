from datetime import datetime

from pydantic import BaseModel, Field


class PublicCaseLookupRequest(BaseModel):
    phone: str = Field(min_length=1, max_length=32)
    reference_code: str = Field(min_length=1, max_length=32)


class PublicCaseEvent(BaseModel):
    event_type: str
    description: str
    created_at: datetime


class PublicCaseResponse(BaseModel):
    ticket_number: str
    customer_name: str
    device_type: str
    device_brand: str
    device_model: str
    status: str
    estimated_completion: str | None
    created_at: datetime
    events: list[PublicCaseEvent]
