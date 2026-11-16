from src.data.database_manager import get_database_connection

class AccountRepository:
    def get_for_customer(self, customer_id):
        connection = get_database_connection()
        try:
            row = connection.execute("SELECT * FROM account WHERE customer_id = ?", (customer_id,),).fetchall()
            return [dict(r) for r in row]
        finally:
            connection.close()