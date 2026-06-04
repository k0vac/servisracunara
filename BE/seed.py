from decimal import Decimal

from sqlalchemy import select

from database import SessionLocal
from models import LaborType, ShopSettings, User, UserRole
from security import hash_password


def seed() -> None:
    session = SessionLocal()
    try:
        admin = session.scalar(select(User).where(User.username == "admin"))
        if admin is None:
            session.add(
                User(
                    username="admin",
                    password_hash=hash_password("password"),
                    role=UserRole.ADMIN,
                    must_change_password=True,
                    is_active=True,
                )
            )

        settings = session.scalar(select(ShopSettings).limit(1))
        if settings is None:
            session.add(
                ShopSettings(
                    shop_name="PC Repair Service",
                    shop_address=None,
                    shop_phone=None,
                    default_tax_rate=Decimal("0.00"),
                    payment_terms=None,
                )
            )

        default_labor_types = [
            ("General repair", Decimal("2500.00")),
            ("Diagnostic", Decimal("3000.00")),
            ("Software / OS", Decimal("2000.00")),
        ]
        for name, rate in default_labor_types:
            existing_type = session.scalar(select(LaborType).where(LaborType.name == name))
            if existing_type is None:
                session.add(LaborType(name=name, hourly_rate=rate, is_active=True))

        session.commit()
        print("Seed data applied")
    finally:
        session.close()


if __name__ == "__main__":
    seed()
