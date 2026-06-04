from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import get_db
from deps import get_current_user
from models import LaborType, User
from schemas.labor import LaborTypeItem

router = APIRouter(prefix="/api/labor-types", tags=["labor-types"])


@router.get("", response_model=list[LaborTypeItem])
def list_labor_types(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[LaborTypeItem]:
    labor_types = db.scalars(
        select(LaborType).where(LaborType.is_active.is_(True)).order_by(LaborType.name)
    ).all()
    return [LaborTypeItem.model_validate(item) for item in labor_types]
