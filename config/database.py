"""
database.py

Database Configuration
AutoSearch V4
"""

import os

from dotenv import load_dotenv


# ============================================================
# Load Environment Variables
# ============================================================

load_dotenv()


# ============================================================
# Database Configuration
# ============================================================

HOST = os.getenv(
    "DB_HOST",
    "localhost"
)

PORT = int(
    os.getenv(
        "DB_PORT",
        "3306"
    )
)


USER = os.getenv(
    "DB_USER",
    "root"
)

PASSWORD = os.getenv(
    "DB_PASSWORD",
    ""
)


DATABASE = os.getenv(
    "DB_NAME",
    "autosearch"
)


CHARSET = os.getenv(
    "DB_CHARSET",
    "utf8mb4"
)