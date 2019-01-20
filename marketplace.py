from uuid import uuid4
from flask import Flask, jsonify, abort, make_response, request, url_for
from tinydb import TinyDB, Query
from tinydb.operations import decrement

db = TinyDB('db.json')
products = db.table('products')
users = db.table('users')
orders = db.table('orders')

app = Flask(__name__)


### DB functions ###

"""User functions"""

def sign_up(uname, pwd, email):
    """
    Sign up a new user to the database.

    :param str uname: Username (has to be unique)
    :param str pwd: Password
    :param str email: Email (has to be unique)

    :returns: Username of the new user
    :rtype: *str*

    """
    users.insert({'username': uname, 'password': pwd, 'email': email, 'cart': []})
    return uname


def sign_in(uname, pwd):
    """
    Perform sign in of a user.

    :param str uname: Username
    :param str pwd: Password

    :returns:
        * 0 - successful login.
        * 1 - user not found.
        * 2 - incorrect password.

    """
    User_query = Query()
    found_user = users.get(User_query.username == uname)
    if not found_user:
        return 1

    if found_user['password'] != pwd:
        return 2

    return 0


def get_user(uname):
    """
    Retrieve user based on their username.

    :param str uname: Username

    :returns: User whose username matches the passed parameter
    :rtype: *dict*

    - Example

    .. code-block:: JSON

        {
            "username": "johndoe",
            "email": "johndoe@email.com"
            "cart": [
                "63f6-bj6m-345k",
                "354g-3427-nb38"
            ]
        }

    """
    User_query = Query()
    user = users.get(User_query.username == uname)
    user.pop('password')
    return user


def get_user_by_email(email):
    """
    Retrieve user based on their email.

    :param str email: User's email

    :returns: User whose username matches the passed parameter
    :rtype: *dict*

    - Example

    .. code-block:: JSON

        {
            "username": "johndoe",
            "email": "johndoe@email.com"
            "cart": [
                "63f6-bj6m-345k",
                "354g-3427-nb38"
            ]
        }

    """
    User_query = Query()
    user = users.get(User_query.email == email)
    user.pop('password')
    return user


"""Product functions"""

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



"""Cart functions"""

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


"""Order functions"""

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


"""Helper functions"""

def generate_product_uri(product_id):
    """
    Generate a product URI based on its ID.

    :param str product_id: ID of the product

    :returns: A URI for the given product
    :rtype: *str*

    """

    return url_for('route_get_product', pid=product_id, _external=True)


def find_func(string, substring):
    """
    Check if one string is present in another string.

    :param str string: String to check in
    :param str substring: Substring we are interested in

    :returns:
        - *True* if the substring is present in the string
        - *False* if the substring is *not* present in the string

    """

    if substring.lower() in string.lower():
        return True

    return False


'''
Endpoints
'''

"""User endpoints"""

@app.route('/marketplace/api/sign-up', methods=['POST'])
def route_sign_up():
    """
    Sign up a new user to the database.

    **Example** -

    :Request JSON Object:

    .. code-block:: JSON

        {
            "username": "johndoe",
            "password": "gaslbj3l4i",
            "email": "johndoe@email.com"
        }

    :Response JSON Object:

    .. code-block:: JSON

        {
            "message": "User signed up successfully",
            "new_user":
                {
                    "username": "johndoe",
                    "email": "johndoe@email.com"
                    "cart": [
                        "63f6-bj6m-345k",
                        "354g-3427-nb38"
                    ]
                }
        }

    :Status Codes:
        - 201 Created - New user signed up
        - 400 Bad Request - Malformed request

    """

    username, password, email = request.json['username'], request.json['password'], request.json['email']
    error_msg = ""
    error_occured = True
    if not username:
        error_msg = "Username not provided"
    elif get_user(username):
        error_msg = "Username already being used"
    elif not password:
        error_msg = "Password not provided"
    elif not email:
        error_msg = "Email not provided"
    elif get_user_by_email(email):
        error_msg = "Email already registered"
    else:
        error_occured = False

    if error_occured:
        abort(400, error_msg)

    uname = sign_up(username, password, email)
    new_user = get_user(uname)

    return jsonify({'message': 'User signed up successfully', 'new_user': new_user}), 201


@app.route('/marketplace/api/sign-in', methods=['POST'])
def route_sign_in():
    """
    Perform sign in of a user.

    **Example** -

    :Request JSON Object:

    .. code-block:: JSON

        {
            "username": "johndoe",
            "password": "gaslbj3l4i"
        }

    :Response JSON Object:

    .. code-block:: JSON

        {
            "message": "Login successful"
        }

    :Status Codes:
        - 200 OK - Login successful
        - 404 Not found - Username not found
        - 400 Bad request - Incorrect password

    """

    error_code = sign_in(request.json['username'], request.json['password'])
    if error_code == 1:
        abort(404, "Username not found")

    if error_code == 2:
        abort(400, "Incorrect password")

    return jsonify({'message': 'Login successful'})


