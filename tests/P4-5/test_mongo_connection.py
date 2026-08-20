"""
tests/P4-5/test_mongo_connection.py

AutoSearch V4

MongoDB Connection Test

用途：

    驗證 AutoSearch V4 MongoDB Connection Layer。

測試：

    1. MongoConnection 可以建立。
    2. MongoDB Server 可以正常連線。
    3. MongoDB ping 成功。
    4. 可以取得 autosearch Database。
    5. 可以取得指定 Collection。
    6. Connection 可以正常關閉。

目前架構：

    config/mongo_config.py
            |
            v
    database/mongo_connection.py
            |
            v
    MongoDB Community Server
            |
            v
    autosearch

注意：

    本測試只驗證 Connection。

    不測試：

        Raw HTML Repository
        Crawler
        ArticleRepository
        MySQL
        archive/html
        MongoDB CRUD
"""


import pytest


from config.mongo_config import (
    MONGO_DATABASE,
    MONGO_RAW_HTML_COLLECTION
)


from database.mongo_connection import (
    MongoConnection
)


# ==================================================
# MongoDB Connection Test
# ==================================================


def test_mongo_connection():
    """
    測試 MongoDB Connection。

    驗證：

        MongoDB Server
            ↓
        MongoConnection
            ↓
        Database
            ↓
        Collection
    """

    connection = None

    try:

        # ==========================================
        # Create Connection
        # ==========================================

        connection = MongoConnection()

        assert connection is not None

        # ==========================================
        # Client
        # ==========================================

        assert connection.client is not None

        # ==========================================
        # Database
        # ==========================================

        database = (
            connection.get_database()
        )

        assert database is not None

        assert (
            database.name
            == MONGO_DATABASE
        )

        # ==========================================
        # MongoDB Ping
        # ==========================================

        result = (
            connection.client
            .admin
            .command("ping")
        )

        assert result is not None

        assert result.get(
            "ok"
        ) == 1.0

        # ==========================================
        # Collection
        # ==========================================

        collection = (
            connection.get_collection(
                MONGO_RAW_HTML_COLLECTION
            )
        )

        assert collection is not None

        assert (
            collection.name
            == MONGO_RAW_HTML_COLLECTION
        )

    finally:

        # ==========================================
        # Close Connection
        # ==========================================

        if connection is not None:

            connection.close()
