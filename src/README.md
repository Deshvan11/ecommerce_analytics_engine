# Source Code Guide

This document explains the Python modules in `src/`: `main.py`, `data_loader.py`, and `db_config.py`. The application is a command-line e-commerce analytics engine backed by SQLite. It creates and manages customer, product, order, order-detail, and audit-log data.

## Running the Application

Run the application from the repository root so its relative `sql/` and `data/` paths resolve correctly:

```bash
python -m src.main
```

At startup, the program creates the database schema and views, then imports the customer and product CSV files. It then displays an interactive menu.

## `main.py`

This module provides the command-line interface and coordinates database setup, data loading, order operations, and analytics.

### Imports

- `import os`: builds paths to SQL files and checks whether the analytics SQL file exists.
- `import sqlite3`: opens a separate SQLite connection when a failed order needs to be written to the audit log independently of the order transaction.
- `from datetime import datetime`: creates the current date and timestamps for customer signups and orders.
- `from src.db_config import DatabaseManager`: imports the class that owns the SQLite connection and executes SQL scripts.
- `from src.data_loader import DataLoader`: imports the class that loads CSV data into the database.

### `ECommerceCLI`

The class is the application's interactive interface. Its methods use `self.db_mgr` to access the shared database connection.

#### `__init__(self)`

```python
def __init__(self):
	self.db_mgr = DatabaseManager()
	self.db_mgr.connect()
```

1. `self.db_mgr = DatabaseManager()` creates a database manager with its default database path, `ecommerce.db`.
2. `self.db_mgr.connect()` opens the SQLite database and enables foreign-key enforcement for that connection.

#### `initialize_system(self)`

```python
def initialize_system(self):
	print("\n[INFO] Setting up database schema, indexes, and views...")
	self.db_mgr.execute_script(os.path.join("sql", "schema.sql"))
	self.db_mgr.execute_script(os.path.join("sql", "procedures_and_views.sql"))

	loader = DataLoader(self.db_mgr)
	loader.load_all_data()
```

1. Prints a message that schema, indexes, and views are being set up.
2. `os.path.join("sql", "schema.sql")` builds the path to the schema script using the operating system's path separator.
3. `self.db_mgr.execute_script(...)` executes that script. The schema defines tables and indexes, creating them only if they do not already exist.
4. The next `execute_script` call runs `sql/procedures_and_views.sql`, which defines the database views and other SQL objects in that file.
5. `DataLoader(self.db_mgr)` creates a loader that uses this same database manager and connection.
6. `loader.load_all_data()` imports the customer and product CSV records, if the files are present.

#### `_ensure_connection(self)`

```python
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
```

This private helper attempts to make sure the manager has a usable connection before a menu operation uses it.

1. `try:` begins a block where connection checks can fail.
2. `if not self.db_mgr.connection:` checks whether the manager currently has a connection object; if not, it calls `connect()` to open one.
3. Otherwise, `self.db_mgr.connection.cursor()` attempts to create a cursor as a basic check that the connection can still be used.
4. `except Exception:` catches an error from either check.
5. `self.db_mgr.connect()` opens a new connection after an error.

#### `insert_user(self)`

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

1. Calls `_ensure_connection()` before accessing SQLite.
2. Stores the manager's connection in the local variable `conn`.
3. Creates a cursor, which is used to execute SQL statements.
4. Prompts the operator for a customer name.
5. Prompts for the customer's email address.
6. Prompts for the customer's city.
7. Formats the current date as `YYYY-MM-DD` for the signup date.
8. Executes a parameterized `INSERT` into `Customers`. The `?` placeholders keep entered values separate from the SQL text.
9. Executes a second parameterized `INSERT` into `AuditLogs`, recording the `INSERT_USER` action and the customer's name in the message.
10. `conn.commit()` saves both inserts as one committed unit.
11. Prints a success message.

#### `select_inventory(self)`

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

