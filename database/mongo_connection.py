"""
database/mongo_connection.py

AutoSearch V4

MongoDB Connection

用途：

    建立 MongoDB Connection
    提供 Database Instance
    管理 MongoDB Client Lifecycle

Architecture：

    .env
        |
        v
    config/mongo_config.py
        |
        v
    MongoConnection
        |
        v
    MongoDB
        |
        v
    autosearch Database

目前：

    MongoDB Community Server
    localhost:27017

注意：

    本模組只負責 Connection。
    不負責：

        Raw HTML Storage
        Article Repository
        MongoDB Collection CRUD
"""

from pymongo import MongoClient

from config.mongo_config import (
    MONGO_URI,
    MONGO_DATABASE
)

from utils.logger import logger


class MongoConnection:
    """
    MongoDB Connection Manager
    """

    # ==================================================
    # Initialize
    # ==================================================

    def __init__(self):

        self.client = None

        self.database = None

        self.connect()

    # ==================================================
    # Connect
    # ==================================================

    def connect(self):
        """
        建立 MongoDB Connection。

        MongoDB：

            localhost:27017

        Database：

            autosearch
        """

        try:

            logger.info(
                "Connecting to MongoDB..."
            )

            self.client = MongoClient(
                MONGO_URI,
                serverSelectionTimeoutMS=5000
            )

            # ==========================================
            # Test Connection
            # ==========================================

            self.client.admin.command(
                "ping"
            )

            # ==========================================
            # Database
            # ==========================================

            self.database = self.client[
                MONGO_DATABASE
            ]

            logger.info(
                "MongoDB connection successful."
            )

            logger.info(
                f"MongoDB URI      : {MONGO_URI}"
            )

            logger.info(
                f"MongoDB Database : {MONGO_DATABASE}"
            )

            return True

        except Exception as e:

            logger.exception(
                "MongoDB connection failed: "
                f"{e}"
            )

            self.client = None

            self.database = None

            return False

    # ==================================================
    # Get Database
    # ==================================================

    def get_database(self):
        """
        取得 MongoDB Database Instance。
        """

        if self.database is None:

            raise Exception(
                "MongoDB database is not connected."
            )

        return self.database

    # ==================================================
    # Get Collection
    # ==================================================

    def get_collection(
        self,
        collection_name
    ):
        """
        取得指定 MongoDB Collection。
        """

        if not collection_name:

            raise ValueError(
                "Collection name cannot be empty."
            )

        database = self.get_database()

        return database[
            collection_name
        ]

    # ==================================================
    # Close
    # ==================================================

    def close(self):
        """
        關閉 MongoDB Connection。
        """

        try:

            if self.client is not None:

                self.client.close()

                logger.info(
                    "MongoDB connection closed."
                )

        except Exception as e:

            logger.exception(
                "MongoDB connection close failed: "
                f"{e}"
            )


# ==================================================
# Global Connection Helper
# ==================================================

_mongo_connection = None


def get_mongo_connection():
    """
    取得 MongoConnection Singleton。
    """

    global _mongo_connection

    if _mongo_connection is None:

        _mongo_connection = (
            MongoConnection()
        )

    return _mongo_connection


def get_mongo_database():
    """
    取得 MongoDB Database。
    """

    connection = (
        get_mongo_connection()
    )

    return connection.get_database()


def get_mongo_collection(
    collection_name
):
    """
    取得 MongoDB Collection。
    """

    connection = (
        get_mongo_connection()
    )

    return connection.get_collection(
        collection_name
    )