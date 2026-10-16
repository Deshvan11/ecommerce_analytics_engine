# SQL Scripts Guide

This folder contains the SQL used by the e-commerce analytics engine. The scripts define the SQLite schema, create the monthly summary view, and provide example filtering, aggregation, join, CTE, and window-function queries.

Run the application from the repository root so the paths to this folder resolve:

```bash
python -m src.main
```

During startup, `main.py` executes `schema.sql` and `procedures_and_views.sql`. The CLI reads `analytics_queries.sql` only when menu option 7 is selected.

## `schema.sql`

This script enables foreign-key checking, creates the application's tables, and adds indexes used to speed up common lookups.

```sql
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS Customers (
    customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    city VARCHAR(100) NOT NULL,
    signup_date DATETIME NOT NULL
);

CREATE TABLE IF NOT EXISTS Products (
    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_name VARCHAR(150) NOT NULL,
    category VARCHAR(100) NOT NULL,
    price DECIMAL(10,2) CHECK (price > 0) NOT NULL,
    stock_qty INTEGER CHECK (stock_qty >= 0) NOT NULL
);

CREATE TABLE IF NOT EXISTS Orders (
    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    order_date DATETIME NOT NULL,
    total_amount DECIMAL(12,2) NOT NULL,
    status VARCHAR(50) DEFAULT 'Completed',
    FOREIGN KEY (customer_id) REFERENCES Customers(customer_id)
);

CREATE TABLE IF NOT EXISTS OrderDetails (
    detail_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER CHECK (quantity > 0) NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    subtotal DECIMAL(12,2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES Orders(order_id),
    FOREIGN KEY (product_id) REFERENCES Products(product_id)
);

CREATE TABLE IF NOT EXISTS AuditLogs (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    action VARCHAR(255) NOT NULL,
    executed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    status_message TEXT NOT NULL
);

-- Performance Indexes
CREATE INDEX IF NOT EXISTS idx_orders_customer ON Orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_products_cat ON Products(category);
```

### Schema Statements

- `PRAGMA foreign_keys = ON;` enables SQLite foreign-key enforcement on the connection executing this statement. The Python database manager also enables it when opening its connection.
- `CREATE TABLE IF NOT EXISTS` creates a table only when it does not already exist. It does not update an existing table if the schema later changes.
- `INTEGER PRIMARY KEY AUTOINCREMENT` makes the column the row identifier and asks SQLite to assign a new increasing ID when an insert omits it.
- `NOT NULL` prohibits a row from omitting a required value.
- `UNIQUE` prevents duplicate values in that column; here it ensures customer emails are unique.
- `CHECK (price > 0)` permits only positive product prices.
- `CHECK (stock_qty >= 0)` prevents product stock from becoming negative.
- `CHECK (quantity > 0)` requires order-detail quantities to be positive.
- `DEFAULT 'Completed'` supplies the order status when an insert does not specify one.
- `DEFAULT CURRENT_TIMESTAMP` records SQLite's current timestamp if an audit row does not provide `executed_at`.
- Each `FOREIGN KEY` links a child row to a parent row: orders to customers, and order details to both orders and products. With foreign keys enabled, a referenced parent must exist.
- `CREATE INDEX IF NOT EXISTS idx_orders_customer ON Orders(customer_id);` creates an index for customer-based order lookups.
- `CREATE INDEX IF NOT EXISTS idx_products_cat ON Products(category);` creates an index for product category filtering.

### Tables and Columns

**`Customers`** stores customer identity and signup information:

- `customer_id`: automatically assigned primary key.
- `name`: required customer name, up to 100 characters by declaration.
- `email`: required unique email, up to 150 characters by declaration.
- `city`: required customer city.
- `signup_date`: required signup date or timestamp.

**`Products`** stores the inventory catalog:

- `product_id`: automatically assigned primary key.
- `product_name`: required product name.
- `category`: required product category.
- `price`: required positive price.
- `stock_qty`: required nonnegative inventory count.

**`Orders`** stores one row per order:

- `order_id`: automatically assigned primary key.
- `customer_id`: required reference to a customer.
- `order_date`: required date and time of the order.
- `total_amount`: required order total.
- `status`: order status, defaulting to `Completed`.

**`OrderDetails`** stores the product line or lines belonging to an order:

- `detail_id`: automatically assigned primary key.
- `order_id`: required reference to the parent order.
- `product_id`: required reference to a product.
- `quantity`: required positive number of units.
- `unit_price`: required price for one unit at the time of the order.
- `subtotal`: required line total.

**`AuditLogs`** records application actions:

- `log_id`: automatically assigned primary key.
- `action`: required action name, such as `PLACE_ORDER`.
- `executed_at`: timestamp supplied automatically when omitted.
- `status_message`: required description of the action or result.

SQLite uses type affinity rather than enforcing declared types exactly as some database servers do. Declarations such as `VARCHAR(100)` and `DECIMAL(10,2)` document the intended data but do not by themselves guarantee a maximum text length or fixed decimal precision in SQLite.

## `procedures_and_views.sql`

Despite the filename, this SQLite script currently creates a view; it does not define a stored procedure.

