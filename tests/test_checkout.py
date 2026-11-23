"""Contains tests for defects 1 and 8, which are in CheckoutService."""

import sqlite3

from cart import ShoppingCart
from checkout import CheckoutService
from payments import FakePaymentGateway
from repository import StoreRepository
from setup_db import SCHEMA

def test_failed_payment():
    original_mouse_stock = 1
    repo = StoreRepository(':memory:')
    repo.conn.executescript(SCHEMA)
    repo.conn.executemany('INSERT OR IGNORE INTO products VALUES (?, ?, ?, ?)', [
        ('MOU-01', 'Wireless mouse', 29.95, original_mouse_stock),
    ])
    cart = ShoppingCart('demo-user', repo)
    payment_method = FakePaymentGateway(should_approve=False)
    cart.add_item('MOU-01', 1)
    checkout_service = CheckoutService(repo, payment_method)
    result = checkout_service.checkout(cart, 'TEST_TOKEN', 'checkout_service_request')
    assert repo.get_product('MOU-01').stock == original_mouse_stock
    assert result.status == 'declined'

def test_successful_payment():
    original_mouse_stock = 2
    repo = StoreRepository(':memory:')
    repo.conn.executescript(SCHEMA)
    repo.conn.executemany('INSERT OR IGNORE INTO products VALUES (?, ?, ?, ?)', [
        ('MOU-01', 'Wireless mouse', 29.95, original_mouse_stock),
    ])
    cart = ShoppingCart('demo-user', repo)
    # this test also asserts that default behaviour of this class is to approve
    payment_method = FakePaymentGateway()
    cart.add_item('MOU-01', 1)
    checkout_service = CheckoutService(repo, payment_method)
    result = checkout_service.checkout(cart, 'TEST_TOKEN', 'checkout_service_request')
    assert repo.get_product('MOU-01').stock == original_mouse_stock - 1
    assert result.status == 'paid'

def test_untouched_cart_on_decline():
    original_mouse_stock = 1
    repo = StoreRepository(':memory:')
    repo.conn.executescript(SCHEMA)
    repo.conn.executemany('INSERT OR IGNORE INTO products VALUES (?, ?, ?, ?)', [
        ('MOU-01', 'Wireless mouse', 29.95, original_mouse_stock),
        ('MOU-02', 'Wireless mouse 2', 39.95, original_mouse_stock),
    ])
    cart = ShoppingCart('demo-user', repo)
    payment_method = FakePaymentGateway(should_approve=False)
    cart.add_item('MOU-01', 2)
    cart.add_item('MOU-02', 3)
    checkout_service = CheckoutService(repo, payment_method)
    checkout_service.checkout(cart, 'TEST_TOKEN', 'checkout_service_request')
    assert len([line for line in cart.lines if line.sku == 'MOU-01']) == 1
    assert [line for line in cart.lines if line.sku == 'MOU-01'][0].quantity == 2
    assert len([line for line in cart.lines if line.sku == 'MOU-02']) == 1
    assert [line for line in cart.lines if line.sku == 'MOU-02'][0].quantity == 3

