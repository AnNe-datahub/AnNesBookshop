import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os
import database

BG_MAIN  = "#C9B59C"
BG_LIGHT = "#f9f6e8"
BG_PANEL = "#A18D6D"
FG_DARK  = "#594a47"
FG_LIGHT = "#f9f6e8"

CATEGORIES = ["All", "Fiction", "Non-Fiction",
              "Children's Books", "Science and Fiction",
              "History and Biography", "Self Help",
              "Classics", "Others"]

DOMAINS = ["Product ID", "Title",
           "Product Category", "Product Barcode"]


class ProductReportWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("An Ne's Bookshop - [Products Report]")
        self.state("zoomed")
        self.configure(bg=BG_MAIN)
        self.bc_img = None
        self.build_ui()
        self.load_products()
        self.load_sales_summary()

    # UI
    def build_ui(self):
        # Header
        header = tk.Frame(self, bg=BG_LIGHT, height=90)
        header.pack(fill="x")
        header.pack_propagate(False)

        try:
            logo_img = Image.open("assets/anne_logo.png").resize(
                (100, 100), Image.Resampling.LANCZOS)
            self.logo = ImageTk.PhotoImage(logo_img)
            tk.Label(header, image=self.logo,
                     bg=BG_LIGHT).place(x=10, y=8)
        except:
            pass

        tk.Label(header, text="An Ne's Bookshop",
                 font=("Baskerville Old Face", 32, "bold"),
                 bg=BG_LIGHT,
                 fg=FG_DARK).place(relx=0.5, rely=0.5,
                                   anchor="center")

        # Body — left and right
        body = tk.Frame(self, bg=BG_MAIN)
        body.pack(fill="both", expand=True, padx=8, pady=6)

        body.columnconfigure(0, weight=3)
        body.columnconfigure(1, weight=2)
        body.rowconfigure(0, weight=1)

        # LEFT
        left = tk.Frame(body, bg=BG_MAIN)
        left.grid(row=0, column=0, sticky="nsew",
                  padx=(0, 4))
        self.build_left(left)

        # RIGHT
        right = tk.Frame(body, bg=BG_MAIN)
        right.grid(row=0, column=1, sticky="nsew")
        self.build_right(right)

    def build_left(self, parent):
        # Products Details label
        tk.Label(parent, text="Products Details:",
                 font=("Arial", 15, "bold"),
                 bg=BG_MAIN, fg=FG_DARK).pack(
            anchor="w", pady=(4, 2))

        # Products grid
        cols = ("ProductID", "Barcode", "ProductName",
                "Category", "Price", "Cost",
                "StockQuantity", "DateAdded", "Description")

        self.products_tree = ttk.Treeview(
            parent, columns=cols,
            show="headings", height=12)

        for col in cols:
            self.products_tree.heading(col, text=col)
            self.products_tree.column(col, width=110,
                                      anchor="center")

        sx1 = ttk.Scrollbar(parent, orient="horizontal",
                            command=self.products_tree.xview)
        sy1 = ttk.Scrollbar(parent, orient="vertical",
                            command=self.products_tree.yview)
        self.products_tree.configure(
            xscrollcommand=sx1.set,
            yscrollcommand=sy1.set)

        sy1.pack(side="right", fill="y")
        self.products_tree.pack(fill="both", expand=True)
        sx1.pack(fill="x")

        self.products_tree.bind(
            "<ButtonRelease-1>", self.on_product_click)

    def build_right(self, parent):
        # Top controls: Refresh + Category
        controls = tk.Frame(parent, bg=BG_MAIN)
        controls.pack(fill="x", pady=(4, 6))

        # Category filter (left side)
        self.category_var = tk.StringVar(value="All")
        cat_combo = ttk.Combobox(controls,
                                 textvariable=self.category_var,
                                 values=CATEGORIES,
                                 width=30, state="readonly",
                                 font=("Arial", 11))
        cat_combo.pack(side="left", padx=(0, 6), ipady=3)
        cat_combo.bind("<<ComboboxSelected>>",
                       self.on_category_change)

        # Refresh button (right of category)
        tk.Button(controls, text="Refresh",
                  command=self.refresh,
                  bg=BG_PANEL, fg=FG_LIGHT,
                  font=("Arial", 11),
                  width=12).pack(side="left", ipady=3)

        # Search row
        search_frame = tk.Frame(parent, bg=BG_MAIN)
        search_frame.pack(fill="x", pady=(0, 6))

        # Domain dropdown
        self.domain_var = tk.StringVar(value="Product Barcode")
        ttk.Combobox(search_frame,
                     textvariable=self.domain_var,
                     values=DOMAINS,
                     width=18,
                     state="readonly",
                     font=("Arial", 11)).pack(
            side="left", padx=(0, 4), ipady=3)

        # Search entry
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame,
                                textvariable=self.search_var,
                                bg=BG_PANEL, fg=FG_LIGHT,
                                font=("Arial", 11),
                                width=28)
        search_entry.pack(side="left", padx=(0, 4), ipady=3)
        search_entry.bind("<Return>",
                          lambda e: self.search_product())

        # Search button on the RIGHT
        tk.Button(search_frame, text="🔍",
                  command=self.search_product,
                  bg=BG_PANEL, fg=FG_LIGHT,
                  font=("Arial", 20)).pack(side="right")

        # ── Barcode image ──
        barcode_frame = tk.Frame(parent, bg=BG_PANEL,
                                 height=100,
                                 relief="sunken", bd=1)
        barcode_frame.pack(fill="x", pady=(0, 2))
        barcode_frame.pack_propagate(False)
        self.barcode_label = tk.Label(barcode_frame,
                                      bg=BG_PANEL)
        self.barcode_label.pack(fill="both", expand=True)

        tk.Label(parent, text="Barcode",
                 bg=BG_MAIN, fg=FG_DARK,
                 font=("Arial", 11, "italic")).pack(pady=(0, 4))

        # ── Sales Details ──
        tk.Label(parent, text="Sales Details:",
                 font=("Arial", 13, "bold"),
                 bg=BG_MAIN,
                 fg=FG_DARK).pack(anchor="w", pady=(4, 2))

        sales_cols = ("ProductID", "ProductName",
                      "Quantity", "StockNow",
                      "SaleDate", "TransactionNo")

        self.sales_tree = ttk.Treeview(
            parent, columns=sales_cols,
            show="headings", height=14)

        for col in sales_cols:
            self.sales_tree.heading(col, text=col)
            self.sales_tree.column(col, width=85,
                                   anchor="center")

        sx2 = ttk.Scrollbar(parent, orient="horizontal",
                             command=self.sales_tree.xview)
        sy2 = ttk.Scrollbar(parent, orient="vertical",
                             command=self.sales_tree.yview)
        self.sales_tree.configure(
            xscrollcommand=sx2.set,
            yscrollcommand=sy2.set)

        sy2.pack(side="right", fill="y")
        self.sales_tree.pack(fill="both", expand=True)
        sx2.pack(fill="x")

    #  LOAD DATA
    def load_products(self):
        for row in self.products_tree.get_children():
            self.products_tree.delete(row)
        rows = database.get_all_products()
        for row in rows:
            self.products_tree.insert(
                "", "end",
                values=(row[0], row[1], row[2],
                        row[3], row[4], row[5],
                        row[6], row[7], row[8]))

    def load_sales_summary(self):
        for row in self.sales_tree.get_children():
            self.sales_tree.delete(row)
        rows = database.get_all_sales()
        if rows:
            for row in rows:
                self.sales_tree.insert("", "end",
                                       values=tuple(row))
        #else:
            #messagebox.showinfo(
                #"Info",
                #"No sales data yet. "
                #"Start selling to see sales details!")

    # EVENTS
    def on_product_click(self, event):
        selected = self.products_tree.focus()
        if not selected:
            return
        values = self.products_tree.item(selected, "values")
        if not values:
            return
        product_id = values[0]

        # Load sales for this product
        rows = database.get_sales_by_product(product_id)
        for row in self.sales_tree.get_children():
            self.sales_tree.delete(row)
        if rows:
            for row in rows:
                self.sales_tree.insert("", "end",
                                       values=tuple(row))

        # Load barcode image
        row = database.get_product_by_id(product_id)
        if row:
            bc = row[11] if len(row) > 11 else ""
            if bc and os.path.exists(str(bc)):
                img = Image.open(bc).resize(
                    (300, 85), Image.Resampling.LANCZOS)
                self.bc_img = ImageTk.PhotoImage(img)
                self.barcode_label.config(image=self.bc_img)
            else:
                self.barcode_label.config(image="")

    def on_category_change(self, event):
        self.barcode_label.config(image="")
        category = self.category_var.get()
        rows = database.get_products_by_category(category)
        for row in self.products_tree.get_children():
            self.products_tree.delete(row)
        for row in rows:
            self.products_tree.insert(
                "", "end",
                values=(row[0], row[1], row[2],
                        row[3], row[4], row[5],
                        row[6], row[7], row[8]))

    def search_product(self):
        keyword = self.search_var.get().strip()
        domain = self.domain_var.get()
        if not keyword:
            return

        rows = database.search_products(keyword, domain)
        for row in self.products_tree.get_children():
            self.products_tree.delete(row)

        for row in rows:
            self.products_tree.insert(
                "", "end",
                values=(row[0], row[1], row[2],
                        row[3], row[4], row[5],
                        row[6], row[7], row[8]))

            # Show barcode of first result
            bc = row[11] if len(row) > 11 else ""
            if bc and os.path.exists(str(bc)):
                img = Image.open(bc).resize(
                    (300, 85), Image.Resampling.LANCZOS)
                self.bc_img = ImageTk.PhotoImage(img)
                self.barcode_label.config(image=self.bc_img)
                break

    def refresh(self):
        self.load_products()
        self.load_sales_summary()
        self.barcode_label.config(image="")
        self.category_var.set("All")
        self.search_var.set("")
        messagebox.showinfo("Refresh", "Data refreshed!", parent = self)