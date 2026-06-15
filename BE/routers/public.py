from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from database import get_db
from models import Case, CaseEvent
from schemas.public import PublicCaseEvent, PublicCaseLookupRequest, PublicCaseResponse
from utils.phone import phones_match

router = APIRouter(prefix="/api/public", tags=["public"])


def _to_public_response(case: Case) -> PublicCaseResponse:
    public_events = [
        PublicCaseEvent(
            event_type=event.event_type.value,
            description=event.description,
            created_at=event.created_at,
        )
        for event in case.events
        if event.is_public
    ]

    return PublicCaseResponse(
        ticket_number=case.ticket_number,
        customer_name=case.customer_name,
        device_type=case.device_type,
        device_brand=case.device_brand,
        device_model=case.device_model,
        status=case.status.value,
        estimated_completion=case.estimated_completion,
        created_at=case.created_at,
        events=public_events,
    )


@router.post("/case-lookup", response_model=PublicCaseResponse)
def lookup_case(
    payload: PublicCaseLookupRequest,
    db: Session = Depends(get_db),
) -> PublicCaseResponse:
    reference_code = payload.reference_code.strip().upper()

    case = db.scalar(
        select(Case)
        .options(joinedload(Case.events))
        .where(Case.ticket_number == reference_code)
    )

    if case is None or not phones_match(case.customer_phone, payload.phone):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No case found matching that phone and reference code.",
        )

    return _to_public_response(case)
