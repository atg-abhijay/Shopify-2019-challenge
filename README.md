# Shopify_2019_challenge

This is my submission for the [Developer Internship Challenge](https://docs.google.com/document/d/1J49NAOIoWYOumaoQCKopPfudWI_jsQWVKlXmw1f1r-4/edit). I have made a [Flask](http://flask.pocoo.org/) server that utilises [TinyDB](https://tinydb.readthedocs.io/en/latest/index.html) as the database.

Tested using Python 3.5.2 

To install the requirements for the challenge, please execute
the following command from the location of the file *requirements.txt*:
```python
pip install -r "requirements.txt"
```

The documentation can be found in: (generated using [Sphinx](http://www.sphinx-doc.org/en/master/))
```
build/html/index.html
```

To run the server, run the following command from the location of the file *marketplace.py*:
```python
python marketplace.py
```

To run the tests, run the following command from the *tests* directory:
```python
python run_tests.py -h
```

Some examples of how the test can be run are:
```
python run_tests.py --spec all
python run_tests.py --spec product
```

The endpoints provided are:
* User endpoints:-
  * Sign up
  * Sign in
  
* Product endpoints:-
  * Add product
  * Get all products
  * Get product
  * Find products
  * Delete product

* Cart endpoints:-
  * Add product to cart
  * Remove product from cart
  * Get a user's cart
  * Complete a user's cart
  
* Order endpoints:-
  * Get order
