import os
import sqlite3
from datetime import datetime
from src.db_config import DatabaseManager
from src.data_loader import DataLoader

class ECommerceCLI:
    """CLI Analytics Interface[cite: 3]."""
    def __init__(self):
        self.db_mgr = DatabaseManager()
        self.db_mgr.connect()

    def initialize_system(self):
        print("\n[INFO] Setting up database schema, indexes, and views...")
        self.db_mgr.execute_script(os.path.join("sql", "schema.sql"))
        self.db_mgr.execute_script(os.path.join("sql", "procedures_and_views.sql"))
        
        loader = DataLoader(self.db_mgr)
        loader.load_all_data()

    def _ensure_connection(self):
        """Ensures the main database connection is active, reconnecting if necessary."""
        try:
            if not self.db_mgr.connection:
                self.db_mgr.connect()
            else:
                # Test the connection cursor
                self.db_mgr.connection.cursor()
        except Exception:
            self.db_mgr.connect()

    def insert_user(self):
        self._ensure_connection()
        conn = self.db_mgr.connection
        cursor = conn.cursor()
        name = input("Enter Name: ")
        email = input("Enter Email: ")
        city = input("Enter City: ")
        date = datetime.now().strftime('%Y-%m-%d')
        
        cursor.execute("INSERT INTO Customers (name, email, city, signup_date) VALUES (?, ?, ?, ?);", (name, email, city, date))
        cursor.execute("INSERT INTO AuditLogs (action, status_message) VALUES ('INSERT_USER', ?);", (f"Added user {name}",))
        conn.commit()
        print("[SUCCESS] User inserted and logged!")

    def select_inventory(self):
        self._ensure_connection()
        conn = self.db_mgr.connection
        cursor = conn.cursor()
        cursor.execute("SELECT product_id, product_name, category, price, stock_qty FROM Products;")
        for r in cursor.fetchall():
            print(f"ID: {r[0]} | {r[1]} | {r[2]} | ${r[3]} | Stock: {r[4]}")
        cursor.execute("INSERT INTO AuditLogs (action, status_message) VALUES ('SELECT_INVENTORY', 'Queried inventory');")
        conn.commit()

    def update_stock(self):
        self._ensure_connection()
        conn = self.db_mgr.connection
        cursor = conn.cursor()
        pid = input("Enter Product ID: ")
        stock = int(input("Enter New Stock Qty: "))
        cursor.execute("UPDATE Products SET stock_qty = ? WHERE product_id = ?;", (stock, pid))
        cursor.execute("INSERT INTO AuditLogs (action, status_message) VALUES ('UPDATE_STOCK', ?);", (f"Updated product {pid} stock to {stock}",))
        conn.commit()
        print("[SUCCESS] Stock updated and logged!")

    def delete_order(self):
        self._ensure_connection()
        conn = self.db_mgr.connection
        cursor = conn.cursor()
        oid = input("Enter Order ID to delete: ")
        cursor.execute("BEGIN TRANSACTION;")
        cursor.execute("DELETE FROM OrderDetails WHERE order_id = ?;", (oid,))
        cursor.execute("DELETE FROM Orders WHERE order_id = ?;", (oid,))
        cursor.execute("INSERT INTO AuditLogs (action, status_message) VALUES ('DELETE_ORDER', ?);", (f"Deleted order {oid}",))
        conn.commit()
        print("[SUCCESS] Order deleted safely!")

    def view_audit_logs(self):
        self._ensure_connection()
        conn = self.db_mgr.connection
        cursor = conn.cursor()
        cursor.execute("SELECT log_id, action, executed_at, status_message FROM AuditLogs;")
        for r in cursor.fetchall():
            print(f"Log ID: {r[0]} | {r[1]} | {r[2]} | {r[3]}")

    def _log_audit_independent(self, action, message):
        """Uses a fully isolated temporary connection to log rollbacks safely."""
        try:
            temp_conn = sqlite3.connect(self.db_mgr.db_path)
            temp_cursor = temp_conn.cursor()
            temp_cursor.execute("INSERT INTO AuditLogs (action, status_message) VALUES (?, ?);", (action, message))
            temp_conn.commit()
            temp_conn.close()
        except Exception as e:
            print(f"[DEBUG] Independent audit logging failed: {e}")

    def place_order(self):
        self._ensure_connection()
        conn = self.db_mgr.connection
        cursor = conn.cursor()
        cid = input("Customer ID: ")
        pid = input("Product ID: ")
        qty = int(input("Quantity: "))
        
        try:
            conn.execute("BEGIN TRANSACTION;")
            cursor.execute("SELECT price, stock_qty FROM Products WHERE product_id = ?;", (pid,))
            prod = cursor.fetchone()
            
            if not prod:
                conn.rollback()
                self._log_audit_independent("FAILED_ORDER", f"Attempted order for non-existent Product ID {pid}")
                print("[ERROR] Product not found. Rolling back.")
                return
                
            if prod[1] < qty:
                conn.rollback()
                self._log_audit_independent("FAILED_ORDER", f"Stock failure for Product ID {pid}. Requested: {qty}, Available: {prod[1]}")
                print("[ERROR] Insufficient stock. Rolling back.")
                return
            
            subtotal = prod[0] * qty
            date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            cursor.execute("UPDATE Products SET stock_qty = stock_qty - ? WHERE product_id = ?;", (qty, pid))
            cursor.execute("INSERT INTO Orders (customer_id, order_date, total_amount, status) VALUES (?, ?, ?, 'Completed');", (cid, date, subtotal))
            oid = cursor.lastrowid
            cursor.execute("INSERT INTO OrderDetails (order_id, product_id, quantity, unit_price, subtotal) VALUES (?, ?, ?, ?, ?);", (oid, pid, qty, prod[0], subtotal))
            
            cursor.execute("INSERT INTO AuditLogs (action, status_message) VALUES ('PLACE_ORDER', ?);", (f"Placed Order #{oid}",))
            
            conn.commit()
            print(f"[SUCCESS] Order #{oid} placed successfully!")
        except Exception as e:
            conn.rollback()
            self._log_audit_independent("FAILED_ORDER_ERROR", f"Transaction exception: {str(e)}")
            print(f"[ERROR] Transaction failed: {e}")

    def run_analytics_reports(self):
        self._ensure_connection()
        path = os.path.join("sql", "analytics_queries.sql")
        if not os.path.exists(path):
            print("[ERROR] analytics_queries.sql not found.")
            return

        with open(path, "r", encoding="utf-8") as f:
            script_sql = f.read()

        conn = self.db_mgr.connection
        cursor = conn.cursor()
        
        print("\n--- EXECUTING ANALYTICS QUERIES FROM FILE ---")
        try:
            statements = script_sql.split(";")
            for idx, stmt in enumerate(statements, 1):
                clean_stmt = stmt.strip()
                if clean_stmt:
                    print(f"\n[Executing Query #{idx}]:")
                    cursor.execute(clean_stmt)
                    rows = cursor.fetchall()
                    if rows:
                        for r in rows:
                            print(r)
                    else:
                        print("(Query executed successfully, but returned 0 rows)")
            conn.commit()
        except Exception as e:
            print(f"[ERROR] Failed executing script: {e}")

    def view_monthly_summary(self):
        self._ensure_connection()
        conn = self.db_mgr.connection
        cursor = conn.cursor()
        
        print("\n--- MONTHLY SUMMARY VIEW ---")
        cursor.execute("SELECT * FROM vw_monthly_summary;")
        rows = cursor.fetchall()
        if not rows:
            print("[INFO] No completed orders found yet. Place an order to populate this view!")
        else:
            for r in rows:
                print(f"Month: {r[0]} | Orders: {r[1]} | Active Buyers: {r[2]} | Revenue: ${r[3]:.2f}")

    def run(self):
        self.initialize_system()
        while True:
            print("\n=== E-COMMERCE CLI ENGINE ===")
            print("1. Insert User (CRUD)")
            print("2. View Inventory (CRUD)")
            print("3. Update Stock (CRUD)")
            print("4. Delete Order (CRUD)")
            print("5. View Audit Logs")
            print("6. Place Order (ACID Transaction)")
            print("7. Run Analytics Queries (CTE / Window Functions)")
            print("8. View Monthly Summary (SQL View)")
            print("9. Exit")
            
            choice = input("Select option (1-9): ")
            if choice == '1': self.insert_user()
            elif choice == '2': self.select_inventory()
            elif choice == '3': self.update_stock()
            elif choice == '4': self.delete_order()
            elif choice == '5': self.view_audit_logs()
            elif choice == '6': self.place_order()
            elif choice == '7': self.run_analytics_reports()
            elif choice == '8': self.view_monthly_summary()
            elif choice == '9':
                print("\n[INFO] Exiting E-Commerce Analytics Engine. Goodbye!")
                self.db_mgr.close()
                break

if __name__ == "__main__":
    app = ECommerceCLI()
    app.run()