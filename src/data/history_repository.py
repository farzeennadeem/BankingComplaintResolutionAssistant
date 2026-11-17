from sqlalchemy import text

class HistoryRepository:
    def __init__(self, conn):
        self.conn = conn

    def get_for_complaint(self, complaint_id):
        rows = self.conn.execute(
            text(
                "SELECT h.history_id, h.complaint_id, h.old_status, h.new_status, h.changed_at, e.role AS changed_by_role "                       # the person's role, from the employee table
                "FROM complaint_status_history h "
                "LEFT JOIN employee e ON h.changed_by = e.employee_id "  # LEFT JOIN: keep the row even if no employee matches
                "WHERE h.complaint_id = :complaint_id "
                "ORDER BY h.changed_at, h.history_id"              # oldest first as the contract wants
            ),
            {"complaint_id": complaint_id},).mappings().fetchall()
        return [dict(r) for r in rows]

    def add(self, complaint_id, old_status, new_status, changed_at, changed_by):
        result = self.conn.execute(
            text(
                "INSERT INTO complaint_status_history (complaint_id, old_status, new_status, changed_at, changed_by) "
                "VALUES (:complaint_id, :old_status, :new_status, :changed_at, :changed_by)"
            ),
            {
                "complaint_id": complaint_id,
                "old_status": old_status,
                "new_status": new_status,
                "changed_at": changed_at,
                "changed_by": changed_by,
            },
        )
        return result.lastrowid  # the new history_id of the row just added