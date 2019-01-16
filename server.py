from uuid import uuid4
from flask import Flask, jsonify, abort, make_response, request, url_for
from tinydb import TinyDB, Query

db = TinyDB('db.json')
products = db.table('products')

app = Flask(__name__)

'''
DB functions
'''

def add_product(title, price, inventory_count):
    product_id = str(uuid4())
    products.insert({'title': title, 'price': price, 'inventory_count': inventory_count, 'uri': url_for('route_get_product', pid=product_id, _external=True)})
    return product_id


def return_all_products():
    return products.all()


def return_product(product_id):
    Product_query = Query()
    return products.search(Product_query.uri == url_for('route_get_product', pid=product_id, _external=True))


def find_products(search_title):
    if not search_title:
        return return_all_products()

    Product_query = Query()
    return products.search(Product_query.title.test(find_func, search_title))


def find_func(string, substring):
    if substring in string:
        return True

    return False


def delete_product(product_id):
    # products.remove(doc_ids=[prod_id])
    Product_query = Query()
    prod_to_delete = products.search(Product_query.uri == url_for('route_get_product', pid=product_id, _external=True))
    if not prod_to_delete:
        return [False]

    products.remove(doc_ids=[prod_to_delete[0].doc_id])
    return [True, prod_to_delete[0]]


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

    return jsonify({'product': product[0]})


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Product(s) not found'}), 404)


@app.route('/marketplace/api/add-product', methods=['POST'])
def route_add_product():
    new_product_id = add_product(request.json['title'], request.json['price'], request.json['inventory_count'])

    return jsonify({'product': return_product(new_product_id)[0]}), 201


@app.route('/marketplace/api/find-products/<title>', methods=['GET'])
def route_find_products(title):
    matching_products = find_products(title)
    if not matching_products:
        return jsonify({'products': 'none found!'})

    return jsonify({'products': matching_products})


@app.route('/marketplace/api/delete-product/<pid>', methods=['DELETE'])
def route_delete_product(pid):
    outcome = delete_product(pid)
    if not outcome[0]:
        return jsonify({'message': 'No such product exists'})

    return jsonify({'removed_product': outcome[1], 'message': 'Product deleted successfully'})


if __name__ == '__main__':
    app.run(debug=True)