1. Ensures the database connection is available.
2. Gets the connection and creates a cursor.
3. Selects the product ID, name, category, price, and stock quantity for every row in `Products`.
4. `fetchall()` retrieves all selected rows; the `for` loop processes them one at a time.
5. The formatted print statement displays each product's fields, including a dollar sign before its price.
6. Inserts an audit record with the action `SELECT_INVENTORY` and the message `Queried inventory`.
7. Commits the audit record. The inventory query itself does not modify product rows.

#### `update_stock(self)`

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

1. Ensures the connection is available.
2. Gets the connection and creates a cursor.
3. Prompts for the product ID to update.
4. Prompts for the new stock quantity and converts the input to an integer.
5. Updates `Products.stock_qty` for the row whose `product_id` matches. The values are passed through placeholders.
6. Writes an `UPDATE_STOCK` audit record containing the product ID and requested quantity.
7. Commits the stock update and audit record.
8. Prints a success message. If the ID does not match a product, SQLite updates zero product rows; this method does not separately check that case.

#### `delete_order(self)`

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

1. Ensures the connection is available.
2. Gets the connection and creates a cursor.
3. Prompts for the order ID to delete.
4. Starts an explicit SQLite transaction.
5. Deletes the order's `OrderDetails` rows first, avoiding a foreign-key conflict with the detail-to-order relationship.
6. Deletes the matching row from `Orders`.
7. Inserts a `DELETE_ORDER` audit record with the order ID in its message.
8. Commits the deletions and audit record together.
9. Prints a success message. It does not check whether an order with the entered ID existed.

#### `view_audit_logs(self)`

```python
def view_audit_logs(self):
	self._ensure_connection()
	conn = self.db_mgr.connection
	cursor = conn.cursor()
	cursor.execute("SELECT log_id, action, executed_at, status_message FROM AuditLogs;")
	for r in cursor.fetchall():
		print(f"Log ID: {r[0]} | {r[1]} | {r[2]} | {r[3]}")
```

1. Ensures the connection is available.
2. Gets the connection and creates a cursor.
3. Selects each audit log's ID, action, timestamp, and status message.
4. Retrieves all result rows and loops over them.
5. Prints the four selected values for each log. This method only reads data and does not commit a change.

#### `_log_audit_independent(self, action, message)`

```python
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
```

This private helper writes an audit record through a temporary connection, so a rollback on the main connection does not erase the failure record.

1. The docstring summarizes why the helper uses a separate connection.
2. `try:` begins error handling for the independent write.
3. `sqlite3.connect(self.db_mgr.db_path)` opens another connection to the same database file.
4. Creates a cursor for the temporary connection.
5. Inserts the supplied `action` and `message` into `AuditLogs` using placeholders.
6. Commits the audit insert on the temporary connection.
7. Closes the temporary connection after a successful write.
8. If an exception occurs, the `except` block catches it as `e`.
9. Prints a debug message containing the exception. The exception is not re-raised, so audit logging failure does not replace the original order result.

#### `place_order(self)`

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

This method checks inventory and creates an order, its detail row, and an audit row in one transaction. It rolls back the main transaction if a check or SQL operation fails.

