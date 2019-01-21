import requests
TEST_PRODUCT_URI = ""
TEST_PRODUCT_BODY = {}
url = "http://localhost:5000/marketplace/api/add-product"


def test_product_title_missing():
    body = {
	"title": "",
	"price": 12.49,
	"inventory_count": 23
    }
    r = requests.post(url, json=body)
    assert r.status_code == 400
    assert r.json()['message'] == "Title of product is missing"

def test_price_not_number():
    body = {
	"title": "Mango cake",
	"price": "sgsg",
	"inventory_count": 23
    }
    r = requests.post(url, json=body)
    assert r.status_code == 400
    assert r.json()['message'] == "Price of product has to be a number"

def test_price_negative():
    body = {
	"title": "Mango cake",
	"price": -234,
	"inventory_count": 23
    }
    r = requests.post(url, json=body)
    assert r.status_code == 400
    assert r.json()['message'] == "Price of product has to be non-negative"

def test_inventory_count_not_number():
    body = {
	"title": "Mango cake",
	"price": 12.40,
	"inventory_count": 45.2
    }
    r = requests.post(url, json=body)
    assert r.status_code == 400
    assert r.json()['message'] == "Inventory of product has to be a number"

def test_inventory_count_negative():
    body = {
	"title": "Mango cake",
	"price": 12.40,
	"inventory_count": -26
    }
    r = requests.post(url, json=body)
    assert r.status_code == 400
    assert r.json()['message'] == "Inventory of product has to be non-negative"

def test_add_product():
    body = {
	"title": "Mango cake",
	"price": 12.40,
	"inventory_count": 10
    }
    r = requests.post(url, json=body)
    global TEST_PRODUCT_URI
    global TEST_PRODUCT_BODY
    TEST_PRODUCT_URI = r.json()['added_product']['uri']
    TEST_PRODUCT_BODY = body
    assert r.status_code == 201

def test_get_all_products():
    r = requests.get("http://localhost:5000/marketplace/api/products")

def test_get_one_product():
    global TEST_PRODUCT_BODY
    global TEST_PRODUCT_URI
    r = requests.get(TEST_PRODUCT_URI)
    assert r.status_code == 200
    assert r.json()['product']['inventory_count'] == TEST_PRODUCT_BODY['inventory_count']
    assert r.json()['product']['title'] == TEST_PRODUCT_BODY['title']
    assert r.json()['product']['price'] == TEST_PRODUCT_BODY['price']