"""Product endpoints"""

@app.route('/marketplace/api/add-product', methods=['POST'])
def route_add_product():
    """
    Add product to database.

    **Example** -

    :Request JSON Object:

    .. code-block:: JSON

        {
            "inventory_count": 27,
            "price": 8.49,
            "title": "Strawberry tart"
        }

    :Response JSON Object:

    .. code-block:: JSON

        {
            "added_product": {
                "inventory_count": 27,
                "price": 8.49,
                "title": "Strawberry tart",
                "uri": "http://localhost:5000/marketplace/api/product/c6e63640-a8f0-48fb-921e-a2c5467dfdda"
            }
        }

    :Status Codes:
        - 201 Created - Product created/added
        - 400 Bad request - Malformed request

    """

    title, price, inventory = request.json['title'], request.json['price'], request.json['inventory_count']
    error_msg = ""
    error_occured = True
    if not title:
        error_msg = "Title of product is missing"
    elif not isinstance(price, (int, float)):
        error_msg = "Price of product has to be a number"
    elif price < 0:
        error_msg = "Price of product has to be non-negative"
    elif not isinstance(inventory, int):
        error_msg = "Inventory of product has to be a number"
    elif inventory < 0:
        error_msg = "Inventory of product has to be non-negative"
    else:
        error_occured = False

    if error_occured:
        abort(400, error_msg)

    new_product_id = add_product(title, price, inventory)
    return jsonify({'added_product': {'title': title, 'price': price, 'inventory_count': inventory, 'uri': generate_product_uri(new_product_id)}}), 201


@app.route('/marketplace/api/products', methods=['GET'])
def route_get_all_products():
    """
    Get all the products in the database with inventory greater than zero.

    **Example** -

    :Response JSON Object:

    .. code-block:: JSON

        {
            "products": [
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
                },
            ]
        }

    :Status Codes:
        - 200 OK - Products found
        - 404 Not found - Product(s) not found

    """

    all_products = get_all_products()
    if not all_products:
        abort(404, 'Product(s) not found')

    return jsonify({'products': all_products})


@app.route('/marketplace/api/product/<pid>', methods=['GET'])
def route_get_product(pid):
    """
    Get a single product from the database by its ID. Only returns product if it has inventory greater than zero.

    **Example** -

    .. code-block:: python

        /marketplace/api/product/84a1c5d6-d1fd-4db0-bc1e-f450a70ca7d9

    :Response JSON Object:

    .. code-block:: JSON

        {
            "product": {
                "inventory_count": 18,
                "price": 15.65,
                "title": "Mango pizza",
                "uri": "http://localhost:5000/marketplace/api/product/84a1c5d6-d1fd-4db0-bc1e-f450a70ca7d9"
            }
        }

    :Status Codes:
        - 200 OK - Product found
        - 404 Not found - Product not found

    """

    product = get_product(pid)
    if not product:
        abort(404, 'Product not found')

    return jsonify({'product': product})


@app.route('/marketplace/api/find-products/<title>', methods=['GET'])
def route_find_products(title):
    """
    Find products in the database whose title match *title* at least partially.
    Performs case-insensitive search. Only returns products with inventory greater than zero.

    **Example** -

    .. code-block:: python

        /marketplace/api/find-products/PCaK

    :Response JSON Object:

    .. code-block:: JSON

        {
            "products": [
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
        }

    :Status Codes:
        - 200 OK - Product(s) found
        - 404 Not found - Product(s) not found

    """

    matching_products = find_products(title)
    if not matching_products:
        abort(404, 'Product(s) not found')

    return jsonify({'products': matching_products})


@app.route('/marketplace/api/delete-product/<pid>', methods=['DELETE'])
def route_delete_product(pid):
    """
    Delete product whose ID matches the given ID from the database.

    **Example**

    .. code-block:: python

        /marketplace/api/delete-product/c6e63640-a8f0-48fb-921e-a2c5467dfdda

    :Response JSON Object:

    .. code-block:: JSON

        {
            "message": "Product deleted successfully",
            "removed_product": {
                "inventory_count": 27,
                "price": 8.49,
                "title": "Strawberry tart",
                "uri": "http://localhost:5000/marketplace/api/product/c6e63640-a8f0-48fb-921e-a2c5467dfdda"
            }
        }

    :Status Codes:
        - 200 OK - Product deleted
        - 404 Not found - Product not found

    """

    outcome = delete_product(pid)
    if not outcome[0]:
        abort(404, 'Product not found')

    return jsonify({'removed_product': outcome[1], 'message': 'Product deleted successfully'})


"""Cart endpoints"""