1. Ensures the connection is available.
2. Gets the connection and creates a cursor.
3. Prompts for the customer ID.
4. Prompts for the product ID.
5. Prompts for the quantity and converts it to an integer. These prompts and the conversion happen before the `try` block.
6. `try:` begins exception handling for the database transaction.
7. Starts an explicit transaction on the connection.
8. Selects the product price and available stock for the requested product ID.
9. `fetchone()` returns the matching product row, or `None` if no product matched.
10. `if not prod:` handles the missing-product case.
11. Rolls back the transaction because the order cannot be completed.
12. Writes a `FAILED_ORDER` audit record using the independent connection, which survives the rollback.
13. Prints an error explaining that the product was not found.
14. `return` exits the method without continuing to create an order.
15. `if prod[1] < qty:` compares available stock (`prod[1]`) with the requested quantity.
16. Rolls back when there is insufficient stock.
17. Independently logs the product ID, requested quantity, and available quantity as a `FAILED_ORDER` action.
18. Prints the insufficient-stock message.
19. Returns without creating an order.
20. `subtotal = prod[0] * qty` calculates the line total using the product price (`prod[0]`) and requested quantity.
21. Formats the current date and time as `YYYY-MM-DD HH:MM:SS` for the order date.
22. Decreases the product's stock by the requested quantity.
23. Inserts an `Orders` row with the customer ID, timestamp, total amount, and `Completed` status.
24. `cursor.lastrowid` captures the ID generated for the new order.
25. Inserts an `OrderDetails` row that links the new order to the product and records quantity, unit price, and subtotal.
26. Inserts a `PLACE_ORDER` audit record containing the generated order ID.
27. Commits the stock change, order, detail, and audit record together.
28. Prints a success message containing the new order ID.
29. `except Exception as e:` catches database or other exceptions raised inside the `try` block.
30. `conn.rollback()` undoes any uncommitted changes in the main transaction.
31. Writes a `FAILED_ORDER_ERROR` audit record independently, including the exception text.
32. Prints the transaction error. The exception is handled here rather than re-raised.

#### `run_analytics_reports(self)`

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

1. Ensures the connection is available.
2. Builds the relative path to `sql/analytics_queries.sql`.
3. Checks whether the file exists.
4. If it is missing, prints an error and returns without running anything.
5. Opens the file in read mode using UTF-8 encoding.
6. Reads the full SQL script into `script_sql`.
7. Gets the connection and creates a cursor.
8. Prints a heading before running the reports.
9. `try:` begins error handling for the analytics SQL execution.
10. Splits the script at semicolons to get individual SQL statements.
11. Enumerates those statements starting at 1, providing both an index and the statement text.
12. Strips whitespace from the current statement.
13. Skips empty segments, such as the one that may follow a final semicolon.
14. Prints the query number before executing a nonempty statement.
15. Executes the statement with the cursor.
16. Calls `fetchall()` to retrieve its result rows.
17. If rows exist, loops through them.
18. Prints each row in SQLite's tuple representation.
19. If no rows exist, prints a message saying the query returned zero rows. This message can also occur for statements that do not produce result rows.
20. Commits after the full loop completes.
21. If execution raises an exception, prints the failure message. This handler does not explicitly roll back the connection.

#### `view_monthly_summary(self)`

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

1. Ensures the connection is available.
2. Gets the connection and creates a cursor.
3. Prints a heading for the monthly report.
4. Selects all columns from the `vw_monthly_summary` SQL view.
5. Retrieves all rows from the view.
6. If there are no rows, prints a hint that completed orders are needed to populate the summary.
7. Otherwise, loops through each monthly summary row.
8. Prints the month, order count, active buyer count, and revenue. Revenue is displayed with two digits after the decimal point.

#### `run(self)`

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

1. Calls `initialize_system()` once before displaying the menu.
2. `while True:` repeats the menu until the user selects Exit.
3. Prints the application title.
4. Prints menu option 1, for inserting a customer.
5. Prints menu option 2, for viewing inventory.
6. Prints menu option 3, for updating product stock.
7. Prints menu option 4, for deleting an order.
8. Prints menu option 5, for viewing audit logs.
9. Prints menu option 6, for placing an order.
10. Prints menu option 7, for running the analytics SQL queries.
11. Prints menu option 8, for viewing the monthly summary.
12. Prints menu option 9, for exiting.
13. Prompts for a menu choice and stores the input as text in `choice`.
14. If the choice is `'1'`, calls `insert_user()`.
15. If the choice is `'2'`, calls `select_inventory()`.
16. If the choice is `'3'`, calls `update_stock()`.
17. If the choice is `'4'`, calls `delete_order()`.
18. If the choice is `'5'`, calls `view_audit_logs()`.
19. If the choice is `'6'`, calls `place_order()`.
20. If the choice is `'7'`, calls `run_analytics_reports()`.
21. If the choice is `'8'`, calls `view_monthly_summary()`.
22. If the choice is `'9'`, begins the exit branch.
23. Prints the goodbye message.
24. Closes the database connection through the manager.
25. `break` leaves the menu loop. Inputs other than `'1'` through `'9'` have no explicit response; the loop displays the menu again.

