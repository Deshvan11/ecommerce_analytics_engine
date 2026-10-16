import sqlite3
import os

class DatabaseManager:
    """Database Connection Class[cite: 3]."""
    def __init__(self, db_path="ecommerce.db"):
        self.db_path = db_path
        self.connection = None

    def connect(self):
        self.connection = sqlite3.connect(self.db_path)
        self.connection.execute("PRAGMA foreign_keys = ON;")
        return self.connection

    def execute_script(self, script_path):
        if not self.connection:
            self.connect()
        with open(script_path, 'r', encoding='utf-8') as f:
            script_sql = f.read()
        cursor = self.connection.cursor()
        cursor.executescript(script_sql)
        self.connection.commit()

    def close(self):
        if self.connection:
            self.connection.close()