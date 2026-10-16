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

1. `self.db_mgr = DatabaseManager()` creates a database manager with its default database path, `ecommerce.db`.
2. `self.db_mgr.connect()` opens the SQLite database and enables foreign-key enforcement for that connection.

#### `initialize_system(self)`

1. Prints a message that schema, indexes, and views are being set up.
2. `os.path.join("sql", "schema.sql")` builds the path to the schema script using the operating system's path separator.
3. `self.db_mgr.execute_script(...)` executes that script. The schema defines tables and indexes, creating them only if they do not already exist.
4. The next `execute_script` call runs `sql/procedures_and_views.sql`, which defines the database views and other SQL objects in that file.
5. `DataLoader(self.db_mgr)` creates a loader that uses this same database manager and connection.
6. `loader.load_all_data()` imports the customer and product CSV records, if the files are present.

#### `_ensure_connection(self)`

This private helper attempts to make sure the manager has a usable connection before a menu operation uses it.

1. `try:` begins a block where connection checks can fail.
2. `if not self.db_mgr.connection:` checks whether the manager currently has a connection object; if not, it calls `connect()` to open one.
3. Otherwise, `self.db_mgr.connection.cursor()` attempts to create a cursor as a basic check that the connection can still be used.
4. `except Exception:` catches an error from either check.
5. `self.db_mgr.connect()` opens a new connection after an error.

#### `insert_user(self)`

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

1. Ensures the database connection is available.
2. Gets the connection and creates a cursor.
3. Selects the product ID, name, category, price, and stock quantity for every row in `Products`.
4. `fetchall()` retrieves all selected rows; the `for` loop processes them one at a time.
5. The formatted print statement displays each product's fields, including a dollar sign before its price.
6. Inserts an audit record with the action `SELECT_INVENTORY` and the message `Queried inventory`.
7. Commits the audit record. The inventory query itself does not modify product rows.

#### `update_stock(self)`

1. Ensures the connection is available.
2. Gets the connection and creates a cursor.
3. Prompts for the product ID to update.
4. Prompts for the new stock quantity and converts the input to an integer.
5. Updates `Products.stock_qty` for the row whose `product_id` matches. The values are passed through placeholders.
6. Writes an `UPDATE_STOCK` audit record containing the product ID and requested quantity.
7. Commits the stock update and audit record.
8. Prints a success message. If the ID does not match a product, SQLite updates zero product rows; this method does not separately check that case.

#### `delete_order(self)`

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

1. Ensures the connection is available.
2. Gets the connection and creates a cursor.
3. Selects each audit log's ID, action, timestamp, and status message.
4. Retrieves all result rows and loops over them.
5. Prints the four selected values for each log. This method only reads data and does not commit a change.

#### `_log_audit_independent(self, action, message)`

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

1. Ensures the connection is available.
2. Gets the connection and creates a cursor.
3. Prints a heading for the monthly report.
4. Selects all columns from the `vw_monthly_summary` SQL view.
5. Retrieves all rows from the view.
6. If there are no rows, prints a hint that completed orders are needed to populate the summary.
7. Otherwise, loops through each monthly summary row.
8. Prints the month, order count, active buyer count, and revenue. Revenue is displayed with two digits after the decimal point.

#### `run(self)`

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

1. `db_manager` is the manager whose open connection will receive the imported rows.
2. `data_dir` defaults to the relative directory `data`; callers can supply another directory.
3. `self.db_manager = db_manager` stores the supplied manager on the loader.
4. `self.data_dir = data_dir` stores the directory containing the input CSV files.

#### `load_all_data(self)`

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

1. `db_path` is the database filename or path; it defaults to `ecommerce.db` in the current working directory.
2. `self.db_path = db_path` stores the path for connection creation and independent audit logging.
3. `self.connection = None` initializes the connection field to indicate that no connection has been opened yet.

#### `connect(self)`

1. `sqlite3.connect(self.db_path)` opens a connection to the configured SQLite database. SQLite creates the database file if it does not exist.
2. `PRAGMA foreign_keys = ON` enables foreign-key checks for this connection.
3. `return self.connection` returns the live connection so the caller can use it directly if needed.

#### `execute_script(self, script_path)`

1. `if not self.connection:` checks whether a connection is stored; `connect()` opens one if needed.
2. Opens the SQL file at `script_path` in text read mode using UTF-8 encoding.
3. Reads the entire SQL file into `script_sql`.
4. Creates a cursor from the manager's connection.
5. `cursor.executescript(script_sql)` executes the SQL script, which may contain multiple statements.
6. `self.connection.commit()` commits the script's changes.

#### `close(self)`

1. Checks whether a connection object is stored.
2. If so, closes it and releases its database resources. The attribute is not reset to `None`; callers should not use that stored connection after closing it.

## How the Modules Work Together

1. `main.py` constructs `DatabaseManager`, which opens `ecommerce.db`.
2. `ECommerceCLI.initialize_system()` uses the manager to execute the schema and view scripts.
3. `DataLoader` uses the same manager connection to import CSV records.
4. The CLI methods query or update the same database and write audit records for key operations.
5. `DatabaseManager.close()` closes the connection when the operator exits through menu option 9.

The SQL scripts and CSV files are addressed with paths relative to the process's current working directory. Starting the program from the repository root keeps those paths aligned with the project layout.