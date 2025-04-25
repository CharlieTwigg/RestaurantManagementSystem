# Import the Database class for SQLite operations
from Database import Database

def init_database():
    """Initialize the restaurant management system database with required tables"""
    # Create database connection
    db = Database("restaurant.db")
    
    # Create facility configuration table
    # Stores restaurant details like name, icon, table count, and seat count
    db.create_table("""
        CREATE TABLE IF NOT EXISTS fac_config (
            id INTEGER PRIMARY KEY,
            fac_name TEXT,
            fac_icon TEXT,
            table_num INTEGER,
            seat_num INTEGER
        )
    """)
    
    # Create menu configuration table
    # Stores menu items with their names and prices
    db.create_table("""
        CREATE TABLE IF NOT EXISTS menu_config (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL,
            product_price REAL NOT NULL
        )
    """)
    
    # Create orders table
    # Tracks current orders with their status (pending/cooked)
    db.create_table("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            table_num INTEGER,
            product_name TEXT,
            order_quantity INTEGER,
            order_price REAL,
            order_status TEXT DEFAULT 'pending'
        )
    """)
    
    # Create cooked orders table
    # Stores completed orders for billing purposes
    db.create_table("""
        CREATE TABLE IF NOT EXISTS cooked_orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            table_num INTEGER,
            product_name TEXT,
            order_quantity INTEGER,
            order_price REAL
        )
    """)

# Run database initialization if script is run directly
if __name__ == "__main__":
    init_database()
    print("Database initialized successfully!") 