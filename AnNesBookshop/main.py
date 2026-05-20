import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os

class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("An Ne's Bookshop - Management System")
        self.state("zoomed")  # maximized
        self.configure(bg="#c9b59c")

        # Store child windows
        self.open_windows = {}

        self.create_folders()
        self.build_menu()
        self.build_background()
        self.build_logo()

    def create_folders(self):
        os.makedirs(r"C:\POSSystem\Barcodes", exist_ok=True)
        os.makedirs(r"C:\POSSystem\QRCodes", exist_ok=True)

    # MENU BAR
    def build_menu(self):
        menubar = tk.Menu(self, bg="#7fa7c1", fg="#3d2817",
                          font=("Baskerville Old Face", 10))

        # Products Stocking
        menubar.add_command(
            label="Products Stocking",
            command=self.open_product_stocking
        )

        # View Record
        menubar.add_command(
            label="View Record",
            command=self.open_product_report
        )

        # POS
        menubar.add_command(
            label="POS",
            command=self.open_cashier
        )

        # Window menu
        window_menu = tk.Menu(menubar, tearoff=0,
                              bg="#7fa7c1", fg="#3d2817")
        window_menu.add_command(label="Cascade",
                                command=self.cascade_windows)
        window_menu.add_command(label="Tile Vertical",
                                command=self.tile_vertical)
        window_menu.add_command(label="Tile Horizontal",
                                command=self.tile_horizontal)
        menubar.add_cascade(label="Window Form",
                            menu=window_menu)

        self.config(menu=menubar)

    # BACKGROUND
    def build_background(self):
        try:
            img = Image.open("assets/bookshop_background.png")
            img = img.resize((self.winfo_screenwidth(),
                              self.winfo_screenheight()),
                             Image.Resampling.LANCZOS)
            self.bg_image = ImageTk.PhotoImage(img)
            bg_label = tk.Label(self, image=self.bg_image,
                                bg="#c9b59c")
            bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        except Exception as e:
            print(f"Background image not found: {e}")

    # LOGO
    def build_logo(self):
        try:
            img = Image.open("assets/anne_logo.png")
            img = img.resize((185, 185), Image.Resampling.LANCZOS)
            self.logo_image = ImageTk.PhotoImage(img)
            logo_label = tk.Label(self, image=self.logo_image,
                                  bg="#c9b59c")
            logo_label.place(x=30, y=50)
        except Exception as e:
            print(f"Logo not found: {e}")

    # OPEN FORMS
    def open_product_stocking(self):
        from product_stocking import ProductStockingWindow
        self.open_child("stocking", ProductStockingWindow)

    def open_product_report(self):
        from product_report import ProductReportWindow
        self.open_child("report", ProductReportWindow)

    def open_cashier(self):
        from cashier import CashierWindow
        self.open_child("cashier", CashierWindow)

    def open_child(self, key, window_class):

        if key in self.open_windows:
            win = self.open_windows[key]
            if win.winfo_exists():
                win.lift()
                win.state("zoomed")
                return

        win = window_class(self)
        self.open_windows[key] = win
        win.protocol("WM_DELETE_WINDOW",
                     lambda: self.close_child(key, win))

    def close_child(self, key, win):
        if key in self.open_windows:
            del self.open_windows[key]
        win.destroy()

    # WINDOW LAYOUT
    def cascade_windows(self):
        x, y = 30, 30
        for win in self.open_windows.values():
            if win.winfo_exists():
                win.geometry(f"800x600+{x}+{y}")
                x += 30
                y += 30

    def tile_vertical(self):
        windows = [w for w in self.open_windows.values()
                   if w.winfo_exists()]
        if not windows:
            return
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        w = sw // len(windows)
        for i, win in enumerate(windows):
            win.geometry(f"{w}x{sh}+{i * w}+0")

    def tile_horizontal(self):
        windows = [w for w in self.open_windows.values()
                   if w.winfo_exists()]
        if not windows:
            return
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        h = sh // len(windows)
        for i, win in enumerate(windows):
            win.geometry(f"{sw}x{h}+0+{i * h}")


# RUN
if __name__ == "__main__":
    app = MainApp()
    app.mainloop()