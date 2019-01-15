from flask import Flask, jsonify, abort, make_response, request, url_for
from tinydb import TinyDB, Query

db = TinyDB('db.json')
products = db.table('products')

app = Flask(__name__)
num_products = 0

'''
DB functions
'''

def add_product(title, price, inventory_count):
    global num_products
    num_products += 1
    products.insert({'title': title, 'price': price, 'inventory_count': inventory_count, 'uri': url_for('route_get_product', pid=num_products, _external=True)})
    return num_products


def return_all_products():
    return products.all()


def return_product(product_id):
    return products.get(doc_id=product_id)

'''
Endpoints
'''

@app.route('/marketplace/api/products', methods=['GET'])
def route_get_products():
    all_products = return_all_products()
    if not all_products:
        abort(404)

    return jsonify({'products': all_products})


@app.route('/marketplace/api/product/<int:pid>', methods=['GET'])
def route_get_product(pid):
    product = return_product(pid)
    if not product:
        abort(404)

    return jsonify({'product': product})


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'not found'}), 404)


@app.route('/marketplace/api/products', methods=['POST'])
def route_add_product():
    new_product_id = add_product(request.json['title'], request.json['price'], request.json['inventory_count'])

    return jsonify({'product': return_product(new_product_id)})


if __name__ == '__main__':
    app.run(debug=True)
