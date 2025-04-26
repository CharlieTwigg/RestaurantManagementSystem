# Import standard libraries
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from sqlite3 import Error
import os
import webbrowser

# Import HTML parsing library
from bs4 import BeautifulSoup

# Import database handler
from Database import Database


class PrintOrders(tk.Toplevel):
    """
    Window for printing order receipts.
    Allows staff to view and print receipts for completed orders by table.
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.init_database()  # Initialize database connection

        self.order_ls = []  # List to store order items

        # Configure window dimensions and position
        self.win_width = 640
        self.win_height = 470
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

        # Create print orders section
        self.cst_lbl = ttk.LabelFrame(self.main_frame, text="Print Orders")
        self.cst_lbl.grid(column=0, row=0, columnspan=4,
                          sticky=tk.NSEW, padx=10)

        # Get facility information
        self.fac_info = self.retrieve_fac_info()

        # Create and position facility name label
        self.fc_name = ttk.Label(
            self.cst_lbl,
            text=f"\"{self.fac_info[0]}\"",
            font="Helvetica 14 bold"
        )
        self.fc_name.grid(column=1, row=0)

        # Create table number input section
        self.tb_name = ttk.Label(self.cst_lbl, text="Table number:")
        self.tb_name.grid(column=1, row=1)

        # Set up table number validation
        vcmd_tn = (self.register(self.callback_table_num))

        # Create table number entry with validation
        self.tb_name_entry = ttk.Entry(
            self.cst_lbl,
            width=4,
            validate='all',
            validatecommand=(vcmd_tn, "%P")
        )
        self.tb_name_entry.grid(row=1, column=1, padx=(150, 0))

        # Create scrollbar for treeview
        self.tr_v_vscr = ttk.Scrollbar(self.cst_lbl, orient="vertical")

        # Configure treeview columns
        self.tr_view_columns = ('id', 'name', 'quantity', 'tot_price')
        self.tr_view = ttk.Treeview(
            self.cst_lbl,
            columns=self.tr_view_columns,
            show='headings',
            height=15,
            selectmode='browse',
            yscrollcommand=self.tr_v_vscr.set
        )
        
        # Set up column widths and alignments
        self.tr_view.column('id', width=50, anchor=tk.CENTER)
        self.tr_view.column('name', width=200, anchor=tk.CENTER)
        self.tr_view.column('quantity', width=100, anchor=tk.CENTER)
        self.tr_view.column('tot_price', width=200, anchor=tk.CENTER)

        # Set column headers
        self.tr_view.heading('id', text="ID")
        self.tr_view.heading('name', text="Product Name")
        self.tr_view.heading('quantity', text="Quantity")
        self.tr_view.heading('tot_price', text="Total Price(ft)")

        # Position treeview and scrollbar
        self.tr_view.grid(column=0, row=3, rowspan=6,
                          columnspan=3, pady=10, padx=10)
        self.tr_v_vscr.config(command=self.tr_view.yview)
        self.tr_v_vscr.grid(column=3, row=3, rowspan=6,  sticky=tk.NS)

        # Initialize row counter
        self.row_count = tk.IntVar()
        self.row_count.set(1)

        # Create control buttons
        self.load_orders_btn = ttk.Button(
            self.main_frame, text="Load orders", command=self.load_orders)
        self.load_orders_btn.grid(column=0, row=2, padx=(50, 0), pady=10)

        self.close_btn = ttk.Button(
            self.main_frame, text='Clear', command=self.clear_all)
        self.close_btn.grid(column=1, row=2, padx=(50, 0), pady=10)

        self.print_receipt_btn = ttk.Button(
            self.main_frame,
            text='Print receipt',
            state=tk.DISABLED,
            command=self.print_receipt
        )
        self.print_receipt_btn.grid(column=2, row=2, padx=(50, 0), pady=10)

    def init_database(self):
        """Initialize database connection"""
        self.fac_db = Database("restaurant.db")

    def load_orders(self):
        """Load and display orders for selected table"""
        try:
            self.t_num = self.tb_name_entry.get()
            if self.t_num:
                # Query orders for selected table
                load_query = """SELECT id, product_name, SUM(order_quantity) as order_quantity, SUM(order_price) as order_price FROM cooked_orders WHERE table_num = ?  GROUP BY product_name"""
                res = self.fac_db.read_val(load_query, (self.t_num))
                if res:
                    # Display orders in treeview
                    for r in res:
                        self.tr_view.insert("", tk.END, values=(
                            r[0], r[1], r[2], f"{r[3]:.2f}"))
                    self.print_receipt_btn.config(state=tk.ACTIVE)
                else:
                    messagebox.showwarning(
                        "No orders", f"No order has been cooked for table №{self.t_num}")
                    self.print_receipt_btn.config(state=tk.DISABLED)
            else:
                messagebox.showerror(
                    "Empty imput field", "Please fill in the table number to get orders!")
                self.print_receipt_btn.config(state=tk.DISABLED)

        except Error as e:
            print(e)

    def html_order(self, top_pad, name, quantity, price):
        """Generate HTML elements for an order item"""
        # Create HTML spans for product details with positioning
        p_name = f"<span style='top:{150+(top_pad * 20)}pt; left:85pt; position:absolute; font-size:20pt;'>{name}</span>"
        p_quantity = f"<span style='top:{150+(top_pad * 20)}pt; left:275pt; position:absolute; font-size:20pt;'>x{quantity}</span>"
        p_price = f"<span style='top:{150+(top_pad * 20)}pt; right:85pt; position:absolute; font-size:20pt;'>{price}</span>"
        return (BeautifulSoup(p_name, "html.parser"), BeautifulSoup(p_quantity, "html.parser"), BeautifulSoup(p_price, "html.parser"))

    def print_receipt(self):
        """Generate and display HTML receipt"""
        tags = []
        ind = 1
        tot_p = 0  # Total price
        tot_q = 0  # Total quantity
        
        # Process each order item
        for child in self.tr_view.get_children():
            val = self.tr_view.item(child)['values']
            tot_p += float(val[3])
            tot_q += int(val[2])
            tag = self.html_order(ind, val[1], val[2], val[3])
            tags.append(tag)
            ind += 1
            
        # Create total summary
        total_price = f"<span style='top:{170+(len(tags) * 40)}pt; left:85pt; position:absolute; font-size:20pt;'>Total: total ordered products {tot_q}, total price to be paid: {tot_p}</span>"

        # Load and modify HTML template
        with open("order_template.html") as html_doc:
            doc = BeautifulSoup(html_doc, 'html.parser')
            doc.find(text="Fac_name").replace_with(f"\"{self.fac_info[0]}\"")
            doc.find(text="t_num").replace_with(f"Table №{self.t_num}")
            
            # Add order items
            for tag in tags:
                doc.div.append(tag[0])
                doc.div.append(tag[1])
                doc.div.append(tag[2])
                
            # Add separator and total
            doc.div.append(BeautifulSoup(
                f"<hr style='top:{170+(len(tags)*30)}pt;' />", "html.parser"))
            doc.div.append(BeautifulSoup(total_price, "html.parser"))

            str_doc = str(doc.prettify())
            
        # Save and open receipt
        with open(f"order_{self.t_num}.html", "w+", encoding='utf-8') as p_or_fl:
            p_or_fl.write(str_doc)

        webbrowser.open_new_tab(f"order_{self.t_num}.html")
        self.clear_all()

    def clear_all(self):
        """Clear all entries and displayed orders"""
        self.tb_name_entry.delete(0, tk.END)
        for child in self.tr_view.get_children():
            self.tr_view.delete(child)
        self.print_receipt_btn.config(state=tk.DISABLED)

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

    def destroy(self):
        """Clean up and destroy window"""
        super().destroy()
