import os, shutil                                      # os: set DB_PATH; shutil: copy files
import pytest
from src.data.customer_repository import CustomerRepository
from src.data.account_repository import AccountRepository
from src.data.complaint_repository import ComplaintRepository

def use_test_db(tmp_path):                             # make a throwaway copy of the database for each test
    test_db = tmp_path / "test.db"
    shutil.copy("docs/database/bank.db", test_db)      # the real database is never touched
    os.environ["DB_PATH"] = str(test_db)               #points code at the copy


# VALID cases
def test_customer_found(tmp_path):
    use_test_db(tmp_path)
    # cust_id = input("Enter a valid customer ID (e.g., CUS001): ")
    assert CustomerRepository().get_by_id("CUS001") is not None  # 'assert' checks if something is True or False. False means test fails

def test_accounts_for_customer(tmp_path):
    use_test_db(tmp_path)
    assert len(AccountRepository().get_for_customer("CUS001")) > 0 # at least one account

def test_create_complaint(tmp_path):
    use_test_db(tmp_path)
    new = ComplaintRepository().create("CMP999", "CUS001", "ACC001", "Email", "Fee Dispute", "Test complaint", "Low")
    assert new is not None

# MISSING cases
def test_complaint_not_found(tmp_path):
    use_test_db(tmp_path)
    assert ComplaintRepository().get_by_id("CMP000") is None

def test_no_complaints_for_unknown_customer(tmp_path):
    use_test_db(tmp_path)
    assert CustomerRepository().get_by_id("CUS999") is None

# FAILURE cases
def test_duplicate_complaint_rejected(tmp_path):
    use_test_db(tmp_path)
    with pytest.raises(Exception):                     # passes only if the code inside raises an error
        ComplaintRepository().create("CMP001", "CUS001", "ACC001", "Email",
                                     "Fee Dispute", "Duplicate", "Low")  # CMP001 already exists

def test_bad_database_path():
    os.environ["DB_PATH"] = "/no/such/folder/x.db"     # a location that doesn't exist
    with pytest.raises(Exception):                     # we expect an error, not a silent failure
        ComplaintRepository().get_by_id("CMP001")

