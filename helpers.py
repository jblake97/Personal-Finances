from flask import redirect, session
from functools import wraps
import sqlite3
from sqlite3 import Error

def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


# Connect to sqlite database
def create_connection(path):
    connection = None
    #postgresql://personal_finances_user:Ab3Sw3li20vMg5atsczLtPXDes3QL36R@dpg-cgupopo2qv28lbeg7ur0-a.ohio-postgres.render.com/personal_finances
    try:
        connection = sqlite3.connect(path)
        print("Connected successfully!")
    except Error as e:
        print(f"The error '{e}' occured")

    return connection


def execute_read_query(connection, query):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        connection.commit()
        return result
    except Error as e:
        print(f"The error '{e}' occured")


def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print("Query executed successfully")
    except Error as e:
        print(f"The error '{e}' occured")