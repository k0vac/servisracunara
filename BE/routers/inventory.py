from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session, joinedload

from database import get_db
from deps import get_current_user
from models import Category, Part, User
from schemas.inventory import (
    AdjustStockRequest,
    CategoryItem,
    CreatePartRequest,
    PartDetailResponse,
    PartListItem,
    PartListResponse,
    UpdatePartRequest,
)

router = APIRouter(prefix="/api/inventory", tags=["inventory"])


def _is_low_stock(part: Part) -> bool:
    if part.low_stock_threshold is None:
        return False
    return part.quantity_on_hand <= part.low_stock_threshold


def _get_or_create_category(db: Session, category_name: str | None) -> Category | None:
    if category_name is None or not category_name.strip():
        return None

    normalized = category_name.strip()
    existing = db.scalar(select(Category).where(Category.name == normalized))
    if existing is not None:
        return existing

    category = Category(name=normalized)
    db.add(category)
    db.flush()
    return category


def _to_list_item(part: Part) -> PartListItem:
    return PartListItem(
        id=part.id,
        name=part.name,
        category_id=part.category_id,
        category_name=part.category.name if part.category else None,
        unit_price=part.unit_price,
        quantity_on_hand=part.quantity_on_hand,
        low_stock_threshold=part.low_stock_threshold,
        is_active=part.is_active,
        is_low_stock=_is_low_stock(part),
        created_at=part.created_at,
    )


def _to_detail(part: Part) -> PartDetailResponse:
    return PartDetailResponse(
        id=part.id,
        name=part.name,
        category_id=part.category_id,
        category_name=part.category.name if part.category else None,
        unit_price=part.unit_price,
        quantity_on_hand=part.quantity_on_hand,
        low_stock_threshold=part.low_stock_threshold,
        notes=part.notes,
        is_active=part.is_active,
        is_low_stock=_is_low_stock(part),
        created_at=part.created_at,
    )


def _load_part(db: Session, part_id: int) -> Part | None:
    return db.scalar(
        select(Part).options(joinedload(Part.category)).where(Part.id == part_id)
    )


@router.get("/categories", response_model=list[CategoryItem])
def list_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[CategoryItem]:
    categories = db.scalars(select(Category).order_by(Category.name)).all()
    return [CategoryItem.model_validate(category) for category in categories]


@router.get("/parts", response_model=PartListResponse)
def list_parts(
    search: str | None = Query(default=None, max_length=128),
    category_id: int | None = None,
    include_inactive: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PartListResponse:
    query = select(Part).options(joinedload(Part.category))

    if not include_inactive:
        query = query.where(Part.is_active.is_(True))

    if category_id is not None:
        query = query.where(Part.category_id == category_id)

    if search:
        term = f"%{search.strip()}%"
        query = query.join(Category, Part.category_id == Category.id, isouter=True).where(
            or_(Part.name.like(term), Category.name.like(term))
        )

    query = query.order_by(Part.name)

    parts = db.scalars(query).unique().all()
    items = [_to_list_item(part) for part in parts]
    return PartListResponse(items=items, total=len(items))


@router.get("/parts/{part_id}", response_model=PartDetailResponse)
def get_part(
    part_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PartDetailResponse:
    part = _load_part(db, part_id)
    if part is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Part not found")

    return _to_detail(part)


@router.post("/parts", response_model=PartDetailResponse, status_code=status.HTTP_201_CREATED)
def create_part(
    payload: CreatePartRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PartDetailResponse:
    category = _get_or_create_category(db, payload.category_name)

    part = Part(
        name=payload.name.strip(),
        category_id=category.id if category else None,
        unit_price=Decimal(payload.unit_price),
        quantity_on_hand=payload.quantity_on_hand,
        low_stock_threshold=payload.low_stock_threshold,
        notes=payload.notes.strip() if payload.notes else None,
        is_active=True,
    )

    db.add(part)
    db.commit()

    part = _load_part(db, part.id)
    assert part is not None

    return _to_detail(part)


@router.patch("/parts/{part_id}", response_model=PartDetailResponse)
def update_part(
    part_id: int,
    payload: UpdatePartRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PartDetailResponse:
    part = _load_part(db, part_id)
    if part is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Part not found")

    if payload.name is not None:
        part.name = payload.name.strip()

    if payload.category_name is not None:
        category = _get_or_create_category(db, payload.category_name)
        part.category_id = category.id if category else None

    if payload.unit_price is not None:
        part.unit_price = Decimal(payload.unit_price)

    if payload.low_stock_threshold is not None:
        part.low_stock_threshold = payload.low_stock_threshold

    if payload.notes is not None:
        part.notes = payload.notes.strip() or None

    if payload.is_active is not None:
        part.is_active = payload.is_active

    db.commit()

    part = _load_part(db, part_id)
    assert part is not None

    return _to_detail(part)


@router.post("/parts/{part_id}/adjust-stock", response_model=PartDetailResponse)
def adjust_stock(
    part_id: int,
    payload: AdjustStockRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PartDetailResponse:
    part = _load_part(db, part_id)
    if part is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Part not found")

    new_quantity = part.quantity_on_hand + payload.delta
    if new_quantity < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Stock cannot go below zero",
        )

    part.quantity_on_hand = new_quantity
    db.commit()

    part = _load_part(db, part_id)
    assert part is not None

    return _to_detail(part)
