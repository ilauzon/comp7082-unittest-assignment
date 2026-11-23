"""Contains tests for defects 2, 5, 6, and 7, which are in ShoppingCart."""

from cart import ShoppingCart
from checkout import CheckoutService
from payments import FakePaymentGateway
from repository import StoreRepository
from setup_db import SCHEMA

def test_null_uid_rejected():
    repo = StoreRepository(':memory:')
    try:
        _ = ShoppingCart(None, repo)
    except TypeError:
        assert True
        return
    assert False

def test_string_uid_accepted():
    repo = StoreRepository(':memory:')
    try:
        _ = ShoppingCart('user-id', repo)
    except TypeError:
        assert False
        return
    assert True

def test_overquantity_add_fails():
    repo = StoreRepository(':memory:')
    _ = repo.conn.executescript(SCHEMA)
    _ = repo.conn.executemany('INSERT OR IGNORE INTO products VALUES (?, ?, ?, ?)', [
        ('MOU-01', 'Wireless mouse', 29.95, 5),
    ])
    cart = ShoppingCart('demo-user', repo)
    assert cart.add_item('MOU-01', 3) == True
    assert cart.add_item('MOU-01', 3) == False

def test_underquantity_double_add_passes():
    repo = StoreRepository(':memory:')
    _ = repo.conn.executescript(SCHEMA)
    _ = repo.conn.executemany('INSERT OR IGNORE INTO products VALUES (?, ?, ?, ?)', [
        ('MOU-01', 'Wireless mouse', 29.95, 5),
    ])
    cart = ShoppingCart('demo-user', repo)
    assert cart.add_item('MOU-01', 2) == True
    assert cart.add_item('MOU-01', 3) == True

def test_discount_SAVE15():
    repo = StoreRepository(':memory:')
    _ = repo.conn.executescript(SCHEMA)
    _ = repo.conn.executemany('INSERT OR IGNORE INTO products VALUES (?, ?, ?, ?)', [
        ('MOU-01', 'Wireless mouse', 14, 5),
    ])
    cart = ShoppingCart('demo-user', repo)
    _ = cart.add_item('MOU-01', 1)
    assert cart.apply_discount('SAVE15') == True;
    assert cart.discounted_total != None and cart.discounted_total == 0;

def test_discount_SAVE15_above_0():
    repo = StoreRepository(':memory:')
    _ = repo.conn.executescript(SCHEMA)
    _ = repo.conn.executemany('INSERT OR IGNORE INTO products VALUES (?, ?, ?, ?)', [
        ('MOU-01', 'Wireless mouse', 16, 5),
    ])
    cart = ShoppingCart('demo-user', repo)
    _ = cart.add_item('MOU-01', 1)
    assert cart.apply_discount('SAVE15') == True;
    assert cart.discounted_total != None and cart.discounted_total == 1;
