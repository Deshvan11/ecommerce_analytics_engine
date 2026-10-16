import csv
import os
from src.db_config import DatabaseManager

class DataLoader:
    """CSV ETL Ingestion Pipeline[cite: 3]."""
    def __init__(self, db_manager: DatabaseManager, data_dir="data"):
        self.db_manager = db_manager
        self.data_dir = data_dir

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