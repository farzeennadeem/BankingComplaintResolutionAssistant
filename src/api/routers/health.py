"""Health checks (Exercise 3.2.1). No actor headers needed. 
live  = the process is up (never touches the database). 
ready = the process can do real work (the database answers SELECT 1).""" 
from fastapi import APIRouter, Request
from sqlalchemy import text

router = APIRouter(prefix="/health", tags=["Health"]) 

@router.get("/live") # we assign functions to URLs to start creating operations for our app
def live(): 
    return {"status": "ok"} 

# TODO "Readiness and the 503": GET /ready 
@router.get("/ready")
def ready(request: Request):
    with request.app.state.db.transaction() as conn:        # open one transaction using the app's DatabaseManager
        conn.execute(text("SELECT 1"))                      # simple query to check the database answers
    return {"status": "ready", "checks": {"complaint_db": "ok"}}