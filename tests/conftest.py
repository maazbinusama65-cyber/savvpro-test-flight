"""
conftest.py — shared fixtures for FlightHub tests.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# StaticPool ensures all connections share the same in-memory database
engine_test = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)

# Patch database module BEFORE the app imports it
import database
database.engine = engine_test
database.SessionLocal = TestingSession

from database import Base, get_db
from main import app

import pytest
from fastapi.testclient import TestClient


def _override_get_db():
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def client():
    Base.metadata.create_all(bind=engine_test)
    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine_test)
    app.dependency_overrides.clear()


@pytest.fixture
def sample_flight(client):
    resp = client.post("/api/flights/", json={
        "flight_number": "TEST001",
        "origin": "Karachi",
        "destination": "Lahore",
        "departure_time": "2025-08-15T08:00:00",
        "arrival_time": "2025-08-15T09:15:00",
        "price_per_seat": 8500.0,
        "total_seats": 5,
    })
    assert resp.status_code == 201, resp.text
    return resp.json()
