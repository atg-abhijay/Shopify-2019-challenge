import requests
url = "http://localhost:5000/marketplace/api/sign-in"

def test_successful_login():
    body = {
	"username": "Abhijay",
	"password": "a123"
    }   
    r = requests.post(url, json=body)
    assert r.json()['message'] == "Login successful"

def test_non_existent_username():
    body = {
	"username": "Alakazam",
	"password": "a123"
    }   
    r = requests.post(url, json=body)
    assert r.json()['message'] == "Username not found"

def test_incorrect_password():
    body = {
	"username": "Abhijay",
	"password": "sfa23"
    }   
    r = requests.post(url, json=body)
    assert r.json()['message'] == "Incorrect password"