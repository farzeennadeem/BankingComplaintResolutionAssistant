from sqlalchemy import text

class ServiceRequestRepository:
    def __init__(self, conn):
        self.conn = conn

    def get_for_complaint(self, complaint_id):
        rows = self.conn.execute(
            text("SELECT s.request_id, s.request_type, s.status, s.created_at AS created_date "
                 "FROM service_request s "
                 "JOIN complaint c ON s.account_id = c.account_id WHERE c.complaint_id = :complaint_id "
                 "ORDER BY s.created_at, s.request_id"),
                 {"complaint_id": complaint_id},
        ).mappings().fetchall()
        return [dict(r) for r in rows]