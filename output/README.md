# E-Commerce CLI Output

The read-only results below come from the current `ecommerce.db`. Examples for choices 1, 3, 4, and 6 show representative input and output; those write operations were not run. Output may differ if the database contents or entered values change.

## Choice 1: Insert User

```text
Select option (1-9): 1
Enter Name: Sample User
Enter Email: sample.user@example.com
Enter City: Mumbai
[SUCCESS] User inserted and logged!
```

## Choice 2: View Inventory

```text
Select option (1-9): 2
ID: 1 | Wireless Ergonomic Mouse | Electronics | $49.99 | Stock: 150
ID: 2 | Mechanical Gaming Keyboard | Electronics | $89.99 | Stock: 200
ID: 3 | Ultra-Wide 34-inch Monitor | Electronics | $399.99 | Stock: 45
ID: 4 | Noise-Canceling Headphones | Electronics | $199.99 | Stock: 80
ID: 5 | USB-C Docking Station | Electronics | $129.99 | Stock: 60
ID: 6 | Smart LED Desk Lamp | Home | $34.99 | Stock: 220
ID: 7 | Ergonomic Office Chair | Home | $249.99 | Stock: 30
ID: 8 | Standing Desk Converter | Home | $179.99 | Stock: 25
ID: 9 | Stainless Steel Kettle | Home | $45 | Stock: 110
ID: 10 | Memory Foam Pillow | Home | $59.99 | Stock: 90
ID: 11 | Python Crash Course Book | Books | $39.99 | Stock: 150
ID: 12 | Clean Code Handbook | Books | $44.99 | Stock: 130
ID: 13 | Designing Data-Intensive Apps | Books | $49.99 | Stock: 95
ID: 14 | Introduction to Algorithms | Books | $85 | Stock: 50
ID: 15 | Machine Learning Yearning | Books | $29.99 | Stock: 200
ID: 16 | Running Shoes Pro | Sports | $119.99 | Stock: 74
ID: 17 | Adjustable Dumbbell Set | Sports | $199.99 | Stock: 40
ID: 18 | Yoga Mat Premium | Sports | $29.99 | Stock: 300
ID: 19 | Resistance Bands Kit | Sports | $19.99 | Stock: 250
ID: 20 | Stainless Water Bottle | Sports | $24.99 | Stock: 180
ID: 21 | Bluetooth Speaker Portable | Electronics | $59.99 | Stock: 140
ID: 22 | 4K Action Camera | Electronics | $299.99 | Stock: 55
ID: 23 | External SSD 1TB | Electronics | $109.99 | Stock: 120
ID: 24 | Wireless Charging Pad | Electronics | $25.99 | Stock: 210
ID: 25 | Smartwatch Series 5 | Electronics | $249.99 | Stock: 65
ID: 26 | Air Purifier HEPA | Home | $129.99 | Stock: 40
ID: 27 | Espresso Machine | Home | $349.99 | Stock: 20
ID: 28 | Robot Vacuum Cleaner | Home | $299.99 | Stock: 35
ID: 29 | Non-Stick Cookware Set | Home | $149.99 | Stock: 50
ID: 30 | Cast Iron Skillet | Home | $39.99 | Stock: 100
ID: 31 | Deep Learning with PyTorch | Books | $54.99 | Stock: 80
ID: 32 | SQL Performance Explained | Books | $42.99 | Stock: 110
ID: 33 | System Design Interview | Books | $49.99 | Stock: 140
ID: 34 | The Pragmatic Programmer | Books | $45 | Stock: 160
ID: 35 | Refactoring Code | Books | $48 | Stock: 90
ID: 36 | Cycling Helmet | Sports | $49.99 | Stock: 85
ID: 37 | Fitness Tracker Band | Sports | $69.99 | Stock: 130
ID: 38 | Pro Tennis Racket | Sports | $129.99 | Stock: 45
ID: 39 | Camping Tent 4-Person | Sports | $189.99 | Stock: 25
ID: 40 | Hydration Backpack | Sports | $54.99 | Stock: 95
ID: 41 | Graphic Tablet Pro | Electronics | $219.99 | Stock: 50
ID: 42 | Smart Wi-Fi Plug | Electronics | $19.99 | Stock: 300
ID: 43 | HD Security Camera | Electronics | $79.99 | Stock: 115
ID: 44 | True Wireless Earbuds | Electronics | $89.99 | Stock: 160
ID: 45 | Thunderbolt 4 Cable | Electronics | $39.99 | Stock: 240
ID: 46 | Boutique French Press | Home | $32.99 | Stock: 120
ID: 47 | Bamboo Cutlery Organizer | Home | $22.99 | Stock: 150
ID: 48 | Smart Thermostat | Home | $179.99 | Stock: 60
ID: 49 | LED Strip Lights 10m | Home | $27.99 | Stock: 200
ID: 50 | Ceramic Dinnerware Set | Home | $89.99 | Stock: 68
```

