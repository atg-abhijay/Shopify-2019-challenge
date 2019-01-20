from tinydb import TinyDB, Query
from helper_functions import generate_product_uri
from user_functions import get_user

users = TinyDB('db.json').table('users')
products = TinyDB('db.json').table('products')


def add_product_to_cart(uname, product_id):
    """
    Add the product with *product_id* to the given user's cart.

    :param str uname: Username
    :param str product_id: ID of the product to add to the user's cart

    :returns: Username along with the product added to the cart
    :rtype: *dict*

    - Example

    .. code-block:: JSON

        {
            "username": "Midoriya",
            "product": {
                "inventory_count": 51,
                "price": 4.99,
                "title": "Guava cupcake",
                "uri": "http://localhost:5000/marketplace/api/product/a37b3418-cc8f-40fa-8d63-661b3912eb71"
            }
        }

    """

    User_query = Query()
    Product_query = Query()
    current_user = users.get(User_query.username == uname)
    current_user['cart'].append(product_id)

    users.update({'cart': current_user['cart']}, User_query.username == uname)

    return {'username': uname, 'product': products.get(Product_query.uri == generate_product_uri(product_id))}


def remove_product_from_cart(uname, product_id):
    """
    Remove the product with *product_id* from the given user's cart.

    :param str uname: Username
    :param str product_id: Product to remove from user's cart

    :returns: Username along with the product removed from the cart
    :rtype: *dict*

    - Example

    .. code-block:: JSON

        {
            "username": "Midoriya",
            "product": {
                "inventory_count": 51,
                "price": 4.99,
                "title": "Guava cupcake",
                "uri": "http://localhost:5000/marketplace/api/product/a37b3418-cc8f-40fa-8d63-661b3912eb71"
            }
        }

    """

    User_query = Query()
    Product_query = Query()
    current_user = users.get(User_query.username == uname)
    current_user['cart'].remove(product_id)
    users.update({'cart': current_user['cart']}, User_query.username == uname)

    return {'username': uname, 'product': products.get(Product_query.uri == generate_product_uri(product_id))}


def get_user_cart(uname):
    """
    Get the given user's cart.

    :param str uname: Username

    :returns: The given user's cart
    :rtype: *dict*

    - Example

    .. code-block:: JSON

        {
            "products": [
                {
                    "inventory_count": 12,
                    "price": 7.99,
                    "title": "Orange cupcake",
                    "uri": "http://localhost:5000/marketplace/api/product/f4ad5da8-2cc5-4ec0-86f3-4c02367c082f"
                },
                {
                    "inventory_count": 51,
                    "price": 4.99,
                    "title": "Guava cupcake",
                    "uri": "http://localhost:5000/marketplace/api/product/a37b3418-cc8f-40fa-8d63-661b3912eb71"
                }
            ],
            "total_price": 12.98
        }

    """

    User_query = Query()
    Product_query = Query()
    current_user_cart = users.get(User_query.username == uname)['cart']

    cart = {'products': [], 'total_price': 0}
    for product_id in current_user_cart:
        cart_product = products.get(Product_query.uri == generate_product_uri(product_id))
        cart['products'].append(cart_product)
        cart['total_price'] += cart_product['price']

    return cart


def clear_user_cart(uname):
    """
    Clear the given user's cart

    :param str uname: Username

    :returns: Username along with their empty cart
    :rtype: *dict*

    - Example

    .. code-block:: JSON

        {
            "username": "Midoriya",
            "user_cart": []
        }

    """

    User_query = Query()
    users.update({'cart': []}, User_query.username == uname)
    affected_user = get_user(uname)
    return {'username': uname, 'user_cart': affected_user['cart']}
