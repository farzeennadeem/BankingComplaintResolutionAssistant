"""Smoke tests for the 3.2.2 routes: one per route plus no-prefix check."""
from tests.api.conftest import ANALYST

NEW_COMPLAINT = {"customer_id": "C0096", "channel": "Email", "category": "Fee Dispute",
                 "complaint_text": "Charged twice for the same transfer", "priority": "Medium"}


def test_get_customer_returns_only_four_fields(client):
    response = client.get("/customers/C0096")
    assert response.status_code == 200
    assert set(response.json()) == {"customer_id", "first_name", "last_name", "segment"}   # no extra fields leak


def test_get_customer_complaints(client):
    response = client.get("/customers/C0096/complaints")
    assert response.status_code == 200
    assert len(response.json()["complaints"]) == 5                  # the fake store has 5 complaints


def test_get_complaint_includes_history(client):
    response = client.get("/complaints/CP00002")
    assert response.status_code == 200
    assert response.json()["status"] == "In Review"
    assert response.json()["history"][0]["new_status"] == "In Review"


def test_create_complaint_returns_201(client, store):
    response = client.post("/complaints", json=NEW_COMPLAINT, headers=ANALYST)
    assert response.status_code == 201
    assert response.json() == {"complaint_id": "CP00006", "status": "Open"}
    assert store.history[-1]["new_status"] == "Open"                # a history row was recorded


def test_patch_status_as_analyst(client, store):
    response = client.patch("/complaints/CP00001/status",
                            json={"target_status": "In Review", "reason": "Picked up"}, headers=ANALYST)
    assert response.status_code == 200
    assert response.json()["previous_status"] == "Open"
    assert response.json()["changed_by"] == "EMP001"
    assert response.json()["audit_event_id"] == "AUD-000006"       # the 6th history row
    assert store.history[-1]["changed_by_role"] == "Analyst"


def test_no_api_v1_prefix(client):
    assert client.get("/api/v1/customers/C0096").status_code == 404