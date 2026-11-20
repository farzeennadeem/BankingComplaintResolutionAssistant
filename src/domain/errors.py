"""Domain errors: what the service raises when a rule is broken.
Each has the contract's error code and HTTP status, so the API (3.3.2) can turn it into a response."""

class DomainError(Exception):
    code = "INTERNAL_ERROR" # the error code the API will send back
    http_status = 500       # the HTTP status the API use

    retryable = False       # can the caller try again later?

    def __init__(self, message, details=None):
        super().__init__(message)
        self.message = message      # readable text e.g. "Complaint CMP999 not found"
        self.details = details      # optional extra info

class NotFound(DomainError):        # e.g. a complaint ID that doesn't exist
    code = "NOT_FOUND"
    http_status = 404

class ForbiddenRole(DomainError):
    code = "FORBIDDEN_ROLE"
    http_status = 403

class InvalidTransition(DomainError):  # the status change isn't allowed at all
    code = "INVALID_TRANSITION"
    http_status = 409


class ApprovalRequired(DomainError):   # compensation above CAD 1,000 without approval
    code = "APPROVAL_REQUIRED"
    http_status = 409


class ValidationError(DomainError):    # bad input, e.g. a reason that's too short (your coach mentioned this one)
    code = "VALIDATION_ERROR"
    http_status = 422
