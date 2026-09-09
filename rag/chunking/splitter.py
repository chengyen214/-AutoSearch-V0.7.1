"""
rag/chunking/splitter.py

AutoSearch V7

RAG-2.2

Document Splitter

功能：

    將 RAG-1.5 Prepared LangChain Document
    使用 RecursiveCharacterTextSplitter
    切割成多個 LangChain Document chunks。

資料流程：

    RAG-1.5
    Prepared LangChain Document
            ↓
    RecursiveCharacterTextSplitter
            ↓
    List[LangChain Document]

目前設定：

    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200

本階段負責：

    1. 建立 RecursiveCharacterTextSplitter
    2. Split LangChain Document
    3. 回傳 Chunk Documents

本階段不負責：

    1. MCP
    2. Database
    3. SQL
    4. Article Retrieval
    5. Content Cleaning
    6. Embedding
    7. ChromaDB
    8. Retriever
    9. Context Builder
    10. LLM
"""


from langchain_text_splitters import (
    RecursiveCharacterTextSplitter
)

from rag.chunking.config import (
    CHUNK_SIZE,
    CHUNK_OVERLAP,
)


class DocumentSplitter:
    """
    RAG-2.2 Document Splitter。

    使用：

        RecursiveCharacterTextSplitter

    將單一 LangChain Document
    切割成多個 Document chunks。
    """

    # ==================================================
    # Initialize
    # ==================================================

    def __init__(
        self,
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    ):
        """
        初始化 Document Splitter。

        Parameters:
            chunk_size:
                每個 Chunk 的目標字元數。

            chunk_overlap:
                Chunk 之間的重疊字元數。
        """

        if chunk_size <= 0:
            raise ValueError(
                "chunk_size must be greater than 0."
            )

        if chunk_overlap < 0:
            raise ValueError(
                "chunk_overlap cannot be negative."
            )

        if chunk_overlap >= chunk_size:
            raise ValueError(
                "chunk_overlap must be smaller than chunk_size."
            )

        self.chunk_size = chunk_size

        self.chunk_overlap = chunk_overlap

        self.splitter = (
            RecursiveCharacterTextSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
            )
        )

    # ==================================================
    # Split One Document
    # ==================================================

    def split_document(
        self,
        document
    ):
        """
        將單一 LangChain Document
        切割成多個 chunks。

        Parameters:
            document:
                LangChain Document。

        Returns:
            list[Document]
        """

        if document is None:
            raise ValueError(
                "Document cannot be None."
            )

        chunks = self.splitter.split_documents(
            [document]
        )

        if not chunks:
            raise ValueError(
                "Document splitting returned no chunks."
            )

        return chunks

    # ==================================================
    # Split Documents
    # ==================================================

    def split_documents(
        self,
        documents
    ):
        """
        將多個 LangChain Documents
        切割成多個 chunks。

        Parameters:
            documents:
                LangChain Document list。

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

        chunks = self.splitter.split_documents(
            documents
        )

        if not chunks:
            raise ValueError(
                "Document splitting returned no chunks."
            )

        return chunks


__all__ = [
    "DocumentSplitter"
]