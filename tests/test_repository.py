"""Contains tests for defects 2, 5, 6, and 7, which are in ShoppingCart."""

from cart import ShoppingCart
from checkout import CheckoutService
from payments import FakePaymentGateway
from repository import StoreRepository
from setup_db import SCHEMA


def test_order_filtering():
    repo = StoreRepository(':memory:')
    _ = repo.conn.executescript(SCHEMA)
    _ = repo.conn.executemany('INSERT OR IGNORE INTO orders VALUES (?, ?, ?, ?, ?)', [
        (1, 'u1', 5, 'u1 order 1', 'u1-request-1'),
        (2, 'u1', 10, 'u1 order 2', 'u1-request-2'),
        (3, 'u2', 5, 'u2 order 1', 'u2-request-1'),
        (4, 'u2', 10, 'u2 order 2', 'u2-request-2'),
    ])
    assert len([order for order in repo.list_orders('u1') if order[1] == 'u2']) == 0
    assert len([order for order in repo.list_orders('u2') if order[1] == 'u1']) == 0
    assert len([order for order in repo.list_orders('u1') if order[1] == 'u1']) == 2
    assert len([order for order in repo.list_orders('u2') if order[1] == 'u2']) == 2

def test_get_product_sql_injection():
    repo = StoreRepository(':memory:')
    _ = repo.conn.executescript(SCHEMA)
    _ = repo.conn.executemany('INSERT OR IGNORE INTO products VALUES (?, ?, ?, ?)', [
        ('MOU-01', 'Wireless mouse', 29.95, 5),
    ])
    assert repo.get_product("' OR '1'='1") is None

def test_get_saved_cart_sql_injection():
    repo = StoreRepository(':memory:')
    _ = repo.conn.executescript(SCHEMA)
    _ = repo.conn.executemany('INSERT INTO saved_cart VALUES (?, ?, ?)', [
        ('u1', 'MOU-01', 1),
        ('u2', 'MOU-01', 3),
    ])
    assert repo.get_saved_cart("' OR '1'='1") == []
