"""
rag/chroma/client.py

AutoSearch V7

RAG-4.2

ChromaDB Client

功能：

    建立 Persistent ChromaDB Client。

資料流程：

    RAG-4.1 ChromaDB Configuration
            ↓
    CHROMA_PERSIST_DIRECTORY
            ↓
    ChromaDB PersistentClient
            ↓
    Persistent ChromaDB

本檔案負責：

    1. 建立 Persistent ChromaDB Client
    2. 提供 Client 取得方法

本檔案不負責：

    1. Collection
    2. Document Index
    3. Embedding
    4. MySQL
    5. Full Indexing
    6. Incremental Indexing
    7. Retriever
"""


import chromadb

from rag.chroma.config import (
    CHROMA_PERSIST_DIRECTORY
)


class ChromaDBClient:
    """
    RAG-4.2 ChromaDB Client。

    使用：

        chromadb.PersistentClient

    建立持久化 ChromaDB Client。

    Persist Directory
        ↓
    PersistentClient
    """

    # ==================================================
    # Initialize
    # ==================================================

    def __init__(
        self,
        persist_directory=None
    ):
        """
        初始化 ChromaDB Client。

        Parameters:
            persist_directory:
                ChromaDB 持久化目錄。

                若未提供，
                使用 RAG-4.1 Configuration。
        """

        self.persist_directory = (
            persist_directory
            if persist_directory is not None
            else CHROMA_PERSIST_DIRECTORY
        )

        self.persist_directory = (
            str(
                self.persist_directory
            ).strip()
        )

        if not self.persist_directory:
            raise ValueError(
                "Persist directory cannot be empty."
            )

        self.client = (
            chromadb.PersistentClient(
                path=self.persist_directory
            )
        )

    # ==================================================
    # Get Client
    # ==================================================

    def get_client(self):
        """
        取得 Persistent ChromaDB Client。

        Returns:
            chromadb.PersistentClient
        """

        return self.client

    # ==================================================
    # Get Persist Directory
    # ==================================================

    def get_persist_directory(self):
        """
        取得目前 ChromaDB Persist Directory。
        """

        return self.persist_directory


__all__ = [
    "ChromaDBClient"
]