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

from app.database import Base, get_db
from app.main import app

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


# Small helpers so tests stay short and readable.

_isbn_counter = iter(range(1000000000, 9999999999))


def add_book(client, title="Clean Code", author="Robert C. Martin", copies=1):
    body = {
        "title": title,
        "author": author,
        "isbn": str(next(_isbn_counter)),
        "total_copies": copies,
    }
    response = client.post("/books", json=body)
    assert response.status_code == 201, response.text
    return response.json()


def add_member(client, name="Ada Lovelace", email=None):
    email = email or f"{name.split()[0].lower()}{next(_isbn_counter)}@example.com"
    response = client.post("/members", json={"name": name, "email": email})
    assert response.status_code == 201, response.text
    return response.json()


def borrow(client, book, member):
    return client.post("/loans", json={"book_id": book["id"], "member_id": member["id"]})
