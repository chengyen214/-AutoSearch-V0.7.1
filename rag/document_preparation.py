"""
rag/document_preparation.py

AutoSearch V7

RAG-1

Document Preparation

功能：

    主控 RAG-1 Document Preparation 完整流程。

資料流程：

    MCP
      ↓
    ArticleSource
      ↓
    Article
      ↓
    ArticleDocument
      ↓
    LangChain Document
      ↓
    ContentCleaner
      ↓
    Prepared LangChain Document

RAG-1 Components：

    RAG-1.1 Article Source
        ArticleSource

    RAG-1.2 Document Model
        ArticleDocument

    RAG-1.3 Metadata
        ArticleDocument metadata

    RAG-1.4 Content Cleaning
        ContentCleaner

本模組負責：

    1. 控制 RAG-1 Document Preparation 流程
    2. 透過 ArticleSource 取得 Article
    3. 將 Article 轉換成 LangChain Document
    4. 清理 Document.page_content
    5. 保留既有 Document metadata
    6. 回傳準備完成的 LangChain Document

本模組不負責：

    1. MCP Server
    2. Database
    3. SQL
    4. Parser
    5. Chunking
    6. Embedding
    7. ChromaDB
    8. Retriever
    9. Context Builder
    10. LLM
"""


from langchain_core.documents import Document

from rag.article_source import (
    ArticleSource
)

from rag.document_model import (
    ArticleDocument
)

from rag.content_cleaner import (
    ContentCleaner
)


class DocumentPreparation:
    """
    RAG-1 Document Preparation Orchestrator。

    負責將：

        Article Source
            ↓
        Document Model
            ↓
        Content Cleaning

    串成完整流程。
    """

    # ==================================================
    # Initialize
    # ==================================================

    def __init__(
        self,
        article_source=None
    ):
        """
        初始化 DocumentPreparation。

        Parameters:
            article_source:
                可注入的 ArticleSource。

                若未提供，
                自動建立 ArticleSource。
        """

        self.article_source = (
            article_source
            if article_source is not None
            else ArticleSource()
        )

    # ==================================================
    # Prepare Article
    # ==================================================

    def _prepare_article(
        self,
        article
    ):
        """
        將 Article
        準備成最終 LangChain Document。

        流程：

            Article
              ↓
            ArticleDocument
              ↓
            ContentCleaner
              ↓
            Document
        """

        if article is None:
            raise ValueError(
                "Article cannot be None."
            )

        if not isinstance(
            article,
            dict
        ):
            raise TypeError(
                "Article must be a dict."
            )

        # ----------------------------------------------
        # RAG-1.2 / RAG-1.3
        # Article → Document + Metadata
        # ----------------------------------------------

        document = ArticleDocument.from_article(
            article
        )

        # ----------------------------------------------
        # RAG-1.4
        # Clean page_content
        # ----------------------------------------------

        cleaned_content = ContentCleaner.clean(
            document.page_content
        )

        # ----------------------------------------------
        # Build Prepared Document
        # ----------------------------------------------

        return Document(
            page_content=cleaned_content,
            metadata=document.metadata
        )

    # ==================================================
    # Prepare By Document ID
    # ==================================================

    def prepare_by_document_id(
        self,
        document_id
    ):
        """
        依 Document ID
        執行完整 RAG-1 Document Preparation。

        流程：

            Document ID
                ↓
            MCP ArticleSource
                ↓
            Article
                ↓
            Document
                ↓
            Content Cleaning
                ↓
            Prepared Document

        Returns:
            langchain_core.documents.Document
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

        article = (
            self.article_source.get_by_document_id(
                document_id
            )
        )

        if article is None:
            raise ValueError(
                "Article not found for "
                f"document_id: {document_id}"
            )

        return self._prepare_article(
            article
        )

    # ==================================================
    # Prepare By URL
    # ==================================================

    def prepare_by_url(
        self,
        url
    ):
        """
        依 URL
        執行完整 RAG-1 Document Preparation。

        Returns:
            langchain_core.documents.Document
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

        article = (
            self.article_source.get_by_url(
                url
            )
        )

        if article is None:
            raise ValueError(
                "Article not found for "
                f"url: {url}"
            )

        return self._prepare_article(
            article
        )


__all__ = [
    "DocumentPreparation"
]