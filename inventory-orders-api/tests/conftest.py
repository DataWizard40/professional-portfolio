"""Shared test setup.

Tests use an in-memory SQLite database by default, so they run without MySQL.
To run them against MySQL instead, set TEST_DATABASE_URL, for example:
    TEST_DATABASE_URL=mysql+pymysql://root:root@127.0.0.1:3306/test_db pytest
"""

import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.auth import create_access_token, hash_password
from app.database import Base, get_db
from app.main import app
from app.models import Product, User

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL") or "sqlite://"

if TEST_DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        TEST_DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
else:
    engine = create_engine(TEST_DATABASE_URL)

TestingSessionLocal = sessionmaker(bind=engine, autoflush=False)


@pytest.fixture
def db():
    # Fresh, empty tables for every test.
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    session = TestingSessionLocal()
    yield session
    session.close()


@pytest.fixture
def client(db):
    def override_get_db():
        session = TestingSessionLocal()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


def make_user(db, email, is_admin=False):
    user = User(email=email, hashed_password=hash_password("password123"), is_admin=is_admin)
    db.add(user)
    db.commit()
    return user


def auth_header(user):
    return {"Authorization": f"Bearer {create_access_token(user.id)}"}


@pytest.fixture
def admin_headers(db):
    return auth_header(make_user(db, "admin@example.com", is_admin=True))


@pytest.fixture
def user_headers(db):
    return auth_header(make_user(db, "customer@example.com"))


@pytest.fixture
def product(db):
    item = Product(name="Keyboard", sku="KB-1", price="25.00", quantity=10)
    db.add(item)
    db.commit()
    return item
