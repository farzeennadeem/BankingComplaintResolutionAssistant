"""Exercise 3.3.1: every write changes the complaint and its history row together,
and a failure part-way leaves the database exactly as it was.

python -m pytest tests/integration -v      # 3 passed
python -m pytest tests/integration -v      # run again: 3 passed (nothing left behind proves nothing was changed in db)
"""
from decimal import Decimal

import pytest

from src.data.history_repository import HistoryRepository
from tests.integration.conftest import history_count, status_of


def fail(*args, **kwargs):
    raise RuntimeError("history insert failed")             # stands in for a real database failure


def test_status_and_history_are_written_together(db, service):
    before = history_count(db, "CMP001")
    service.change_status("CMP001", "In Review", "Picked up", role="Analyst", actor_id="EMP001")
    assert status_of(db, "CMP001") == "In Review"           # status changed
    assert history_count(db, "CMP001") == before + 1        # and exactly one history row added


def test_change_status_rolls_back_when_history_fails(db, service, monkeypatch):
    before = history_count(db, "CMP001")
    monkeypatch.setattr(HistoryRepository, "add", fail)     # make the history insert fail AFTER the UPDATE
    with pytest.raises(RuntimeError):
        service.change_status("CMP001", "In Review", "Picked up", role="Analyst", actor_id="EMP001")
    assert status_of(db, "CMP001") == "Open"                # the UPDATE was rolled back
    assert history_count(db, "CMP001") == before


def test_close_rolls_back_when_history_fails(db, service, monkeypatch):
    before = history_count(db, "CMP002")
    monkeypatch.setattr(HistoryRepository, "add", fail)
    with pytest.raises(RuntimeError):
        service.close("CMP002", Decimal("0"), role="Supervisor", actor_id="EMP009")
    assert status_of(db, "CMP002") == "In Review"           # still In Review, not Closed
    assert history_count(db, "CMP002") == before