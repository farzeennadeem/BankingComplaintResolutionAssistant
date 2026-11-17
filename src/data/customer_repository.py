from sqlalchemy import text                                 # text() wraps a SQL string so SQLAlchemy can run it
from src.data.database_manager import get_database_engine


class CustomerRepository:
    def get_by_id(self, customer_id):
        with get_database_engine().connect() as connection:     # "with" opens the connection and always closes it afterwards
            row = connection.execute(
                text("SELECT * FROM customer WHERE customer_id = :customer_id"),  # :customer_id is the placeholder (instead of ?)
                {"customer_id": customer_id},                    # the value for the placeholder, matched by name
            ).mappings().fetchone()                              # .mappings() lets us read columns by name; one row or None
            return dict(row) if row else None
