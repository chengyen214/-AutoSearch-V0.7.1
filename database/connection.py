"""
connection.py

Database Connection
AutoSearch V4
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
    建立並回傳 MySQL Connection。

    Local:
        HOST=localhost

    Docker:
        HOST=mysql
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

        print(
            f"[Database Error] "
            f"{e}"
        )

        return None