# Import standard libraries
import os
import tkinter as tk
from tkinter import ttk
from PIL import ImageTk, Image

# Import database handler
from Database import Database


class ProductSelector(tk.Frame):
    """
    A custom widget for selecting menu items and their quantities.
    Provides a dropdown menu for item selection and spinbox for quantity.
    """
    def __init__(self, parent, root_frame, row, func):
        self.func = func  # Callback function for deletion
        tk.Frame.__init__(self, parent)

        self.init_database()  # Initialize database connection

        # Create menu button for product selection
        self.menuBtn = ttk.Menubutton(root_frame, text="Select a meal")

        # Create dropdown menu
        self.menu = tk.Menu(self.menuBtn, tearoff=0)
        self.m_var1 = tk.StringVar()
        self.m_var1.set("Select a meal")
        self.retrieve_products()  # Load products from database
        self.menuBtn['menu'] = self.menu

        # Position menu button
        self.menuBtn.grid(column=0, row=row, padx=(15, 85), sticky=tk.W)

        # Create quantity spinbox
        self.pr_qty_var = tk.StringVar(root_frame)
        self.pr_qty_var.set("1")  # Default quantity
        self.spin_box = ttk.Spinbox(
            root_frame,
            from_=1,
            to=100,
            textvariable=self.pr_qty_var,
            wrap=True,
            width=5,
            state=tk.DISABLED,  # Initially disabled until product is selected
        )
        self.spin_box.grid(column=1, row=row)

        # Create order status label
        self.order_st_lb = ttk.Label(root_frame,  text="Choosing")
        self.order_st_lb.grid(column=2, row=row, padx=(110, 10))

        # Load and configure delete button icon
        self.del_icon_png = Image.open(
            os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'delete.png'))
        self.del_icon_res = self.del_icon_png.resize(
            (18, 18), Image.Resampling.LANCZOS)
        self.del_icon = ImageTk.PhotoImage(self.del_icon_res)
        
        # Create delete button
        self.destroy_btn = ttk.Button(
            root_frame, image=self.del_icon, width=10, command=self.destroy_all)
        self.destroy_btn.image = self.del_icon
        self.destroy_btn.grid(column=3, row=row, padx=(10, 0))

    def init_database(self):
        """Initialize database connection"""
        self.fac_db = Database("restaurant.db")

    def retrieve_products(self):
        """Load products from database and populate dropdown menu"""
        load_query = """SELECT * FROM menu_config"""
        result = self.fac_db.read_val(load_query)
        for row in result:
            pr_lbl = row[1]
            self.menu.add_radiobutton(
                label=pr_lbl, variable=self.m_var1, command=self.sel)

    def pad_num(self):
        """Calculate padding based on selected product name length"""
        var_len = len(self.m_var1.get())
        return 165 - ((var_len - 1) * 7.5)

    def sel(self):
        """Handle product selection"""
        selx = self.m_var1.get()
        self.menuBtn.config(text=selx)
        self.pad_n = self.pad_num()
        self.order_updt()

    def retrieve_data(self):
        """Get selected product and quantity"""
        return (self.m_var1.get(), self.pr_qty_var.get())

    def order_updt(self):
        """Update UI after product selection"""
        self.order_st_lb.config(text="Ordered")
        self.spin_box.config(state=tk.ACTIVE)  # Enable quantity selection
        self.spin_box.config(textvariable=self.pr_qty_var)
        self.menuBtn.grid_configure(padx=(15, self.pad_n))

    def destroy_all(self):
        """Clean up and destroy all widget components"""
        super().destroy()
        self.menuBtn.destroy()
        self.menu.destroy()
        self.spin_box.destroy()
        self.order_st_lb.destroy()
        self.destroy_btn.destroy()
        self.func()  # Call callback function
