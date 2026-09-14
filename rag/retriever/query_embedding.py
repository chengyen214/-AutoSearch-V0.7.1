"""
rag/retriever/query_embedding.py

AutoSearch V7

RAG-5.2

Query Embedding

功能：

    將使用者 Query
    轉換成 Query Embedding Vector。

流程：

    User Query
        ↓
    Query Embedding
        ↓
    RAG-3 Embedder
        ↓
    Qwen/Qwen3-Embedding-0.6B
        ↓
    1024 維 Vector

本階段不負責：

    1. ChromaDB Search
    2. Top-K Retrieval
    3. Similarity Threshold
    4. Result Ranking
    5. Context Builder
    6. LLM


重要原則：

    RAG-5.2 重用 RAG-3
    已經建立的 Embedding Model。

    不重新實作：

        EmbeddingModel
        Model Loading
        Encoding Logic
"""


# ============================================================
# Imports
# ============================================================

from rag.embedding.embedder import (
    Embedder
)

from rag.retriever.config import (
    EMBEDDING_DIMENSION
)


# ============================================================
# Query Embedding
# ============================================================

class QueryEmbedding:
    """
    AutoSearch V7 RAG-5.2 Query Embedding。

    負責：

        Query
          ↓
        Embedding Vector

    使用既有 RAG-3 Embedder。
    """

    # ========================================================
    # Initialize
    # ========================================================

    def __init__(
        self,
        embedder=None
    ):
        """
        初始化 Query Embedding。

        Parameters:
            embedder:
                RAG-3 Embedder。

        支援 Dependency Injection。
        """

        self.embedder = (
            embedder
            if embedder is not None
            else Embedder()
        )

        self.dimension = (
            self.embedder
            .get_dimension()
        )

        if (
            self.dimension
            != EMBEDDING_DIMENSION
        ):
            raise ValueError(
                "Embedding dimension mismatch: "
                f"expected {EMBEDDING_DIMENSION}, "
                f"got {self.dimension}"
            )

    # ========================================================
    # Validate Query
    # ========================================================

    @staticmethod
    def _validate_query(
        query
    ):
        """
        驗證 Query。
        """

        if query is None:
            raise ValueError(
                "Query cannot be None."
            )

        if not isinstance(
            query,
            str
        ):
            raise TypeError(
                "Query must be a str."
            )

        query = query.strip()

        if not query:
            raise ValueError(
                "Query cannot be empty."
            )

        return query

    # ========================================================
    # Embed Query
    # ========================================================

    def embed(
        self,
        query
    ):
        """
        將 Query 轉換成 Embedding Vector。

        Parameters:
            query:
                使用者 Query。

        Returns:
            list[float]
        """

        query = (
            self._validate_query(
                query
            )
        )

        embedding = (
            self.embedder
            .embed_text(
                query
            )
        )

        if embedding is None:
            raise ValueError(
                "Query embedding "
                "returned None."
            )

        if not isinstance(
            embedding,
            list
        ):
            raise TypeError(
                "Query embedding "
                "must be a list."
            )

        if len(
            embedding
        ) != self.dimension:
            raise ValueError(
                "Query embedding dimension "
                "mismatch: "
                f"expected {self.dimension}, "
                f"got {len(embedding)}"
            )

        return embedding

    # ========================================================
    # Dimension
    # ========================================================

    def get_dimension(
        self
    ):
        """
        取得 Query Embedding Dimension。
        """

        return self.dimension


# ============================================================
# Export
# ============================================================

__all__ = [
    "QueryEmbedding"
]