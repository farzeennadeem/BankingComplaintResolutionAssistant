"""Turns every error into the contract error envelope (Exercises 3.2.1, 3.2.2, 3.3.2):
    {"error": {"code", "message", "correlation_id", "retryable", ["details"]}}
No stack traces, SQL or exception text ever go into a response."""
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import OperationalError
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.domain.errors import DomainError
from src.logging_config import get_logger


class ApiError(Exception):
    """Raised by API dependencies (for example missing actor headers)."""
    def __init__(self, http_status, code, message):
        super().__init__(message)
        self.http_status, self.code, self.message = http_status, code, message


def error_response(request, http_status, code, message, retryable=False, details=None):
    correlation_id = getattr(request.state, "correlation_id", "")   # set by the middleware in main.py
    request.state.error_code = code                                 # so the middleware can log it
    error = {
        "code": code,
        "message": message,
        "correlation_id": correlation_id,
        "retryable": retryable,
    }
    if details is not None:
        error["details"] = details
    return JSONResponse(status_code=http_status, content={"error": error},
                        headers={"X-Correlation-Id": correlation_id})


def field_name(err):
    """The request field a validation error is about. Invalid JSON names the whole body."""
    if err["type"] == "json_invalid":
        return "body"
    return ".".join(str(p) for p in err["loc"] if p not in ("body", "path", "header")) or "body"


def internal_error(request):
    """The 500 response: a fixed message, never the real error text (it could contain SQL or data)."""
    return error_response(request, 500, "INTERNAL_ERROR",
                          "Unexpected error. Quote the correlation ID when reporting it.")


def install_error_handlers(app):
    @app.exception_handler(DomainError)                 # NotFound, ForbiddenRole, InvalidTransition, ...
    async def domain_error(request: Request, exc: DomainError):
        return error_response(request, exc.http_status, exc.code, exc.message, exc.retryable,
                              details=exc.details)

    @app.exception_handler(ApiError)                    # errors raised by the API itself
    async def api_error(request: Request, exc: ApiError):
        return error_response(request, exc.http_status, exc.code, exc.message)

    @app.exception_handler(OperationalError)            # database unreachable
    async def database_unavailable(request: Request, exc: OperationalError):
        return error_response(request, 503, "DEPENDENCY_UNAVAILABLE",
                              "Complaint database unavailable.", retryable=True)

    @app.exception_handler(RequestValidationError)      # bad body, header or path; extra field; broken JSON
    async def validation_error(request: Request, exc: RequestValidationError):
        details = [{"field": field_name(err), "issue": err["msg"]} for err in exc.errors()]
        return error_response(request, 422, "VALIDATION_ERROR", "Request validation failed.",
                              details=details)

    @app.exception_handler(StarletteHTTPException)      # unknown URL (404) or wrong method (405)
    async def http_error(request: Request, exc: StarletteHTTPException):
        if exc.status_code == 405:
            return error_response(request, 405, "METHOD_NOT_ALLOWED",
                                  f"Method {request.method} is not allowed on this path.")
        if exc.status_code == 404:
            return error_response(request, 404, "NOT_FOUND", "Resource not found.")
        return internal_error(request)

    @app.exception_handler(Exception)                   # anything unexpected
    async def unexpected_error(request: Request, exc: Exception):
        get_logger().error(f"unexpected error: {type(exc).__name__}")   # log the TYPE only, e.g. ValueError
        return internal_error(request)