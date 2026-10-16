-- ========================================================
-- MODULE 3.2: FILTERING, AGGREGATIONS & JOINS
-- ========================================================

-- 1. Filtering & Operators[cite: 2, 14]
SELECT product_id, product_name, category, price, stock_qty
FROM Products
WHERE category IN ('Electronics', 'Home')
  AND price BETWEEN 10.00 AND 300.00
  AND product_name LIKE '%Smart%';

-- 2. Aggregations & HAVING[cite: 2, 14]
SELECT 
    category,
    COUNT(product_id) AS product_count,
    SUM(stock_qty) AS total_stock,
    AVG(price) AS average_price
FROM Products
GROUP BY category
HAVING AVG(price) > 20;

-- 3. Joins (Inner, Left, Cross)[cite: 2, 14]
SELECT o.order_id, c.name, o.total_amount, o.order_date
FROM Orders o
INNER JOIN Customers c ON o.customer_id = c.customer_id;

-- ========================================================
-- MODULE 3.3: ADVANCED ANALYTICAL QUERIES & WINDOW FUNCTIONS
-- ========================================================

-- 4. CTEs (Regional Sales)[cite: 2, 14]
WITH RegionalSales AS (
    SELECT c.city, SUM(o.total_amount) AS revenue 
    FROM Customers c
    JOIN Orders o ON c.customer_id = o.customer_id 
    GROUP BY c.city
)
SELECT city, revenue FROM RegionalSales;

-- 5. Window Functions (Project Guide Specification)[cite: 2, 14]
SELECT 
    product_id, 
    category, 
    price, 
    RANK() OVER(PARTITION BY category ORDER BY price DESC) as price_rank, 
    SUM(price) OVER(PARTITION BY category) as category_total 
FROM Products;