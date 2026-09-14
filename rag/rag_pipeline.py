"""
rag/rag_pipeline.py

AutoSearch V7

RAG Pipeline

目前支援：

    RAG-1 Document Preparation
            ↓
    RAG-2 Chunking
            ↓
    RAG-3 Embedding
            ↓
    Embedding Mapping
            ↓
    Embedding Validation
            ↓
    RAG-4 ChromaDB Index

資料流程：

    Document ID / URL
            ↓
    RAG Pipeline
            ↓
    RAG-1 Document Preparation
            ↓
    Prepared LangChain Document
            ↓
    RAG-2 Document Chunking
            ↓
    Chunk Documents
            ↓
    RAG-3 Embedding Pipeline
            ↓
    Embeddings
            ↓
    Chunk ↔ Embedding Mapping
            ↓
    Embedding Validation
            ↓
    RAG-4 ChromaDB Index
            ↓
    ChromaDB

未來擴充：

    RAG-5 Retriever
            ↓
    RAG-6 Context Builder
            ↓
    RAG-7 LLM Generation

本階段不負責：

    1. MCP Server
    2. Database
    3. SQL
    4. Parser
    5. Chunking implementation
    6. Embedding implementation
    7. Embedding Model implementation
    8. ChromaDB Client implementation
    9. ChromaDB Collection implementation
    10. ChromaDB Indexer implementation
    11. Retriever
    12. Context Builder
    13. LLM
"""


from rag.document_preparation import (
    DocumentPreparation
)

from rag.chunking.document_chunking import (
    DocumentChunking
)

from rag.embedding.embedding_pipeline import (
    EmbeddingPipeline
)

from rag.chroma.indexer import (
    ChromaIndexer
)


