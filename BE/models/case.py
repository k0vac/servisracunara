from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base, TimestampMixin
from models.enums import CaseEventType, CasePriority, CaseStatus


class Case(Base, TimestampMixin):
    __tablename__ = "cases"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ticket_number: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    customer_name: Mapped[str] = mapped_column(String(128), nullable=False)
    customer_phone: Mapped[str] = mapped_column(String(32), nullable=False)
    device_type: Mapped[str] = mapped_column(String(64), nullable=False)
    device_brand: Mapped[str] = mapped_column(String(64), nullable=False)
    device_model: Mapped[str] = mapped_column(String(64), nullable=False)
    reported_issue: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[CaseStatus] = mapped_column(
        Enum(CaseStatus, native_enum=False, length=32),
        nullable=False,
        default=CaseStatus.OPEN,
    )
    priority: Mapped[CasePriority] = mapped_column(
        Enum(CasePriority, native_enum=False, length=16),
        nullable=False,
        default=CasePriority.NORMAL,
    )
    assigned_to: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    estimated_completion: Mapped[str | None] = mapped_column(String(128), nullable=True)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    assigned_to_user: Mapped["User | None"] = relationship(
        back_populates="assigned_cases",
        foreign_keys=[assigned_to],
    )
    events: Mapped[list["CaseEvent"]] = relationship(
        back_populates="case",
        cascade="all, delete-orphan",
        order_by="CaseEvent.created_at",
    )
    part_usages: Mapped[list["PartUsage"]] = relationship(
        back_populates="case",
        cascade="all, delete-orphan",
    )
    labor_entries: Mapped[list["CaseLabor"]] = relationship(
        back_populates="case",
        cascade="all, delete-orphan",
    )
    invoice: Mapped["Invoice | None"] = relationship(
        back_populates="case",
        uselist=False,
        cascade="all, delete-orphan",
    )


class CaseEvent(Base, TimestampMixin):
    __tablename__ = "case_events"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    case_id: Mapped[int] = mapped_column(
        ForeignKey("cases.id", ondelete="CASCADE"),
        nullable=False,
    )
    event_type: Mapped[CaseEventType] = mapped_column(
        Enum(CaseEventType, native_enum=False, length=32),
        nullable=False,
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    is_public: Mapped[bool] = mapped_column(nullable=False, default=False)
    created_by: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    case: Mapped["Case"] = relationship(back_populates="events")
    created_by_user: Mapped["User | None"] = relationship(back_populates="case_events")
    part_usages: Mapped[list["PartUsage"]] = relationship(back_populates="case_event")
    labor_entries: Mapped[list["CaseLabor"]] = relationship(back_populates="case_event")
