from fastapi.responses import JSONResponse
from sqlalchemy.exc import OperationalError
from fastapi import Request

from src.domain.errors import DomainError

class ApiError(Exception):
    """Raised by API dependencies (for example missing actor headers)."""
    def __init__(self, http_status, code, message):
        super().__init__(message)
        self.http_status, self.code, self.message = http_status, code, message

def error_response(request, http_status, code, message, retryable=False, details=None):
    error = {
        "code": code,
        "message": message,
        "correlation_id": request.headers.get("X-Correlation-Id", ""),  # empty for now
        "retryable": retryable,
    }
    if details is not None:                         # only added when there are details
        error["details"] = details
    return JSONResponse(status_code=http_status, content={"error": error})


def install_error_handlers(app):
    @app.exception_handler(DomainError)             # NotFound, ForbiddenRole, InvalidTransition, ...
    async def domain_error(request: Request, exc: DomainError):
        return error_response(request, exc.http_status, exc.code, exc.message, exc.retryable,
                              details=exc.details)

    @app.exception_handler(ApiError)                # errors raised by the API itself, e.g. missing headers
    async def api_error(request: Request, exc: ApiError):
        return error_response(request, exc.http_status, exc.code, exc.message)


    @app.exception_handler(OperationalError)        # if DB gives error (e.g. connection failing), call function below
    def database_unavailable(request, exc):
        return error_response(request, 503, "DEPENDENCY_UNAVAILABLE",
                              "Complaint database unavailable.", retryable=True)

    