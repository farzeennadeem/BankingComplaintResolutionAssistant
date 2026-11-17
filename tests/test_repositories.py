import shutil                                          # copy files
import pytest
from src.data.database_manager import DatabaseManager
from src.data.customer_repository import CustomerRepository
from src.data.account_repository import AccountRepository
from src.data.complaint_repository import ComplaintRepository


def make_test_db(tmp_path):
    """A throwaway copy of bank.db, so the real database is never touched."""
    test_db = tmp_path / "test.db"
    shutil.copy("docs/database/bank.db", test_db)
    return DatabaseManager(f"sqlite:///{test_db}")     # point the manager straight at the copy


# VALID cases
def test_customer_found(tmp_path):
    db = make_test_db(tmp_path)
    with db.transaction() as conn:
        assert CustomerRepository(conn).get_by_id("CUS001") is not None

def test_accounts_for_customer(tmp_path):
    db = make_test_db(tmp_path)
    with db.transaction() as conn:
        assert len(AccountRepository(conn).get_for_customer("CUS001")) > 0

def test_complaints_for_customer(tmp_path):
    db = make_test_db(tmp_path)
    with db.transaction() as conn:
        assert len(ComplaintRepository(conn).get_for_customer("CUS001")) > 0

def test_create_complaint(tmp_path):
    db = make_test_db(tmp_path)
    with db.transaction() as conn:
        new = ComplaintRepository(conn).create("CMP999", "CUS001", "ACC001", "Email",
                                               "Fee Dispute", "Test complaint", "Low")
    assert new is not None
    with db.transaction() as conn:                     # a NEW transaction: proves it was committed
        assert ComplaintRepository(conn).get_by_id("CMP999") is not None


# MISSING cases
def test_complaint_not_found(tmp_path):
    db = make_test_db(tmp_path)
    with db.transaction() as conn:
        assert ComplaintRepository(conn).get_by_id("CMP000") is None

def test_customer_not_found(tmp_path):
    db = make_test_db(tmp_path)
    with db.transaction() as conn:
        assert CustomerRepository(conn).get_by_id("CUS999") is None


# FAILURE cases
def test_duplicate_complaint_rejected(tmp_path):
    db = make_test_db(tmp_path)
    with pytest.raises(Exception):                     # CMP001 already exists
        with db.transaction() as conn:
            ComplaintRepository(conn).create("CMP001", "CUS001", "ACC001", "Email",
                                             "Fee Dispute", "Duplicate", "Low")

def test_error_rolls_back_the_whole_transaction(tmp_path):
    db = make_test_db(tmp_path)
    with pytest.raises(RuntimeError):
        with db.transaction() as conn:
            ComplaintRepository(conn).create("CMP998", "CUS001", "ACC001", "Email",
                                             "Fee Dispute", "Should not be saved", "Low")
            raise RuntimeError("something failed after the insert")
    with db.transaction() as conn:                     # the insert must have been undone
        assert ComplaintRepository(conn).get_by_id("CMP998") is None

def test_bad_database_path():
    db = DatabaseManager("sqlite:////no/such/folder/x.db")   # a location that doesn't exist
    with pytest.raises(Exception):
        with db.transaction() as conn:
            ComplaintRepository(conn).get_by_id("CMP001")
