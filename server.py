from uuid import uuid4
from flask import Flask, jsonify, abort, make_response, request, url_for
from tinydb import TinyDB, Query

db = TinyDB('db.json')
products = db.table('products')
users = db.table('users')

app = Flask(__name__)

'''
DB functions
'''

def sign_up(uname, pwd, email):
    new_user_id = users.insert({'username': uname, 'password': pwd, 'email': email})

    return new_user_id


def sign_in(uname, pwd):
    User_query = Query()
    found_user = users.get(User_query.username == uname)
    if not found_user:
        return 1

    if found_user['password'] != pwd:
        return 2

    return 0


def get_user(user_id):
    return users.get(doc_id=user_id)


def add_product(title, price, inventory_count):
    product_id = str(uuid4())
    products.insert({'title': title, 'price': price, 'inventory_count': inventory_count,
                     'uri': url_for('route_get_product', pid=product_id, _external=True)})
    return product_id


def return_all_products():
    Product_query = Query()
    return products.search(Product_query.inventory_count > 0)


def return_product(product_id):
    Product_query = Query()
    return products.get((Product_query.uri ==
                            url_for('route_get_product', pid=product_id, _external=True))
                           & (Product_query.inventory_count > 0))


def find_products(search_title):
    if not search_title:
        return return_all_products()

    Product_query = Query()
    return products.search((Product_query.title.test(find_func, search_title))
                           & (Product_query.inventory_count > 0))


def find_func(string, substring):
    if substring in string:
        return True

    return False


def delete_product(product_id):
    Product_query = Query()
    prod_to_delete = products.get(Product_query.uri ==
                                     url_for('route_get_product', pid=product_id, _external=True))
    if not prod_to_delete:
        return [False]

    products.remove(doc_ids=[prod_to_delete.doc_id])
    return [True, prod_to_delete]


'''
Endpoints
'''

@app.route('/marketplace/api/products', methods=['GET'])
def route_get_products():
    all_products = return_all_products()
    if not all_products:
        abort(404)

    return jsonify({'products': all_products})


@app.route('/marketplace/api/product/<pid>', methods=['GET'])
def route_get_product(pid):
    product = return_product(pid)
    if not product:
        abort(404)

    return jsonify({'product': product})


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'message': 'Product(s) not found'}), 404)


@app.route('/marketplace/api/add-product', methods=['POST'])
def route_add_product():
    new_product_id = add_product(request.json['title'],
                                 request.json['price'], request.json['inventory_count'])

    return jsonify({'added_product': return_product(new_product_id)}), 201


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


@app.route('/marketplace/api/sign-up', methods=['POST'])
def route_sign_up():
    new_user_id = sign_up(request.json['username'],
                          request.json['password'], request.json['email'])

    new_user = get_user(new_user_id)
    new_user['password'] = '***************'

    return jsonify({'new_user': new_user})


@app.route('/marketplace/api/sign-in', methods=['POST'])
def route_sign_in():
    error_code = sign_in(request.json['username'], request.json['password'])
    if error_code == 1:
        return jsonify({'message': 'Username not found'})

    if error_code == 2:
        return jsonify({'message': 'Incorrect password'})

    return jsonify({'message': 'Login successful'})


if __name__ == '__main__':
    app.run(debug=True)