### Module Entry Point

```python
if __name__ == "__main__":
	app = ECommerceCLI()
	app.run()
```

1. `if __name__ == "__main__":` checks whether Python is running this file as the program entry point rather than importing it as a module.
2. `app = ECommerceCLI()` creates the application and opens its database connection.
3. `app.run()` initializes the schema and data, then starts the interactive menu.

## `data_loader.py`

This module reads customer and product CSV files and inserts their data into the corresponding SQLite tables.

### Imports

- `import csv`: reads CSV files and maps column headers to values.
- `import os`: joins the data directory with each CSV filename and checks whether each file exists.
- `from src.db_config import DatabaseManager`: imports the database-manager type used by the constructor's annotation.

### `DataLoader`

#### `__init__(self, db_manager: DatabaseManager, data_dir="data")`

```python
def __init__(self, db_manager: DatabaseManager, data_dir="data"):
	self.db_manager = db_manager
	self.data_dir = data_dir
```

1. `db_manager` is the manager whose open connection will receive the imported rows.
2. `data_dir` defaults to the relative directory `data`; callers can supply another directory.
3. `self.db_manager = db_manager` stores the supplied manager on the loader.
4. `self.data_dir = data_dir` stores the directory containing the input CSV files.

#### `load_all_data(self)`

```python
def load_all_data(self):
	conn = self.db_manager.connection
	cursor = conn.cursor()

	# Load Customers
	cust_path = os.path.join(self.data_dir, "customers.csv")
	if os.path.exists(cust_path):
		with open(cust_path, "r", encoding="utf-8") as f:
			reader = csv.DictReader(f)
			rows = [(r['customer_id'], r['name'], r['email'], r['city'], r['signup_date']) for r in reader]
			cursor.executemany("""
				INSERT OR IGNORE INTO Customers (customer_id, name, email, city, signup_date)
				VALUES (?, ?, ?, ?, ?);
			""", rows)
		print("[INFO] Customers feed loaded.")

	# Load Products
	prod_path = os.path.join(self.data_dir, "products.csv")
	if os.path.exists(prod_path):
		with open(prod_path, "r", encoding="utf-8") as f:
			reader = csv.DictReader(f)
			rows = [(r['product_id'], r['product_name'], r['category'], float(r['price']), int(r['stock_qty'])) for r in reader]
			cursor.executemany("""
				INSERT OR IGNORE INTO Products (product_id, product_name, category, price, stock_qty)
				VALUES (?, ?, ?, ?, ?);
			""", rows)
		print("[INFO] Products feed loaded.")

	conn.commit()
```

