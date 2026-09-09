"""
rag/embedding/embedding_pipeline.py

AutoSearch V7

RAG-3 Embedding Pipeline

功能：

    將 RAG-2 Chunk Documents
    交由既有 Embedder
    完成：

        Chunk
          ↓
        Embedding
          ↓
        Mapping
          ↓
        Validation

資料流程：

    RAG-2 Chunking
          ↓
    List[LangChain Document]
          ↓
    EmbeddingPipeline
          ↓
    Embedder
          ↓
    EmbeddingModel
          ↓
    Qwen/Qwen3-Embedding-0.6B
          ↓
    1024 維 Embedding
          ↓
    Chunk ↔ Embedding Mapping
          ↓
    Embedding Validation

本檔案負責：

    1. 接收 RAG-2 Chunks
    2. 呼叫既有 Embedder
    3. 建立 Embedding
    4. 建立 Chunk ↔ Embedding Mapping
    5. 執行 Embedding Validation
    6. 回傳 RAG-3 結果

本檔案不負責：

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


from langchain_core.documents import Document

from rag.embedding.embedder import (
    Embedder
)


class EmbeddingPipeline:
    """
    RAG-3 Embedding Pipeline。

    負責將 RAG-2 Chunk Documents
    串接至既有 Embedder。

    流程：

        Chunks
          ↓
        Embedder
          ↓
        Embedding Mapping
          ↓
        Validation
          ↓
        RAG-3 Result
    """

    # ==================================================
    # Initialize
    # ==================================================

    def __init__(
        self,
        embedder=None
    ):
        """
        初始化 EmbeddingPipeline。

        Parameters:
            embedder:
                可注入的 Embedder。

                若未提供，
                自動建立 Embedder。
        """

        self.embedder = (
            embedder
            if embedder is not None
            else Embedder()
        )

    # ==================================================
    # Validate Documents
    # ==================================================

    def _validate_documents(
        self,
        documents
    ):
        """
        驗證 RAG-2 Chunk Documents。
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

            if not isinstance(
                document,
                Document
            ):
                raise TypeError(
                    "Document "
                    f"{index} must be a LangChain Document."
                )

            if not isinstance(
                document.page_content,
                str
            ):
                raise TypeError(
                    "Document "
                    f"{index} page_content must be a str."
                )

            if not document.page_content.strip():
                raise ValueError(
                    "Document "
                    f"{index} page_content cannot be empty."
                )

    # ==================================================
    # Process Documents
    # ==================================================

    def process(
        self,
        documents
    ):
        """
        執行完整 RAG-3 Embedding 流程。

        流程：

            Documents
                ↓
            Embedding
                ↓
            Mapping
                ↓
            Validation

        Parameters:
            documents:
                RAG-2 Chunk Documents。

        Returns:
            dict

        結構：

            {
                "documents": [...],
                "embeddings": [...],
                "mappings": [...],
            }
        """

        self._validate_documents(
            documents
        )

        # --------------------------------------------------
        # RAG-3.3
        # Chunk → Embedding
        # --------------------------------------------------

        embeddings = (
            self.embedder.embed_documents(
                documents
            )
        )

        # --------------------------------------------------
        # RAG-3.4
        # Chunk ↔ Embedding Mapping
        # --------------------------------------------------

        mappings = (
            self.embedder.embed_documents_with_mapping(
                documents
            )
        )

        # --------------------------------------------------
        # RAG-3.5
        # Embedding Validation
        # --------------------------------------------------

        self.embedder.validate_embeddings(
            embeddings
        )

        self.embedder.validate_mappings(
            mappings
        )

        # --------------------------------------------------
        # Final Count Validation
        # --------------------------------------------------

        if (
            len(documents)
            != len(embeddings)
            or len(documents)
            != len(mappings)
        ):
            raise ValueError(
                "Document, embedding, and mapping "
                "counts must match."
            )

        return {
            "documents": documents,
            "embeddings": embeddings,
            "mappings": mappings,
        }

    # ==================================================
    # Process Single Document
    # ==================================================

    def process_document(
        self,
        document
    ):
        """
        執行單一 Document 的
        RAG-3 Embedding 流程。

        Parameters:
            document:
                LangChain Document。

        Returns:
            dict
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

        result = self.process(
            [document]
        )

        return {
            "document": result[
                "documents"
            ][0],

            "embedding": result[
                "embeddings"
            ][0],

            "mapping": result[
                "mappings"
            ][0],
        }

    # ==================================================
    # Process Chunk Documents
    # ==================================================

    def process_chunks(
        self,
        chunks
    ):
        """
        RAG-2 Chunks
        → RAG-3 Embedding。

        Parameters:
            chunks:
                RAG-2 Chunk Documents。

        Returns:
            dict
        """

        return self.process(
            chunks
        )

    # ==================================================
    # Get Embedder
    # ==================================================

    def get_embedder(self):
        """
        取得目前使用的 Embedder。
        """

        return self.embedder

    # ==================================================
    # Get Dimension
    # ==================================================

    def get_dimension(self):
        """
        取得 Embedding Dimension。
        """

        return self.embedder.get_dimension()


__all__ = [
    "EmbeddingPipeline"
]