"""
rag/embedding/embedder.py

AutoSearch V7

RAG-3.3
RAG-3.4
RAG-3.5

Chunk → Embedding
Embedding Mapping
Embedding Validation

功能：

    將 RAG-2 Chunk Documents
    轉換成 Embedding Vectors。

    同時提供：

        Chunk ↔ Embedding Mapping

    以及：

        Embedding Validation

資料流程：

    RAG-2 Chunking
          ↓
    List[LangChain Document]
          ↓
    Embedder
          ↓
    EmbeddingModel
          ↓
    taide/embeddinggemma-GTAIDE-300m-2605
          ↓
    768 維 Embedding Vectors
          ↓
    Embedding Mapping
          ↓
    Chunk + Embedding
          ↓
    Embedding Validation

RAG-3.3 負責：

    1. 接收 LangChain Document
    2. 取得 Document.page_content
    3. 使用既有 EmbeddingModel
    4. 產生 Embedding Vector
    5. 支援單一 Document
    6. 支援多個 Documents

RAG-3.4 負責：

    1. 建立 Chunk ↔ Embedding 對應
    2. 保留原始 Document
    3. 保留原始 Document Metadata
    4. 確保 Chunk 與 Embedding 一一對應

RAG-3.5 負責：

    1. 驗證單一 Embedding
    2. 驗證多個 Embeddings
    3. 驗證 Embedding 維度
    4. 驗證 Embedding 數值型別
    5. 驗證 Embedding 數值為有限值
    6. 驗證 Embedding 不為全零向量

本階段不負責：

    1. MCP
    2. Database
    3. SQL
    4. Document Preparation
    5. Chunking
    6. Embedding Model Loading
    7. ChromaDB
    8. Retriever
    9. Context Builder
    10. LLM
"""


import math


from langchain_core.documents import Document

from rag.embedding.model import (
    EmbeddingModel
)


