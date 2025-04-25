# Import SQLite database modules
import sqlite3
from sqlite3 import Error


class Database:
    """
    Database handler class for SQLite operations.
    Provides methods for CRUD operations and table management.
    """
    def __init__(self, db):
        """Initialize database connection and create general config table"""
        # Create/connect to SQLite database
        self.conn = sqlite3.connect(db)
        self.cur = self.conn.cursor()
        
        # Create general configuration table if it doesn't exist
        self.cur.execute(
            "CREATE TABLE IF NOT EXISTS gen_config (id INTEGER PRIMARY KEY, conf_name text);")
        self.conn.commit()

        # Initialize general configuration entries
        self.insert_genconfig()

    def create_table(self, create_table_query):
        """Execute a CREATE TABLE query"""
        try:
            cursor = self.cur
            cursor.execute(create_table_query)
            self.conn.commit()
        except Error as e:
            print(e)

    def insert_genconfig(self):
        """Initialize general configuration entries if they don't exist"""
        try:
            # Insert facility configuration entry
            self.cur.execute("INSERT OR IGNORE INTO gen_config(id, conf_name) VALUES (?, ?)",
                             (1, "fac_config"))
            # Insert menu configuration entry
            self.cur.execute("INSERT OR IGNORE INTO gen_config(id, conf_name) VALUES (?, ?)",
                             (2, "menu_config"))
            # Insert orders entry
            self.cur.execute("INSERT OR IGNORE INTO gen_config(id, conf_name) VALUES (?, ?)",
                             (3, "orders"))
            self.conn.commit()
        except Error as e:
            print(e)

    def insert_spec_config(self, insert_query, values):
        """Execute an INSERT query with specified values"""
        try:
            con = self.cur
            con.execute(insert_query, values)
            self.conn.commit()
        except Error as e:
            print(e)

    def update(self, update_query, values):
        """Execute an UPDATE query with specified values"""
        try:
            con = self.cur
            con.execute(update_query, values)
            self.conn.commit()
        except Error as e:
            print(e)

    def read_val(self, read_query, table_num=''):
        """Execute a SELECT query and return results
        
        Handles both simple queries and queries with WHERE clauses
        """
        try:
            con = self.cur
            if "WHERE" in read_query:
                con.execute(read_query, table_num)
                rows = con.fetchall()
            else:
                con.execute(read_query)
                rows = con.fetchall()
            return rows
        except Error as e:
            print(e)

    def delete_val(self, delete_query, item_id):
        """Execute a DELETE query with specified item ID"""
        try:
            con = self.cur
            con.execute(delete_query, item_id)
            self.conn.commit()
        except Error as e:
            print(e)

    def __del__(self):
        """Destructor - ensure database connection is closed"""
        self.conn.close()
