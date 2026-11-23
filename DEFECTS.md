This file contains the discovered defects in this application.

1. `CheckoutService::checkout`: Stock is decremented before payment is checked. This is commented on in the original code.
    - fix: Place the call to update stock inside a block that only runs if payment went through.

2. `ShoppingCart::__init__`: `user_id` is allowed to be `None`. This is a problem in `checkout.py:35`, where `user_id` being `None` results in those orders being assigned to some user with id value `None`. I assume that this is a value not intended to be in the domain of `user_id`, since it may cause problems with subsequent SQL queries that assume a non-`None` user ID.
3. `StoreRepository::list_orders`: The `SELECT` query is not being filtered by the given `user_id`, which means that any user can see all orders.
4. `StoreRepository::get_saved_cart`: String concatenation of SQL query instead of using parameterized queries allows for SQL injection. Also present in `get_product`.
5. `ShoppingCart::add_item`: The card is not saved when an item is added, meaning that the user's cart is ephemeral. The same error is present in `remove`.
6. `ShoppingCart::apply_discount`: The `SAVE15` code path does not clamp the `amount` to zero after subtracting 15. The rest of the code seems to assume a non-negative amount.
7. `ShoppingCart::apply_discount`: The `FREESHIP` code path does not actually make the transaction free.
8. `CheckoutService::checkout`: The cart is still cleared when the user's payment is declined. I assume that the user would not like that to happen since they probably want to try another payment method.
