import requests
url = "http://localhost:5000/marketplace/api/sign-up"

def test_username_not_provided():
    body = {
	"username": "",
	"password": "3gst3b",
	"email": "b@bk.com"
    }
    r = requests.post(url, json=body)
    assert r.json()['message'] == "Username not provided"

def test_username_already_being_used():
    body = {
	"username": "Abhijay",
	"password": "3gst3b",
	"email": "k@cs.com"
    }
    r = requests.post(url, json=body)
    assert r.json()['message'] == "Username already being used"

def test_password_not_provided():
    body = {
	"username": "Blake",
	"password": "",
	"email": "k@cs.com"
    }
    r = requests.post(url, json=body)
    assert r.json()['message'] == "Password not provided"

def test_email_not_provided():
    body = {
	"username": "Aaron",
	"password": "52tfsfa24t",
	"email": ""
    }
    r = requests.post(url, json=body)
    assert r.json()['message'] == "Email not provided"

def test_email_already_registered():
    body = {
	"username": "Jacqueline",
	"password": "52tfsfa24t",
	"email": "a@aj.com"
    }
    r = requests.post(url, json=body)
    assert r.json()['message'] == "Email already registered"