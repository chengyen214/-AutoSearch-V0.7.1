"""
rag/embedding/model.py

AutoSearch V7

RAG-3.2

Embedding Model

功能：

    載入 RAG-3 Embedding Model。

目前模型：

    Provider:
        sentence-transformers

    Model:
        taide/embeddinggemma-GTAIDE-300m-2605

    Dimension:
        768

資料流程：

    RAG-3.1 Embedding Configuration
            ↓
    EmbeddingModel
            ↓
    SentenceTransformer
            ↓
    taide/embeddinggemma-GTAIDE-300m-2605

本階段負責：

    1. 讀取 Embedding Configuration
    2. 建立 SentenceTransformer Model
    3. 提供已載入的 Embedding Model
    4. 驗證 Model Dimension

本階段不負責：

    1. Chunking
    2. Chunk → Embedding
    3. ChromaDB
    4. Retriever
    5. Context Builder
    6. LLM
"""


from sentence_transformers import SentenceTransformer

from rag.embedding.config import (
    EMBEDDING_PROVIDER,
    EMBEDDING_MODEL,
    EMBEDDING_DIMENSION,
)


class EmbeddingModel:
    """
    RAG-3.2 Embedding Model。

    負責載入並管理
    Sentence Transformers Embedding Model。
    """

    # ==================================================
    # Initialize
    # ==================================================

    def __init__(
        self,
        model_name=EMBEDDING_MODEL
    ):
        """
        初始化 Embedding Model。

        Parameters:
            model_name:
                Sentence Transformers Model 名稱。
        """

        if EMBEDDING_PROVIDER != (
            "sentence-transformers"
        ):
            raise ValueError(
                "Unsupported embedding provider: "
                f"{EMBEDDING_PROVIDER}"
            )

        if model_name is None:
            raise ValueError(
                "Embedding model name cannot be None."
            )

        model_name = str(
            model_name
        ).strip()

        if not model_name:
            raise ValueError(
                "Embedding model name cannot be empty."
            )

        self.model_name = model_name

        self.dimension = EMBEDDING_DIMENSION

        # ----------------------------------------------
        # Load Model
        # ----------------------------------------------

        self.model = SentenceTransformer(
            self.model_name
        )

    # ==================================================
    # Dimension
    # ==================================================

    def get_dimension(self):
        """
        取得 Embedding Dimension。
        """

        return self.dimension

    # ==================================================
    # Underlying Model
    # ==================================================

    def get_model(self):
        """
        取得已載入的 SentenceTransformer Model。
        """

        return self.model


__all__ = [
    "EmbeddingModel"
]