1. Reads the manager's current connection into `conn`. The connection is expected to have been opened before this method is called.
2. Creates a cursor for executing inserts.
3. The `# Load Customers` comment marks the customer import section.
4. Joins `self.data_dir` and `customers.csv` to create the customer-file path.
5. Checks whether that path exists. If it does not, the customer import block is skipped.
6. Opens the customer CSV for reading with UTF-8 encoding.
7. `csv.DictReader(f)` reads each row as a dictionary keyed by the CSV header names.
8. Builds a list of tuples containing `customer_id`, `name`, `email`, `city`, and `signup_date`, in the order expected by the SQL placeholders.
9. `cursor.executemany(...)` runs the same insert statement once for each tuple.
10. `INSERT OR IGNORE` inserts customers that can be inserted and skips rows that violate SQLite constraints, including duplicate primary keys or unique values.
11. Prints a message after the customer feed has been processed. This message is printed whenever the file exists, even if it contains no data rows.
12. The `# Load Products` comment marks the product import section.
13. Joins `self.data_dir` and `products.csv` to create the product-file path.
14. Checks whether the product file exists. If it does not, the product import block is skipped.
15. Opens the product CSV for reading with UTF-8 encoding.
16. Creates a `DictReader` so values can be accessed by their header names.
17. Builds product tuples from `product_id`, `product_name`, `category`, `price`, and `stock_qty`. Price is converted to `float`, and stock quantity is converted to `int` before insertion.
18. `executemany(...)` inserts each product tuple into `Products`.
19. The product insert also uses `INSERT OR IGNORE`, so rows rejected by SQLite constraints are skipped rather than replacing existing records.
20. Prints a message after the product feed has been processed, provided the file exists.
21. `conn.commit()` commits all successful customer and product inserts made by this call.

The CSV headers must match the field names used by the loader. Missing files are silently skipped; malformed rows, missing required headers, or values that cannot be converted to `float` or `int` can raise errors.

## `db_config.py`

This module wraps the basic SQLite connection lifecycle and script execution in a reusable class.

### Imports

- `import sqlite3`: provides Python's built-in SQLite driver.
- `import os`: imported in this module but not currently used by its methods.

### `DatabaseManager`

#### `__init__(self, db_path="ecommerce.db")`

```python
def __init__(self, db_path="ecommerce.db"):
	self.db_path = db_path
	self.connection = None
```

1. `db_path` is the database filename or path; it defaults to `ecommerce.db` in the current working directory.
2. `self.db_path = db_path` stores the path for connection creation and independent audit logging.
3. `self.connection = None` initializes the connection field to indicate that no connection has been opened yet.

#### `connect(self)`

```python
def connect(self):
	self.connection = sqlite3.connect(self.db_path)
	self.connection.execute("PRAGMA foreign_keys = ON;")
	return self.connection
```

1. `sqlite3.connect(self.db_path)` opens a connection to the configured SQLite database. SQLite creates the database file if it does not exist.
2. `PRAGMA foreign_keys = ON` enables foreign-key checks for this connection.
3. `return self.connection` returns the live connection so the caller can use it directly if needed.

#### `execute_script(self, script_path)`

```python
def execute_script(self, script_path):
	if not self.connection:
		self.connect()
	with open(script_path, 'r', encoding='utf-8') as f:
		script_sql = f.read()
	cursor = self.connection.cursor()
	cursor.executescript(script_sql)
	self.connection.commit()
```

1. `if not self.connection:` checks whether a connection is stored; `connect()` opens one if needed.
2. Opens the SQL file at `script_path` in text read mode using UTF-8 encoding.
3. Reads the entire SQL file into `script_sql`.
4. Creates a cursor from the manager's connection.
5. `cursor.executescript(script_sql)` executes the SQL script, which may contain multiple statements.
6. `self.connection.commit()` commits the script's changes.

#### `close(self)`

```python
def close(self):
	if self.connection:
		self.connection.close()
```

1. Checks whether a connection object is stored.
2. If so, closes it and releases its database resources. The attribute is not reset to `None`; callers should not use that stored connection after closing it.

## How the Modules Work Together

1. `main.py` constructs `DatabaseManager`, which opens `ecommerce.db`.
2. `ECommerceCLI.initialize_system()` uses the manager to execute the schema and view scripts.
3. `DataLoader` uses the same manager connection to import CSV records.
4. The CLI methods query or update the same database and write audit records for key operations.
5. `DatabaseManager.close()` closes the connection when the operator exits through menu option 9.

The SQL scripts and CSV files are addressed with paths relative to the process's current working directory. Starting the program from the repository root keeps those paths aligned with the project layout.