import os                                   # lets Python read settings like DB_PATH
from sqlalchemy import create_engine        # SQLAlchemy's way of setting up a database connection


def get_database_engine():
    db_path = os.getenv("DB_PATH", "docs/database/bank.db")   # read DB_PATH, or use the default file
    return create_engine(f"sqlite:///{db_path}")                # "sqlite:///" tells SQLAlchemy which kind of database this is
    # To move to another database later (e.g. PostgreSQL), only this URL changes.
