from datetime import datetime
from sqlalchemy import text
from src.data.database_manager import get_database_engine


class ComplaintRepository:
    def get_by_id(self, complaint_id):
        with get_database_engine().connect() as connection:
            row = connection.execute(
                text("SELECT * FROM complaint WHERE complaint_id = :complaint_id"),
                {"complaint_id": complaint_id},
            ).mappings().fetchone()
            return dict(row) if row else None

    def get_for_customer(self, customer_id):
        with get_database_engine().connect() as connection:
            rows = connection.execute(
                text("SELECT * FROM complaint WHERE customer_id = :customer_id"),
                {"customer_id": customer_id},
            ).mappings().fetchall()
            return [dict(r) for r in rows]

    def create(self, complaint_id, customer_id, account_id, channel, category, complaint_text, priority):
        # .begin() = a transaction: it COMMITS automatically if the block finishes,
        # and ROLLS BACK automatically if an error happens inside it. No manual commit/rollback needed.
        with get_database_engine().begin() as connection:
            connection.execute(
                text(
                    "INSERT INTO complaint (complaint_id, customer_id, account_id, channel, category, "
                    "complaint_text, priority, status, received_at) "
                    "VALUES (:complaint_id, :customer_id, :account_id, :channel, :category, "
                    ":complaint_text, :priority, 'Open', :received_at)"
                ),
                {
                    "complaint_id": complaint_id,
                    "customer_id": customer_id,
                    "account_id": account_id,
                    "channel": channel,
                    "category": category,
                    "complaint_text": complaint_text,
                    "priority": priority,
                    "received_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                },
            )
        return self.get_by_id(complaint_id)                      # read back the saved complaint
