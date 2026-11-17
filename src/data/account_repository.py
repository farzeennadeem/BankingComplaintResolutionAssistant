from sqlalchemy import text
from src.data.database_manager import get_database_engine


class AccountRepository:
    def get_for_customer(self, customer_id):
        with get_database_engine().connect() as connection:     # opens and always closes the connection
            rows = connection.execute(
                text("SELECT * FROM account WHERE customer_id = :customer_id"),
                {"customer_id": customer_id},
            ).mappings().fetchall()                              # every matching row
            return [dict(r) for r in rows]                       # [] if none
