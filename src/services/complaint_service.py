"""Complaint service: the business rules the API exposes (Exercises 3.1.2 and 3.3.1). 

The service never writes SQL; repositories do. Every method opens ONE 
transaction, so a status change and its history row commit or roll back together. 

    service = ComplaintService(DatabaseManager()) 
    service.change_status("CP00001", "In Review", "Picked up for review", role="Analyst") 
""" 

from dataclasses import dataclass 
from datetime import date, datetime, timezone 
from decimal import Decimal 

from src.data.account_repository import AccountRepository 
from src.data.complaint_repository import ComplaintRepository 
from src.data.customer_repository import CustomerRepository 
from src.data.history_repository import HistoryRepository 
from src.data.service_request_repository import ServiceRequestRepository 
from src.domain.errors import ApprovalRequired, ForbiddenRole, InvalidTransition, NotFound 
from src.domain.models import CLOSABLE, ComplaintStatus, Role, needs_approval, transition_problem 

@dataclass 
class Repositories: 

    customers: object 
    accounts: object 
    complaints: object 
    history: object 
    requests: object

def make_repositories(conn): 
    """The real repositories, all on one connection (so one transaction).""" 
    return Repositories(CustomerRepository(conn), AccountRepository(conn), ComplaintRepository(conn), 
                        HistoryRepository(conn), ServiceRequestRepository(conn)) 

  

def audit_event_id_for(history_id): 
    """Week 3 has no audit table: every write adds one history row, that row is the 
    write's audit record, and audit_event_id names it (H00281 -> AUD-000281). 
    Sprint 3's audit log replaces this.""" 
    return f"AUD-{int(history_id):06d}" 


class ComplaintService:
    def __init__(self, db, repositories=make_repositories, today=date.today): 
        self.db = db                      # anything with a transaction() context manager 
        self.repositories = repositories  # conn -> Repositories (tests pass fakes) 
        self.today = today 

    def get_customer(self, customer_id): 
        with self.db.transaction() as conn: 
            customer = self.repositories(conn).customers.get_by_id(customer_id) 
        if customer is None: 
            raise NotFound(f"Customer {customer_id} not found.") 
        return customer 
  
    # TODO get_accounts, get_complaint (+ _complaint_with_children), change_status, 
    #      close
    def get_accounts(self, customer_id):
        with self.db.transaction() as conn:
            accounts = self.repositories(conn).accounts.get_for_customer(customer_id)
            if accounts is None:
                raise NotFound(f"Customer {customer_id} not found.")
        return {"customer_id": customer_id, "accounts": accounts}

    def get_complaint(self, complaint_id):
            with self.db.transaction() as conn:
                complaint = self.repositories(conn).complaints.get_by_id(complaint_id)
                if complaint is None:
                    raise NotFound(f"Complaint {complaint_id} not found.")
                complaint["history"] = self.repositories(conn).history.get_for_complaint(complaint_id)
                complaint["linked_service_requests"] = self.repositories(conn).requests.get_for_complaint(complaint_id)
            return complaint

    def change_status(self, complaint_id, target_status, reason, role, actor_id=None):
        target = _v(target_status)                           # accept "In Review" or ComplaintStatus.IN_REVIEW
        with self.db.transaction() as conn:
            repos = self.repositories(conn)

            complaint = repos.complaints.get_by_id(complaint_id)
            if complaint is None:
                raise NotFound(f"Complaint {complaint_id} not found.")
            current = complaint["status"]

            problem = transition_problem(current, target, role) # check using models.py rules (3.1.1)

            if problem == "FORBIDDEN_ROLE":
                raise ForbiddenRole(f"Role {_v(role)} cannot move complaint {complaint_id} from {current} to {target}")
            if problem is not None:
                message = f"{complaint_id} cannot move from {current} to {target}: {problem}"
                raise InvalidTransition(message) # in errors.py

            changed_at = datetime.now(timezone.utc)
            repos.complaints.update_status(complaint_id, target)
            history_id = repos.history.add(complaint_id, current, target, changed_at.strftime("%Y-%m-%d %H:%M:%S"), actor_id)

        return {"complaint_id": complaint_id, "previous_status": current, "status": target, "changed_by": actor_id, "changed_at": changed_at.isoformat(), "audit_event_id": audit_event_id_for(history_id)}

    def close(self, complaint_id, compensation_cad=Decimal("0"), role="Supervisor", actor_id=None):
        if _v(role) != Role.SUPERVISOR.value:
            raise ForbiddenRole(f"Role {_v(role)} cannot close complaint.")

        with self.db.transaction() as conn:
            repos = self.repositories(conn)

            complaint = repos.complaints.get_by_id(complaint_id)
            if complaint is None:
                raise NotFound(f"Complaint {complaint_id} not found.")
            current = complaint["status"]

            if ComplaintStatus(current) not in CLOSABLE:
                 raise InvalidTransition(f"A complaint in status {current} cannot be closed.")
            if needs_approval(compensation_cad):
                raise ApprovalRequired(f"Compensation above CAD 1000 needs an approved request.")

            date_closed = self.today()
            repos.complaints.update_status(complaint_id, ComplaintStatus.CLOSED.value)
            history_id = repos.history.add(complaint_id, current, ComplaintStatus.CLOSED.value, datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"), actor_id)

        return {"complaint_id": complaint_id, "previous_status": current, "status": ComplaintStatus.CLOSED.value, "date_closed": date_closed.isoformat(), "closed_by": actor_id, "approval_id": None, "audit_event_id": audit_event_id_for(history_id)}

    def get_customer_complaints(self, customer_id):
        with self.db.transaction() as conn:
            repos = self.repositories(conn)
            if repos.customers.get_by_id(customer_id) is None:
                raise NotFound(f"Customer {customer_id} not found.")
            complaints = repos.complaints.get_for_customer(customer_id)
        return {"customer_id": customer_id, "complaints": complaints}

    def create_complaint(self, customer_id, account_id, channel, category, complaint_text, priority, actor_id=None):
        with self.db.transaction() as conn:
            repos = self.repositories(conn)
            if repos.customers.get_by_id(customer_id) is None:
                raise NotFound(f"Customer {customer_id} not found.")
            complaint_id = repos.complaints.next_id()
            complaint = repos.complaints.create(complaint_id, customer_id, account_id, channel,
                                                category, complaint_text, priority)
            repos.history.add(complaint_id, None, complaint["status"],
                              datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"), actor_id)
        return {"complaint_id": complaint_id, "status": complaint["status"]}


def _v(value):
    """Enum member or plain string -> plain string.""" 
    return getattr(value, "value", value) 