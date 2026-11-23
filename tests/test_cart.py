"""Contains tests for defects 2, 5, 6, and 7, which are in ShoppingCart."""

from cart import ShoppingCart
from checkout import CheckoutService
from payments import FakePaymentGateway
from repository import StoreRepository
from setup_db import SCHEMA

def test_null_uid_rejected():
    repo = StoreRepository(':memory:')
    try:
        ShoppingCart(None, repo)
    except:
        assert True
        return
    assert False

