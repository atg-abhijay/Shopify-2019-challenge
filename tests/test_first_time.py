import requests 
import pytest

url = "http://localhost:5000/marketplace/api/sign-up"

@pytest.mark.firsttime
def test_route_sign_up_success():
    body = {
	"username": "Abhijay",
    "password": "a123",
    "email": "a@aj.com"
    }
    r = requests.post(url, json=body)
    assert r.json()['message'] == 'User signed up successfully'

@pytest.mark.firsttime
def test_all_products_when_no_product_has_been_added():
    url = "http://localhost:5000/marketplace/api/products"
    r = requests.get(url)
    assert r.status_code == 404
    assert r.json()['message'] == "Product(s) not found"