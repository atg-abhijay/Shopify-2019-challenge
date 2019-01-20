from uuid import uuid4
from tinydb import TinyDB, Query
from tinydb.operations import decrement
from helper_functions import generate_product_uri, find_func

products = TinyDB('db.json').table('products')
users = TinyDB('db.json').table('users')

def add_product(title, price, inventory_count):
    """
    Add product to database.

    :param str title: Title of the product
    :param float price: Price of the product
    :param int inventory_count: Inventory count of the product

    :returns: ID of the added product
    :rtype: *str*

    """

    product_id = str(uuid4())
    products.insert({'title': title, 'price': price, 'inventory_count': inventory_count,
                     'uri': generate_product_uri(product_id)})
    return product_id


def get_all_products():
    """
    Get all the products in the database with inventory greater than zero.

    :returns: A list of products

    - Example

    .. code-block:: JSON

        [
            {
                "inventory_count": 18,
                "price": 15.65,
                "title": "Mango pizza",
                "uri": "http://localhost:5000/marketplace/api/product/84a1c5d6-d1fd-4db0-bc1e-f450a70ca7d9"
            },
            {
                "inventory_count": 51,
                "price": 4.99,
                "title": "Guava cupcake",
                "uri": "http://localhost:5000/marketplace/api/product/a37b3418-cc8f-40fa-8d63-661b3912eb71"
            }
        ]

    """

    Product_query = Query()
    return products.search(Product_query.inventory_count > 0)


def get_product(product_id):
    """
    Get a single product from the database by its ID. Only returns product if it
    has inventory greater than zero.

    :param str product_id: ID of the product

    :returns: Product whose ID matches the parameter passed
    :rtype: *dict*

    - Example

    .. code-block:: JSON

            {
                "inventory_count": 51,
                "price": 4.99,
                "title": "Guava cupcake",
                "uri": "http://localhost:5000/marketplace/api/product/a37b3418-cc8f-40fa-8d63-661b3912eb71"
            }
    """

    Product_query = Query()
    return products.get((Product_query.uri == generate_product_uri(product_id))
                        & (Product_query.inventory_count > 0))


def find_products(search_title):
    """
    Find products in the database whose title match *search_title* at least partially.
    Performs case-insensitive search. Only returns products with inventory greater than zero.

    :param str search_title: Title to search products by

    :returns: A list of products whose titles match the search title at least partially

    - Example: For the search title "PCaK", the products returned are:

    .. code-block:: JSON

        [
            {
                "inventory_count": 51,
                "price": 4.99,
                "title": "Guava cupcake",
                "uri": "http://localhost:5000/marketplace/api/product/a37b3418-cc8f-40fa-8d63-661b3912eb71"
            },
            {
                "inventory_count": 12,
                "price": 7.99,
                "title": "Orange cupcake",
                "uri": "http://localhost:5000/marketplace/api/product/f4ad5da8-2cc5-4ec0-86f3-4c02367c082f"
            }
        ]
    """

    Product_query = Query()
    return products.search((Product_query.title.test(find_func, search_title))
                           & (Product_query.inventory_count > 0))


def delete_product(product_id):
    """
    Delete product whose ID matches *product_id* from the database.

    :param str product_id: ID of the product to delete

    :returns:
        - A list containing only *False* if the product was not found in the database.
        - A list containing *True* and the product that was deleted.

    """

    Product_query = Query()
    prod_to_delete = products.get(Product_query.uri == generate_product_uri(product_id))
    if not prod_to_delete:
        return [False]

    products.remove(doc_ids=[prod_to_delete.doc_id])
    return [True, prod_to_delete]


def decrement_inventories(uname):
    """
    Decrement the inventories of the products that
    the user purchased.

    :param str uname: Username

    :returns: A list of products whose inventories were decreased

    - Example

    .. code-block:: JSON

        [
            {
                "inventory_count": 51,
                "price": 4.99,
                "title": "Guava cupcake",
                "uri": "http://localhost:5000/marketplace/api/product/a37b3418-cc8f-40fa-8d63-661b3912eb71"
            },
            {
                "inventory_count": 12,
                "price": 7.99,
                "title": "Orange cupcake",
                "uri": "http://localhost:5000/marketplace/api/product/f4ad5da8-2cc5-4ec0-86f3-4c02367c082f"
            }
        ]

    """

    User_query = Query()
    Product_query = Query()
    current_user_cart = users.get(User_query.username == uname)['cart']
    affected_products = []
    for product_id in current_user_cart:
        products.update(decrement('inventory_count'), Product_query.uri == generate_product_uri(product_id))

    for product_id in set(current_user_cart):
        affected_products.append(products.get(Product_query.uri == generate_product_uri(product_id)))

    return affected_products