class Embedder:
    """
    RAG-3.3 / RAG-3.4 / RAG-3.5 Embedder。

    RAG-3.3：

        Chunk Document
            ↓
        Embedding Vector

    RAG-3.4：

        Chunk Document
            ↕
        Embedding Vector

        建立一一對應 Mapping。

    RAG-3.5：

        Embedding Vector
            ↓
        Validation

    使用既有：

        RAG-3.2 EmbeddingModel

    不重新載入其他 Provider。
    """

    # ==================================================
    # Initialize
    # ==================================================

    def __init__(
        self,
        embedding_model=None
    ):
        """
        初始化 Embedder。

        Parameters:
            embedding_model:
                可注入的 EmbeddingModel。

                若未提供，
                自動建立 EmbeddingModel。
        """

        self.embedding_model = (
            embedding_model
            if embedding_model is not None
            else EmbeddingModel()
        )

        self.model = (
            self.embedding_model.get_model()
        )

        self.dimension = (
            self.embedding_model.get_dimension()
        )

    # ==================================================
    # Validate Text
    # ==================================================

    @staticmethod
    def _validate_text(
        text
    ):
        """
        驗證文字輸入。
        """

        if text is None:
            raise ValueError(
                "Text cannot be None."
            )

        if not isinstance(
            text,
            str
        ):
            raise TypeError(
                "Text must be a str."
            )

        text = text.strip()

        if not text:
            raise ValueError(
                "Text cannot be empty."
            )

        return text

    # ==================================================
    # Validate Document
    # ==================================================

    @staticmethod
    def _validate_document(
        document
    ):
        """
        驗證 LangChain Document。
        """

        if document is None:
            raise ValueError(
                "Document cannot be None."
            )

        if not isinstance(
            document,
            Document
        ):
            raise TypeError(
                "Document must be a LangChain Document."
            )

        if not isinstance(
            document.page_content,
            str
        ):
            raise TypeError(
                "Document.page_content must be a str."
            )

        if not document.page_content.strip():
            raise ValueError(
                "Document.page_content cannot be empty."
            )

    # ==================================================
    # Validate Documents
    # ==================================================

    @classmethod
    def _validate_documents(
        cls,
        documents
    ):
        """
        驗證 LangChain Document list。
        """

        if documents is None:
            raise ValueError(
                "Documents cannot be None."
            )

        if not isinstance(
            documents,
            list
        ):
            raise TypeError(
                "Documents must be a list."
            )

        if not documents:
            raise ValueError(
                "Documents cannot be empty."
            )

        for index, document in enumerate(
            documents
        ):

            try:

                cls._validate_document(
                    document
                )

            except (
                TypeError,
                ValueError
            ) as error:

                raise type(error)(
                    f"Document {index} validation failed: "
                    f"{error}"
                ) from error

    # ==================================================
    # RAG-3.5
    # Validate Embedding
    # ==================================================

    def validate_embedding(
        self,
        embedding
    ):
        """
        驗證單一 Embedding。

        驗證內容：

            1. 必須為 list
            2. 不可為空
            3. 維度必須符合設定
            4. 每個值必須為 numeric
            5. 每個值必須為 finite
            6. 不可為全零向量

        Parameters:
            embedding:
                list[float]

        Returns:
            True
        """

        # ----------------------------------------------
        # Type
        # ----------------------------------------------

        if not isinstance(
            embedding,
            list
        ):
            raise TypeError(
                "Embedding must be a list."
            )

        # ----------------------------------------------
        # Empty
        # ----------------------------------------------

        if not embedding:
            raise ValueError(
                "Embedding cannot be empty."
            )

        # ----------------------------------------------
        # Dimension
        # ----------------------------------------------

        if len(embedding) != self.dimension:
            raise ValueError(
                "Embedding dimension mismatch: "
                f"expected {self.dimension}, "
                f"got {len(embedding)}."
            )

        # ----------------------------------------------
        # Numeric + Finite
        # ----------------------------------------------

        for index, value in enumerate(
            embedding
        ):

            if not isinstance(
                value,
                (int, float)
            ):
                raise TypeError(
                    "Embedding value at index "
                    f"{index} must be numeric."
                )

            if not math.isfinite(
                value
            ):
                raise ValueError(
                    "Embedding value at index "
                    f"{index} must be finite."
                )

        # ----------------------------------------------
        # Not All Zero
        # ----------------------------------------------

        if all(
            value == 0
            for value in embedding
        ):
            raise ValueError(
                "Embedding cannot be an all-zero vector."
            )

        return True

    # ==================================================
    # RAG-3.5
    # Validate Embeddings
    # ==================================================

    def validate_embeddings(
        self,
        embeddings
    ):
        """
        驗證多個 Embeddings。

        驗證內容：

            1. 必須為 list
            2. 不可為空
            3. 每個 Embedding
               都必須通過 validate_embedding()

        Parameters:
            embeddings:
                list[list[float]]

        Returns:
            True
        """

        # ----------------------------------------------
        # Type
        # ----------------------------------------------

        if not isinstance(
            embeddings,
            list
        ):
            raise TypeError(
                "Embeddings must be a list."
            )

        # ----------------------------------------------
        # Empty
        # ----------------------------------------------

        if not embeddings:
            raise ValueError(
                "Embeddings cannot be empty."
            )

        # ----------------------------------------------
        # Validate Every Embedding
        # ----------------------------------------------

        for index, embedding in enumerate(
            embeddings
        ):

            try:

                self.validate_embedding(
                    embedding
                )

            except (
                TypeError,
                ValueError
            ) as error:

                raise type(error)(
                    f"Embedding {index} validation failed: "
                    f"{error}"
                ) from error

        return True

    # ==================================================
    # Embed Text
    # ==================================================

    def embed_text(
        self,
        text
    ):
        """
        將單一文字轉換成 Embedding Vector。

        Parameters:
            text:
                要進行 Embedding 的文字。

        Returns:
            list[float]
        """

        text = self._validate_text(
            text
        )

        embeddings = self.model.encode(
            [text]
        )

        if embeddings is None:
            raise ValueError(
                "Embedding generation returned None."
            )

        if len(embeddings) != 1:
            raise ValueError(
                "Unexpected embedding result size."
            )

        vector = embeddings[0]

        if len(vector) != self.dimension:
            raise ValueError(
                "Embedding dimension mismatch: "
                f"expected {self.dimension}, "
                f"got {len(vector)}"
            )

        result = vector.tolist()

        # --------------------------------------------------
        # RAG-3.5 Validation
        # --------------------------------------------------

        self.validate_embedding(
            result
        )

        return result

    # ==================================================
    # Embed Document
    # ==================================================

    def embed_document(
        self,
        document
    ):
        """
        將單一 LangChain Document
        轉換成 Embedding Vector。

        Parameters:
            document:
                LangChain Document。

        Returns:
            list[float]
        """

        self._validate_document(
            document
        )

        return self.embed_text(
            document.page_content
        )

    # ==================================================
    # Embed Documents
    # ==================================================

    def embed_documents(
        self,
        documents
    ):
        """
        將多個 LangChain Documents
        轉換成 Embedding Vectors。

        Parameters:
            documents:
                LangChain Document list。

        Returns:
            list[list[float]]
        """

        self._validate_documents(
            documents
        )

        texts = [
            document.page_content.strip()
            for document in documents
        ]

        embeddings = self.model.encode(
            texts
        )

        if embeddings is None:
            raise ValueError(
                "Embedding generation returned None."
            )

        if len(embeddings) != len(documents):
            raise ValueError(
                "Embedding count does not match "
                "document count: "
                f"documents={len(documents)}, "
                f"embeddings={len(embeddings)}"
            )

        vectors = []

        for index, embedding in enumerate(
            embeddings
        ):

            if len(embedding) != self.dimension:
                raise ValueError(
                    f"Document {index} embedding "
                    "dimension mismatch: "
                    f"expected {self.dimension}, "
                    f"got {len(embedding)}"
                )

            vector = embedding.tolist()

            vectors.append(
                vector
            )

        # --------------------------------------------------
        # RAG-3.5 Validation
        # --------------------------------------------------

        self.validate_embeddings(
            vectors
        )

        return vectors

    # ==================================================
    # RAG-3.4
    # Embed Document With Mapping
    # ==================================================

    def embed_document_with_mapping(
        self,
        document
    ):
        """
        將單一 Document
        轉換成 Embedding Mapping。

        Mapping：

            Document
                ↕
            Embedding

        Returns:
            dict

        結構：

            {
                "document": Document,
                "embedding": list[float],
            }
        """

        self._validate_document(
            document
        )

        embedding = self.embed_document(
            document
        )

        return {
            "document": document,
            "embedding": embedding,
        }

    # ==================================================
    # RAG-3.4
    # Embed Documents With Mapping
    # ==================================================

    def embed_documents_with_mapping(
        self,
        documents
    ):
        """
        將多個 Documents
        建立 Chunk ↔ Embedding Mapping。

        Parameters:
            documents:
                LangChain Document list。

        Returns:
            list[dict]

        結構：

            [
                {
                    "document": Document,
                    "embedding": list[float],
                },
                ...
            ]
        """

        self._validate_documents(
            documents
        )

        embeddings = self.embed_documents(
            documents
        )

        if len(embeddings) != len(documents):
            raise ValueError(
                "Embedding count does not match "
                "document count."
            )

        mappings = []

        for document, embedding in zip(
            documents,
            embeddings
        ):

            mappings.append(
                {
                    "document": document,
                    "embedding": embedding,
                }
            )

        return mappings

    # ==================================================
    # RAG-3.4
    # Validate Mapping
    # ==================================================

    def validate_mapping(
        self,
        mapping
    ):
        """
        驗證單一 Embedding Mapping。

        必須包含：

            document
            embedding
        """

        if mapping is None:
            raise ValueError(
                "Mapping cannot be None."
            )

        if not isinstance(
            mapping,
            dict
        ):
            raise TypeError(
                "Mapping must be a dict."
            )

        if "document" not in mapping:
            raise ValueError(
                "Mapping is missing 'document'."
            )

        if "embedding" not in mapping:
            raise ValueError(
                "Mapping is missing 'embedding'."
            )

        document = mapping[
            "document"
        ]

        embedding = mapping[
            "embedding"
        ]

        self._validate_document(
            document
        )

        # --------------------------------------------------
        # RAG-3.5
        # Validate Embedding
        # --------------------------------------------------

        self.validate_embedding(
            embedding
        )

        return True

    # ==================================================
    # RAG-3.4
    # Validate Mappings
    # ==================================================

    def validate_mappings(
        self,
        mappings
    ):
        """
        驗證多個 Embedding Mappings。

        Returns:
            True
        """

        if mappings is None:
            raise ValueError(
                "Mappings cannot be None."
            )

        if not isinstance(
            mappings,
            list
        ):
            raise TypeError(
                "Mappings must be a list."
            )

        if not mappings:
            raise ValueError(
                "Mappings cannot be empty."
            )

        for index, mapping in enumerate(
            mappings
        ):

            try:

                self.validate_mapping(
                    mapping
                )

            except (
                TypeError,
                ValueError
            ) as error:

                raise type(error)(
                    f"Mapping {index} validation failed: "
                    f"{error}"
                ) from error

        return True

    # ==================================================
    # Embedding Dimension
    # ==================================================

    def get_dimension(self):
        """
        取得 Embedding Dimension。
        """

        return self.dimension


__all__ = [
    "Embedder"
]