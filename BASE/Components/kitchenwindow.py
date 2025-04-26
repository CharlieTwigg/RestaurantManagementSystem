# Import GUI libraries
import tkinter as tk
from tkinter import ttk

# Import custom components
from orderedproducts import OrderedProducts
from Database import Database


class KitchenWindow(tk.Toplevel):
    """
    Kitchen management window for handling food orders.
    Displays orders by table and allows kitchen staff to mark items as cooked.
    """
    def __init__(self, parent, func):
        super().__init__(parent)
        self.func = func  # Callback function for window closure
        self.init_database()  # Initialize database connection

        # Configure window dimensions and position
        self.win_width = 625
        self.win_height = 390
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # Calculate center position for the window
        self.center_x = int(screen_width/2 - self.win_width/2)
        self.center_y = int(screen_height/2 - self.win_height/2)

        # Set window properties
        self.geometry(
            f'{self.win_width}x{self.win_height}+{self.center_x}+{self.center_y}')
        self.title('Restaurant Management System')
        self.resizable(0, 0)  # Prevent window resizing

        self.orders = []  # List to store order objects

        # Create main frame
        self.main_frame = ttk.Frame(self)
        self.main_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=15, pady=10)

        # Create kitchen receipt label frame
        self.kt_lb = ttk.LabelFrame(self.main_frame, text="Kitchen receipt")
        self.kt_lb.grid(column=0, row=0, sticky=tk.NSEW, columnspan=3)

        # Create notebook for table-wise order display
        self.nt = ttk.Notebook(self.kt_lb)
        self.nt.grid(column=0, row=0, ipadx=10, ipady=10, padx=10)
        
        # Load and display orders
        self.add_widgets()

    def destroy(self):
        """Clean up and destroy window"""
        super().destroy()
        self.func()  # Call callback function

    def init_database(self):
        """Initialize database connection"""
        self.fac_db = Database("restaurant.db")

    def add_widgets(self):
        """Load and display orders grouped by table"""
        # Get list of tables with pending orders
        retrieve_query = """SELECT table_num FROM orders GROUP BY table_num"""
        res = self.fac_db.read_val(retrieve_query)
        
        # Create order display for each table
        for r in reversed(res):
            self.retrieve_pr(r[0])

    def retrieve_pr(self, table_num):
        """Create order display widget for a specific table"""
        self.op = OrderedProducts(
            self.main_frame, self.nt, self.kt_lb, str(table_num), self.destroy)
