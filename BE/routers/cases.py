from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload

from database import get_db
from deps import get_current_user
from models import Case, CaseStatus, User
from schemas.case import CaseListItem, CaseListResponse

router = APIRouter(prefix="/api/cases", tags=["cases"])


@router.get("", response_model=CaseListResponse)
def list_cases(
    status: CaseStatus | None = None,
    search: str | None = Query(default=None, max_length=128),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CaseListResponse:
    query = select(Case).options(joinedload(Case.assigned_to_user)).order_by(Case.created_at.desc())

    if status is not None:
        query = query.where(Case.status == status)

    if search:
        term = f"%{search.strip()}%"
        query = query.where(
            or_(
                Case.ticket_number.like(term),
                Case.customer_name.like(term),
                Case.customer_phone.like(term),
                Case.device_brand.like(term),
                Case.device_model.like(term),
            )
        )

    cases = db.scalars(query).unique().all()
    items = [
        CaseListItem(
            id=case.id,
            ticket_number=case.ticket_number,
            customer_name=case.customer_name,
            customer_phone=case.customer_phone,
            device_type=case.device_type,
            device_brand=case.device_brand,
            device_model=case.device_model,
            status=case.status.value,
            priority=case.priority.value,
            assigned_to_username=case.assigned_to_user.username if case.assigned_to_user else None,
            created_at=case.created_at,
        )
        for case in cases
    ]

    return CaseListResponse(items=items, total=len(items))
