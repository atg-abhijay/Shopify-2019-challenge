from flask import Flask, jsonify, abort, make_response, request
from tinydb import TinyDB
from user_functions import sign_in, sign_up, get_user, get_user_by_email
from product_functions import add_product, get_all_products, get_product, find_products, delete_product, decrement_inventories
from helper_functions import generate_product_uri
from cart_functions import add_product_to_cart, remove_product_from_cart, get_user_cart, clear_user_cart
from order_functions import get_order, generate_order

db = TinyDB('db.json')
products = db.table('products')
users = db.table('users')
orders = db.table('orders')

app = Flask(__name__)


'''
Endpoints
'''

### User endpoints ###

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


### Product endpoints ###

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


### Cart endpoints ###

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
        - 404 Not found - Product not in cart anymore

    """

    uname_product = remove_product_from_cart(request.json['username'], request.json['product_id'])
    if not uname_product:
        abort(404, 'Product not in cart anymore')

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
        - 404 Not found - User not found or User's cart is empty

    """

    username = request.json['username']
    user = get_user(username)
    if not user:
        abort(404, "User not found")

    if not user['cart']:
        abort(404, "User's cart is empty")

    affected_products = decrement_inventories(username)
    order = get_order(generate_order(username))
    clear_user_cart(username)

    return jsonify({'order': order, 'affected_products': affected_products})


### Order endpoints ###

@app.route('/marketplace/api/order/<order_id>', methods=['GET'])
def route_get_order(order_id):
    """
    Get order with the given ID.

    **Example** -

    .. code-block:: python

        /marketplace/api/order/274a5c89-f9ad-4043-a07c-0d545512291b

    :Response JSON Object:

    .. code-block:: JSON

        {
            "order": {
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
                "username": "Midoriya"
            }
        }

    :Status Codes:
        - 200 OK - Order found
        - 404 Not found - Order *not* found

    """

    order = get_order(order_id)
    if not order:
        abort(404, 'Order not found')

    return jsonify({'order': order})


'''
Error handling
'''

@app.errorhandler(404)
def not_found(error):
    """
    Return a 404 (Not found) error with a custom message.
    """
    return make_response(jsonify({'message': error.description}), 404)


@app.errorhandler(400)
def bad_request(error):
    """
    Return a 400 (Bad request) error with a custom message.
    """
    return make_response(jsonify({'message': error.description}), 400)


if __name__ == '__main__':
    app.run(debug=True, ssl_context=('cert.pem', 'key.pem'))
