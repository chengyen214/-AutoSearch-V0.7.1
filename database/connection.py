"""
connection.py

Database Connection
AutoSearch V2.5
"""

import mysql.connector
from mysql.connector import Error

from config.database import (
    HOST,
    PORT,
    USER,
    PASSWORD,
    DATABASE,
    CHARSET
)


def get_connection():
    """
    建立並回傳 MySQL Connection
    """

    try:

        connection = mysql.connector.connect(

            host=HOST,

            port=PORT,

            user=USER,

            password=PASSWORD,

            database=DATABASE,

            charset=CHARSET

        )

        return connection

    except Error as e:

        print(f"[Database Error] {e}")

        return None