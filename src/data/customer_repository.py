from sqlalchemy import text   # text() wraps a SQL string so SQLAlchemy can run it


class CustomerRepository:
    def __init__(self, conn):
        self.conn = conn                        # the connection is given to us; we never open or commit it

    def get_by_id(self, customer_id):
        row = self.conn.execute(
            text("SELECT * FROM customer WHERE customer_id = :customer_id"),  # :name placeholder
            {"customer_id": customer_id},
        ).mappings().fetchone()                 # one row (readable by column name) or None
        return dict(row) if row else None
