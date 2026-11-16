from src.data.database_manager import get_database_connection

class CustomerRepository:
    def get_by_id(self, customer_id):
        connection = get_database_connection()
        try:
            row = connection.execute("SELECT * FROM customer WHERE customer_id = ?", (customer_id,),).fetchone()
            return dict(row) if row else None
        finally:
            connection.close()