## Choice 3: Update Stock

```text
Select option (1-9): 3
Enter Product ID: 1
Enter New Stock Qty: 155
[SUCCESS] Stock updated and logged!
```

## Choice 4: Delete Order

```text
Select option (1-9): 4
Enter Order ID to delete: 2
[SUCCESS] Order deleted safely!
```

## Choice 5: View Audit Logs

```text
Select option (1-9): 5
Log ID: 1 | INSERT_USER | 2026-10-16 16:53:00 | Added user Tanmay Deshmukh
Log ID: 2 | SELECT_INVENTORY | 2026-10-16 16:53:15 | Queried inventory
Log ID: 3 | UPDATE_STOCK | 2026-10-16 16:53:40 | Updated product 1 stock to 155
Log ID: 4 | PLACE_ORDER | 2026-10-16 16:54:09 | Placed Order #1
Log ID: 5 | DELETE_ORDER | 2026-10-16 16:55:25 | Deleted order 1
Log ID: 6 | PLACE_ORDER | 2026-10-16 17:02:43 | Placed Order #2
Log ID: 7 | FAILED_ORDER | 2026-10-16 17:47:17 | Stock failure for Product ID 25. Requested: 66, Available: 65
Log ID: 8 | FAILED_ORDER | 2026-10-16 17:56:01 | Stock failure for Product ID 1. Requested: 155, Available: 150
Log ID: 9 | FAILED_ORDER | 2026-10-16 17:58:50 | Stock failure for Product ID 1. Requested: 152, Available: 150
Log ID: 10 | PLACE_ORDER | 2026-10-16 17:59:29 | Placed Order #3
Log ID: 11 | SELECT_INVENTORY | 2026-10-16 18:03:18 | Queried inventory
Log ID: 12 | UPDATE_STOCK | 2026-10-16 18:04:01 | Updated product 51 stock to 21
```

## Choice 6: Place Order

```text
Select option (1-9): 6
Customer ID: 50
Product ID: 1
Quantity: 1
[SUCCESS] Order #4 placed successfully!
```

## Choice 7: Run Analytics Queries

