
import sqlite3
import os
import logging

class DatabaseManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self.logger = logging.getLogger("CodeIndexer.DB")

    def connect(self):
        """Connects to the SQLite database, creating directory if needed."""
        try:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            self.logger.info(f"Connected to DB: {self.db_path}")
            self._init_schema()
        except Exception as e:
            self.logger.error(f"Failed to connect to DB: {e}")
            raise e

    def _init_schema(self):
        """Initializes the database schema."""
        if not self.conn:
            return

        # Table: symbols (Definitions)
        # Using INSERT OR REPLACE to handle re-indexing simply
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS symbols (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                file_path TEXT NOT NULL,
                start_line INTEGER,
                end_line INTEGER,
                docstring TEXT,
                UNIQUE(file_path, name, start_line)
            )
        """)
        
        # Index for fast search by name
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_symbol_name ON symbols(name)")
        self.conn.commit()

    def clear_file_symbols(self, file_path: str):
        """Removes all symbols associated with a specific file (for incremental updates)."""
        if not self.conn:
            return
        self.cursor.execute("DELETE FROM symbols WHERE file_path = ?", (file_path,))
        self.conn.commit()

    def insert_symbol(self, name, symbol_type, file_path, start_line, end_line, docstring=None):
        """Inserts a symbol definition."""
        if not self.conn:
            return
        
        try:
            self.cursor.execute("""
                INSERT OR REPLACE INTO symbols (name, type, file_path, start_line, end_line, docstring)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (name, symbol_type, file_path, start_line, end_line, docstring))
        except Exception as e:
            self.logger.error(f"Failed to insert symbol {name}: {e}")

    def commit(self):
        if self.conn:
            self.conn.commit()

    def close(self):
        if self.conn:
            self.conn.close()
            self.logger.info("DB Connection closed.")
