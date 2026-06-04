from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models import CaseEvent, CaseLabor, LaborType, Part, PartUsage, User


def record_repair_parts(
    db: Session,
    *,
    case_id: int,
    case_event: CaseEvent,
    parts_used: list,
    current_user: User,
) -> None:
    for item in parts_used:
        part = db.get(Part, item.part_id)
        if part is None or not part.is_active:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Part {item.part_id} not found")

        if part.quantity_on_hand < item.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Not enough stock for {part.name}",
            )

        db.add(
            PartUsage(
                case_id=case_id,
                case_event_id=case_event.id,
                part_id=part.id,
                quantity=item.quantity,
                unit_price_at_time=part.unit_price,
                recorded_by=current_user.id,
            )
        )
        part.quantity_on_hand -= item.quantity


def record_repair_labor(
    db: Session,
    *,
    case_id: int,
    case_event: CaseEvent,
    labor_items: list,
    current_user: User,
) -> None:
    for item in labor_items:
        labor_type = db.get(LaborType, item.labor_type_id)
        if labor_type is None or not labor_type.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Labor type {item.labor_type_id} not found",
            )

        db.add(
            CaseLabor(
                case_id=case_id,
                case_event_id=case_event.id,
                labor_type_id=labor_type.id,
                hours=Decimal(item.hours),
                rate_at_time=labor_type.hourly_rate,
                recorded_by=current_user.id,
            )
        )