@app.route('/marketplace/api/add-product-to-cart', methods=['POST'])
def route_add_product_to_cart():
    """
    Add the given product to the given user's cart.

    **Example** -

    :Request JSON Object:

    .. code-block:: JSON

        {
            "username": "Midoriya",
            "product_id": "a37b3418-cc8f-40fa-8d63-661b3912eb71"
        }

    :Response JSON Object:

    .. code-block:: JSON

        {
            "added_product_to_cart": {
                "message": "Product added to cart successfully",
                "product": {
                    "inventory_count": 51,
                    "price": 4.99,
                    "title": "Guava cupcake",
                    "uri": "http://localhost:5000/marketplace/api/product/a37b3418-cc8f-40fa-8d63-661b3912eb71"
                },
                "username": "Midoriya"
            }
        }

    :Status Codes:
        - 200 OK - Product added to user's cart

    """

    uname_product = add_product_to_cart(request.json['username'], request.json['product_id'])
    uname_product['message'] = "Product added to cart successfully"

    return jsonify({'added_product_to_cart': uname_product})


@app.route('/marketplace/api/remove-product-from-cart', methods=['DELETE'])
def route_remove_product_from_cart():
    """
    Remove the given product from the given user's cart.

    **Example** -

    :Request JSON Object:

    .. code-block:: JSON

        {
            "username": "Midoriya",
            "product_id": "a37b3418-cc8f-40fa-8d63-661b3912eb71"
        }

    :Response JSON Object:

    .. code-block:: JSON

        {
            "removed_product_from_cart": {
                "message": "Product removed from cart successfully",
                "product": {
                    "inventory_count": 51,
                    "price": 4.99,
                    "title": "Guava cupcake",
                    "uri": "http://localhost:5000/marketplace/api/product/a37b3418-cc8f-40fa-8d63-661b3912eb71"
                },
                "username": "Midoriya"
            }
        }

    :Status Codes:
        - 200 OK - Product removed from user's cart

    """

    uname_product = remove_product_from_cart(request.json['username'], request.json['product_id'])
    uname_product['message'] = "Product removed from cart successfully"

    return jsonify({'removed_product_from_cart': uname_product})


@app.route('/marketplace/api/get-user-cart', methods=['POST'])
def route_get_user_cart():
    """
    Get the given user's cart.

    **Example** -

    :Request JSON Object:

    .. code-block:: JSON

        {
            "username": "Uraraka"
        }

    :Response JSON Object:

    .. code-block:: JSON

        {
            "user_cart": {
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
                    }
                ],
                "total_price": 15.98
            },
            "username": "Uraraka"
        }

    :Status Codes:
        - 200 OK - Retrieved user's cart

    """

    username = request.json['username']
    cart = get_user_cart(username)

    return jsonify({'user_cart': cart, 'username': username})


@app.route('/marketplace/api/complete-cart', methods=['POST'])
def route_complete_cart():
    """
    Complete the given user's cart. The cart is used to generate
    an order. The user's cart is cleared. The inventories of the
    products purchased by the user are decremented.

    Return the order information along with the product(s) whose
    inventories were decremented.

    **Example** -

    :Request JSON Object:

    .. code-block:: JSON

        {
            "username": "Midoriya"
        }

    :Response JSON Object:

    .. code-block:: JSON

        {
            "affected_products": [
                {
                    "inventory_count": 7,
                    "price": 7.99,
                    "title": "Orange cupcake",
                    "uri": "http://localhost:5000/marketplace/api/product/f4ad5da8-2cc5-4ec0-86f3-4c02367c082f"
                }
            ],
            "order": {
                "amount": 15.98,
                "order_id": "baef750f-9c54-41f8-a7a5-647640ff62d1",
                "products": [
                    {
                        "inventory_count": 7,
                        "price": 7.99,
                        "title": "Orange cupcake",
                        "uri": "http://localhost:5000/marketplace/api/product/f4ad5da8-2cc5-4ec0-86f3-4c02367c082f"
                    },
                    {
                        "inventory_count": 7,
                        "price": 7.99,
                        "title": "Orange cupcake",
                        "uri": "http://localhost:5000/marketplace/api/product/f4ad5da8-2cc5-4ec0-86f3-4c02367c082f"
                    },
                ],
                "username": "Uraraka"
            }
        }

    :Status Codes:
        - 200 OK - Cart completed

    """

    username = request.json['username']
    affected_products = decrement_inventories(username)
    order = get_order(generate_order(username))
    clear_user_cart(username)

    return jsonify({'order': order, 'affected_products': affected_products})


"""Order endpoints"""

@app.route('/marketplace/api/order/<order_id>', methods=['GET'])
def route_get_order(order_id):
    order = get_order(order_id)
    if not order:
        abort(404, 'Order not found')

    return jsonify({'order': order})


'''
Error handling
'''

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'message': error.description}), 404)


@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'message': error.description}), 400)


if __name__ == '__main__':
    app.run(debug=True)
