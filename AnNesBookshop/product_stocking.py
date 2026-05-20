import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
from tkcalendar import DateEntry
from datetime import datetime
import barcode
from barcode.writer import ImageWriter
import qrcode
import os
import database

BG_MAIN  = "#C9B59C"
BG_LIGHT = "#f9f6e8"
BG_PANEL = "#D9CFC7"
FG_DARK  = "#594a47"

CATEGORIES = [
    "Fiction", "Non-Fiction", "Children's Books",
    "Science and Fiction", "History and Biography",
    "Self Help", "Classics", "Others"
]


class ProductStockingWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("An Ne's Bookshop - [Product Stocking]")
        self.state("zoomed")
        self.configure(bg=BG_MAIN)

        # image references
        self.prod_img = None
        self.bc_img   = None
        self.qr_img   = None

        # file paths
        self.pic_path     = ""
        self.barcode_path = ""
        self.qr_path      = ""

        # StringVars
        self.search_var       = tk.StringVar()
        self.product_id_var   = tk.StringVar(value="Auto-generated")
        self.product_name_var = tk.StringVar()
        self.barcode_var      = tk.StringVar()
        self.price_var        = tk.StringVar()
        self.cost_var         = tk.StringVar()
        self.stock_var        = tk.StringVar()
        self.author_var       = tk.StringVar()
        self.publisher_var    = tk.StringVar()
        self.isbn_var         = tk.StringVar()
        self.edition_var      = tk.StringVar()
        self.year_var         = tk.StringVar()
        self.picpath_var      = tk.StringVar()
        self.supplier_var     = tk.StringVar()
        self.category_var     = tk.StringVar(value=CATEGORIES[0])

        self._build_header()

        # FRAME 3
        self._build_frame_database()

        # Frame 1 + Frame 2
        body = tk.Frame(self, bg=BG_MAIN)
        body.pack(side="top", fill="both", expand=True, padx=6, pady=(4, 2))

        self._build_frame_buttons(body)
        self._build_frame_details(body)

        self.load_grid()

    #  HEADER

    def _build_header(self):
        header = tk.Frame(self, bg=BG_LIGHT, height=90)
        header.pack(side="top", fill="x")
        header.pack_propagate(False)

        try:
            logo_img = Image.open("assets/anne_logo.png").resize(
                (90, 90), Image.Resampling.LANCZOS)
            self.logo = ImageTk.PhotoImage(logo_img)
            tk.Label(header, image=self.logo, bg=BG_LIGHT).place(x=10, y=7)
        except Exception:
            pass

        tk.Label(
            header,
            text="An Ne's Bookshop",
            font=("Baskerville Old Face", 30, "bold"),
            bg=BG_LIGHT, fg=FG_DARK
        ).place(relx=0.5, rely=0.5, anchor="center")

    #  FRAME 3 – DATABASE GRID

    def _build_frame_database(self):
        self.frame_database = tk.Frame(self, bg=BG_MAIN, height=200)
        self.frame_database.pack(side="bottom", fill="x", padx=6, pady=(2, 6))
        self.frame_database.pack_propagate(False)

        cols = (
            "ProductID", "Barcode", "ProductName", "Category",
            "Price", "Cost", "StockQuantity", "DateAdded",
            "Description", "Supplier", "PicPathText"
        )

        self.tree = ttk.Treeview(self.frame_database,
                                 columns=cols, show="headings", height=7)
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor="center")

        sy = ttk.Scrollbar(self.frame_database, orient="vertical",
                           command=self.tree.yview)
        sx = ttk.Scrollbar(self.frame_database, orient="horizontal",
                           command=self.tree.xview)
        self.tree.configure(yscrollcommand=sy.set, xscrollcommand=sx.set)

        sy.pack(side="right",  fill="y")
        sx.pack(side="bottom", fill="x")
        self.tree.pack(side="top", fill="both", expand=True)

        self.tree.bind("<ButtonRelease-1>", self.on_row_click)


    #  FRAME 1 – BUTTONS + BARCODE + QR

    def _build_frame_buttons(self, parent):
        self.frame_buttons = tk.Frame(parent, bg=BG_PANEL, width=250)
        self.frame_buttons.pack(side="left", fill="y", padx=(0, 4))
        self.frame_buttons.pack_propagate(False)

        p = self.frame_buttons

        tk.Entry(p, textvariable=self.search_var,
                 bg=BG_LIGHT, fg=FG_DARK, font=("Arial", 11),
                 width=22).pack(padx=10, pady=(10, 4))

        for text, cmd in [
            ("Search", self.search_product),
            ("Save",   self.save_product),
            ("Edit",   self.edit_product),
            ("Delete", self.delete_product),
            ("Clear",  self.clear_form),
            ("Cancel", self.destroy),
        ]:
            tk.Button(p, text=text, command=cmd,
                      bg=BG_MAIN, fg=FG_DARK,
                      font=("Arial", 12, "bold"), width=18,
                      height=2, relief="raised", bd=2).pack(pady=2, padx=10)

        tk.Frame(p, bg=BG_PANEL, height=20).pack()

        tk.Label(p, text="Barcode:", bg=BG_PANEL, fg=FG_DARK,
                 font=("Arial", 9, "bold")).pack(anchor="w", padx=12)
        barcode_frame = tk.Frame(p, bg="white", relief="sunken",
                                 bd=1, width=200, height=65)
        barcode_frame.pack(padx=10, pady=(2, 6))
        barcode_frame.pack_propagate(False)
        self.barcode_label = tk.Label(barcode_frame, bg="white")
        self.barcode_label.pack(fill="both", expand=True)

        tk.Button(p, text="Generate QR", command=self.generate_codes,
                  bg=BG_MAIN, fg=FG_DARK,
                  font=("Arial", 12, "bold"), width=18,
                  height=2, relief="raised", bd=2).pack(pady=2, padx=10)

        tk.Frame(p, bg=BG_PANEL, height=20).pack()

        tk.Label(p, text="QR Code:", bg=BG_PANEL, fg=FG_DARK,
                 font=("Arial", 9, "bold")).pack(anchor="w", padx=12)
        qr_frame = tk.Frame(p, bg="white", relief="sunken",
                            bd=1, width=150, height=150)
        qr_frame.pack(padx=10, pady=(2, 8))
        qr_frame.pack_propagate(False)
        self.qr_label = tk.Label(qr_frame, bg="white")
        self.qr_label.pack(fill="both", expand=True)


    #  FRAME 2 – PRODUCT DETAILS

    def _build_frame_details(self, parent):
        self.frame_details = tk.Frame(parent, bg=BG_LIGHT)
        self.frame_details.pack(side="left", fill="both", expand=True)


        img_col = tk.Frame(self.frame_details, bg=BG_PANEL, width=270)
        img_col.pack(side="left", fill="y")
        img_col.pack_propagate(False)

        tk.Frame(img_col, bg=BG_PANEL, height=10).pack()

        img_frame = tk.Frame(img_col, bg="white", relief="sunken",
                             bd=1, width=240, height=300)
        img_frame.pack(padx=14, pady=(8, 4))
        img_frame.pack_propagate(False)
        self.product_img_label = tk.Label(img_frame, bg="white")
        self.product_img_label.pack(fill="both", expand=True)

        tk.Button(img_col, text="Browse", command=self.browse_image,
                  bg=BG_LIGHT, fg=FG_DARK,
                  font=("Arial", 10), width=14).pack(pady=5)

        tk.Label(img_col, text="Description:", bg=BG_PANEL, fg=FG_DARK,
                 font=("Arial", 10, "bold"), anchor="w").pack(fill="x", padx=14)
        self.desc_text = tk.Text(img_col, height=10, width=30,
                                 bg=BG_LIGHT, fg=FG_DARK, font=("Arial", 9))
        self.desc_text.pack(padx=14, pady=(2, 6))

        tk.Label(img_col, text="Supplier:", bg=BG_PANEL, fg=FG_DARK,
                 font=("Arial", 10, "bold"), anchor="w").pack(fill="x", padx=14)
        tk.Entry(img_col, textvariable=self.supplier_var,
                 bg=BG_LIGHT, fg=FG_DARK,
                 font=("Arial", 10), width=28).pack(padx=14, pady=(2, 6))


        fields_col = tk.Frame(self.frame_details, bg=BG_LIGHT)
        fields_col.pack(side="left", fill="both", expand=True, padx=20, pady=15)

        fields_col.columnconfigure(1, weight=1)

        field_defs = [
            ("Product ID:",     self.product_id_var,    True),
            ("Title:",          self.product_name_var,  False),
            ("Author:",         self.author_var,        False),
            ("ISBN:",           self.isbn_var,          False),
            ("Edition:",        self.edition_var,       False),
            ("Publisher:",      self.publisher_var,     False),
            ("Year:",           self.year_var,          False),
            ("Category:",       None,                   False),
            ("Price:",          self.price_var,         False),
            ("Cost:",           self.cost_var,          False),
            ("Stock Quantity:", self.stock_var,         False),
            ("Date Added:",     None,                   False),
            ("Barcode:",        self.barcode_var,       False),
        ]

        for i, (label, var, readonly) in enumerate(field_defs):
            tk.Label(fields_col, text=label,
                     bg=BG_LIGHT, fg=FG_DARK,
                     font=("Arial", 10, "bold"),
                     width=14, anchor="e").grid(
                row=i, column=0, sticky="e", pady=5, padx=(0, 8))

            if label == "Category:":
                ttk.Combobox(fields_col, textvariable=self.category_var,
                             values=CATEGORIES, width=38,
                             state="readonly").grid(
                    row=i, column=1, sticky="ew", pady=5)

            elif label == "Date Added:":
                self.date_picker = DateEntry(
                    fields_col,
                    background=BG_LIGHT, foreground=FG_DARK,
                    date_pattern="mm/dd/yyyy", width=38)
                self.date_picker.grid(row=i, column=1, sticky="ew", pady=5)

            else:
                e = tk.Entry(fields_col, textvariable=var,
                             bg=BG_LIGHT, fg=FG_DARK,
                             font=("Arial", 10), width=35)
                if readonly:
                    e.config(state="readonly")
                e.grid(row=i, column=1, sticky="ew", pady=5)


    #  DATA HELPERS
    def load_grid(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for row in database.get_all_products():
            self.tree.insert("", "end", values=tuple(row))

    def on_row_click(self, event):
        selected = self.tree.focus()
        if not selected:
            return
        values = self.tree.item(selected, "values")
        if not values:
            return
        product_id = values[0]
        row = database.get_product_by_id(product_id)
        if row:
            self.fill_form(tuple(row))

    def fill_form(self, values):
        print("Values received:", values)

        self.product_id_var.set(str(values[0]))
        self.barcode_var.set(str(values[1]) if values[1] else "")
        self.product_name_var.set(str(values[2]) if values[2] else "")
        self.category_var.set(str(values[3]) if values[3] else CATEGORIES[0])
        self.price_var.set(str(values[4]) if values[4] else "")
        self.cost_var.set(str(values[5]) if values[5] else "")
        self.stock_var.set(str(values[6]) if values[6] else "")
        self.author_var.set(str(values[13]) if values[13] else "")
        self.publisher_var.set(str(values[14]) if values[14] else "")
        self.isbn_var.set(str(values[15]) if values[15] else "")
        self.edition_var.set(str(values[16]) if values[16] else "")
        self.year_var.set(str(values[17]) if values[17] else "")
        self.supplier_var.set(str(values[9]) if values[9] else "")
        self.picpath_var.set(str(values[10]) if values[10] else "")

        self.desc_text.delete("1.0", "end")
        self.desc_text.insert("1.0", str(values[8]) if values[8] else "")

        # Product image
        pic = values[10] if values[10] else ""
        if pic and os.path.exists(str(pic)):
            img = Image.open(pic).resize((210, 180), Image.Resampling.LANCZOS)
            self.prod_img = ImageTk.PhotoImage(img)
            self.product_img_label.config(image=self.prod_img)
        else:
            self.product_img_label.config(image="")

        # Barcode image
        bc = values[11] if values[11] else ""
        if bc and os.path.exists(str(bc)):
            img = Image.open(bc).resize((160, 55), Image.Resampling.LANCZOS)
            self.bc_img = ImageTk.PhotoImage(img)
            self.barcode_label.config(image=self.bc_img)
        else:
            self.barcode_label.config(image="")

        # QR image
        qr = values[12] if values[12] else ""
        if qr and os.path.exists(str(qr)):
            img = Image.open(qr).resize((110, 110), Image.Resampling.LANCZOS)
            self.qr_img = ImageTk.PhotoImage(img)
            self.qr_label.config(image=self.qr_img)
        else:
            self.qr_label.config(image="")

        self.update_idletasks()
        self.after(50, self._refresh_fields)

    def _refresh_fields(self):
        self.update()
        self.update_idletasks()
        self.product_id_var.set(self.product_id_var.get())
        self.product_name_var.set(self.product_name_var.get())
        self.barcode_var.set(self.barcode_var.get())
        self.price_var.set(self.price_var.get())
        self.cost_var.set(self.cost_var.get())
        self.stock_var.set(self.stock_var.get())
        self.author_var.set(self.author_var.get())
        self.publisher_var.set(self.publisher_var.get())
        self.isbn_var.set(self.isbn_var.get())
        self.edition_var.set(self.edition_var.get())
        self.year_var.set(self.year_var.get())
        self.supplier_var.set(self.supplier_var.get())


    #  ACTIONS

    def browse_image(self):
        path = filedialog.askopenfilename(
            parent=self,
            filetypes=[("Image Files", "*.jpg *.jpeg *.png *.bmp"),
                       ("All Files", "*.*")])
        if path:
            self.pic_path = path
            self.picpath_var.set(path)
            img = Image.open(path).resize((210, 180), Image.Resampling.LANCZOS)
            self.prod_img = ImageTk.PhotoImage(img)
            self.product_img_label.config(image=self.prod_img)

    def generate_codes(self):
        barcode_text = self.barcode_var.get().strip()
        if not barcode_text:
            messagebox.showwarning("Input Required",
                                   "Please enter a Barcode first!",
                                   parent=self)
            return
        self.barcode_path = self._generate_barcode(barcode_text)
        self.qr_path      = self._generate_qr(barcode_text)

    def _generate_barcode(self, barcode_text):
        try:
            os.makedirs(r"C:\POSSystem\Barcodes", exist_ok=True)
            code128 = barcode.get("code128", barcode_text, writer=ImageWriter())
            ts  = datetime.now().strftime("%Y%m%d%H%M%S")
            fp  = rf"C:\POSSystem\Barcodes\BC_{barcode_text}_{ts}"
            code128.save(fp)
            full = fp + ".png"
            img = Image.open(full).resize((160, 55), Image.Resampling.LANCZOS)
            self.bc_img = ImageTk.PhotoImage(img)
            self.barcode_label.config(image=self.bc_img)
            return full
        except Exception as ex:
            messagebox.showerror("Error", f"Barcode error: {ex}", parent=self)
            return ""

    def _generate_qr(self, barcode_text):
        try:
            os.makedirs(r"C:\POSSystem\QRCodes", exist_ok=True)
            qr_data = (
                f"=== PRODUCT INFO ===\n"
                f"Name: {self.product_name_var.get()}\n"
                f"Barcode: {barcode_text}\n"
                f"Category: {self.category_var.get()}\n"
                f"Price: ₱{self.price_var.get()}\n"
                f"Description: {self.desc_text.get('1.0', 'end').strip()}\n"
                f"Supplier: {self.supplier_var.get()}"
            )
            qr = qrcode.make(qr_data)
            ts  = datetime.now().strftime("%Y%m%d%H%M%S")
            fp  = rf"C:\POSSystem\QRCodes\QR_{barcode_text}_{ts}.png"
            qr.save(fp)
            img = Image.open(fp).resize((110, 110), Image.Resampling.LANCZOS)
            self.qr_img = ImageTk.PhotoImage(img)
            self.qr_label.config(image=self.qr_img)
            return fp
        except Exception as ex:
            messagebox.showerror("Error", f"QR error: {ex}", parent=self)
            return ""

    def save_product(self):
        # VALIDATION
        if not self.product_name_var.get().strip():
            messagebox.showwarning("Required Field",
                                   "Please enter the Product Title!",
                                   parent=self)
            return
        if not self.barcode_var.get().strip():
            messagebox.showwarning("Required Field",
                                   "Please enter the Barcode!",
                                   parent=self)
            return
        if not self.price_var.get().strip():
            messagebox.showwarning("Required Field",
                                   "Please enter the Price!",
                                   parent=self)
            return
        if not self.stock_var.get().strip():
            messagebox.showwarning("Required Field",
                                   "Please enter the Stock Quantity!",
                                   parent=self)
            return
        if not self.category_var.get().strip():
            messagebox.showwarning("Required Field",
                                   "Please select a Category!",
                                   parent=self)
            return

        # VALIDATE NUMBERS
        try:
            float(self.price_var.get())
        except ValueError:
            messagebox.showwarning("Invalid Input",
                                   "Price must be a valid number!",
                                   parent=self)
            return
        try:
            int(self.stock_var.get())
        except ValueError:
            messagebox.showwarning("Invalid Input",
                                   "Stock Quantity must be a valid number!",
                                   parent=self)
            return
        if self.cost_var.get().strip():
            try:
                float(self.cost_var.get())
            except ValueError:
                messagebox.showwarning("Invalid Input",
                                       "Cost must be a valid number!",
                                       parent=self)
                return

        try:
            barcode_text = self.barcode_var.get().strip()
            bp = self._generate_barcode(barcode_text) \
                if barcode_text else ""
            qp = self._generate_qr(barcode_text) \
                if barcode_text else ""
            data = (
                barcode_text,
                self.product_name_var.get(),
                self.category_var.get(),
                float(self.price_var.get() or 0),
                float(self.cost_var.get() or 0),
                int(self.stock_var.get() or 0),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                self.desc_text.get("1.0", "end").strip(),
                self.supplier_var.get(),
                self.picpath_var.get(),
                bp, qp,
                self.author_var.get(),
                self.publisher_var.get(),
                self.isbn_var.get(),
                self.edition_var.get(),
                self.year_var.get(),
            )
            database.save_product(data)
            messagebox.showinfo("Success", "Product saved!",
                                parent=self)
            self.clear_form()
            self.load_grid()
        except Exception as ex:
            messagebox.showerror("Error",
                                 f"Error saving product: {ex}",
                                 parent=self)

    def search_product(self):
        keyword = self.search_var.get().strip()
        if not keyword:
            return

        row = database.get_product_by_id(keyword)

        if not row:
            row = database.get_product_by_barcode(keyword)

        if not row:
            results = database.search_products(keyword, domain="Title")
            if results:
                row = results[0]

        if row:
            self.fill_form(tuple(row))
        else:
            messagebox.showwarning("Not Found",
                                   "Product not found!",
                                   parent=self)

    def edit_product(self):
        pid = self.product_id_var.get()
        if pid == "Auto-generated" or not pid:
            messagebox.showwarning("No Product Selected",
                                   "Please search for a product first!",
                                   parent=self)
            return
        try:
            data = (
                self.barcode_var.get(),
                self.product_name_var.get(),
                self.category_var.get(),
                float(self.price_var.get() or 0),
                float(self.cost_var.get() or 0),
                int(self.stock_var.get() or 0),
                self.date_picker.get_date().strftime("%Y-%m-%d %H:%M:%S"),
                self.desc_text.get("1.0", "end").strip(),
                self.supplier_var.get(),
                self.picpath_var.get(),
                getattr(self, "barcode_path", ""),
                getattr(self, "qr_path", ""),
                self.author_var.get(),
                self.publisher_var.get(),
                self.isbn_var.get(),
                self.edition_var.get(),
                self.year_var.get(),
                int(pid),
            )
            database.update_product(data)
            messagebox.showinfo("Update", "Product updated successfully!",
                                parent=self)
            self.clear_form()
            self.load_grid()
        except Exception as ex:
            messagebox.showerror("Error", f"Error updating: {ex}", parent=self)

    def delete_product(self):
        pid = self.product_id_var.get()
        if pid == "Auto-generated" or not pid:
            messagebox.showwarning("No Product Selected",
                                   "Please search for a product first!",
                                   parent=self)
            return
        if messagebox.askyesno("Confirm Delete",
                               "Are you sure you want to delete this product?",
                               parent=self):
            database.delete_product(int(pid))
            messagebox.showinfo("Delete", "Product deleted successfully!",
                                parent=self)
            self.clear_form()
            self.load_grid()

    def clear_form(self):
        self.product_id_var.set("Auto-generated")
        self.product_name_var.set("")
        self.barcode_var.set("")
        self.price_var.set("")
        self.cost_var.set("")
        self.stock_var.set("")
        self.author_var.set("")
        self.publisher_var.set("")
        self.isbn_var.set("")
        self.edition_var.set("")
        self.year_var.set("")
        self.picpath_var.set("")
        self.supplier_var.set("")
        self.category_var.set(CATEGORIES[0])
        self.desc_text.delete("1.0", "end")
        self.product_img_label.config(image="")
        self.barcode_label.config(image="")
        self.qr_label.config(image="")
        self.search_var.set("")
        self.pic_path     = ""
        self.barcode_path = ""
        self.qr_path      = ""
        from datetime import date
        self.date_picker.set_date(date.today())