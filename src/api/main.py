"""The FastAPI app (Exercise 3.2.1). Run from the repository root: 
    uvicorn src.api.main:app --reload 
    curl -s localhost:8000/health/live 

create_app() takes optional db and service objects so tests can pass their own. 
""" 

from fastapi import FastAPI 

from src.api.errors import install_error_handlers 
from src.api.routers import health 
from src.config import get_settings 
from src.data.database_manager import DatabaseManager 
from src.services.complaint_service import ComplaintService 
  

def create_app(db=None, service=None): 
    settings = get_settings() 
    app = FastAPI(title=settings.app_name, version=settings.version) #fastAPI constructor, which creates the app object (REST API server)
    app.state.db = db or DatabaseManager() 
    app.state.service = service or ComplaintService(app.state.db) 
    install_error_handlers(app) 
    app.include_router(health.router) 

    return app 

app = create_app() 