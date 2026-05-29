from decimal import Decimal

from sqlalchemy import Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class ShopSettings(Base):
    """Singleton row for shop branding and invoice defaults."""

    __tablename__ = "shop_settings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    shop_name: Mapped[str] = mapped_column(String(128), nullable=False, default="PC Repair Service")
    shop_address: Mapped[str | None] = mapped_column(Text, nullable=True)
    shop_phone: Mapped[str | None] = mapped_column(String(32), nullable=True)
    default_tax_rate: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False, default=0)
    payment_terms: Mapped[str | None] = mapped_column(Text, nullable=True)
