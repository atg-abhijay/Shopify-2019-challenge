from flask import url_for

def generate_product_uri(product_id):
    """
    Generate a product URI based on its ID.

    :param str product_id: ID of the product

    :returns: A URI for the given product
    :rtype: *str*

    """

    return url_for('route_get_product', pid=product_id, _external=True)


def find_func(string, substring):
    """
    Check if one string is present in another string.

    :param str string: String to check in
    :param str substring: Substring we are interested in

    :returns:
        - *True* if the substring is present in the string
        - *False* if the substring is *not* present in the string

    """

    if substring.lower() in string.lower():
        return True

    return False
