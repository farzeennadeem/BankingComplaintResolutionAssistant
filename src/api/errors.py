from fastapi.responses import JSONResponse
from sqlalchemy.exc import OperationalError

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
    @app.exception_handler(OperationalError)        # "whenever this error escapes a route, run this"
    def database_unavailable(request, exc):
        return error_response(request, 503, "DEPENDENCY_UNAVAILABLE",
                              "Complaint database unavailable.", retryable=True)