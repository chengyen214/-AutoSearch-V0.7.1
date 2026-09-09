"""
rag/chunking/document_chunking.py

AutoSearch V7

RAG-2

Document Chunking

功能：

    主控 RAG-2 Chunking 完整流程。

資料流程：

    RAG-1.5
    Prepared LangChain Document
            ↓
    DocumentChunking
            ↓
    DocumentSplitter
            ↓
    Chunk Documents

RAG-2 Components：

    RAG-2.1 Chunking Configuration
        rag.chunking.config

    RAG-2.2 Document Splitter
        rag.chunking.splitter

    RAG-2.3 Metadata Preservation
        由 DocumentSplitter.split_documents()
        保留原始 Document metadata

    RAG-2.4 Chunk Validation
        由本主控流程進行基本驗證

本模組負責：

    1. 控制 RAG-2 Chunking 流程
    2. 接收 Prepared LangChain Document
    3. 呼叫 DocumentSplitter
    4. 驗證 Chunk 基本結構
    5. 回傳完成的 Chunk Documents

本模組不負責：

    1. MCP
    2. Database
    3. SQL
    4. Parser
    5. Content Cleaning
    6. Embedding
    7. Qwen Embedding
    8. ChromaDB
    9. Retriever
    10. Context Builder
    11. LLM
"""


from langchain_core.documents import Document

from rag.chunking.splitter import (
    DocumentSplitter
)

from rag.chunking.config import (
    CHUNK_SIZE,
)


class DocumentChunking:
    """
    RAG-2 Document Chunking Orchestrator。

    負責將：

        Prepared Document
            ↓
        DocumentSplitter
            ↓
        Chunks

    並進行基本 Chunk Validation。
    """

    # ==================================================
    # Initialize
    # ==================================================

    def __init__(
        self,
        document_splitter=None
    ):
        """
        初始化 DocumentChunking。

        Parameters:
            document_splitter:
                可注入的 DocumentSplitter。

                若未提供，
                自動建立 DocumentSplitter。
        """

        self.document_splitter = (
            document_splitter
            if document_splitter is not None
            else DocumentSplitter()
        )

    # ==================================================
    # Validate Source Document
    # ==================================================

    @staticmethod
    def _validate_source_document(
        document
    ):
        """
        驗證輸入 Prepared Document。
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

        if not isinstance(
            document.metadata,
            dict
        ):
            raise TypeError(
                "Document.metadata must be a dict."
            )

    # ==================================================
    # Validate Chunks
    # ==================================================

    @staticmethod
    def _validate_chunks(
        chunks
    ):
        """
        驗證 Chunk 結果。

        基本要求：

            1. chunks 必須是 list
            2. 至少有一個 Chunk
            3. 每個 Chunk 必須是 Document
            4. page_content 必須是 str
            5. page_content 不可為空
            6. Chunk 長度不可超過 CHUNK_SIZE
            7. metadata 必須是 dict
        """

        if not isinstance(
            chunks,
            list
        ):
            raise TypeError(
                "Chunks must be a list."
            )

        if not chunks:
            raise ValueError(
                "Chunking returned no chunks."
            )

        for index, chunk in enumerate(
            chunks
        ):

            if not isinstance(
                chunk,
                Document
            ):
                raise TypeError(
                    f"Chunk {index} must be "
                    "a LangChain Document."
                )

            if not isinstance(
                chunk.page_content,
                str
            ):
                raise TypeError(
                    f"Chunk {index} page_content "
                    "must be a str."
                )

            if not chunk.page_content.strip():
                raise ValueError(
                    f"Chunk {index} page_content "
                    "cannot be empty."
                )

            if len(
                chunk.page_content
            ) > CHUNK_SIZE:
                raise ValueError(
                    f"Chunk {index} exceeds "
                    f"CHUNK_SIZE={CHUNK_SIZE}: "
                    f"{len(chunk.page_content)}"
                )

            if not isinstance(
                chunk.metadata,
                dict
            ):
                raise TypeError(
                    f"Chunk {index} metadata "
                    "must be a dict."
                )

    # ==================================================
    # Chunk One Document
    # ==================================================

    def chunk(
        self,
        document
    ):
        """
        將單一 Prepared Document
        切割成 Chunks。

        流程：

            Prepared Document
                ↓
            DocumentSplitter
                ↓
            Chunks
                ↓
            Validation

        Returns:
            list[Document]
        """

        self._validate_source_document(
            document
        )

        chunks = self.document_splitter.split_document(
            document
        )

        self._validate_chunks(
            chunks
        )

        return chunks

    # ==================================================
    # Chunk Multiple Documents
    # ==================================================

    def chunk_documents(
        self,
        documents
    ):
        """
        將多個 Prepared Documents
        切割成 Chunks。

        Returns:
            list[Document]
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
                self._validate_source_document(
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

        chunks = self.document_splitter.split_documents(
            documents
        )

        self._validate_chunks(
            chunks
        )

        return chunks


__all__ = [
    "DocumentChunking"
]