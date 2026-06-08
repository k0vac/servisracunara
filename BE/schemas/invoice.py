from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class InvoiceLineItemResponse(BaseModel):
    id: int
    description: str
    quantity: Decimal
    unit_price: Decimal
    line_total: Decimal
    source: str

    model_config = {"from_attributes": True}


class InvoiceResponse(BaseModel):
    id: int
    invoice_number: str
    case_id: int
    ticket_number: str
    customer_name: str
    status: str
    subtotal: Decimal
    tax_rate: Decimal
    tax_amount: Decimal
    total: Decimal
    issued_at: datetime | None
    paid_at: datetime | None
    retraction_reason: str | None
    retracted_at: datetime | None
    created_by_username: str | None
    created_at: datetime
    line_items: list[InvoiceLineItemResponse]


class InvoiceListItem(BaseModel):
    id: int
    invoice_number: str
    case_id: int
    ticket_number: str
    customer_name: str
    status: str
    total: Decimal
    issued_at: datetime | None
    paid_at: datetime | None
    created_at: datetime


class InvoiceListResponse(BaseModel):
    items: list[InvoiceListItem]
    total: int


class CaseInvoiceSummary(BaseModel):
    id: int
    invoice_number: str
    status: str
    subtotal: Decimal
    tax_rate: Decimal
    tax_amount: Decimal
    total: Decimal
    issued_at: datetime | None
    paid_at: datetime | None
    retraction_reason: str | None
    retracted_at: datetime | None
    line_items: list[InvoiceLineItemResponse]


class RetractInvoiceRequest(BaseModel):
    reason: str = Field(min_length=1, max_length=2000)
