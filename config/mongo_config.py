"""
config/mongo_config.py

AutoSearch V4

MongoDB Configuration

用途：

    MongoDB 連線與 Raw HTML Storage 設定。

負責：

    - MongoDB URI
    - MongoDB Database Name
    - Raw HTML Collection Name

不負責：

    - MongoDB Connection
    - Repository
    - CRUD
    - Crawler
    - HTML Processing

目前：

    MongoDB Community Server
    localhost:27017

Database：

    autosearch

Collection：

    raw_html
"""

import os


# ==================================================
# MongoDB Connection
# ==================================================

MONGO_URI = os.getenv(
    "MONGO_URI",
    "mongodb://localhost:27017"
)


# ==================================================
# MongoDB Database
# ==================================================

MONGO_DATABASE = os.getenv(
    "MONGO_DATABASE",
    "autosearch"
)


# ==================================================
# Raw HTML Collection
# ==================================================

MONGO_RAW_HTML_COLLECTION = os.getenv(
    "MONGO_RAW_HTML_COLLECTION",
    "raw_html"
)


# ==================================================
# Configuration Validation
# ==================================================

def validate_mongo_config():
    """
    驗證 MongoDB 設定。

    Returns
    -------

    bool
        True:
            設定有效

        False:
            設定無效
    """

    if not MONGO_URI:

        return False

    if not MONGO_DATABASE:

        return False

    if not MONGO_RAW_HTML_COLLECTION:

        return False

    return True