```text
Select option (1-9): 7

--- EXECUTING ANALYTICS QUERIES FROM FILE ---

[Executing Query #1]:
(25, 'Smartwatch Series 5', 'Electronics', 249.99, 65)
(42, 'Smart Wi-Fi Plug', 'Electronics', 19.99, 300)
(6, 'Smart LED Desk Lamp', 'Home', 34.99, 220)
(48, 'Smart Thermostat', 'Home', 179.99, 60)

[Executing Query #2]:
('Books', 10, 1205, 49.093)
('Electronics', 15, 1990, 137.72333333333333)
('Home', 15, 1318, 126.25733333333334)
('Sports', 10, 1224, 88.99)

[Executing Query #3]:
(2, 'Surya Sivakumar', 249.95000000000002, '2026-10-16 22:32:43')
(3, 'Nikhil More', 119.99, '2026-10-16 23:29:29')

[Executing Query #4]:
('Chennai', 249.95000000000002)
('Pune', 119.99)

[Executing Query #5]:
(14, 'Books', 85, 1, 490.93)
(31, 'Books', 54.99, 2, 490.93)
(13, 'Books', 49.99, 3, 490.93)
(33, 'Books', 49.99, 3, 490.93)
(35, 'Books', 48, 5, 490.93)
(34, 'Books', 45, 6, 490.93)
(12, 'Books', 44.99, 7, 490.93)
(32, 'Books', 42.99, 8, 490.93)
(11, 'Books', 39.99, 9, 490.93)
(15, 'Books', 29.99, 10, 490.93)
(3, 'Electronics', 399.99, 1, 2065.85)
(22, 'Electronics', 299.99, 2, 2065.85)
(25, 'Electronics', 249.99, 3, 2065.85)
(41, 'Electronics', 219.99, 4, 2065.85)
(4, 'Electronics', 199.99, 5, 2065.85)
(5, 'Electronics', 129.99, 6, 2065.85)
(23, 'Electronics', 109.99, 7, 2065.85)
(2, 'Electronics', 89.99, 8, 2065.85)
(44, 'Electronics', 89.99, 8, 2065.85)
(43, 'Electronics', 79.99, 10, 2065.85)
(21, 'Electronics', 59.99, 11, 2065.85)
(1, 'Electronics', 49.99, 12, 2065.85)
(45, 'Electronics', 39.99, 13, 2065.85)
(24, 'Electronics', 25.99, 14, 2065.85)
(42, 'Electronics', 19.99, 15, 2065.85)
(27, 'Home', 349.99, 1, 1893.8600000000001)
(28, 'Home', 299.99, 2, 1893.8600000000001)
(7, 'Home', 249.99, 3, 1893.8600000000001)
(8, 'Home', 179.99, 4, 1893.8600000000001)
(48, 'Home', 179.99, 4, 1893.8600000000001)
(29, 'Home', 149.99, 6, 1893.8600000000001)
(26, 'Home', 129.99, 7, 1893.8600000000001)
(50, 'Home', 89.99, 8, 1893.8600000000001)
(10, 'Home', 59.99, 9, 1893.8600000000001)
(9, 'Home', 45, 10, 1893.8600000000001)
(30, 'Home', 39.99, 11, 1893.8600000000001)
(6, 'Home', 34.99, 12, 1893.8600000000001)
(46, 'Home', 32.99, 13, 1893.8600000000001)
(49, 'Home', 27.99, 14, 1893.8600000000001)
(47, 'Home', 22.99, 15, 1893.8600000000001)
(17, 'Sports', 199.99, 1, 889.9)
(39, 'Sports', 189.99, 2, 889.9)
(38, 'Sports', 129.99, 3, 889.9)
(16, 'Sports', 119.99, 4, 889.9)
(37, 'Sports', 69.99, 5, 889.9)
(40, 'Sports', 54.99, 6, 889.9)
(36, 'Sports', 49.99, 7, 889.9)
(18, 'Sports', 29.99, 8, 889.9)
(20, 'Sports', 24.99, 9, 889.9)
(19, 'Sports', 19.99, 10, 889.9)
```

## Choice 8: Monthly Summary

```text
Select option (1-9): 8

--- MONTHLY SUMMARY VIEW ---
Month: 2026-10 | Orders: 2 | Active Buyers: 2 | Revenue: $369.94
```

## Choice 9: Exit

```text
Select option (1-9): 9

[INFO] Exiting E-Commerce Analytics Engine. Goodbye!
```

## `ecommerce.db` Presentation

```text
DATABASE: ecommerce.db

TABLE Customers       51 rows
  customer_id | name | email | city | signup_date
  1 | Aarav Sharma | aarav.sharma@example.com | Mumbai | 2026-01-10
  2 | Ananya Patel | ananya.patel@example.com | Pune | 2026-01-12
  3 | Rohan Verma | rohan.verma@example.com | Bangalore | 2026-01-15

TABLE Products        50 rows
  product_id | product_name | category | price | stock_qty
  1 | Wireless Ergonomic Mouse | Electronics | 49.99 | 150
  2 | Mechanical Gaming Keyboard | Electronics | 89.99 | 200
  3 | Ultra-Wide 34-inch Monitor | Electronics | 399.99 | 45

TABLE Orders           2 rows
  order_id | customer_id | order_date | total_amount | status
  2 | 50 | 2026-10-16 22:32:43 | 249.95000000000002 | Completed
  3 | 23 | 2026-10-16 23:29:29 | 119.99 | Completed

TABLE OrderDetails     2 rows
  detail_id | order_id | product_id | quantity | unit_price | subtotal
  2 | 2 | 1 | 5 | 49.99 | 249.95000000000002
  3 | 3 | 16 | 1 | 119.99 | 119.99

TABLE AuditLogs       12 rows
  log_id | action | executed_at | status_message
  1 | INSERT_USER | 2026-10-16 16:53:00 | Added user Tanmay Deshmukh
  2 | SELECT_INVENTORY | 2026-10-16 16:53:15 | Queried inventory
  3 | UPDATE_STOCK | 2026-10-16 16:53:40 | Updated product 1 stock to 155
  ... 9 more rows

VIEW vw_monthly_summary
  order_month | total_orders | active_buyers | monthly_revenue
  2026-10 | 2 | 2 | 369.94
```