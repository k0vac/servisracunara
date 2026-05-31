from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session, joinedload

from database import get_db
from deps import get_current_user
from models import Case, CaseEvent, CaseEventType, CaseStatus, User
from schemas.case import (
    CaseDetailResponse,
    CaseEventItem,
    CaseListItem,
    CaseListResponse,
    CreateCaseRequest,
)

router = APIRouter(prefix="/api/cases", tags=["cases"])


def _to_list_item(case: Case) -> CaseListItem:
    return CaseListItem(
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


def _to_detail(case: Case) -> CaseDetailResponse:
    return CaseDetailResponse(
        id=case.id,
        ticket_number=case.ticket_number,
        customer_name=case.customer_name,
        customer_phone=case.customer_phone,
        device_type=case.device_type,
        device_brand=case.device_brand,
        device_model=case.device_model,
        reported_issue=case.reported_issue,
        status=case.status.value,
        priority=case.priority.value,
        assigned_to_username=case.assigned_to_user.username if case.assigned_to_user else None,
        estimated_completion=case.estimated_completion,
        created_at=case.created_at,
        closed_at=case.closed_at,
        events=[
            CaseEventItem(
                id=event.id,
                event_type=event.event_type.value,
                description=event.description,
                is_public=event.is_public,
                created_by_username=event.created_by_user.username if event.created_by_user else None,
                created_at=event.created_at,
            )
            for event in case.events
        ],
    )


def _load_case(db: Session, case_id: int) -> Case | None:
    return db.scalar(
        select(Case)
        .options(
            joinedload(Case.assigned_to_user),
            joinedload(Case.events).joinedload(CaseEvent.created_by_user),
        )
        .where(Case.id == case_id)
    )


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
    items = [_to_list_item(case) for case in cases]

    return CaseListResponse(items=items, total=len(items))


@router.get("/{case_id}", response_model=CaseDetailResponse)
def get_case(
    case_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CaseDetailResponse:
    case = _load_case(db, case_id)
    if case is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")

    return _to_detail(case)


@router.post("", response_model=CaseListItem, status_code=status.HTTP_201_CREATED)
def create_case(
    payload: CreateCaseRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CaseListItem:
    case = Case(
        ticket_number="TEMP",
        customer_name=payload.customer_name.strip(),
        customer_phone=payload.customer_phone.strip(),
        device_type=payload.device_type.strip(),
        device_brand=payload.device_brand.strip(),
        device_model=payload.device_model.strip(),
        reported_issue=payload.reported_issue.strip(),
        status=CaseStatus.OPEN,
        priority=payload.priority,
        assigned_to=current_user.id,
    )

    db.add(case)
    db.flush()
    case.ticket_number = f"REP-{case.id:04d}"

    db.add(
        CaseEvent(
            case_id=case.id,
            event_type=CaseEventType.NOTE,
            description=f"Case opened. Reported issue: {payload.reported_issue.strip()}",
            is_public=False,
            created_by=current_user.id,
        )
    )

    db.commit()

    case = _load_case(db, case.id)
    assert case is not None

    return _to_list_item(case)
