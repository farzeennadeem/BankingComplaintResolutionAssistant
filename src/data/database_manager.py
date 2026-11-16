import os
import sqlite3

def get_database_connection():
    db_path = os.getenv("DB_PATH", "docs/database/bank.db")
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row        # makes each row readable by column name
    return connection