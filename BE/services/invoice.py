from datetime import UTC, datetime
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from models import (
    Case,
    CaseEvent,
    CaseEventType,
    CaseLabor,
    CaseStatus,
    Invoice,
    InvoiceLineItem,
    InvoiceLineItemSource,
    InvoiceStatus,
    PartUsage,
    ShopSettings,
    User,
)


def invoice_is_active(invoice: Invoice | None) -> bool:
    return invoice is not None and invoice.status in (
        InvoiceStatus.PENDING,
        InvoiceStatus.PAID,
    )


def case_edit_blocked(case: Case) -> str | None:
    if case.status == CaseStatus.CLOSED:
        return "Cannot modify a closed case"
    if invoice_is_active(case.invoice):
        return "Case is locked while an invoice is pending or paid"
    return None


def _get_shop_settings(db: Session) -> ShopSettings:
    settings = db.scalar(select(ShopSettings).limit(1))
    if settings is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Shop settings are not configured",
        )
    return settings


def _load_case_for_invoice(db: Session, case_id: int) -> Case | None:
    return db.scalar(
        select(Case)
        .options(
            joinedload(Case.invoice).joinedload(Invoice.line_items),
            joinedload(Case.part_usages).joinedload(PartUsage.part),
            joinedload(Case.labor_entries).joinedload(CaseLabor.labor_type),
        )
        .where(Case.id == case_id)
    )


def _remove_cancelled_invoice(db: Session, case: Case) -> None:
    if case.invoice is not None and case.invoice.status == InvoiceStatus.CANCELLED:
        db.delete(case.invoice)
        db.flush()
        case.invoice = None


def _build_line_items(case: Case) -> list[InvoiceLineItem]:
    line_items: list[InvoiceLineItem] = []

    for usage in case.part_usages:
        quantity = Decimal(usage.quantity)
        unit_price = usage.unit_price_at_time
        line_items.append(
            InvoiceLineItem(
                description=usage.part.name,
                quantity=quantity,
                unit_price=unit_price,
                line_total=quantity * unit_price,
                source=InvoiceLineItemSource.MATERIAL,
                part_usage_id=usage.id,
            )
        )

    for entry in case.labor_entries:
        line_items.append(
            InvoiceLineItem(
                description=f"Labor: {entry.labor_type.name}",
                quantity=entry.hours,
                unit_price=entry.rate_at_time,
                line_total=entry.hours * entry.rate_at_time,
                source=InvoiceLineItemSource.LABOR,
                case_labor_id=entry.id,
            )
        )

    return line_items


def generate_case_invoice(db: Session, case_id: int, current_user: User) -> Invoice:
    case = _load_case_for_invoice(db, case_id)
    if case is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")

    if case.status == CaseStatus.CLOSED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot generate payment for a closed case",
        )

    if invoice_is_active(case.invoice):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This case already has an active invoice",
        )

    _remove_cancelled_invoice(db, case)

    line_items = _build_line_items(case)
    if not line_items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Add parts or labor on the case before generating payment",
        )

    settings = _get_shop_settings(db)
    subtotal = sum((item.line_total for item in line_items), Decimal("0"))
    tax_rate = settings.default_tax_rate
    tax_amount = (subtotal * tax_rate / Decimal("100")).quantize(Decimal("0.01"))
    total = subtotal + tax_amount
    now = datetime.now(UTC)

    invoice = Invoice(
        invoice_number="TEMP",
        case_id=case.id,
        customer_name=case.customer_name,
        status=InvoiceStatus.PENDING,
        subtotal=subtotal,
        tax_rate=tax_rate,
        tax_amount=tax_amount,
        total=total,
        issued_at=now,
        created_by=current_user.id,
        line_items=line_items,
    )
    db.add(invoice)
    db.flush()
    invoice.invoice_number = f"INV-{invoice.id:04d}"

    case.status = CaseStatus.AWAITING_PAYMENT

    db.add(
        CaseEvent(
            case_id=case.id,
            event_type=CaseEventType.NOTE,
            description=f"Payment invoice {invoice.invoice_number} generated ({total} RSD).",
            is_public=False,
            created_by=current_user.id,
        )
    )

    db.commit()
    db.refresh(invoice)
    return invoice


def mark_case_invoice_paid(db: Session, case_id: int, current_user: User) -> Invoice:
    case = _load_case_for_invoice(db, case_id)
    if case is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")

    invoice = case.invoice
    if invoice is None or invoice.status != InvoiceStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Case has no pending invoice",
        )

    now = datetime.now(UTC)
    invoice.status = InvoiceStatus.PAID
    invoice.paid_at = now
    case.status = CaseStatus.CLOSED
    case.closed_at = now

    db.add(
        CaseEvent(
            case_id=case.id,
            event_type=CaseEventType.NOTE,
            description=f"Invoice {invoice.invoice_number} marked as paid.",
            is_public=False,
            created_by=current_user.id,
        )
    )

    db.commit()
    db.refresh(invoice)
    return invoice


def retract_case_invoice(
    db: Session,
    case_id: int,
    reason: str,
    current_user: User,
) -> Invoice:
    case = _load_case_for_invoice(db, case_id)
    if case is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")

    invoice = case.invoice
    if invoice is None or invoice.status != InvoiceStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only a pending invoice can be retracted",
        )

    now = datetime.now(UTC)
    trimmed_reason = reason.strip()
    invoice.status = InvoiceStatus.CANCELLED
    invoice.retraction_reason = trimmed_reason
    invoice.retracted_at = now

    if case.status == CaseStatus.AWAITING_PAYMENT:
        case.status = CaseStatus.IN_PROGRESS

    db.add(
        CaseEvent(
            case_id=case.id,
            event_type=CaseEventType.NOTE,
            description=(
                f"Invoice {invoice.invoice_number} retracted. Reason: {trimmed_reason}"
            ),
            is_public=False,
            created_by=current_user.id,
        )
    )

    db.commit()
    db.refresh(invoice)
    return invoice
