from decimal import Decimal
from enum import Enum  # enum is a fixed list of allowed values

class Category(str, Enum):
    FEES = "Fees"
    CARD_OR_TRANSACTION_DISPUTE = "Card or Transaction Dispute"
    DIGITAL_BANKING = "Digital Banking"
    SERVICE_QUALITY = "Service Quality"
    MORTGAGE_SERVICING = "Mortgage Servicing"
    ACCOUNT_ACCESS = "Account Access"

class ComplaintStatus(str, Enum):
    OPEN = "Open"
    IN_REVIEW = "In Review"
    PENDING_APPROVAL = "Pending Approval"
    ESCALATED = "Escalated"
    CLOSED = "Closed"

class Priority(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"

class Channel(str, Enum):
    EMAIL = "Email"
    PHONE = "Phone"
    WEB = "Web"
    BRANCH = "Branch"

class Role(str, Enum):
    ANALYST = "Analyst"
    SUPERVISOR = "Supervisor"


ALLOWED_TRANSITIONS = {
    (ComplaintStatus.OPEN, ComplaintStatus.IN_REVIEW): {Role.ANALYST, Role.SUPERVISOR},
    (ComplaintStatus.IN_REVIEW, ComplaintStatus.ESCALATED): {Role.ANALYST, Role.SUPERVISOR},
    (ComplaintStatus.ESCALATED, ComplaintStatus.IN_REVIEW): {Role.SUPERVISOR},
}

CLOSABLE = {                    # statuses /close accepts (not Pending Approval OR Closed)
    ComplaintStatus.OPEN,
    ComplaintStatus.IN_REVIEW,
    ComplaintStatus.ESCALATED,
}

APPROVAL_THRESHOLD_CAD = Decimal("10000.00")  # complaints over this amount require supervisor approval



def transition_problem(current, target, role):  #returns None if transition is allowed
    key = (ComplaintStatus(current), ComplaintStatus(target))
    if key not in ALLOWED_TRANSITIONS:
        return "Invalid transition"
    if Role(role) not in ALLOWED_TRANSITIONS[key]:
        return "Forbidden Role"
    return None

def can_transition(current, target, role):      #True if `role` may move a complaint from `current` to `target`
    return transition_problem(current, target, role) is None

def needs_approval(compensation_amount):
    return Decimal(str(compensation_amount)) > APPROVAL_THRESHOLD_CAD   # str() first so floats don't sneak in rounding errors