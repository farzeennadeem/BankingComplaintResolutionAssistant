from sqlalchemy import text


class AccountRepository:
    def __init__(self, conn):
        self.conn = conn                        # shared connection from DatabaseManager.transaction()

    def get_for_customer(self, customer_id):
        rows = self.conn.execute(
            text("SELECT * FROM account WHERE customer_id = :customer_id"),
            {"customer_id": customer_id},
        ).mappings().fetchall()
        return [dict(r) for r in rows]          # [] if none
