import pytest

from models import Case, CaseStatus, Invoice, InvoiceStatus
from services.invoice import case_edit_blocked, invoice_is_active


@pytest.mark.unit
def test_invoice_is_active_for_pending_and_paid_only() -> None:
    assert invoice_is_active(None) is False
    assert invoice_is_active(Invoice(status=InvoiceStatus.PENDING)) is True
    assert invoice_is_active(Invoice(status=InvoiceStatus.PAID)) is True
    assert invoice_is_active(Invoice(status=InvoiceStatus.CANCELLED)) is False


@pytest.mark.unit
def test_case_edit_blocked_when_closed_or_invoiced() -> None:
    closed_case = Case(status=CaseStatus.CLOSED)
    assert case_edit_blocked(closed_case) == "Cannot modify a closed case"

    invoiced_case = Case(
        status=CaseStatus.IN_PROGRESS,
        invoice=Invoice(status=InvoiceStatus.PENDING),
    )
    assert case_edit_blocked(invoiced_case) == "Case is locked while an invoice is pending or paid"

    editable_case = Case(status=CaseStatus.IN_PROGRESS, invoice=None)
    assert case_edit_blocked(editable_case) is None
