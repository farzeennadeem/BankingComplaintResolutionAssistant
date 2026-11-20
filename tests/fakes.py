"""In-memory fakes for unit and API tests (Exercise 3.1.2). No database needed.

    store = FakeStore.sample()
    service = ComplaintService(FakeDB(store), fake_repositories(store), today=lambda: date(2026, 9, 1))

FakeDB.transaction() copies the store first and puts the copy back if the block
raises, so the fakes roll back like the real database does.
"""
import copy
from contextlib import contextmanager
from datetime import date

from src.services.complaint_service import Repositories


class FakeStore:
    def __init__(self):
        self.customers, self.accounts, self.complaints = {}, {}, {}
        self.history, self.requests = [], []
        self.employees = {}                                    # NEW: employee ID -> role, like our employee table

    @classmethod
    def sample(cls):
        s = cls()
        s.employees = {"EMP001": "Analyst", "EMP009": "Supervisor"}   # NEW
        s.customers["C0096"] = {"customer_id": "C0096", "first_name": "Taylor", "last_name": "Wilson",
                                "segment": "Premium"}
        s.accounts["A00061"] = {"account_id": "A00061", "customer_id": "C0096", "account_type": "Mortgage",
                                "status": "Active"}
        for cid, status in [("CP00001", "Open"), ("CP00002", "In Review"), ("CP00003", "Escalated"),
                            ("CP00004", "Closed"), ("CP00005", "Pending Approval")]:
            s.complaints[cid] = {"complaint_id": cid, "customer_id": "C0096", "account_id": None,
                                 "category": "Fees", "status": status,
                                 "received_at": "2026-08-01 09:00:00",          # CHANGED: was date_opened / date_closed
                                 "complaint_text": "Unexpected fee on my account",  # NEW: our Complaint response needs it
                                 "channel": "Web", "priority": "Medium"}
            s.history.append({"history_id": len(s.history) + 1,         # CHANGED: a number (1, 2, ...), not "H00001"
                              "complaint_id": cid,
                              "old_status": None, "new_status": status,
                              "changed_at": "2026-08-01 09:00:00",      # CHANGED: text, like our database returns
                              "changed_by_role": "System"})
        return s


class FakeDB:
    def __init__(self, store):
        self.store = store

    @contextmanager
    def transaction(self):
        saved = copy.deepcopy(self.store.__dict__)
        try:
            yield None
        except Exception:
            self.store.__dict__.clear()
            self.store.__dict__.update(saved)
            raise


class FakeCustomers:
    def __init__(self, s): self.s = s
    def get_by_id(self, customer_id): return self.s.customers.get(customer_id)


class FakeAccounts:
    def __init__(self, s): self.s = s
    def get_for_customer(self, customer_id):
        return sorted((a for a in self.s.accounts.values() if a["customer_id"] == customer_id),
                      key=lambda a: a["account_id"])


class FakeComplaints:
    def __init__(self, s): self.s = s
    def get_by_id(self, complaint_id):
        row = self.s.complaints.get(complaint_id)
        return dict(row) if row else None
    def get_for_customer(self, customer_id):              # used by get_customer_complaints
        return [dict(c) for c in self.s.complaints.values() if c["customer_id"] == customer_id]

    def next_id(self):                                    # used by create_complaint: 5 complaints -> "CP00006"
        return f"CP{len(self.s.complaints) + 1:05d}"

    def create(self, complaint_id, customer_id, account_id, channel, category, complaint_text, priority):
        self.s.complaints[complaint_id] = {"complaint_id": complaint_id, "customer_id": customer_id,
                                           "account_id": account_id, "category": category, "status": "Open",
                                           "received_at": "2026-09-01 09:00:00", "complaint_text": complaint_text,
                                           "channel": channel, "priority": priority}
        return self.get_by_id(complaint_id)
    
    def update_status(self, complaint_id, status, date_closed=None):
        self.s.complaints[complaint_id].update(status=status, date_closed=date_closed)
        return 1


class FakeHistory:
    def __init__(self, s): self.s = s
    def get_for_complaint(self, complaint_id):
        return [h for h in self.s.history if h["complaint_id"] == complaint_id]
    def add(self, complaint_id, old_status, new_status, changed_at, changed_by):   # CHANGED: changed_by, not changed_by_role
        history_id = len(self.s.history) + 1                                       # CHANGED: a number, not "H00006"
        self.s.history.append({"history_id": history_id, "complaint_id": complaint_id, "old_status": old_status,
                               "new_status": new_status, "changed_at": changed_at,
                               "changed_by_role": self.s.employees.get(changed_by)})  # look up the role, like our JOIN does
        return history_id


class FakeRequests:
    def __init__(self, s): self.s = s
    def get_for_complaint(self, complaint_id):
        return [r for r in self.s.requests if r.get("complaint_id") == complaint_id]


def fake_repositories(store):
    return lambda _conn: Repositories(FakeCustomers(store), FakeAccounts(store), FakeComplaints(store),
                                      FakeHistory(store), FakeRequests(store))
