from collections.abc import Generator
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from database import get_db
from main import app
from models import Base, LaborType, ShopSettings, User, UserRole
from security import hash_password

TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def seed_test_data(db: Session) -> User:
    user = User(
        username="admin",
        password_hash=hash_password("password"),
        role=UserRole.ADMIN,
        must_change_password=False,
        is_active=True,
    )
    db.add(user)
    db.add(
        ShopSettings(
            shop_name="Test Shop",
            default_tax_rate=Decimal("20.00"),
        )
    )
    db.add(
        LaborType(
            name="General repair",
            hourly_rate=Decimal("2500.00"),
            is_active=True,
        )
    )
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db_session: Session) -> Generator[TestClient, None, None]:
    def override_get_db() -> Generator[Session, None, None]:
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def seeded_client(client: TestClient, db_session: Session) -> TestClient:
    seed_test_data(db_session)
    return client


def login(client: TestClient, username: str = "admin", password: str = "password") -> None:
    response = client.post(
        "/api/auth/login",
        json={"username": username, "password": password},
    )
    assert response.status_code == 200, response.text
