"""
rag/chroma/collection.py

AutoSearch V7

RAG-4.3

ChromaDB Collection

功能：

    建立 / 取得 ChromaDB Collection。

資料流程：

    RAG-4.2 ChromaDB Client
            ↓
    ChromaDB Collection
            ↓
    autosearch_knowledge

本檔案負責：

    1. Create Collection
    2. Get Existing Collection
    3. Get or Create Collection
    4. 設定 Distance Metric

本檔案不負責：

    1. Document Index
    2. Embedding
    3. Metadata Mapping
    4. MySQL
    5. Full Indexing
    6. Incremental Indexing
    7. Retriever
"""


from rag.chroma.client import (
    ChromaDBClient
)

from rag.chroma.config import (
    CHROMA_COLLECTION_NAME,
    CHROMA_DISTANCE_METRIC,
)


class ChromaCollection:
    """
    RAG-4.3 ChromaDB Collection。

    負責：

        Create / Get Collection

    使用：

        RAG-4.2 ChromaDBClient
    """

    # ==================================================
    # Initialize
    # ==================================================

    def __init__(
        self,
        chroma_client=None,
        collection_name=None,
        distance_metric=None
    ):
        """
        初始化 ChromaDB Collection。

        Parameters:
            chroma_client:
                ChromaDBClient。

                若未提供，
                自動建立 ChromaDBClient。

            collection_name:
                Collection 名稱。

                若未提供，
                使用 RAG-4.1 Configuration。

            distance_metric:
                Distance Metric。

                若未提供，
                使用 RAG-4.1 Configuration。
        """

        # --------------------------------------------------
        # Client
        # --------------------------------------------------

        self.chroma_client = (
            chroma_client
            if chroma_client is not None
            else ChromaDBClient()
        )

        self.client = (
            self.chroma_client.get_client()
        )

        # --------------------------------------------------
        # Collection Name
        # --------------------------------------------------

        self.collection_name = (
            collection_name
            if collection_name is not None
            else CHROMA_COLLECTION_NAME
        )

        self.collection_name = (
            str(
                self.collection_name
            ).strip()
        )

        if not self.collection_name:
            raise ValueError(
                "Collection name cannot be empty."
            )

        # --------------------------------------------------
        # Distance Metric
        # --------------------------------------------------

        self.distance_metric = (
            distance_metric
            if distance_metric is not None
            else CHROMA_DISTANCE_METRIC
        )

        self.distance_metric = (
            str(
                self.distance_metric
            ).strip().lower()
        )

        if not self.distance_metric:
            raise ValueError(
                "Distance metric cannot be empty."
            )

        # --------------------------------------------------
        # Collection
        # --------------------------------------------------

        self.collection = (
            self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={
                    "hnsw:space": self.distance_metric
                }
            )
        )

    # ==================================================
    # Get Collection
    # ==================================================

    def get_collection(self):
        """
        取得目前 Collection。

        Returns:
            ChromaDB Collection
        """

        return self.collection

    # ==================================================
    # Get Collection Name
    # ==================================================

    def get_collection_name(self):
        """
        取得 Collection 名稱。
        """

        return self.collection_name

    # ==================================================
    # Get Distance Metric
    # ==================================================

    def get_distance_metric(self):
        """
        取得 Distance Metric。
        """

        return self.distance_metric

    # ==================================================
    # Get Client
    # ==================================================

    def get_client(self):
        """
        取得 ChromaDB Client。
        """

        return self.client


__all__ = [
    "ChromaCollection"
]