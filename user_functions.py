from tinydb import TinyDB, Query

users = TinyDB('db.json').table('users')

def sign_up(uname, pwd, email):
    """
    Sign up a new user to the database.

    :param str uname: Username (has to be unique)
    :param str pwd: Password
    :param str email: Email (has to be unique)

    :returns: Username of the new user
    :rtype: *str*

    """
    users.insert({'username': uname, 'password': pwd, 'email': email, 'cart': []})
    return uname


def sign_in(uname, pwd):
    """
    Perform sign in of a user.

    :param str uname: Username
    :param str pwd: Password

    :returns:
        * 0 - successful login.
        * 1 - user not found.
        * 2 - incorrect password.

    """
    User_query = Query()
    found_user = users.get(User_query.username == uname)
    if not found_user:
        return 1

    if found_user['password'] != pwd:
        return 2

    return 0


def get_user(uname):
    """
    Retrieve user based on their username.

    :param str uname: Username

    :returns: User whose username matches the passed parameter
    :rtype: *dict*

    - Example

    .. code-block:: JSON

        {
            "username": "johndoe",
            "email": "johndoe@email.com"
            "cart": [
                "63f6-bj6m-345k",
                "354g-3427-nb38"
            ]
        }

    """
    User_query = Query()
    user = users.get(User_query.username == uname)
    if user:
        user.pop('password')

    return user


def get_user_by_email(email):
    """
    Retrieve user based on their email.

    :param str email: User's email

    :returns: User whose username matches the passed parameter
    :rtype: *dict*

    - Example

    .. code-block:: JSON

        {
            "username": "johndoe",
            "email": "johndoe@email.com"
            "cart": [
                "63f6-bj6m-345k",
                "354g-3427-nb38"
            ]
        }

    """
    User_query = Query()
    user = users.get(User_query.email == email)
    if user:
        user.pop('password')

    return user
