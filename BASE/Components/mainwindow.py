# Import standard library modules
import os
import tkinter as tk
from tkinter import ttk
from PIL import ImageTk, Image
from sqlite3 import Error

# Import application windows and components
from printorders import PrintOrders
from configwindow import ConfigWindow
from kitchenwindow import KitchenWindow
from createorders import CreateOrders
from aboutwindow import AboutWindow
from Database import Database

# basedir = os.path.dirname(__file__)
# print(basedir)


class MainWindow(tk.Tk):
    """
    Main application window for the Restaurant Management System.
    Provides access to all major functions through a menu interface.
    """
    def __init__(self):
        super().__init__()

        # Configure window dimensions and position
        self.win_width = 600
        self.win_height = 400
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # Calculate center position for the window
        self.center_x = int(screen_width/2 - self.win_width/2)
        self.center_y = int(screen_height/2 - self.win_height/2)

        # Set window properties
        self.geometry(
            f'{self.win_width}x{self.win_height}+{self.center_x}+{self.center_y}')
        self.resizable(0, 0)  # Prevent window resizing
        self.title('Restaurant Management System')

        # Create main frame
        self.m_frame = ttk.Frame(self, width=600, height=400)
        self.m_frame.grid(row=0, column=0,  sticky=tk.NSEW)

        # Load and set application icon
        icon_path = os.path.join(os.path.dirname(
            os.path.dirname(__file__)), 'assets', 'icon_m.png')
        self.icon_image = Image.open(icon_path)
        self.python_image = ImageTk.PhotoImage(self.icon_image)
        self.iconphoto(True, self.python_image)

        # Create menu bar
        self.menubar = tk.Menu(self.m_frame)
        
        # Create File menu
        self.filebar = tk.Menu(self.menubar, tearoff=0)
        # Add menu items - initially disabled until data is available
        self.filebar.add_cascade(
            label="Print Receipts", command=self.print_win, state=tk.DISABLED)
        self.filebar.add_cascade(
            label="Kitchen", command=self.kitchen_win, state=tk.DISABLED)
        self.filebar.add_cascade(
            label="Create Orders", command=self.customer_win, state=tk.DISABLED)
        self.filebar.add_cascade(
            label="Configure Facility/Menu", command=self.config_window)
        self.filebar.add_separator()
        self.filebar.add_cascade(label="Exit", command=self.quit)
        self.menubar.add_cascade(label="File", menu=self.filebar)

        # Create Help/About menu
        self.helpmenu = tk.Menu(self.menubar, tearoff=0)
        self.helpmenu.add_command(label="About...", command=self.about_win)
        self.menubar.add_cascade(label="About", menu=self.helpmenu)

        # Attach menu to window
        self.config(menu=self.menubar)

        # Load and display main window image
        self.img = Image.open(os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 'assets', 'main_win_ph.png'))
        self.img = self.img.resize((250, 250), Image.Resampling.LANCZOS)
        self.img = ImageTk.PhotoImage(self.img)
        
        # Create main label with image and text
        self.panel = tk.Label(
            self.m_frame,
            image=self.img,
            text="Restaurant Management System",
            compound='top',
            font=("Helvetica Bold", 20)
        )
        self.panel.image = self.img
        self.panel.grid(row=0, column=0, sticky=tk.NSEW, padx=90, pady=35)

        # Check database state and enable/disable menu items
        self.check_databases()

    def check_databases(self):
        """Check database tables and update menu item states accordingly"""
        try:
            self.fac_db = Database("restaurant.db")
            
            # Check menu items - enable Create Orders if menu exists
            load_query = """SELECT * FROM menu_config"""
            res = self.fac_db.read_val(load_query)
            customer_state = tk.NORMAL if res else tk.DISABLED
            self.filebar.entryconfig(2, state=customer_state)

            # Check orders - enable Kitchen if orders exist
            load_query1 = """SELECT * FROM orders"""
            res1 = self.fac_db.read_val(load_query1)
            kitchen_state = tk.NORMAL if res1 else tk.DISABLED
            self.filebar.entryconfig(1, state=kitchen_state)

            # Check cooked orders - enable Print Receipts if cooked orders exist
            load_query2 = """SELECT * FROM cooked_orders"""
            res2 = self.fac_db.read_val(load_query2)
            print_order_state = tk.NORMAL if res2 else tk.DISABLED
            self.filebar.entryconfig(0, state=print_order_state)
        except Error as e:
            print(e)

    def config_window(self):
        """Open facility/menu configuration window"""
        config_window = ConfigWindow(self, self.check_databases)
        config_window.grab_set()  # Make window modal

    def kitchen_win(self):
        """Open kitchen management window"""
        kitchen_win = KitchenWindow(self, self.check_databases)
        kitchen_win.grab_set()  # Make window modal

    def customer_win(self):
        """Open order creation window"""
        customer_win = CreateOrders(self, self.check_databases)
        customer_win.grab_set()  # Make window modal

    def about_win(self):
        """Open about window"""
        about_win = AboutWindow(self)
        about_win.grab_set()  # Make window modal

    def print_win(self):
        """Open receipt printing window"""
        print_win = PrintOrders(self)
        print_win.grab_set()  # Make window modal
