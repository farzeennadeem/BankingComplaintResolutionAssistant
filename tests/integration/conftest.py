"""Integration tests run the real service against a throwaway copy of bank.db.
Each test gets a fresh copy, so the real database is never changed and the
tests pass every time they run."""
import shutil

import pytest
from sqlalchemy import text

from src.data.database_manager import DatabaseManager
from src.services.complaint_service import ComplaintService


@pytest.fixture
def db(tmp_path):
    test_db = tmp_path / "test.db"
    shutil.copy("docs/database/bank.db", test_db)          # fresh copy for this test
    manager = DatabaseManager(f"sqlite:///{test_db}")
    with manager.transaction() as conn:                     # test data in the contract spellings
        conn.execute(text("UPDATE complaint SET status = 'Open' WHERE complaint_id = 'CMP001'"))        # data uses OPEN but the rules would reject that so we use this test data, real bank.db never touched
        conn.execute(text("UPDATE complaint SET status = 'In Review' WHERE complaint_id = 'CMP002'"))
    return manager


@pytest.fixture
def service(db):
    return ComplaintService(db)                             # the REAL service and repositories


def status_of(db, complaint_id):
    """The complaint's current status, read straight from the database."""
    with db.transaction() as conn:
        return conn.execute(text("SELECT status FROM complaint WHERE complaint_id = :id"),
                            {"id": complaint_id}).scalar()


def history_count(db, complaint_id):
    """How many history rows the complaint has."""
    with db.transaction() as conn:
        return conn.execute(text("SELECT COUNT(*) FROM complaint_status_history WHERE complaint_id = :id"),
                            {"id": complaint_id}).scalar()