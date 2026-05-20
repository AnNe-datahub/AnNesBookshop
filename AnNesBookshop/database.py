import sqlite3
import os

# Database path
DB_PATH = r"C:\Users\leann\Documents\AnNesBookshop\BookstoreDataset.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # allows accessing columns by name
    return conn


# ─── PRODUCT QUERIES ────────────────────────────────────────────

def get_all_products():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT ProductID, Barcode, ProductName, Category,
               Price, Cost, StockQuantity, DateAdded,
               Description, Supplier, PicPathText,
               BarcodeImagePath, QRCodeImagePath,
               Author, Publisher, ISBN, Edition, PublishedYear
        FROM ProductInfo
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_product_by_id(product_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT ProductID, Barcode, ProductName, Category,
               Price, Cost, StockQuantity, DateAdded,
               Description, Supplier, PicPathText,
               BarcodeImagePath, QRCodeImagePath,
               Author, Publisher, ISBN, Edition, PublishedYear
        FROM ProductInfo 
        WHERE ProductID = ?
    """, (product_id,))
    row = cursor.fetchone()
    conn.close()
    return row


def get_product_by_barcode(barcode):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT ProductID, Barcode, ProductName, Category,
               Price, Cost, StockQuantity, DateAdded,
               Description, Supplier, PicPathText,
               BarcodeImagePath, QRCodeImagePath,
               Author, Publisher, ISBN, Edition, PublishedYear
        FROM ProductInfo 
        WHERE Barcode = ?
    """, (barcode,))
    row = cursor.fetchone()
    conn.close()
    return row


def search_products(keyword, domain="All"):
    conn = get_connection()
    cursor = conn.cursor()
    if domain == "Product ID":
        cursor.execute("SELECT * FROM ProductInfo WHERE ProductID = ?", (keyword,))
    elif domain == "Title":
        cursor.execute("SELECT * FROM ProductInfo WHERE ProductName LIKE ?", (f"%{keyword}%",))
    elif domain == "Product Category":
        cursor.execute("SELECT * FROM ProductInfo WHERE Category = ?", (keyword,))
    elif domain == "Product Barcode":
        cursor.execute("SELECT * FROM ProductInfo WHERE Barcode LIKE ?", (f"%{keyword}%",))
    else:
        cursor.execute("SELECT * FROM ProductInfo")
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_products_by_category(category="All"):
    conn = get_connection()
    cursor = conn.cursor()
    if category == "All":
        cursor.execute("SELECT * FROM ProductInfo")
    else:
        cursor.execute("SELECT * FROM ProductInfo WHERE Category = ?", (category,))
    rows = cursor.fetchall()
    conn.close()
    return rows


def save_product(data):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO ProductInfo (
            Barcode, ProductName, Category, Price, Cost,
            StockQuantity, DateAdded, Description, Supplier,
            PicPathText, BarcodeImagePath, QRCodeImagePath,
            Author, Publisher, ISBN, Edition, PublishedYear
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, data)
    product_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return product_id


def update_product(data):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE ProductInfo SET
            Barcode = ?, ProductName = ?, Category = ?,
            Price = ?, Cost = ?, StockQuantity = ?,
            DateAdded = ?, Description = ?, Supplier = ?,
            PicPathText = ?, BarcodeImagePath = ?, QRCodeImagePath = ?,
            Author = ?, Publisher = ?, ISBN = ?,
            Edition = ?, PublishedYear = ?
        WHERE ProductID = ?
    """, data)
    conn.commit()
    conn.close()


def delete_product(product_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM ProductInfo WHERE ProductID = ?", (product_id,))
    conn.commit()
    conn.close()


#  SALES QUERIES

def save_sale(transaction_number, total, discount, cash_given, change):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO Sales (
            TransactionNumber, SaleDate, TotalAmount,
            Discount, CashGiven, ChangeAmount
        ) VALUES (?, datetime('now'), ?, ?, ?, ?)
    """, (transaction_number, total, discount, cash_given, change))
    sale_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return sale_id


def save_sale_detail(sale_id, product_id, product_name, quantity, price, total):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO SalesDetails (
            SaleID, ProductID, ProductName,
            Quantity, Price, Total
        ) VALUES (?, ?, ?, ?, ?, ?)
    """, (sale_id, product_id, product_name, quantity, price, total))
    conn.commit()
    conn.close()


def update_stock(product_id, quantity_sold):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE ProductInfo
        SET StockQuantity = StockQuantity - ?
        WHERE ProductID = ?
    """, (quantity_sold, product_id))
    conn.commit()
    conn.close()


def get_all_sales():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT sd.ProductID, p.ProductName, sd.Quantity,
               p.StockQuantity, s.SaleDate, s.TransactionNumber
        FROM SalesDetails sd
        INNER JOIN Sales s ON sd.SaleID = s.SaleID
        INNER JOIN ProductInfo p ON sd.ProductID = p.ProductID
        ORDER BY s.SaleDate DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_sales_by_product(product_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT sd.ProductID, p.ProductName, sd.Quantity,
               p.StockQuantity, s.SaleDate, s.TransactionNumber
        FROM SalesDetails sd
        INNER JOIN Sales s ON sd.SaleID = s.SaleID
        INNER JOIN ProductInfo p ON sd.ProductID = p.ProductID
        WHERE sd.ProductID = ?
        ORDER BY s.SaleDate DESC
    """, (product_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows


#  FOLDERS SETUP

def create_folders():
    os.makedirs(r"C:\POSSystem\Barcodes", exist_ok=True)
    os.makedirs(r"C:\POSSystem\QRCodes", exist_ok=True)


if __name__ == "__main__":
    conn = get_connection()
    print("✅ Connected to database successfully!")
    conn.close()