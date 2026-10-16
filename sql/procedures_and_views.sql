-- Analytical View: Monthly Summary[cite: 2]
CREATE VIEW IF NOT EXISTS vw_monthly_summary AS
SELECT 
    strftime('%Y-%m', o.order_date) AS order_month,
    COUNT(DISTINCT o.order_id) AS total_orders,
    COUNT(DISTINCT o.customer_id) AS active_buyers,
    SUM(o.total_amount) AS monthly_revenue
FROM Orders o
GROUP BY strftime('%Y-%m', o.order_date);

-- DCL Permission Script Reference[cite: 2]
-- GRANT SELECT, INSERT ON ecommerce_db.* TO 'store_app'@'localhost';