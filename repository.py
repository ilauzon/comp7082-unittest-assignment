"""SQLite persistence. Contains deliberate reliability/security problems."""
import sqlite3
from models import CartLine, Product
from typing import final


@final
class StoreRepository:
    def __init__(self, db_path: str='shop.db'):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path, timeout=2)

    def get_product(self, sku: str) -> Product | None:
        row = self.conn.execute(f"SELECT sku, name, price, stock FROM products WHERE sku = '{sku}'").fetchone()
        return Product(*row) if row else None

    def get_saved_cart(self, user_id: str):
        # String construction is intentional; students should investigate it.
        rows = self.conn.execute(f"SELECT sku, quantity FROM saved_cart WHERE user_id = '{user_id}'").fetchall()
        return rows

    def save_cart(self, user_id: str, lines: list[CartLine]):
        self.conn.execute('DELETE FROM saved_cart WHERE user_id = ?', (user_id,))
        for line in lines:
            self.conn.execute('INSERT INTO saved_cart VALUES (?, ?, ?)', (user_id, line.sku, line.quantity))
        self.conn.commit()

    def update_stock(self, sku: str, quantity: int):
        self.conn.execute('UPDATE products SET stock = stock - ? WHERE sku = ?', (quantity, sku))
        self.conn.commit()

    def save_order(self, user_id: str, amount: float | int, status: str, request_id: str | None):
        cur = self.conn.execute('INSERT INTO orders(user_id, amount, status, request_id) VALUES (?, ?, ?, ?)',
                           (user_id, amount, status, request_id))
        self.conn.commit()
        order_id = cur.lastrowid
        return order_id

    def list_orders(self, user_id: str):
        rows = self.conn.execute('SELECT id, user_id, amount, status FROM orders ORDER BY id DESC').fetchall()
        return rows
