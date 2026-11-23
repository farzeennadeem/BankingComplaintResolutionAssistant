"""The FastAPI app (Exercise 3.2.1). Run from the repository root: 
    uvicorn src.api.main:app --reload 
    curl -s localhost:8000/health/live 

create_app() takes optional db and service objects so tests can pass their own. 
""" 
import time
import uuid

from fastapi import FastAPI, Request

from src.api.errors import install_error_handlers, internal_error
from src.logging_config import configure_logging, get_logger
from src.api.routers import complaints, customers, health 
from src.config import get_settings 
from src.data.database_manager import DatabaseManager 
from src.services.complaint_service import ComplaintService 
  

def create_app(db=None, service=None): 
    settings = get_settings()
    configure_logging(settings.log_level) 
    app = FastAPI(title=settings.app_name, version=settings.version) #fastAPI constructor, which creates the app object (REST API server)
    app.state.db = db or DatabaseManager() 
    app.state.service = service or ComplaintService(app.state.db) 
    install_error_handlers(app) 
    app.include_router(health.router) 
    app.include_router(customers.router)
    app.include_router(complaints.router)

    # Add middleware for correlation and logging
    @app.middleware("http")
    async def correlation_and_logging(request: Request, call_next):
        # 1. Correlation ID: use the caller's if it's 1-64 characters, otherwise make one
        incoming = request.headers.get("X-Correlation-Id", "")
        if 1 <= len(incoming) <= 64:
            correlation_id = incoming
        else:
            correlation_id = f"corr-{uuid.uuid4().hex[:12]}"      # e.g. corr-9c3921defa00
        request.state.correlation_id = correlation_id            # error_response reads it from here

        # 2. Run the route, timing it
        start = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception as exc:                                  # safety net for unexpected crashes
            get_logger().error(f"unexpected error: {type(exc).__name__}")
            response = internal_error(request)
        duration_ms = round((time.perf_counter() - start) * 1000, 1)

        # 3. Put the ID on every response, and write one safe log line
        response.headers["X-Correlation-Id"] = correlation_id
        log_fields = {"correlation_id": correlation_id, "method": request.method,
                      "path": request.url.path, "status": response.status_code,
                      "duration_ms": duration_ms}
        error_code = getattr(request.state, "error_code", None)   # set by error_response, if there was an error
        if error_code:
            log_fields["error_code"] = error_code
        get_logger().info("request", extra=log_fields)
        return response

    return app 

app = create_app() 