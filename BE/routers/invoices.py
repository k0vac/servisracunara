from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from database import get_db
from deps import get_current_user
from models import Invoice, InvoiceStatus, User
from schemas.invoice import (
    InvoiceListItem,
    InvoiceListResponse,
    InvoiceResponse,
    RetractInvoiceRequest,
)
from services.invoice import (
    generate_case_invoice,
    mark_case_invoice_paid,
    retract_case_invoice,
)

router = APIRouter(prefix="/api", tags=["invoices"])


def _to_line_items(invoice: Invoice) -> list:
    from schemas.invoice import InvoiceLineItemResponse

    return [
        InvoiceLineItemResponse(
            id=item.id,
            description=item.description,
            quantity=item.quantity,
            unit_price=item.unit_price,
            line_total=item.line_total,
            source=item.source.value,
        )
        for item in invoice.line_items
    ]


def _to_invoice_response(invoice: Invoice) -> InvoiceResponse:
    return InvoiceResponse(
        id=invoice.id,
        invoice_number=invoice.invoice_number,
        case_id=invoice.case_id,
        ticket_number=invoice.case.ticket_number,
        customer_name=invoice.customer_name,
        status=invoice.status.value,
        subtotal=invoice.subtotal,
        tax_rate=invoice.tax_rate,
        tax_amount=invoice.tax_amount,
        total=invoice.total,
        issued_at=invoice.issued_at,
        paid_at=invoice.paid_at,
        retraction_reason=invoice.retraction_reason,
        retracted_at=invoice.retracted_at,
        created_by_username=invoice.created_by_user.username
        if invoice.created_by_user
        else None,
        created_at=invoice.created_at,
        line_items=_to_line_items(invoice),
    )


def _to_list_item(invoice: Invoice) -> InvoiceListItem:
    return InvoiceListItem(
        id=invoice.id,
        invoice_number=invoice.invoice_number,
        case_id=invoice.case_id,
        ticket_number=invoice.case.ticket_number,
        customer_name=invoice.customer_name,
        status=invoice.status.value,
        total=invoice.total,
        issued_at=invoice.issued_at,
        paid_at=invoice.paid_at,
        created_at=invoice.created_at,
    )


def _load_invoice(db: Session, invoice_id: int) -> Invoice | None:
    return db.scalar(
        select(Invoice)
        .options(
            joinedload(Invoice.case),
            joinedload(Invoice.created_by_user),
            joinedload(Invoice.line_items),
        )
        .where(Invoice.id == invoice_id)
    )


@router.get("/invoices", response_model=InvoiceListResponse)
def list_invoices(
    status: InvoiceStatus | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> InvoiceListResponse:
    query = (
        select(Invoice)
        .options(joinedload(Invoice.case))
        .order_by(Invoice.created_at.desc())
    )

    if status is not None:
        query = query.where(Invoice.status == status)

    invoices = db.scalars(query).unique().all()
    items = [_to_list_item(invoice) for invoice in invoices]
    return InvoiceListResponse(items=items, total=len(items))


@router.get("/invoices/{invoice_id}", response_model=InvoiceResponse)
def get_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> InvoiceResponse:
    invoice = _load_invoice(db, invoice_id)
    if invoice is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found")

    return _to_invoice_response(invoice)


@router.post(
    "/cases/{case_id}/invoice/generate",
    response_model=InvoiceResponse,
    status_code=status.HTTP_201_CREATED,
)
def generate_payment(
    case_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> InvoiceResponse:
    invoice = generate_case_invoice(db, case_id, current_user)
    invoice = _load_invoice(db, invoice.id)
    assert invoice is not None
    return _to_invoice_response(invoice)


@router.post("/cases/{case_id}/invoice/mark-paid", response_model=InvoiceResponse)
def mark_paid(
    case_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> InvoiceResponse:
    invoice = mark_case_invoice_paid(db, case_id, current_user)
    invoice = _load_invoice(db, invoice.id)
    assert invoice is not None
    return _to_invoice_response(invoice)


@router.post("/cases/{case_id}/invoice/retract", response_model=InvoiceResponse)
def retract_invoice(
    case_id: int,
    payload: RetractInvoiceRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> InvoiceResponse:
    invoice = retract_case_invoice(db, case_id, payload.reason, current_user)
    invoice = _load_invoice(db, invoice.id)
    assert invoice is not None
    return _to_invoice_response(invoice)
