from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base


class CaseLabor(Base):
    __tablename__ = "case_labor"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    case_id: Mapped[int] = mapped_column(
        ForeignKey("cases.id", ondelete="CASCADE"),
        nullable=False,
    )
    case_event_id: Mapped[int] = mapped_column(
        ForeignKey("case_events.id", ondelete="CASCADE"),
        nullable=False,
    )
    labor_type_id: Mapped[int] = mapped_column(
        ForeignKey("labor_types.id", ondelete="RESTRICT"),
        nullable=False,
    )
    hours: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    rate_at_time: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    recorded_by: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    case: Mapped["Case"] = relationship(back_populates="labor_entries")
    case_event: Mapped["CaseEvent"] = relationship(back_populates="labor_entries")
    labor_type: Mapped["LaborType"] = relationship(back_populates="labor_entries")
    recorded_by_user: Mapped["User | None"] = relationship(back_populates="labor_entries")
