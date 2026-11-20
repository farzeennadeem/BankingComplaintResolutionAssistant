"""API tests run against fake repositories, no database."""
from datetime import date

import pytest
from fastapi.testclient import TestClient

from src.api.main import create_app
from src.services.complaint_service import ComplaintService
from tests.fakes import FakeDB, FakeStore, fake_repositories

ANALYST = {"X-Actor-Id": "EMP001", "X-Actor-Role": "Analyst"}   # headers for "an Analyst is calling"


@pytest.fixture
def store():
    return FakeStore.sample()                 # fresh fake data for every test


@pytest.fixture
def client(store):                            # a test that asks for "client" gets this
    db = FakeDB(store)
    service = ComplaintService(db, fake_repositories(store), today=lambda: date(2026, 9, 1))
    app = create_app(db=db, service=service)  # the real app, but given the fakes instead of bank.db
    return TestClient(app, raise_server_exceptions=False)   # sends requests to the app without uvicorn