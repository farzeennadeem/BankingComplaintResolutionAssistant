"""Settings (Exercise 3.2.1). One source: the root .env (or real environment 
variables). Never read os.environ anywhere else in src/api.""" 

import os 
from dataclasses import dataclass 

try: 
    from dotenv import load_dotenv 
    load_dotenv() 
except ImportError: 
    pass 

@dataclass(frozen=True) 
class Settings: 
    app_name: str = "Complaint Resolution Assistant API" 
    version: str = "0.3.0" 
    db_host: str = "127.0.0.1" 
    db_port: int = 5432 
    db_name: str = "complaints_training" 
    log_level: str = "INFO" 

def get_settings(): 
    return Settings( 
        db_host=os.getenv("DB_HOST", "127.0.0.1"), 
        db_port=int(os.getenv("DB_PORT", "5432")), 
        db_name=os.getenv("DB_NAME", "complaints_training"), 
        log_level=os.getenv("LOG_LEVEL", "INFO"), 

    )