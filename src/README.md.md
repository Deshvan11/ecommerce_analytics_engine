# Technical Breakdown of the `ECommerceCLI` Class

Here is an exhaustive, line-by-line technical breakdown of every method inside the `ECommerceCLI` class in `src/main.py`.

## 1. `__init__(self)`

```python
def __init__(self):
    self.db_mgr = DatabaseManager()

    self.db_mgr.connect()

```

- Line 2: Instantiates a new DatabaseManager object, setting up the configuration and file path handle for ecommerce.db.

- Line 3: Invokes the database manager's connect() method to establish an active SQLite session and enforce foreign key pragma rules immediately upon class instantiation.

## 2. `initialize_system(self)`

```python
def initialize_system(self):
    print("\n[INFO] Setting up database schema, indexes, and views...")

    self.db_mgr.execute_script(os.path.join("sql", "schema.sql"))

    self.db_mgr.execute_script(os.path.join("sql", "procedures_and_views.sql"))

    loader = DataLoader(self.db_mgr)

    loader.load_all_data()

```

- Line 2: Prints an informational console message indicating that system setup has started.

- Line 3: Builds the database architecture by reading and executing DDL statements, table creations, constraints, and performance indexes from sql/schema.sql.

- Line 4: Executes stored procedures, DCL reference comments, and analytical SQL views from sql/procedures_and_views.sql.

- Line 6: Instantiates the DataLoader object, passing the active database manager instance.

- Line 7: Triggers load_all_data() to ingest seed records from customers.csv and products.csv into their respective tables.

## 3. `_ensure_connection(self)`

```python
def _ensure_connection(self):
    try:

        if not self.db_mgr.connection:

            self.db_mgr.connect()

        else:

            self.db_mgr.connection.cursor()

    except Exception:

        self.db_mgr.connect()

```

- Line 2: Wraps connection health-checks in a try-except block to gracefully recover from dropped or closed connections.

- Line 3-4: Checks if the connection reference is None or empty; if so, triggers self.db_mgr.connect() to open a fresh session.

- Line 5-6: If a connection object exists, attempts to pull a cursor from it to test its live state.

- Line 7-8: Catches any exception (such as operating on a closed database) and forces a reconnection via self.db_mgr.connect().

## 4. `insert_user(self)`

```python
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

```

- Line 2: Ensures the database connection is alive and ready.

- Line 3: Retrieves the active SQLite connection reference.

- Line 4: Creates a database cursor for executing SQL commands.

- Lines 5-7: Prompts the user via CLI to input string values for customer name, email address, and city.

- Line 8: Generates the current system date formatted as YYYY-MM-DD to record the signup timestamp.

- Line 10: Executes a parameterized INSERT statement into the Customers table to prevent SQL injection vulnerabilities.

- Line 11: Executes a secondary statement inserting an INSERT_USER action entry into the AuditLogs table.

- Line 12: Commits the transaction changes permanently to disk.

- Line 13: Prints a success notification to the terminal.

## 5. `select_inventory(self)`

```python
def select_inventory(self):
    self._ensure_connection()

    conn = self.db_mgr.connection

    cursor = conn.cursor()

    cursor.execute("SELECT product_id, product_name, category, price, stock_qty FROM Products;")

    for r in cursor.fetchall():

        print(f"ID: {r[0]} | {r[1]} | {r[2]} | ${r[3]} | Stock: {r[4]}")

    cursor.execute("INSERT INTO AuditLogs (action, status_message) VALUES ('SELECT_INVENTORY', 'Queried inventory');")

    conn.commit()

```

- Line 2: Validates and refreshes the database connection state.

- Line 3-4: Acquires the active connection and initializes a cursor.

- Line 5: Executes a SELECT query pulling product IDs, names, categories, prices, and stock quantities from the catalog.

- Line 6-7: Iterates through all fetched rows and prints a formatted text summary for each product to the terminal.

- Line 8: Writes an audit log tracking event (SELECT_INVENTORY) into AuditLogs.

- Line 9: Commits the audit transaction.

## 6. `update_stock(self)`

```python
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

```

- Line 2: Ensures connection health.

- Line 3-4: Pulls connection and cursor instances.

- Lines 5-6: Prompts the user to specify a target product ID and casts the entered stock quantity into an integer.

- Line 7: Executes a parameterized UPDATE statement modifying the product's stock balance.

- Line 8: Inserts an audit log entry (UPDATE_STOCK) capturing the inventory adjustment details.

- Line 9: Commits the changes to the database.

- Line 10: Prints a success message to the console.

## 7. `delete_order(self)`

```python
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

```

- Line 2: Ensures connection health.

- Line 3-4: Pulls connection and cursor instances.

- Line 5: Prompts the user to specify the target Order ID intended for deletion.

- Line 6: Explicitly begins an atomic transaction block.

- Line 7: Deletes child dependency rows from the OrderDetails table first to respect foreign key rules.

- Line 8: Deletes the parent record from the Orders table.

- Line 9: Inserts a DELETE_ORDER tracking record into the AuditLogs table.

- Line 10: Commits the transaction block.

- Line 11: Prints a success confirmation.

## 8. `view_audit_logs(self)`

