from datetime import datetime
from sqlalchemy import text


class ComplaintRepository:
    def __init__(self, conn):
        self.conn = conn                        # shared connection; commit/rollback is NOT our job

    def get_by_id(self, complaint_id):
        row = self.conn.execute(
            text("SELECT * FROM complaint WHERE complaint_id = :complaint_id"),
            {"complaint_id": complaint_id},
        ).mappings().fetchone()
        return dict(row) if row else None

    def get_for_customer(self, customer_id):
        rows = self.conn.execute(
            text("SELECT * FROM complaint WHERE customer_id = :customer_id"),
            {"customer_id": customer_id},
        ).mappings().fetchall()
        return [dict(r) for r in rows]

    def create(self, complaint_id, customer_id, account_id, channel, category, complaint_text, priority):
        # No commit here: whoever opened the transaction decides whether it is saved.
        self.conn.execute(
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
        return self.get_by_id(complaint_id)     # same connection, so it can see the new row

    def update_status(self, complaint_id, status):
        result = self.conn.execute(
            text("UPDATE complaint SET status = :status WHERE complaint_id = :complaint_id"),
            {"status": status, "complaint_id": complaint_id},
        )
        return result.rowcount      # how many rows changed
