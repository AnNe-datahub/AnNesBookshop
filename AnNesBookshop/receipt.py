import tkinter as tk
from PIL import Image, ImageTk
from datetime import datetime


class ReceiptWindow(tk.Toplevel):
    def __init__(self, master, cart,
                 grand_total, cash_given, change):
        super().__init__(master)
        self.title("Receipt")
        self.resizable(False, False)
        self.configure(bg="#f9f6e8")
        self.bg_img_ref = None

        # Calculate height based on items
        item_count = len(cart)
        height = max(700, 400 + (item_count * 30))
        height = min(height, 850)

        w = 580
        x = (self.winfo_screenwidth() // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{w}x{height}+{x}+{y}")

        self.build_receipt(cart, grand_total,
                           cash_given, change, height)

    def build_receipt(self, cart, grand_total,
                      cash_given, change, height):
        # Canvas
        canvas = tk.Canvas(self, width=580,
                           height=height, bd=0,
                           highlightthickness=0)
        canvas.pack(fill="both", expand=True)

        # Background
        try:
            bg = Image.open(
                "assets/bookshop_background.png").resize(
                (580, height), Image.Resampling.LANCZOS)
            # Lighten background
            from PIL import ImageEnhance
            bg = ImageEnhance.Brightness(bg).enhance(1.8)
            self.bg_img_ref = ImageTk.PhotoImage(bg)
            canvas.create_image(0, 0, anchor="nw",
                                image=self.bg_img_ref)
        except:
            canvas.configure(bg="#f9f6e8")

        def parse(text):
            try:
                return float(str(text).replace(
                    "₱", "").replace(",", "").strip())
            except:
                return 0.0

        # DATE & TXN
        date_str = datetime.now().strftime("%m/%d/%Y")
        txn_str  = "TXN-" + datetime.now().strftime("%H%M%S")
        canvas.create_text(50, 45, text=date_str,
                           font=("Courier New", 10),
                           fill="#333", anchor="w")
        canvas.create_text(530, 45, text=txn_str,
                           font=("Courier New", 10),
                           fill="#333", anchor="e")

        # Line
        canvas.create_line(40, 62, 540, 62,
                           dash=(5, 3), fill="#555")

        # RECEIPT TITLE
        canvas.create_text(290, 90,
                           text="RECEIPT",
                           font=("Arial Black", 26, "bold"),
                           fill="black", anchor="center")

        # Line
        canvas.create_line(40, 110, 540, 110,
                           dash=(5, 3), fill="#555")

        # STORE NAME
        canvas.create_text(290, 130,
                           text="An Ne's Bookshop",
                           font=("Arial", 11, "bold"),
                           fill="black", anchor="center")
        canvas.create_text(290, 148,
                           text="Based in PH  |  Since 2020",
                           font=("Arial", 9),
                           fill="#444", anchor="center")

        # Line
        canvas.create_line(40, 162, 540, 162,
                           dash=(5, 3), fill="#555")

        # ITEMS
        y = 185
        subtotal = 0

        for item in cart:
            name = item["name"]
            if len(name) > 35:
                name = name[:32] + "..."
            price_qty = f"₱{item['price']:.2f} x{item['qty']}"
            item_total = item["price"] * item["qty"]
            subtotal  += item_total

            canvas.create_text(50, y, text=name,
                               font=("Courier New", 9),
                               fill="black", anchor="w")
            canvas.create_text(530, y, text=price_qty,
                               font=("Courier New", 9),
                               fill="black", anchor="e")
            y += 28

        #  SUMMARY
        y += 15
        canvas.create_line(40, y, 540, y,
                           dash=(5, 3), fill="#555")
        y += 20

        total_amt  = parse(grand_total)
        cash_amt   = parse(cash_given)
        change_amt = parse(change)

        # Total Amount
        canvas.create_text(50, y,
                           text="TOTAL AMOUNT",
                           font=("Arial", 12, "bold"),
                           fill="black", anchor="w")
        canvas.create_text(530, y,
                           text=f"₱{total_amt:.2f}",
                           font=("Arial", 12, "bold"),
                           fill="black", anchor="e")
        y += 35

        canvas.create_line(40, y, 540, y,
                           dash=(5, 3), fill="#555")
        y += 22

        # Cash
        canvas.create_text(50, y, text="CASH",
                           font=("Arial", 11, "bold"),
                           fill="black", anchor="w")
        canvas.create_text(530, y,
                           text=f"₱{cash_amt:.2f}",
                           font=("Arial", 11),
                           fill="black", anchor="e")
        y += 32

        # Change
        canvas.create_text(50, y, text="CHANGE",
                           font=("Arial", 11, "bold"),
                           fill="black", anchor="w")
        canvas.create_text(530, y,
                           text=f"₱{change_amt:.2f}",
                           font=("Arial", 11),
                           fill="black", anchor="e")
        y += 28

        canvas.create_line(40, y, 540, y,
                           dash=(5, 3), fill="#555")
        y += 35

        # ── THANK YOU ──
        canvas.create_text(290, y,
                           text="THANK  YOU",
                           font=("Arial Black", 24, "bold"),
                           fill="black", anchor="center")
        y += 45

        # ── CLOSE BUTTON ──
        close_btn = tk.Button(self, text="Close",
                              command=self.destroy,
                              bg="#C9B59C", fg="#594a47",
                              font=("Arial", 11, "bold"),
                              width=14, relief="raised", bd=2)