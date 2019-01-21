.. Shopify Dev Challenge documentation master file, created by
   sphinx-quickstart on Sat Jan 19 17:18:51 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Shopify Dev Challenge's documentation
*************************************

.. toctree::
   :maxdepth: 2
   :caption: Contents:

.. contents::

Database functions
==================

User functions
--------------
.. automodule:: user_functions
   :members: sign_up, sign_in, get_user, get_user_by_email


Product functions
-----------------
.. automodule:: product_functions
    :members: add_product, get_all_products, get_product, find_products, delete_product, decrement_inventories


Cart functions
--------------
.. automodule:: cart_functions
    :members: add_product_to_cart, remove_product_from_cart, get_user_cart, clear_user_cart


Order functions
---------------
.. automodule:: order_functions
    :members: get_order, generate_order


Helper functions
----------------
.. automodule:: helper_functions
    :members: generate_product_uri, find_func


Endpoints
=========

User endpoints
--------------
.. autoflask:: marketplace:app
    :endpoints: route_sign_up, route_sign_in


Product endpoints
-----------------
.. autoflask:: marketplace:app
    :endpoints: route_add_product, route_get_all_products, route_get_product, route_find_products, route_delete_product


Cart endpoints
--------------
.. autoflask:: marketplace:app
    :endpoints: route_add_product_to_cart, route_remove_product_from_cart, route_get_user_cart, route_complete_cart


Order endpoints
---------------
.. autoflask:: marketplace:app
    :endpoints: route_get_order


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
