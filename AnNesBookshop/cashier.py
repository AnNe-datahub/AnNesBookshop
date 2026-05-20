import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from datetime import datetime
import database
import os

BG_MAIN   = "#C9B59C"
BG_LIGHT  = "#f9f6e8"
BG_BLUE   = "#7fa7c1"
BG_PINK   = "#ecc8bb"
BG_RED    = "#E49BA6"
BG_GRAY   = "#8a9597"
BG_SCREEN = "#d9d9d9"
FG_DARK   = "#594a47"
FG_LIGHT  = "#f9f6e8"
FG_BROWN  = "#3d2817"

DISCOUNTS = ["No Discount", "Senior Citizen",
             "PWD", "With Discount Card",
             "Employee Discount"]


class CashierWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("An Ne's Bookshop - [Cashier]")
        self.state("zoomed")
        self.configure(bg=BG_MAIN)
        self.cart = []
        self.selected_index = -1
        self.item_img = None
        self.pending_qty = 1
        self.build_ui()
        self.barcode_entry.focus_set()

    def build_ui(self):
        header = tk.Frame(self, bg=BG_LIGHT, height=90)
        header.pack(fill="x")
        header.pack_propagate(False)
        try:
            logo_img = Image.open("assets/anne_logo.png").resize(
                (75, 75), Image.Resampling.LANCZOS)
            self.logo = ImageTk.PhotoImage(logo_img)
            tk.Label(header, image=self.logo, bg=BG_LIGHT).place(x=10, y=7)
        except:
            pass
        tk.Label(header, text="An Ne's Bookshop",
                 font=("Baskerville Old Face", 30, "bold"),
                 bg=BG_LIGHT, fg=FG_DARK).place(relx=0.5, rely=0.5, anchor="center")

        body = tk.Frame(self, bg=BG_MAIN)
        body.pack(fill="both", expand=True)
        body.columnconfigure(0, weight=1)
        body.columnconfigure(1, weight=0)
        body.rowconfigure(0, weight=1)

        left = tk.Frame(body, bg=BG_MAIN)
        left.grid(row=0, column=0, sticky="nsew")
        self._build_cart(left)

        right = tk.Frame(body, bg=BG_BLUE, width=430)
        right.grid(row=0, column=1, sticky="nsew")
        right.grid_propagate(False)
        right.pack_propagate(False)
        self._build_right(right)

    # ══════════════════════════════════════════════════════════
    #  LEFT
    # ══════════════════════════════════════════════════════════
    def _build_cart(self, parent):
        # Treeview — headers always align with data
        tree_frame = tk.Frame(parent, bg=BG_LIGHT)
        tree_frame.pack(fill="both", expand=True)

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Cart.Treeview",
                         background=BG_LIGHT,
                         foreground=FG_DARK,
                         fieldbackground=BG_LIGHT,
                         font=("Arial", 11),
                         rowheight=28)
        style.configure("Cart.Treeview.Heading",
                         background=BG_BLUE,
                         foreground=FG_LIGHT,
                         font=("Arial", 11, "bold"),
                         relief="flat")
        style.map("Cart.Treeview.Heading",
                  background=[("active", BG_BLUE)])
        style.map("Cart.Treeview",
                  background=[("selected", BG_BLUE)],
                  foreground=[("selected", FG_LIGHT)])

        cols = ("No.", "Product Name", "Barcode", "Qty", "Price")
        self.tree_cart = ttk.Treeview(tree_frame, columns=cols,
                                       show="headings",
                                       style="Cart.Treeview")

        self.tree_cart.heading("No.",          text="No.",          anchor="center")
        self.tree_cart.heading("Product Name", text="Product Name", anchor="w")
        self.tree_cart.heading("Barcode",      text="Barcode",      anchor="center")
        self.tree_cart.heading("Qty",          text="Qty",          anchor="center")
        self.tree_cart.heading("Price",        text="Price",        anchor="e")

        self.tree_cart.column("No.",          width=45,  minwidth=45,  anchor="center", stretch=False)
        self.tree_cart.column("Product Name", width=300, minwidth=150, anchor="w",      stretch=True)
        self.tree_cart.column("Barcode",      width=160, minwidth=120, anchor="center", stretch=False)
        self.tree_cart.column("Qty",          width=50,  minwidth=50,  anchor="center", stretch=False)
        self.tree_cart.column("Price",        width=100, minwidth=80,  anchor="e",      stretch=False)

        sy = ttk.Scrollbar(tree_frame, orient="vertical",
                           command=self.tree_cart.yview)
        self.tree_cart.configure(yscrollcommand=sy.set)

        self.tree_cart.pack(side="left", fill="both", expand=True)
        sy.pack(side="right", fill="y")

        self.tree_cart.bind("<ButtonRelease-1>", self.on_cart_click)

        # BOTTOM BAR
        bottom = tk.Frame(parent, bg=BG_BLUE)
        bottom.pack(fill="x", side="bottom")

        for label, var_name, val in [
            ("TOTAL ITEMS:",    "total_items_var", "0"),
            ("TOTAL QUANTITY:", "total_qty_var",   "0"),
            ("SUBTOTAL:",       "subtotal_var",    "₱0.00"),
        ]:
            row = tk.Frame(bottom, bg=BG_BLUE)
            row.pack(fill="x", padx=12, pady=1)
            tk.Label(row, text=label, bg=BG_BLUE, fg=FG_LIGHT,
                     font=("Arial", 11, "bold"), anchor="w").pack(side="left")
            var = tk.StringVar(value=val)
            setattr(self, var_name, var)
            tk.Label(row, textvariable=var, bg=BG_BLUE, fg=FG_LIGHT,
                     font=("Arial", 11, "bold"), anchor="e").pack(side="right")

        disc_row = tk.Frame(bottom, bg=BG_BLUE)
        disc_row.pack(fill="x", padx=12, pady=(3, 3))
        tk.Label(disc_row, text="DISCOUNT:", bg=BG_BLUE, fg=FG_LIGHT,
                 font=("Arial", 11, "bold"), anchor="w").pack(side="left")
        self.discount_var = tk.StringVar(value="No Discount")
        disc_combo = ttk.Combobox(disc_row, textvariable=self.discount_var,
                                  values=DISCOUNTS, font=("Arial", 11),
                                  state="readonly")
        disc_combo.pack(side="right", fill="x", expand=True, padx=(8, 0), ipady=5)
        disc_combo.bind("<<ComboboxSelected>>", lambda e: self.apply_discount())

        btn_row = tk.Frame(bottom, bg=FG_LIGHT)
        btn_row.pack(fill="x", padx=4, pady=6)

        for text, cmd in [
            ("Print Receipt", self.print_receipt),
            ("◀",             self.prev_page),
            ("▶",             self.next_page),
            ("Reset Receipt", self.reset_receipt),
        ]:
            tk.Button(btn_row, text=text, command=cmd,
                      bg=BG_LIGHT, fg=FG_DARK,
                      font=("Arial", 11, "bold"), height=2,
                      relief="raised", bd=2).pack(side="left", padx=3, pady=2)

        tk.Button(btn_row, text="Pay", command=self.process_payment,
                  bg=BG_RED, fg=FG_BROWN,
                  font=("Arial", 13, "bold"),
                  width=10, height=2,
                  relief="raised", bd=2).pack(side="right", padx=3, pady=2)

    # ══════════════════════════════════════════════════════════
    #  RIGHT — image top, fields+entry anchored to bottom
    # ══════════════════════════════════════════════════════════
    def _build_right(self, parent):
        # ── image fills top, expands ──
        img_frame = tk.Frame(parent, bg="white", relief="sunken", bd=1)
        img_frame.pack(side="top", fill="both", expand=True)
        self.item_img_label = tk.Label(img_frame, bg="white")
        self.item_img_label.pack(fill="both", expand=True)

        # ── QTY + BARCODE input rows ──
        input_frame = tk.Frame(parent, bg=BG_BLUE)
        input_frame.pack(side="top", fill="x", padx=8, pady=(6, 2))
        input_frame.columnconfigure(1, weight=1)

        # Quantity row
        tk.Label(input_frame, text="QTY:", bg=BG_BLUE, fg=FG_LIGHT,
                 font=("Arial", 11, "bold")).grid(
            row=0, column=0, sticky="w", padx=(0, 6), pady=2)
        self.qty_var = tk.StringVar(value="")
        qty_entry = tk.Entry(input_frame, textvariable=self.qty_var,
                             bg=BG_SCREEN, fg=FG_DARK,
                             font=("Arial", 12), width=8)
        qty_entry.grid(row=0, column=1, sticky="w", ipady=5, pady=2)
        qty_entry.bind("<Return>", lambda e: self.barcode_entry.focus_set())

        # Barcode row
        tk.Label(input_frame, text="BARCODE:", bg=BG_BLUE, fg=FG_LIGHT,
                 font=("Arial", 11, "bold")).grid(
            row=1, column=0, sticky="w", padx=(0, 6), pady=2)

        bc_frame = tk.Frame(input_frame, bg=BG_BLUE)
        bc_frame.grid(row=1, column=1, sticky="ew", pady=2)
        bc_frame.columnconfigure(0, weight=1)

        self.screen_var = tk.StringVar()
        self.barcode_entry = tk.Entry(bc_frame,
                             textvariable=self.screen_var,
                             bg=BG_SCREEN, fg=FG_DARK,
                             font=("Arial", 12))
        self.barcode_entry.grid(row=0, column=0, sticky="ew", ipady=5, padx=(0, 4))
        self.barcode_entry.bind("<Return>", lambda e: self.barcode_search())

        # keep screen_entry alias so old code still works
        self.screen_entry = self.barcode_entry

        tk.Button(bc_frame, text="X", command=self.clear_screen,
                  bg=BG_LIGHT, fg=FG_DARK,
                  font=("Arial", 11, "bold"), width=3).grid(
            row=0, column=1, padx=2, ipady=5)
        tk.Button(bc_frame, text="Enter", command=self.barcode_search,
                  bg=BG_LIGHT, fg=FG_DARK,
                  font=("Arial", 11, "bold"), width=6).grid(
            row=0, column=2, padx=2, ipady=5)

        #  fields: CASH GIVEN → CHANGE
        fields = [
            ("CASH GIVEN:",       "cash_var",        BG_BLUE, False),
            ("DISCOUNTED GIVEN:", "discounted_var",  BG_BLUE, True),
            ("GRAND TOTAL:",      "grand_total_var", BG_PINK, True),
            ("PAID:",             "paid_var",        BG_RED,  True),
            ("CHANGE:",           "change_var",      BG_GRAY, True),
        ]

        for label, var_name, bg, readonly in fields:
            f = tk.Frame(parent, bg=bg)
            f.pack(side="top", fill="x")
            f.columnconfigure(0, weight=1)
            f.columnconfigure(1, weight=1)

            tk.Label(f, text=label, bg=bg, fg=FG_BROWN,
                     font=("Arial", 11, "bold"),
                     anchor="w").grid(row=0, column=0,
                                      sticky="ew", ipady=8, padx=10)

            var = tk.StringVar(value="")
            setattr(self, var_name, var)

            e = tk.Entry(f, textvariable=var,
                         bg=bg, fg=FG_BROWN,
                         font=("Arial", 14, "bold"),
                         relief="flat", justify="right",
                         disabledbackground=bg,
                         disabledforeground=FG_BROWN)
            if readonly:
                e.config(state="disabled")
            e.grid(row=0, column=1, sticky="ew", ipady=8, padx=10)

    # ══════════════════════════════════════════════════════════
    #  SCROLL
    # ══════════════════════════════════════════════════════════
    def _scroll_all(self, *args):
        pass  # handled by treeview scrollbar

    # ══════════════════════════════════════════════════════════
    #  CART
    # ══════════════════════════════════════════════════════════
    def refresh_cart(self):
        for row in self.tree_cart.get_children():
            self.tree_cart.delete(row)
        grand_total = 0
        total_qty   = 0
        for i, item in enumerate(self.cart):
            self.tree_cart.insert("", "end", iid=str(i), values=(
                i + 1,
                item["name"],
                item["barcode"],
                item["qty"],
                f"₱{item['price']:.2f}"
            ))
            grand_total += item["price"] * item["qty"]
            total_qty   += item["qty"]
        self.total_items_var.set(str(len(self.cart)))
        self.total_qty_var.set(str(total_qty))
        self.subtotal_var.set(f"₱{grand_total:.2f}")
        self.grand_total_var.set(f"₱{grand_total:.2f}")
        self.discounted_var.set("")

    def on_cart_click(self, event):
        sel = self.tree_cart.focus()
        if not sel:
            return
        try:
            self.selected_index = int(sel)
            self.qty_var.set(str(self.cart[self.selected_index]["qty"]))
        except:
            pass

    # ══════════════════════════════════════════════════════════
    #  BARCODE SEARCH — qty-first workflow
    # ══════════════════════════════════════════════════════════
    def barcode_search(self):
        bc = self.screen_var.get().strip()
        if not bc:
            return

        # get pending qty (typed before scan), default 1
        try:
            qty = int(self.qty_var.get().strip())
            if qty <= 0:
                qty = 1
        except:
            qty = 1

        row = database.get_product_by_barcode(bc)
        if not row:
            messagebox.showwarning("Not Found",
                                   f"Product not found: {bc}",
                                   parent=self)
            self.screen_var.set("")
            self.barcode_entry.focus_set()
            return

        product_id   = row[0]
        product_name = row[2]
        price        = float(row[4])
        pic_path     = row[10] if len(row) > 10 else ""

        # show image
        if pic_path and os.path.exists(pic_path):
            img = Image.open(pic_path).resize(
                (430, 300), Image.Resampling.LANCZOS)
            self.item_img = ImageTk.PhotoImage(img)
            self.item_img_label.config(image=self.item_img)
        else:
            self.item_img_label.config(image="")

        # add to cart or increment
        for item in self.cart:
            if item["product_id"] == product_id:
                item["qty"] += qty
                self.refresh_cart()
                self.screen_var.set("")
                self.qty_var.set("")
                self.barcode_entry.focus_set()
                return

        self.cart.append({
            "product_id": product_id,
            "name":       product_name,
            "barcode":    bc,
            "price":      price,
            "qty":        qty,
        })
        self.refresh_cart()
        self.screen_var.set("")
        self.qty_var.set("")
        self.barcode_entry.focus_set()

    def enter_action(self):
        # kept for compatibility — just trigger barcode search
        self.barcode_search()

    def clear_screen(self):
        self.screen_var.set("")
        self.qty_var.set("")
        self.barcode_entry.focus_set()

    # ══════════════════════════════════════════════════════════
    #  DISCOUNT
    # ══════════════════════════════════════════════════════════
    def apply_discount(self):
        try:
            subtotal = float(
                self.subtotal_var.get().replace("₱", "").replace(",", ""))
        except:
            return
        if subtotal == 0:
            messagebox.showwarning("Empty Cart",
                                   "Add items before applying discount!",
                                   parent=self)
            self.discount_var.set("No Discount")
            return
        pct = {"Senior Citizen": 0.20, "PWD": 0.20,
               "With Discount Card": 0.10,
               "Employee Discount": 0.15,
               "No Discount": 0.0}.get(self.discount_var.get(), 0)
        disc = subtotal * pct
        self.discounted_var.set(f"₱{disc:.2f}")
        self.grand_total_var.set(f"₱{subtotal - disc:.2f}")

    # ══════════════════════════════════════════════════════════
    #  PAYMENT
    # ══════════════════════════════════════════════════════════
    def process_payment(self):
        if not self.cart:
            messagebox.showwarning("Empty Cart",
                                   "Cart is empty! Add items first.",
                                   parent=self)
            return
        try:
            cash_given = float(
                self.cash_var.get().replace("₱", "").replace(",", "").strip())
        except:
            messagebox.showwarning("Cash Required",
                                   "Please enter the cash amount given!",
                                   parent=self)
            return
        try:
            grand_total = float(
                self.grand_total_var.get().replace("₱", "").replace(",", "").strip())
        except:
            return
        try:
            discount = float(
                self.discounted_var.get().replace("₱", "").replace(",", "").strip())
        except:
            discount = 0

        change = cash_given - grand_total
        if change < 0:
            messagebox.showwarning("Insufficient Cash",
                                   "Cash given is not enough!",
                                   parent=self)
            return

        self.paid_var.set(f"₱{cash_given:.2f}")
        self.change_var.set(f"₱{change:.2f}")
        self.save_transaction(grand_total, discount,
                              grand_total, cash_given, change)

    def save_transaction(self, total, discount,
                         final_total, cash_given, change):
        try:
            tn = datetime.now().strftime("%Y%m%d%H%M%S")
            sale_id = database.save_sale(
                tn, total, discount, cash_given, change)
            for item in self.cart:
                database.save_sale_detail(
                    sale_id, item["product_id"],
                    item["name"], item["qty"],
                    item["price"],
                    item["price"] * item["qty"])
                database.update_stock(item["product_id"], item["qty"])
        except Exception as ex:
            messagebox.showerror("Error",
                                 f"Error saving transaction: {ex}",
                                 parent=self)

    def print_receipt(self):
        if not self.cart:
            messagebox.showwarning("No Transaction",
                                   "No transaction to print!",
                                   parent=self)
            return
        if not self.paid_var.get():
            messagebox.showwarning("Payment Required",
                                   "Please process payment first!",
                                   parent=self)
            return

        from receipt import ReceiptWindow
        receipt = ReceiptWindow(self, self.cart,
                                self.grand_total_var.get(),
                                self.cash_var.get(),
                                self.change_var.get())

        receipt.protocol("WM_DELETE_WINDOW",
                         lambda: self._close_receipt(receipt))

    def _close_receipt(self, receipt):
        receipt.destroy()
        self.clear_transaction()

    def reset_receipt(self):
        if messagebox.askyesno("Reset Receipt",
                               "Clear current transaction?", parent=self):
            self._clear_all()

    def clear_transaction(self):
        self._clear_all()
        messagebox.showinfo("Transaction Complete",
                            "Ready for next transaction!", parent=self)

    def _clear_all(self):
        self.cart.clear()
        for row in self.tree_cart.get_children():
            self.tree_cart.delete(row)
        self.screen_var.set("")
        self.qty_var.set("")
        self.cash_var.set("")
        self.discounted_var.set("")
        self.paid_var.set("")
        self.change_var.set("")
        self.grand_total_var.set("")
        self.total_items_var.set("0")
        self.total_qty_var.set("0")
        self.subtotal_var.set("₱0.00")
        self.discount_var.set("No Discount")
        self.selected_index = -1
        self.item_img_label.config(image="")
        self.barcode_entry.focus_set()

    def prev_page(self):
        pass

    def next_page(self):
        pass