"""Simulator only: do not use real cards or connect a payment gateway."""
import time
from typing import final


@final
class FakePaymentGateway:
    def __init__(self, should_approve: bool=True, delay: float | int=0):
        self.should_approve = should_approve
        self.delay = delay
        self.calls: list[tuple[float | int, str]] = []

    def charge(self, amount: float | int, payment_token: str):
        time.sleep(self.delay)
        self.calls.append((amount, payment_token))
        return {'approved': self.should_approve, 'transaction_id': 'TEST-001' if self.should_approve else None}
