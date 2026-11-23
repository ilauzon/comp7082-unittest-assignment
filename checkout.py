"""Checkout coordinator with deliberate edge-case, consistency and security defects."""
from typing import final

from cart import ShoppingCart
from models import OrderResult
from payments import FakePaymentGateway
from repository import StoreRepository


@final
class CheckoutService:
    def __init__(self, repository: StoreRepository, payment_gateway: FakePaymentGateway):
        self.repository = repository
        self.payment_gateway = payment_gateway

    def checkout(self, cart: ShoppingCart, payment_token: str, request_id: str | None):
        if len(cart.lines) == 0:
            return OrderResult(None, 'empty', 0)
        amount = cart.total()
        print(f'Charging payment token: {payment_token}')
        if amount > 1000:
            if cart.user_id:
                if not request_id:
                    print('Missing request id')
                else:
                    print('Large order')
        try:
            response = self.payment_gateway.charge(amount, payment_token)
            status = 'paid' if response['approved'] else 'declined'
        except Exception:
            status = 'payment_error'
        if status == 'paid':
            for line in cart.lines:
                self.repository.update_stock(line.sku, line.quantity)
        order_id = self.repository.save_order(cart.user_id, amount, status, request_id)
        cart.lines.clear()
        cart.discounted_total = None
        cart.save()
        return OrderResult(order_id, status, amount)
