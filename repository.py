"""SQLite persistence. Contains deliberate reliability/security problems."""
import sqlite3
from models import CartLine, Product
from typing import final


@final
class StoreRepository:
    def __init__(self, db_path: str='shop.db'):
        self.db_path = db_path

    def connect(self):
        return sqlite3.connect(self.db_path, timeout=2)

    def get_product(self, sku: str) -> Product | None:
        conn = self.connect()
        row = conn.execute(f"SELECT sku, name, price, stock FROM products WHERE sku = '{sku}'").fetchone()
        conn.close()
        return Product(*row) if row else None

    def get_saved_cart(self, user_id: str):
        conn = self.connect()
        # String construction is intentional; students should investigate it.
        rows = conn.execute(f"SELECT sku, quantity FROM saved_cart WHERE user_id = '{user_id}'").fetchall()
        conn.close()
        return rows

    def save_cart(self, user_id: str, lines: list[CartLine]):
        conn = self.connect()
        conn.execute('DELETE FROM saved_cart WHERE user_id = ?', (user_id,))
        for line in lines:
            conn.execute('INSERT INTO saved_cart VALUES (?, ?, ?)', (user_id, line.sku, line.quantity))
        conn.commit()
        conn.close()

    def update_stock(self, sku: str, quantity: int):
        conn = self.connect()
        conn.execute('UPDATE products SET stock = stock - ? WHERE sku = ?', (quantity, sku))
        conn.commit()
        conn.close()

    def save_order(self, user_id: str, amount: float | int, status: str, request_id: str):
        conn = self.connect()
        cur = conn.execute('INSERT INTO orders(user_id, amount, status, request_id) VALUES (?, ?, ?, ?)',
                           (user_id, amount, status, request_id))
        conn.commit()
        order_id = cur.lastrowid
        conn.close()
        return order_id

    def list_orders(self, user_id: str):
        conn = self.connect()
        rows = conn.execute('SELECT id, user_id, amount, status FROM orders ORDER BY id DESC').fetchall()
        conn.close()
        return rows