class RAGPipeline:
    """
    AutoSearch RAG Pipeline。

    目前主控：

        RAG-1
            ↓
        RAG-2
            ↓
        RAG-3
            ↓
        RAG-4

    負責：

        1. Document Preparation
        2. Document Chunking
        3. Embedding Pipeline
        4. 回傳 Prepared Document
        5. 回傳 Chunks
        6. 回傳 Embeddings
        7. 回傳 Embedding Mappings
        8. ChromaDB Index
        9. 回傳 ChromaDB Record IDs

    不負責：

        1. RAG-1 implementation
        2. RAG-2 implementation
        3. RAG-3 implementation
        4. RAG-4 implementation

    上述功能分別交由：

        DocumentPreparation
        DocumentChunking
        EmbeddingPipeline
        ChromaIndexer

    完成。
    """

    # ==================================================
    # Initialize
    # ==================================================

    def __init__(
        self,
        document_preparation=None,
        document_chunking=None,
        embedding_pipeline=None,
        chroma_indexer=None
    ):
        """
        初始化 RAG Pipeline。

        Parameters:
            document_preparation:
                RAG-1 DocumentPreparation。

            document_chunking:
                RAG-2 DocumentChunking。

            embedding_pipeline:
                RAG-3 EmbeddingPipeline。

            chroma_indexer:
                RAG-4 ChromaIndexer。

        支援 Dependency Injection，
        方便測試與未來擴充。
        """

        self.document_preparation = (
            document_preparation
            if document_preparation is not None
            else DocumentPreparation()
        )

        self.document_chunking = (
            document_chunking
            if document_chunking is not None
            else DocumentChunking()
        )

        self.embedding_pipeline = (
            embedding_pipeline
            if embedding_pipeline is not None
            else EmbeddingPipeline()
        )

        self.chroma_indexer = (
            chroma_indexer
            if chroma_indexer is not None
            else ChromaIndexer()
        )

    # ==================================================
    # Process Prepared Document
    # ==================================================

    def process_document(
        self,
        document
    ):
        """
        從既有 Prepared Document
        執行：

            RAG-2 Chunking
                ↓
            RAG-3 Embedding
                ↓
            RAG-4 ChromaDB Index

        這個方法主要提供：

            已經完成 RAG-1
            的情況下，

            直接進入：

                RAG-2
                    ↓
                RAG-3
                    ↓
                RAG-4

        Returns:
            dict

        結構：

            {
                "document": Document,
                "chunks": [...],
                "embeddings": [...],
                "mappings": [...],
                "record_ids": [...],
                "indexed_count": int
            }
        """

        if document is None:
            raise ValueError(
                "Document cannot be None."
            )

        # ----------------------------------------------
        # RAG-2
        # ----------------------------------------------

        chunks = (
            self.document_chunking
            .chunk(
                document
            )
        )

        # ----------------------------------------------
        # RAG-3
        # ----------------------------------------------

        embedding_result = (
            self.embedding_pipeline
            .process_chunks(
                chunks
            )
        )

        embeddings = (
            embedding_result[
                "embeddings"
            ]
        )

        mappings = (
            embedding_result[
                "mappings"
            ]
        )

        # ----------------------------------------------
        # RAG-4
        # ----------------------------------------------

        record_ids = (
            self.chroma_indexer
            .index_mappings(
                mappings
            )
        )

        # ----------------------------------------------
        # Result
        # ----------------------------------------------

        return {
            "document": document,
            "chunks": chunks,
            "embeddings": embeddings,
            "mappings": mappings,
            "record_ids": record_ids,
            "indexed_count": len(
                record_ids
            ),
        }

    # ==================================================
    # Process By Document ID
    # ==================================================

    def process_by_document_id(
        self,
        document_id
    ):
        """
        從 Document ID
        執行完整：

            RAG-1
                ↓
            RAG-2
                ↓
            RAG-3
                ↓
            RAG-4

        流程：

            Document ID
                ↓
            RAG-1 Document Preparation
                ↓
            Prepared Document
                ↓
            RAG-2 Chunking
                ↓
            Chunks
                ↓
            RAG-3 Embedding Pipeline
                ↓
            Embeddings
                ↓
            Mapping
                ↓
            Validation
                ↓
            RAG-4 ChromaDB
                ↓
            Record IDs

        Returns:
            dict
        """

        if document_id is None:
            raise ValueError(
                "Document ID cannot be None."
            )

        document_id = str(
            document_id
        ).strip()

        if not document_id:
            raise ValueError(
                "Document ID cannot be empty."
            )

        # ----------------------------------------------
        # RAG-1
        # ----------------------------------------------

        document = (
            self.document_preparation
            .prepare_by_document_id(
                document_id
            )
        )

        # ----------------------------------------------
        # RAG-2 + RAG-3 + RAG-4
        # ----------------------------------------------

        return self.process_document(
            document
        )

    # ==================================================
    # Process By URL
    # ==================================================

    def process_by_url(
        self,
        url
    ):
        """
        從 URL
        執行完整：

            RAG-1
                ↓
            RAG-2
                ↓
            RAG-3
                ↓
            RAG-4

        流程：

            URL
              ↓
            RAG-1 Document Preparation
              ↓
            Prepared Document
              ↓
            RAG-2 Chunking
              ↓
            RAG-3 Embedding
              ↓
            Mapping
              ↓
            Validation
              ↓
            RAG-4 ChromaDB
              ↓
            Record IDs

        Returns:
            dict
        """

        if url is None:
            raise ValueError(
                "URL cannot be None."
            )

        url = str(
            url
        ).strip()

        if not url:
            raise ValueError(
                "URL cannot be empty."
            )

        # ----------------------------------------------
        # RAG-1
        # ----------------------------------------------

        document = (
            self.document_preparation
            .prepare_by_url(
                url
            )
        )

        # ----------------------------------------------
        # RAG-2 + RAG-3 + RAG-4
        # ----------------------------------------------

        return self.process_document(
            document
        )


__all__ = [
    "RAGPipeline"
]