```python
def view_audit_logs(self):
    self._ensure_connection()

    conn = self.db_mgr.connection

    cursor = conn.cursor()

    cursor.execute("SELECT log_id, action, executed_at, status_message FROM AuditLogs;")

    for r in cursor.fetchall():

        print(f"Log ID: {r[0]} | {r[1]} | {r[2]} | {r[3]}")

```

- Line 2: Ensures connection health.

- Line 3-4: Acquires connection and cursor handles.

- Line 5: Queries all historical audit metrics (log_id, action, executed_at, status_message) from the AuditLogs table.

- Line 6-7: Iterates over the result set and prints structured log entries to the terminal screen.

## 9. `_log_audit_independent(self, action, message)`

```python
def _log_audit_independent(self, action, message):
    try:

        temp_conn = sqlite3.connect(self.db_mgr.db_path)

        temp_cursor = temp_conn.cursor()

        temp_cursor.execute("INSERT INTO AuditLogs (action, status_message) VALUES (?, ?);", (action, message))

        temp_conn.commit()

        temp_conn.close()

    except Exception as e:

        print(f"[DEBUG] Independent audit logging failed: {e}")

```

- Line 2: Opens a protected execution block to catch logging exceptions.

- Line 3: Opens a completely separate, isolated SQLite connection file pointer specifically pointing to ecommerce.db.

- Line 4: Initializes a cursor on this temporary connection.

- Line 5: Executes an independent INSERT statement into AuditLogs for failure logging.

- Line 6: Commits the isolated log entry immediately.

- Line 7: Closes the temporary connection safely without affecting the main application's session state.

- Line 8-9: Catches and prints any unexpected logging exception to debug channels without crashing the app.

## 10. `place_order(self)`

```python
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

```

- Line 2: Ensures connection health.

- Line 3-4: Acquires connection and cursor instances.

- Lines 5-7: Prompts the user for Customer ID, Product ID, and requested Quantity (parsed as an integer).

- Line 9: Enters a try block to monitor atomic execution safety.

- Line 10: Explicitly starts an ACID transaction block (BEGIN TRANSACTION;).

- Line 11: Queries the unit price and available stock for the target product ID.

- Line 12: Fetches the result tuple.

- Line 14-19: Validates if the product exists; if missing, triggers conn.rollback(), logs the failure via _log_audit_independent, prints an error, and terminates execution.

- Line 21-26: Validates stock sufficiency; if requested quantity exceeds inventory, triggers conn.rollback(), logs the stock deficiency, prints an error, and exits.

- Line 28: Computes the row line-item subtotal (price multiplied by quantity).

- Line 29: Generates a timestamp string for order placement.

- Line 31: Updates the product inventory by decrementing the purchased quantity.

- Line 32: Inserts the primary order header record into the Orders table.

- Line 33: Captures the newly generated auto-increment primary key ID (cursor.lastrowid).

- Line 34: Inserts the granular line-item record into the OrderDetails table linking order, product, and quantity.

- Line 36: Writes a success tracking event (PLACE_ORDER) into the AuditLogs table.

- Line 38: Commits all transactional changes together.

- Line 39: Prints a success notice.

- Line 40-43: Catches any general runtime exceptions, rolls back the transaction, invokes independent error logging, and outputs the exception message.

## 11. `run_analytics_reports(self)`

```python
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

```

- Line 2: Ensures connection health.

- Line 3: Resolves the relative file path for sql/analytics_queries.sql.

- Line 4-6: Verifies file existence; if missing, prints an error and returns.

- Line 8-9: Opens and reads the raw text contents of the SQL file.

- Line 11-12: Acquires active connection and cursor handles.

- Line 14: Prints header info for terminal reporting.

- Line 15: Enters a try block for batch SQL execution.

- Line 16: Splits the script text script by semicolons (;) into individual query strings.

- Line 17: Loops through each statement with an enumerated index tracker.

- Line 18: Strips trailing whitespaces or line breaks from the statement string.

- Line 19-27: Checks if the statement contains content; if valid, prints the query index, executes the statement, fetches all result rows, and prints each returned row tuple to the console.

- Line 28: Commits the query execution session.

- Line 29-31: Catches and prints any SQL syntax or runtime execution exceptions.

## 12. `view_monthly_summary(self)`

```python
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

```

- Line 2: Ensures connection health.

- Line 3-4: Pulls connection and cursor references.

- Line 6: Prints report headers.

- Line 7: Executes a SELECT query against the pre-compiled SQL view vw_monthly_summary.

- Line 8: Fetches all resulting aggregation rows.

- Line 9-13: Checks if the view data is empty; if so, displays a helpful hint message, otherwise iterates through the rows and outputs formatted monthly metrics (Month, Orders, Active Buyers, Revenue).

## 13. `run(self)`

```python
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

```

- Line 2: Boots up the system schema, views, and data loader pipelines by calling initialize_system().

- Line 3: Enters an infinite REPL loop (while True) to keep the CLI application running.

- Lines 4-13: Prints the structured 9-option interactive control menu to the terminal window.

- Line 15: Captures string input from the user.

- Lines 16-24: Evaluates the user's numeric choice using if/elif branching and routes execution directly to the corresponding handler method.

- Lines 25-28: Handles exit execution (Option 9) by printing a goodbye message, closing the primary database handle via self.db_mgr.close(), and breaking out of the loop to terminate the application.
