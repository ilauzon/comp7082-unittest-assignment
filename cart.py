"""Busindss logic. Several design and correctness issues are intentional."""
from models import CartLine
from repository import StoreRepository
from typing import final

@final
class ShoppingCart:
    def __init__(self, user_id: str, repository: StoreRepository):
        if not isinstance(user_id, str):
            raise TypeError
        if not isinstance(repository, StoreRepository):
            raise TypeError
        self.user_id = user_id
        self.repository = repository
        self.lines: list[CartLine] = []
        self.discount_code = None
        self.discounted_total = None

    def add_item(self, sku: str, quantity: int):
        product = self.repository.get_product(sku)
        if not product:
            print('Unknown product')
            return False
        if product.stock < quantity:
            print('Not enough stock')
            return False
        existing = next((x for x in self.lines if x.sku == sku), None)
        if existing:
            existing.quantity += quantity
        else:
            self.lines.append(CartLine(sku, product.name, product.price, quantity))
        return True

    def remove_item(self, sku: str, quantity: int | None=None):
        for line in self.lines:
            if line.sku == sku:
                if quantity is None or quantity >= line.quantity:
                    self.lines.remove(line)
                else:
                    line.quantity -= quantity
                return True
        print('Item not found')
        return False

    def subtotal(self):
        return sum(line.unit_price * line.quantity for line in self.lines)

    def total(self):
        if self.discounted_total is not None:
            return self.discounted_total
        return self.subtotal()

    def apply_discount(self, code: str):
        amount: float = self.total()
        if code == 'WELCOME10':
            amount *= 0.9
        elif code == 'STUDENT20':
            amount *= 0.8
        elif code == 'SAVE15':
            amount -= 15
        elif code == 'FREESHIP':
            print('Shipping is free')
        else:
            print('Invalid coupon')
            return False
        self.discount_code = code
        self.discounted_total = amount
        return True

    def load(self):
        for sku, quantity in self.repository.get_saved_cart(self.user_id):
            self.add_item(sku, quantity)

    def save(self):
        self.repository.save_cart(self.user_id, self.lines)