```sql
-- Analytical View: Monthly Summary
CREATE VIEW IF NOT EXISTS vw_monthly_summary AS
SELECT
    strftime('%Y-%m', o.order_date) AS order_month,
    COUNT(DISTINCT o.order_id) AS total_orders,
    COUNT(DISTINCT o.customer_id) AS active_buyers,
    SUM(o.total_amount) AS monthly_revenue
FROM Orders o
GROUP BY strftime('%Y-%m', o.order_date);

-- DCL Permission Script Reference
-- GRANT SELECT, INSERT ON ecommerce_db.* TO 'store_app'@'localhost';
```

### Monthly Summary View

1. `CREATE VIEW IF NOT EXISTS vw_monthly_summary AS` defines a reusable named query. If a view with this name already exists, this statement leaves its existing definition unchanged.
2. `strftime('%Y-%m', o.order_date)` formats each order date as a year-month key, such as `2026-10`. SQLite's `strftime` expects dates in a format it can parse.
3. `COUNT(DISTINCT o.order_id)` counts unique orders in each month.
4. `COUNT(DISTINCT o.customer_id)` counts unique customers who ordered in each month.
5. `SUM(o.total_amount)` totals the order amounts for that month.
6. `FROM Orders o` reads from `Orders` and assigns it the short alias `o`.
7. `GROUP BY strftime('%Y-%m', o.order_date)` collects orders into monthly groups, producing one view row per month with orders.

`ECommerceCLI.view_monthly_summary()` queries this view and displays its month, order count, buyer count, and revenue.

### Permission Reference

The `GRANT` line is commented out, so SQLite does not execute it. It is a MySQL-style permissions example and is not a working SQLite command in this project.

## `analytics_queries.sql`

The CLI reads this file when menu option 7 is selected. The code splits the file at semicolons and executes each nonempty SQL statement separately.

```sql
-- 1. Filtering & Operators
SELECT product_id, product_name, category, price, stock_qty
FROM Products
WHERE category IN ('Electronics', 'Home')
  AND price BETWEEN 10.00 AND 300.00
  AND product_name LIKE '%Smart%';

-- 2. Aggregations & HAVING
SELECT
    category,
    COUNT(product_id) AS product_count,
    SUM(stock_qty) AS total_stock,
    AVG(price) AS average_price
FROM Products
GROUP BY category
HAVING AVG(price) > 20;

-- 3. Inner Join
SELECT o.order_id, c.name, o.total_amount, o.order_date
FROM Orders o
INNER JOIN Customers c ON o.customer_id = c.customer_id;

-- 4. CTE (Regional Sales)
WITH RegionalSales AS (
    SELECT c.city, SUM(o.total_amount) AS revenue
    FROM Customers c
    JOIN Orders o ON c.customer_id = o.customer_id
    GROUP BY c.city
)
SELECT city, revenue FROM RegionalSales;

-- 5. Window Functions
SELECT
    product_id,
    category,
    price,
    RANK() OVER(PARTITION BY category ORDER BY price DESC) AS price_rank,
    SUM(price) OVER(PARTITION BY category) AS category_total
FROM Products;
```

### Query 1: Product Filtering

- Selects the product ID, name, category, price, and stock from `Products`.
- `category IN ('Electronics', 'Home')` keeps products in either listed category.
- `price BETWEEN 10.00 AND 300.00` keeps prices in the inclusive range from 10 through 300.
- `product_name LIKE '%Smart%'` keeps names containing `Smart`; `%` matches any sequence of characters.
- The `AND` operators mean a row must satisfy all three filters.

### Query 2: Category Aggregation

- Groups products by `category`.
- `COUNT(product_id)` counts product IDs in each category.
- `SUM(stock_qty)` calculates total units in stock per category.
- `AVG(price)` calculates the average product price per category.
- `HAVING AVG(price) > 20` filters the grouped results to categories whose average price is above 20. `HAVING` is used because the condition applies to an aggregate, after grouping.

### Query 3: Customer Orders Join

- `Orders` is assigned alias `o`; `Customers` is assigned alias `c`.
- `INNER JOIN` matches each order to its customer where their `customer_id` values are equal.
- The result contains the order ID, customer name, total amount, and order date.
- Because this is an inner join, rows without a matching customer are excluded.

The original section comment says “Inner, Left, Cross,” but only an inner join is implemented in this file; there are no `LEFT JOIN` or `CROSS JOIN` statements here.

### Query 4: Regional Sales CTE

- `WITH RegionalSales AS (...)` defines a Common Table Expression (CTE), a named temporary result used by the immediately following query.
- Inside the CTE, `Customers` is joined with `Orders` by customer ID.
- `SUM(o.total_amount)` totals order revenue for each customer city.
- `GROUP BY c.city` produces one revenue total per city.
- The final `SELECT city, revenue FROM RegionalSales` returns the CTE's two columns.

### Query 5: Product Window Functions

- Returns each product's ID, category, and price.
- `PARTITION BY category` runs each window calculation independently for each category without collapsing product rows.
- `RANK() ... ORDER BY price DESC` ranks products from highest to lowest price inside each category. Products tied at the same price receive the same rank, and the next rank can have a gap.
- `SUM(price) OVER(PARTITION BY category)` repeats the sum of product prices for the product's category on every product row in that category.

## Execution Order

1. `schema.sql` creates the tables and indexes needed by the application.
2. `procedures_and_views.sql` creates `vw_monthly_summary`, which the CLI uses for the monthly report.
3. The Python data loader imports customer and product records from CSV files.
4. `analytics_queries.sql` runs only when requested from the CLI menu.

All file paths used by the application are relative to the process's current working directory. Run the program from the repository root for the expected `sql/` and `data/` folders to be found.