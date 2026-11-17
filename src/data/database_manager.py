import os
from sqlalchemy import create_engine


class DatabaseManager:
    def __init__(self, database_url=None):
        if database_url is None:                                   
            database_url = os.getenv("DATABASE_URL", "sqlite:///docs/database/bank.db")  # use the setting, or the default file
        self.engine = create_engine(database_url)                  # set up the connection to that database

    def transaction(self):
        return self.engine.begin()   # opens a connection; saves (commit) if all goes well, undoes (rollback) on error, then closes
