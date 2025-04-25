import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from Database import Database


class ConfigWindow(tk.Toplevel):
    """
    A window for configuring restaurant facility details and menu items.
    Allows users to set up restaurant name, table count, seat count,
    and manage menu items with prices.
    """
    def __init__(self, parent, func):
        """
        Initialize the configuration window.
        
        Args:
            parent: Parent window
            func: Callback function to execute when window is closed
        """
        super().__init__(parent)
        self.func = func  # Store callback function for window closure
        self.init_database()  # Initialize database connection

        # Set window dimensions and position
        self.win_width = 500
        self.win_height = 600
        screen_width = self.winfo_screenwidth()  # Get screen width for centering
        screen_height = self.winfo_screenheight()  # Get screen height for centering
        self.i = 5  # Counter for unique IDs

        # Calculate center position for the window
        self.center_x = int(screen_width/2 - self.win_width/2)
        self.center_y = int(screen_height/2 - self.win_height/2)

        # Configure window properties
        self.geometry(
            f'{self.win_width}x{self.win_height}+{self.center_x}+{self.center_y}')
        self.title('Restaurant Management System')
        self.resizable(False, False)  # Prevent window resizing

        # Create main frame structure with two rows
        self.main_frame = ttk.Frame(self)
        self.main_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=10, pady=10)
        self.main_frame.rowconfigure(0, weight=1)  # Facility config section
        self.main_frame.rowconfigure(1, weight=1)  # Menu config section

        # Create separate frames for facility and menu configuration
        self.up_frame = ttk.Frame(self.main_frame)  # Upper frame for facility config
        self.up_frame.grid(column=0, row=0, sticky=tk.NSEW)

        self.down_frame = ttk.Frame(self.main_frame)  # Lower frame for menu config
        self.down_frame.grid(column=0, row=1, sticky=tk.NSEW)

        # Initialize both configuration sections
        self._setup_facility_config()  # Setup facility configuration UI
        self._setup_menu_config()  # Setup menu configuration UI

        # Initialize UI state and load data
        self.check_if_empty_database()  # Check database state
        self.check_if_empty_fc_entry()  # Check facility config entries
        self.retreive_menu_items()  # Load existing menu items

    def _setup_facility_config(self):
        """Set up the facility configuration section with entry fields and buttons"""
        # Create a labeled frame for facility configuration
        self.fac_config_lf = ttk.LabelFrame(
            self.up_frame, text="Facility Configuration")
        self.fac_config_lf.grid(
            column=0,
            row=0,
            pady=5,
            rowspan=4,
            columnspan=3,
            sticky=tk.EW
        )

        # Create and position labels for facility name, table count, and seat count
        self.fc_name_lb = ttk.Label(self.fac_config_lf, text="Facility Name:")
        self.fc_name_lb.grid(column=0, row=1, sticky=tk.W, padx=10, pady=10)

        self.fc_table_num_lb = ttk.Label(
            self.fac_config_lf,
            text="Number of Tables:"
        )
        self.fc_table_num_lb.grid(
            column=0,
            row=2,
            sticky=tk.W,
            padx=10,
            pady=10
        )

        self.fc_seat_num_lb = ttk.Label(
            self.fac_config_lf,
            text="Number of Seats:"
        )
        self.fc_seat_num_lb.grid(
            column=0,
            row=3,
            sticky=tk.W,
            padx=10,
            pady=10
        )

        # Create entry fields with validation
        self.fc_name_ent = ttk.Entry(self.fac_config_lf)  # For facility name
        self.fc_name_ent.grid(column=1, row=1, sticky=tk.E, padx=15)

        # Register validation commands for table and seat counts
        vcmd_t = (self.register(self.callback_table))  # Validates table count <= 50
        vcmd_s = (self.register(self.callback_seats))  # Validates seats <= tables * 8

        # Entry field for table count with validation
        self.fc_table_num_ent = ttk.Entry(
            self.fac_config_lf,
            validate='all',
            validatecommand=(vcmd_t, "%P")
        )
        self.fc_table_num_ent.grid(column=1, row=2, sticky=tk.E, padx=15)

        # Entry field for seat count with validation
        self.fc_seat_num_ent = ttk.Entry(
            self.fac_config_lf,
            validate='all',
            validatecommand=(vcmd_s, "%P")
        )
        self.fc_seat_num_ent.grid(column=1, row=3, sticky=tk.E, padx=15)

        # Create and position control buttons
        # Save button - always enabled
        self.fc_save_btn = ttk.Button(
            self.fac_config_lf, text="Save", command=self.save_fac_config)
        self.fc_save_btn.grid(column=2, row=1, pady=5, padx=15)

        # Load button - initially disabled until data exists
        self.fc_load_btn = ttk.Button(
            self.fac_config_lf,
            text="Load",
            command=self.load_fac_config,
            state=tk.DISABLED
        )
        self.fc_load_btn.grid(column=2, row=2, pady=5, padx=15)

        # Clear button - initially disabled until fields have data
        self.fc_clear_btn = ttk.Button(
            self.fac_config_lf,
            text="Clear",
            command=self.fac_conf_clear,
            state=tk.DISABLED
        )
        self.fc_clear_btn.grid(column=2, row=3, pady=5, padx=15)

    def _setup_menu_config(self):
        """Set up the menu configuration section with treeview and buttons"""
        # Create scrollbar for treeview
        self.tr_v_vscr = ttk.Scrollbar(self.down_frame, orient="vertical")

        # Configure treeview columns for menu items
        self.tr_view_columns = ('id', 'name', 'price')
        self.tr_view = ttk.Treeview(
            self.down_frame,
            columns=self.tr_view_columns,
            show='headings',  # Only show column headings
            height=8,         # Show 8 items at a time
            selectmode='browse',  # Single selection mode
            yscrollcommand=self.tr_v_vscr.set
        )
        
        # Configure column widths and alignments
        self.tr_view.column('id', width=50, anchor=tk.CENTER)
        self.tr_view.column('name', width=200, anchor=tk.CENTER)
        self.tr_view.column('price', width=200, anchor=tk.CENTER)

        # Set column headers
        self.tr_view.heading('id', text="ID")
        self.tr_view.heading('name', text="Name")
        self.tr_view.heading('price', text="Price(ft)")

        # Position treeview and scrollbar
        self.tr_view.grid(column=0, row=0, rowspan=6, columnspan=3, pady=10)
        self.tr_v_vscr.config(command=self.tr_view.yview)
        self.tr_v_vscr.grid(column=3, row=0, rowspan=6,  sticky=tk.NS)

        # Bind events for product selection and deletion
        self.tr_view.bind('<ButtonRelease-1>', self.product_selected)  # Click selection
        self.tr_view.bind('<Delete>', self.remove_selected)  # Delete key handling

        # Create frame for adding new products
        self.add_prd_lbf = ttk.LabelFrame(
            self.down_frame, text="Add product")
        self.add_prd_lbf.grid(column=0, row=7, pady=10,
                              padx=5,  columnspan=3, sticky=tk.EW)

        # Create frame for removing products
        self.remove_prd_lbf = ttk.LabelFrame(
            self.down_frame, text="Remove product")
        self.remove_prd_lbf.grid(
            column=0, row=8, pady=10, padx=5,  columnspan=3, sticky=tk.EW)

        # Create and position labels and entries for new product details
        self.food_name_lbl = ttk.Label(
            self.add_prd_lbf, text="Name of the product:")
        self.food_name_lbl.grid(column=0, row=0, sticky=tk.W, padx=10, pady=10)

        self.food_price_lbl = ttk.Label(
            self.add_prd_lbf, text="Price of the product:")
        self.food_price_lbl.grid(
            column=0, row=1, sticky=tk.W, padx=10, pady=10)

        # Entry fields for new product details
        self.food_name_entry = ttk.Entry(self.add_prd_lbf)  # Product name entry
        self.food_name_entry.grid(column=1, row=0, pady=10, padx=10)

        self.food_price_entry = ttk.Entry(self.add_prd_lbf)  # Product price entry
        self.food_price_entry.grid(column=1, row=1, pady=10, padx=10)

        # Labels for showing selected product info
        self.pr_id_lbl = ttk.Label(
            self.remove_prd_lbf, text="Product Selected:")
        self.pr_id_lbl.grid(column=0, row=0, sticky=tk.W, padx=10, pady=10)

        self.sel_pr_id_lbl = ttk.Label(self.remove_prd_lbf, text="")  # Shows selected product
        self.sel_pr_id_lbl.grid(column=1, row=0, sticky=tk.W, padx=10, pady=10)

        # Buttons for adding and removing products
        self.tr_view_add = ttk.Button(
            self.add_prd_lbf, text="Add", command=self.add_record)
        self.tr_view_add.grid(column=2, row=0, rowspan=2, padx=10)

        # Bind Enter key to add product
        self.tr_view_add.bind('<Return>', self.add_record)

        # Remove button - initially disabled until product is selected
        self.tr_view_remove = ttk.Button(
            self.remove_prd_lbf,
            text="Remove",
            command=self.remove_selected,
            state=tk.DISABLED
        )
        self.tr_view_remove.grid(column=2, row=0, padx=10, sticky=tk.E)

    def retreive_menu_items(self):
        """Load existing menu items from database and populate the treeview"""
        # Query all menu items from database
        load_query = """SELECT * FROM menu_config"""
        result = self.fac_db.read_val(load_query)
        
        # If menu items exist, add them to treeview
        if len(result) > 0:
            for el in result:
                self.tr_view.insert('', tk.END, iid=f"{el[0]}", values=el)
        else:
            # Disable remove button if no items exist
            self.tr_view_remove.config(state=tk.DISABLED)

    def get_product_id(self):
        """Get the next available product ID for new menu items"""
        # Get all existing items
        res = self.tr_view.get_children()
        if res:
            # Return last ID + 1
            return res[-1]
        else:
            # Start with ID 1 if no items exist
            return 1

    def init_database(self):
        """Initialize database connection and create required tables"""
        # Connect to SQLite database
        self.fac_db = Database("restaurant.db")
        
        # SQL query to create facility configuration table
        fac_conf_query = """
        CREATE TABLE IF NOT EXISTS fac_config(
            id integer PRIMARY KEY,
            fac_name text NOT NULL,
            table_num integer NOT NULL,
            seat_num integer NOT NULL
        );
        """
        
        # SQL query to create menu configuration table
        menu_conf_query = """
        CREATE TABLE IF NOT EXISTS menu_config(
            id integer PRIMARY KEY,
            product_name text NOT NULL,
            product_price real NOT NULL
        );
        """

        # Create tables if they don't exist
        self.fac_db.create_table(fac_conf_query)
        self.fac_db.create_table(menu_conf_query)

    def check_if_empty_database(self):
        """Check database state and update UI buttons accordingly"""
        # Query facility configuration
        load_query = """SELECT * FROM fac_config"""
        result = self.fac_db.read_val(load_query)
        
        # If facility config exists, enable/disable buttons based on data
        if len(result) > 0:
            f_name = result[0][1]
            t_num = result[0][2]
            s_num = result[0][3]

            if f_name and t_num and s_num:
                self.fc_load_btn.config(state=tk.ACTIVE)
            else:
                self.fc_load_btn.config(state=tk.DISABLED)
                self.tr_view_remove.config(state=tk.DISABLED)

    def check_if_empty_fc_entry(self):
        """Check if facility configuration fields are filled and update clear button state"""
        # Get values from all entry fields
        f_name = self.fc_name_ent.get()
        t_num = self.fc_table_num_ent.get()
        s_num = self.fc_seat_num_ent.get()

        # Enable clear button only if all fields have data
        if f_name and t_num and s_num:
            self.fc_clear_btn.config(state=tk.ACTIVE)
        else:
            self.fc_clear_btn.config(state=tk.DISABLED)

    def product_selected(self, event):
        """Handle product selection in the treeview"""
        try:
            selected_item = self.tr_view.selection()[0]
            sel_item_val = self.tr_view.item(selected_item)['values']
            sel_pr_txt = f"{sel_item_val[0]}) {sel_item_val[1]} {sel_item_val[2]}"
            self.sel_pr_id_lbl.config(text="")
            self.sel_pr_id_lbl.config(text=sel_pr_txt)
            self.tr_view_remove.config(state=tk.ACTIVE)
        except IndexError as e:
            print(e)

    def fac_conf_clear(self):
        self.fc_name_ent.delete(0, tk.END)
        self.fc_seat_num_ent.delete(0, tk.END)
        self.fc_table_num_ent.delete(0, tk.END)

        self.fc_clear_btn.config(state=tk.DISABLED)

    def callback_table(self, P):
        """Validate table number input - must be <= 50"""
        # Check if input is a valid number and <= 50
        if (str.isdigit(P) and int(P) <= 50) or P == "":
            return True
        else:
            messagebox.showerror(
                "Input Error", "Maximum number of tables must not exceed 50!")
            return False

    def callback_seats(self, P):
        """Validate seat number input - must be <= table_count * 8"""
        # Calculate maximum seats based on table count (8 seats per table)
        max_table_num = int(self.fc_table_num_ent.get()) * 8
        if (str.isdigit(P) and int(P) <= max_table_num) or P == "":
            return True
        else:
            messagebox.showerror(
                "Input Error", f"Maximum number of seats cannot exceed {max_table_num}")
            return False

    def validate_product(self, price, name):
        """
        Validate product details before adding to menu.
        - Name must be <= 20 characters
        - Price must be a valid number <= 10M Forints (with override option)
        """
        # Check if price and name meet basic requirements
        if (self.is_float(price) and float(price) <= 10000000) and (len(name) <= 20):
            return True
        # If price exceeds limit but name is valid, ask for confirmation
        elif (self.is_float(price) and float(price) > 10000000) and (len(name) <= 20):
            usr_resp = messagebox.askyesno(
                "Overprice Check", "The price you have entered exceeds maximum allowed (10 million Forints), do you wish to continue?")
            if usr_resp:
                return True
            else:
                self.food_price_entry.delete(0, tk.END)
                return False
        # If both price and name are invalid
        elif (self.is_float(price) and float(price) > 10000000) and (len(name) > 20):
            messagebox.showerror(
                "Wrong inputs", "The price you have entered exceeds maximum allowed (10 million Forints) and product name should be less than 20 characters long")
            self.food_price_entry.delete(0, tk.END)
            self.food_name_entry.delete(0, tk.END)
            return False
        else:
            messagebox.showerror(
                "Wrong input", "Please enter the product name(max. 20 characters long) and price(max 10 mln forints) correctly!")
            return False

    def save_fac_config(self):
        """Save or update facility configuration in database"""
        # Check if facility config already exists
        load_query = """SELECT * FROM fac_config"""
        result = self.fac_db.read_val(load_query)

        # Get current values from entry fields
        fac_name = self.fc_name_ent.get()
        table_num = self.fc_table_num_ent.get()
        seat_num = self.fc_seat_num_ent.get()

        # Only proceed if all fields are filled
        if fac_name and table_num and seat_num:
            # Update existing config
            if len(result) >= 1:
                update_query = """UPDATE fac_config
                SET fac_name = ?,
                table_num = ?,
                seat_num = ?,
                WHERE id = ?
                """
                self.fac_db.update(
                    update_query, (fac_name, table_num, seat_num, 1))
            # Create new config
            else:
                spec_insert_query = """INSERT INTO fac_config VALUES (?, ?, ?, ?)"""
                self.fac_db.insert_spec_config(
                    spec_insert_query, (1, fac_name, table_num, seat_num))
            # Update UI state
            self.check_if_empty_database()
            self.check_if_empty_fc_entry()
        else:
            messagebox.showerror(
                "Empty input fields", "Please enter facility name, table number and seat number accordingly!")

    def load_fac_config(self):
        """Load facility configuration from database into entry fields"""
        # Clear current entries
        self.fac_conf_clear()
        # Load config from database
        load_query = """SELECT * FROM fac_config"""
        result = self.fac_db.read_val(load_query)

        # Populate entry fields with loaded data
        self.fc_name_ent.insert(0, result[0][1])
        self.fc_table_num_ent.insert(0, result[0][2])
        self.fc_seat_num_ent.insert(0, result[0][3])
        self.check_if_empty_fc_entry()

    def remove_selected(self, event=""):
        """Remove selected menu item from database and treeview"""
        try:
            # Get selected item
            selected_item = self.tr_view.selection()
            sel_it_ind = selected_item[0]
            # Delete from database
            delete_query = """DELETE FROM menu_config WHERE id = ?"""
            self.fac_db.delete_val(delete_query, [sel_it_ind])
            # Remove from treeview
            for sel_item in selected_item:
                self.tr_view.delete(sel_item)
            # Reset selection label and disable remove button
            self.sel_pr_id_lbl.config(text="")
            self.tr_view_remove.config(state=tk.DISABLED)
        except IndexError as e:
            print(e)

    def add_record(self, event='<Return>'):
        """Add new menu item to database and treeview"""
        # Get values from entry fields
        food_name = self.food_name_entry.get()
        food_price = self.food_price_entry.get()
        spec_insert_query = """INSERT INTO menu_config VALUES (?, ?, ?)"""
        
        # Calculate next product ID
        pr_id = self.get_product_id()
        pr_ind = pr_id if pr_id == 1 else int(pr_id) + 1
        
        # Only proceed if both fields are filled
        if food_name and food_price:
            validate_product = self.validate_product(food_price, food_name)
            if validate_product:
                # Add to treeview
                self.tr_view.insert("", tk.END, iid=f"{pr_ind}", values=(
                    pr_ind, food_name, food_price))
                # Add to database
                self.fac_db.insert_spec_config(
                    spec_insert_query, (pr_ind, food_name, food_price))
        else:
            er_msg = "Please fill \"Name of the product \" and \"Price of the product\" fields!"
            messagebox.showerror("Empty input fields", er_msg)

        # Clear entry fields after adding
        self.food_name_entry.delete(0, tk.END)
        self.food_price_entry.delete(0, tk.END)

    def is_float(self, element):
        """Check if a string can be converted to float"""
        if element is None:
            return False
        try:
            float(element)
            return True
        except ValueError:
            return False

    def destroy(self):
        """Clean up and destroy window"""
        try:
            self.func()  # Call callback function
        except:
            pass
        super().destroy()

    def __del__(self):
        """Destructor - ensure callback is called"""
        try:
            self.func()  # Call callback function
        except:
            pass
