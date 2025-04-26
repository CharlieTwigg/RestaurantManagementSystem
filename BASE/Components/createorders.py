# Import GUI and database libraries
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from sqlite3 import Error

# Import custom components
from Database import Database
from productselector import ProductSelector


class CreateOrders(tk.Toplevel):
    """
    Window for creating new food orders.
    Allows staff to select table number, add menu items, and send orders to kitchen.
    """
    def __init__(self, parent, func):
        super().__init__(parent)
        self.func = func  # Callback function for window closure
        self.init_database()  # Initialize database connection

        self.order_ls = []  # List to store order items

        # Configure window dimensions and position
        self.win_width = 580
        self.win_height = 550
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

        # Create main frame
        self.main_frame = ttk.Frame(self)
        self.main_frame.grid(
            row=0,
            column=0,
            sticky=tk.NSEW,
            padx=10,
            pady=10,
            ipady=5,
            ipadx=5
        )

        # Create order creation section
        self.cst_lbl = ttk.LabelFrame(self.main_frame, text="Create Order")
        self.cst_lbl.grid(column=0, row=0, columnspan=4,
                          sticky=tk.NSEW, padx=10)

        # Create scrollable frame for product selection
        self.pr_sel_lbl = ttk.Frame(self.cst_lbl)
        self.pr_sel_lbl.grid(column=0, row=5, columnspan=4,
                             rowspan=10, sticky=tk.NSEW)

        # Configure canvas for scrolling
        self.pr_sel_canvas = tk.Canvas(
            self.pr_sel_lbl, borderwidth=0, width=520, height=400)
        self.pr_sel_canvas.grid(column=0, row=0, sticky=tk.NSEW)

        # Create frame for product selectors
        self.pr_sel_canvas_frm = ttk.Frame(self.pr_sel_canvas)
        self.cst_lbl_scroller = ttk.Scrollbar(
            self.pr_sel_lbl, command=self.pr_sel_canvas.yview)
        self.cst_lbl_scroller.grid(column=4, row=0, sticky=tk.NS)
        self.pr_sel_canvas.configure(yscrollcommand=self.cst_lbl_scroller.set)

        # Add frame to canvas
        self.pr_sel_canvas.create_window(
            (5, 5), anchor=tk.NW, window=self.pr_sel_canvas_frm)

        # Configure scrolling
        self.pr_sel_canvas_frm.bind("<Configure>", self.onFrameConfig)

        # Get facility information
        self.fac_info = self.retrieve_fac_info()

        # Create and position labels
        self.fc_name = ttk.Label(
            self.cst_lbl, text=f"\"{self.fac_info[0]}\"", font="Helvetica 14 bold")
        self.fc_name.grid(column=1, row=0)

        self.tb_name = ttk.Label(self.cst_lbl, text="Table number:")
        self.tb_name.grid(column=1, row=1)

        self.pr_name = ttk.Label(self.cst_lbl, text="Product Name")
        self.pr_name.grid(column=0, row=3)

        self.pr_qty = ttk.Label(self.cst_lbl, text="Quantity")
        self.pr_qty.grid(column=1, row=3)

        self.pr_st = ttk.Label(self.cst_lbl, text="Order Status")
        self.pr_st.grid(column=2, row=3)

        # Counter for product rows
        self.row_count = tk.IntVar()
        self.row_count.set(1)

        # Create control buttons
        self.btn_add_product = ttk.Button(
            self.main_frame, text="Add product", command=self.add_product)
        self.btn_add_product.grid(column=0, row=2, padx=(50, 0), pady=10)

        self.close_btn = ttk.Button(
            self.main_frame, text='Close', command=self.destroy)
        self.close_btn.grid(column=1, row=2, padx=(50, 0), pady=10)

        self.send_to_ch = ttk.Button(
            self.main_frame, text='Send to kitchen', state=tk.DISABLED, command=self.send_to_kitchen)
        self.send_to_ch.grid(column=2, row=2, padx=(50, 0), pady=10)

        # Set up table number validation
        vcmd_tn = (self.register(self.callback_table_num))

        # Create table number entry with validation
        self.tb_name_entry = ttk.Entry(
            self.cst_lbl, width=4,  validate='all', validatecommand=(vcmd_tn, "%P"))
        self.tb_name_entry.grid(row=1, column=1, padx=(140, 0))

    def init_database(self):
        """Initialize database connection and create orders table if needed"""
        self.fac_db = Database("restaurant.db")

        # Create orders table if it doesn't exist
        orders_query = """
        CREATE TABLE IF NOT EXISTS orders(
            id integer PRIMARY KEY AUTOINCREMENT,
            table_num integer NOT NULL, 
            product_name text NOT NULL,
            order_quantity integer NOT NULL,
            order_price REAL,
            order_status text DEFAULT 'pending'
        );
        """
        self.fac_db.create_table(orders_query)

    def retrieve_fac_info(self):
        """Get facility name and maximum table number from database"""
        load_query = """SELECT * FROM fac_config"""
        result = self.fac_db.read_val(load_query)
        fac_name = result[0][1]
        max_table_num = result[0][3]
        return (fac_name, max_table_num)

    def callback_table_num(self, P):
        """Validate table number input against maximum allowed tables"""
        if (str.isdigit(P) and int(P) <= self.fac_info[1]) or P == "":
            return True
        else:
            messagebox.showerror(
                "Input Error", f"Maximum number of tables must not exceed {self.fac_info[1]}!")
            self.tb_name_entry.delete(0, tk.END)
            return False

    def add_records(self, orders):
        """Add orders to database"""
        try:
            load_query = """SELECT * FROM orders ORDER BY id DESC LIMIT 1; """
            spec_insert_query = """INSERT INTO orders (table_num, product_name, order_quantity, order_status) VALUES (?, ?, ?, ?)"""
            order_status = "Ordered"
            for order in orders:
                order_name = order[0][0]
                order_quantity = int(order[0][1])
                table_num = int(order[1])
                self.fac_db.insert_spec_config(
                    spec_insert_query, (table_num, order_name, order_quantity, order_status))
        except Error as e:
            print(e)

    def send_to_kitchen(self):
        """Validate and send orders to kitchen"""
        try:
            orders = []
            table_num = self.tb_name_entry.get()
            if table_num:
                # Validate all orders
                for order in self.order_ls:
                    if order.retrieve_data()[0] == 'Select a meal':
                        messagebox.showerror(
                            "Meal is not selected", "Please, either fill \"Select a meal\" or delete that row to continue!")
                        return False
                    else:
                        orders.append((order.retrieve_data(), table_num))
                
                # Add orders to database
                self.add_records(orders)
                
                # Ask if user wants to create more orders
                usr_resp = messagebox.askyesno(
                    "Success", "Order have been sent to the kitchen, you can access it through the main window, do you wish to get more orders?")
                if usr_resp:
                    self.clear()
                else:
                    self.destroy()
            else:
                messagebox.showerror(
                    "Empty Fields", "Please enter a valid table number!")
        except Error as e:
            print(e)

    def clear(self):
        """Clear all entries and orders"""
        self.tb_name_entry.delete(0, tk.END)
        for order in self.order_ls:
            order.destroy_all()
        self.order_ls = []

    def add_product(self):
        """Add new product selector row"""
        self.max = self.pr_sel_canvas_frm.grid_size()
        self.row_count.set((self.row_count.get() + 1)
                           if self.row_count.get() >= self.max[1] else self.max[1] + 1)
        self.pr_sl = ProductSelector(
            self, self.pr_sel_canvas_frm, self.row_count.get(), func=self.des_pr)
        self.order_ls.insert(self.row_count.get(), self.pr_sl)
        self.send_to_ch.config(state=tk.ACTIVE)

    def des_pr(self):
        """Handle product row deletion"""
        if len(self.pr_sel_canvas_frm.winfo_children()) == 0:
            self.send_to_ch.config(state=tk.DISABLED)
            self.row_count.set(1)
            self.order_ls = []
        self.set_val = self.row_count.get() - 1 if self.row_count.get() > 1 else 1
        self.row_count.set(self.set_val)

    def onFrameConfig(self, event):
        """Update scroll region when frame size changes"""
        self.pr_sel_canvas.configure(
            scrollregion=self.pr_sel_canvas.bbox("all"))

    def destroy(self):
        """Clean up and destroy window"""
        self.func()
        super().destroy()

    def __def__(self):
        """Destructor - ensure callback is called"""
        self.func
