from src.data.database_manager import get_database_connection
from datetime import datetime

class ComplaintRepository:
    def get_by_id(self, complaint_id):
        connection = get_database_connection()
        try:
            row = connection.execute("SELECT * FROM complaint WHERE complaint_id = ?", (complaint_id,),).fetchone()
            return dict(row) if row else None
        finally:
            connection.close()

    def get_for_customer(self, customer_id):
        connection = get_database_connection()
        try:
            rows = connection.execute("SELECT * FROM complaint WHERE customer_id = ?", (customer_id),).fetchall()
            return [dict(r) for r in rows]
        finally:
            connection.close()

    def create(self, complaint_id, customer_id, account_id, channel, category, complaint_text, priority):
        connection = get_database_connection()
        try:
            connection.execute(
                "INSERT INTO complaint (complaint_id, customer_id, account_id, channel, category, complaint_text, priority, status, received_at) VALUES (?, ?, ?, ?, ?, ?, ?, 'Open', ?)",
                (complaint_id, customer_id, account_id, channel, category, complaint_text, priority, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            )
            connection.commit()
            return self.get_by_id(complaint_id)
        except Exception as e:
            connection.rollback()
            raise e
        finally:
            connection.close()
