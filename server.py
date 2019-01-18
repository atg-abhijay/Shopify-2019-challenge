from uuid import uuid4
from flask import Flask, jsonify, abort, make_response, request, url_for
from tinydb import TinyDB, Query
from tinydb.operations import decrement

db = TinyDB('db.json')
products = db.table('products')
users = db.table('users')

app = Flask(__name__)

'''
DB functions
'''

"""User functions"""

def sign_up(uname, pwd, email):
    users.insert({'username': uname, 'password': pwd, 'email': email})
    return uname


def sign_in(uname, pwd):
    User_query = Query()
    found_user = users.get(User_query.username == uname)
    if not found_user:
        return 1

    if found_user['password'] != pwd:
        return 2

    return 0


def get_user(uname):
    User_query = Query()
    return users.get(User_query.username == uname)


def get_user_by_email(email):
    User_query = Query()
    return users.get(User_query.email == email)


"""Product functions"""

def add_product(title, price, inventory_count):
    product_id = str(uuid4())
    products.insert({'title': title, 'price': price, 'inventory_count': inventory_count,
                     'uri': generate_product_uri(product_id)})
    return product_id


def get_all_products():
    Product_query = Query()
    return products.search(Product_query.inventory_count > 0)


def get_product(product_id):
    Product_query = Query()
    return products.get((Product_query.uri == generate_product_uri(product_id))
                        & (Product_query.inventory_count > 0))


def find_products(search_title):
    if not search_title:
        return get_all_products()

    Product_query = Query()
    return products.search((Product_query.title.test(find_func, search_title))
                           & (Product_query.inventory_count > 0))


def delete_product(product_id):
    Product_query = Query()
    prod_to_delete = products.get(Product_query.uri == generate_product_uri(product_id))
    if not prod_to_delete:
        return [False]

    products.remove(doc_ids=[prod_to_delete.doc_id])
    return [True, prod_to_delete]


"""Cart functions"""

def add_product_to_cart(uname, product_uri):
    User_query = Query()
    Product_query = Query()
    current_user = users.get(User_query.username == uname)
    if 'cart' not in current_user:
        current_user['cart'] = [product_uri]
    else:
        current_user['cart'].append(product_uri)

    users.update({'cart': current_user['cart']}, User_query.username == uname)

    return jsonify({'message': 'Product added to cart successfully', 'username': uname,
                    'product': products.get(Product_query.uri == product_uri)})


def remove_product_from_cart(uname, product_uri):
    User_query = Query()
    Product_query = Query()
    current_user = users.get(User_query.username == uname)
    current_user['cart'].remove(product_uri)
    users.update({'cart': current_user['cart']}, User_query.username == uname)

    return jsonify({'message': 'Product removed from cart successfully', 'username': uname,
                    'product': products.get(Product_query.uri == product_uri)})


def return_user_cart(uname):
    User_query = Query()
    Product_query = Query()
    current_user_cart = users.get(User_query.username == uname)['cart']
    cart = {'products': [], 'total_price': 0}
    for product_uri in current_user_cart:
        cart_product = products.get(Product_query.uri == product_uri)
        cart['products'].append(cart_product)
        cart['total_price'] += cart_product['price']

    return jsonify({'cart': cart})


"""Helper functions"""

def generate_product_uri(product_id):
    return url_for('route_get_product', pid=product_id, _external=True)


def find_func(string, substring):
    if substring in string:
        return True

    return False


def decrement_inventories(uname):
    User_query = Query()
    Product_query = Query()
    current_user_cart = users.get(User_query.username == uname)['cart']
    for product_uri in current_user_cart:
        products.update(decrement('inventory_count'), Product_query.uri == product_uri)


'''
Endpoints
'''

"""User endpoints"""

@app.route('/marketplace/api/sign-up', methods=['POST'])
def route_sign_up():
    username, password, email = request.json['username'], request.json['password'], request.json['email']
    error_msg = ""
    error_occured = False
    if not username:
        error_msg = "Username not provided"
        error_occured = True
    elif get_user(username):
        error_msg = "Username already being used"
        error_occured = True
    elif not password:
        error_msg = "Password not provided"
        error_occured = True
    elif not email:
        error_msg = "Email not provided"
        error_occured = True
    elif get_user_by_email(email):
        error_msg = "Email already registered"
        error_occured = True

    if error_occured:
        abort(400, error_msg)

    uname = sign_up(username, password, email)
    new_user = get_user(uname)
    new_user.pop('password')

    return jsonify({'message': 'User signed up successfully', 'new_user': new_user})


@app.route('/marketplace/api/sign-in', methods=['POST'])
def route_sign_in():
    error_code = sign_in(request.json['username'], request.json['password'])
    if error_code == 1:
        return jsonify({'message': 'Username not found'})

    if error_code == 2:
        return jsonify({'message': 'Incorrect password'})

    return jsonify({'message': 'Login successful'})


"""Product endpoints"""

@app.route('/marketplace/api/add-product', methods=['POST'])
def route_add_product():
    title, price, inventory = request.json['title'], request.json['price'], request.json['inventory_count']
    if not title:
        abort(400, 'Title of product is missing')

    if not isinstance(price, (int, float)):
        abort(400, 'Price of product has to be a number')

    if price < 0:
        abort(400, 'Price of product has to be non-negative')

    if not isinstance(inventory, int):
        abort(400, 'Inventory of product has to be a number')

    if inventory < 0:
        abort(400, 'Inventory of product has to be non-negative')

    new_product_id = add_product(title, price, inventory)
    return jsonify({'added_product': {'title': title, 'price': price, 'inventory_count': inventory, 'uri': generate_product_uri(new_product_id)}}), 201


@app.route('/marketplace/api/products', methods=['GET'])
def route_get_all_products():
    all_products = get_all_products()
    if not all_products:
        abort(404)

    return jsonify({'products': all_products})


@app.route('/marketplace/api/product/<pid>', methods=['GET'])
def route_get_product(pid):
    product = get_product(pid)
    if not product:
        abort(404)

    return jsonify({'product': product})


@app.route('/marketplace/api/find-products/<title>', methods=['GET'])
def route_find_products(title):
    matching_products = find_products(title)
    if not matching_products:
        return jsonify({'message': 'No such products found'})

    return jsonify({'products': matching_products})


@app.route('/marketplace/api/delete-product/<pid>', methods=['DELETE'])
def route_delete_product(pid):
    outcome = delete_product(pid)
    if not outcome[0]:
        return jsonify({'message': 'No such product exists'})

    return jsonify({'removed_product': outcome[1], 'message': 'Product deleted successfully'})


'''
Error handling
'''

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'message': 'Product(s) not found'}), 404)


@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'message': error.description}), 400)


if __name__ == '__main__':
    app.run(debug=True)
