import requests
import json
TEST_PRODUCT_URI = ""
TEST_PRODUCT_BODY = {}
product_url = "http://localhost:5000/marketplace/api/add-product"


def test_product_title_missing():
    body = {
	"title": "",
	"price": 12.49,
	"inventory_count": 23
    }
    r = requests.post(product_url, json=body)
    assert r.status_code == 400
    assert r.json()['message'] == "Title of product is missing"

def test_price_not_number():
    body = {
	"title": "Mango cake",
	"price": "sgsg",
	"inventory_count": 23
    }
    r = requests.post(product_url, json=body)
    assert r.status_code == 400
    assert r.json()['message'] == "Price of product has to be a number"

def test_price_negative():
    body = {
	"title": "Mango cake",
	"price": -234,
	"inventory_count": 23
    }
    r = requests.post(product_url, json=body)
    assert r.status_code == 400
    assert r.json()['message'] == "Price of product has to be non-negative"

def test_inventory_count_not_number():
    body = {
	"title": "Mango cake",
	"price": 12.40,
	"inventory_count": 45.2
    }
    r = requests.post(product_url, json=body)
    assert r.status_code == 400
    assert r.json()['message'] == "Inventory of product has to be a number"

def test_inventory_count_negative():
    body = {
	"title": "Mango cake",
	"price": 12.40,
	"inventory_count": -26
    }
    r = requests.post(product_url, json=body)
    assert r.status_code == 400
    assert r.json()['message'] == "Inventory of product has to be non-negative"

def test_add_product():
    body = {
	"title": "Crab cake",
	"price": 12.40,
	"inventory_count": 10
    }
    r = requests.post(product_url, json=body)
    global TEST_PRODUCT_URI
    global TEST_PRODUCT_BODY
    TEST_PRODUCT_URI = r.json()['added_product']['uri']
    TEST_PRODUCT_BODY = r.json()['added_product']
    assert r.status_code == 201

def test_get_one_product():
    global TEST_PRODUCT_BODY
    global TEST_PRODUCT_URI
    r = requests.get(TEST_PRODUCT_URI)
    assert r.status_code == 200
    assert r.json()['product']['inventory_count'] == TEST_PRODUCT_BODY['inventory_count']
    assert r.json()['product']['title'] == TEST_PRODUCT_BODY['title']
    assert r.json()['product']['price'] == TEST_PRODUCT_BODY['price']

def test_get_all_products():
    r = requests.get("http://localhost:5000/marketplace/api/products")
    assert r.status_code == 200
    assert r.json()['products']
    assert len(r.json()['products']) >= 1 #checking that there are at least one or more products

def test_existing_product():
    r = requests.get(TEST_PRODUCT_URI)
    assert r.status_code == 200
    assert r.json()['product'] == TEST_PRODUCT_BODY

def test_non_existent_product():
    r = requests.get(TEST_PRODUCT_URI+"gibberish")
    assert r.status_code == 404
    assert r.json()['message'] == "Product not found"

def test_find_existing_products():
    r = requests.get("http://localhost:5000/marketplace/api/find-products/" + TEST_PRODUCT_BODY['title'].split(" ")[0])
    assert r.status_code == 200
    assert r.json()['products']
    assert len(r.json()['products']) >= 1

def test_find_non_existing_products():
    r = requests.get("http://localhost:5000/marketplace/api/find-products/Orrangeee")
    assert r.status_code == 404
    assert r.json()['message'] == "Product(s) not found"

def test_add_product_to_cart():
    body = {
        "username": "Abhijay",
	    "product_id": TEST_PRODUCT_URI.split("/")[-1]
    }
    r = requests.post("http://localhost:5000/marketplace/api/add-product-to-cart", json=body)
    assert r.status_code == 200
    assert r.json()['message'] == "Product added to cart successfully"
    assert r.json()['added_product_to_cart']['username'] == "Abhijay"
    assert r.json()['added_product_to_cart']['product'] == TEST_PRODUCT_BODY

def test_delete_product_from_cart():
    body = {
        "username": "Abhijay",
	    "product_id": TEST_PRODUCT_URI.split("/")[-1]
    }
    r = requests.delete("http://localhost:5000/marketplace/api/remove-product-from-cart", json=body)
    assert r.status_code == 200
    assert r.json()['message'] == "Product removed from cart successfully"
    assert r.json()['removed_product_from_cart']['username'] == "Abhijay"
    assert r.json()['removed_product_from_cart']['product'] == TEST_PRODUCT_BODY

def test_delete_existing_product():
    r = requests.delete("http://localhost:5000/marketplace/api/delete-product/"+TEST_PRODUCT_URI.split('/')[-1])
    assert r.status_code == 200
    assert r.json()['message'] == "Product deleted successfully"
    assert r.json()['removed_product'] == TEST_PRODUCT_BODY

def test_delete_non_existing_product():
    r = requests.delete("http://localhost:5000/marketplace/api/delete-product/"+"gibberish")
    assert r.status_code == 404
    assert r.json()['message'] == "Product not found"