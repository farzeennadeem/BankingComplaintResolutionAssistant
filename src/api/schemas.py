"""Request and response models (Exercise 3.2.2).

Request models check what callers send (wrong or extra fields -> 422).
Response models list only the fields we want to return, so nothing extra
(email, phone, balances) can leak even if a repository returns it.
Values match what is in our bank.db."""
from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")    # requests: unknown fields -> 422


class Out(BaseModel):
    model_config = ConfigDict(extra="ignore")    # responses: any field not listed is dropped


# Responses

class Customer(Out):
    customer_id: str
    first_name: str
    last_name: str
    segment: str


class ComplaintSummary(Out):                  # one complaint in a customer's list
    complaint_id: str
    customer_id: str
    account_id: Optional[str] = None
    category: str
    status: str
    priority: Optional[str] = None
    channel: str
    received_at: str


class CustomerComplaints(Out):
    customer_id: str
    complaints: List[ComplaintSummary]


class HistoryRow(Out):
    history_id: int
    complaint_id: str
    old_status: Optional[str] = None             # None for the first row
    new_status: str
    changed_at: str
    changed_by_role: Optional[str] = None


class ServiceRequest(Out):
    request_id: str
    request_type: Optional[str] = None
    status: Optional[str] = None
    created_date: Optional[str] = None


class Complaint(ComplaintSummary):               # the full complaint = the summary fields plus these
    complaint_text: str
    history: List[HistoryRow]
    linked_service_requests: List[ServiceRequest]


class StatusUpdateResult(Out):
    complaint_id: str
    previous_status: str
    status: str
    changed_by: Optional[str] = None
    changed_at: str
    audit_event_id: str


class CreateComplaintResult(Out):
    complaint_id: str
    status: str


# Requests

class StatusUpdateRequest(Strict):
    target_status: str
    reason: str = Field(min_length=5, max_length=500)


class CreateComplaintRequest(Strict):
    customer_id: str
    account_id: Optional[str] = None
    channel: Literal["Phone", "Email", "Branch", "Web"]
    category: Literal["Fee Dispute", "Service Delay", "Transaction Error", "Online Banking",
                      "Card Issue", "Customer Service", "Fraud Claim"]
    complaint_text: str = Field(min_length=10, max_length=2000)
    priority: Literal["Low", "Medium", "High", "Critical"]
