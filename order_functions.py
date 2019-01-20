from uuid import uuid4
from tinydb import TinyDB, Query
from cart_functions import get_user_cart

orders = TinyDB('db.json').table('orders')


def get_order(order_id):
    """
    Get order with ID *order_id*.

    :param str order_id: ID of the order

    :returns: Order matching ID *order_id*
    :rtype: *dict*

    - Example

    .. code-block:: JSON

        {
            "amount": 23.97,
            "order_id": "274a5c89-f9ad-4043-a07c-0d545512291b",
            "products": [
                {
                    "inventory_count": 12,
                    "price": 7.99,
                    "title": "Orange cupcake",
                    "uri": "http://localhost:5000/marketplace/api/product/f4ad5da8-2cc5-4ec0-86f3-4c02367c082f"
                },
                {
                    "inventory_count": 12,
                    "price": 7.99,
                    "title": "Orange cupcake",
                    "uri": "http://localhost:5000/marketplace/api/product/f4ad5da8-2cc5-4ec0-86f3-4c02367c082f"
                },
                {
                    "inventory_count": 12,
                    "price": 7.99,
                    "title": "Orange cupcake",
                    "uri": "http://localhost:5000/marketplace/api/product/f4ad5da8-2cc5-4ec0-86f3-4c02367c082f"
                }
            ],
            "username": "Uraraka"
        }

    """

    return orders.get(Query().order_id == order_id)


def generate_order(uname):
    """
    Generate an order for the given user from their cart.

    :param str uname: Username

    :returns: Generated order ID
    :rtype: *str*

    """

    user_cart = get_user_cart(uname)
    order_id = str(uuid4())
    orders.insert({'order_id': order_id, 'products': user_cart['products'],
                   'amount': user_cart['total_price'], 'username': uname})

    return order_id
