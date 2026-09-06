"""
autosearch_mcp/tools/article.py

AutoSearch V6.5

MCP-3.3

Article Retrieval Tool

功能：

    提供 MCP Article Retrieval Tool。

支援：

    1. Get Article by Document ID
    2. Get Article by URL

Flow：

    MCP Client / AI Agent
            ↓
        MCP Article Tool
            ↓
        MCP SearchService
            ↓
    MCP ArticleRepository
            ↓
          articles

本 Tool 原則：

    1. 不直接操作 SQL。
    2. 不直接操作 Database。
    3. 不直接操作 Repository。
    4. 使用 MCP SearchService。
    5. Document ID 與 URL 為 MCP-facing identifiers。
    6. article_id 僅作為內部 Database identifier。
"""


from autosearch_mcp.services.search_service import (
    SearchService
)


class ArticleTool:
    """
    AutoSearch MCP Article Retrieval Tool。

    負責：

        Get by Document ID
        Get by URL

    不負責：

        Database
        SQL
        Search
        Search Index
        Search Ranking
        AI Analysis
    """

    def __init__(
        self,
        search_service=None
    ):
        self.search_service = (
            search_service
            if search_service is not None
            else SearchService()
        )

    # ==================================================
    # Get By Document ID
    # ==================================================

    def get_by_document_id(
        self,
        document_id
    ):
        """
        依 Document ID 取得 Article。

        Document ID 是 MCP Article Retrieval
        的主要識別方式之一。
        """

        if document_id is None:
            return None

        document_id = str(
            document_id
        ).strip()

        if not document_id:
            return None

        return self.search_service.find_by_document_id(
            document_id
        )

    # ==================================================
    # Get By URL
    # ==================================================

    def get_by_url(
        self,
        url
    ):
        """
        依 Article URL 取得 Article。

        URL 是 MCP Article Retrieval
        的主要識別方式之一。
        """

        if url is None:
            return None

        url = str(
            url
        ).strip()

        if not url:
            return None

        return self.search_service.find_by_url(
            url
        )

    # ==================================================
    # Close
    # ==================================================

    def close(self):
        """
        關閉 SearchService。
        """

        if self.search_service is not None:
            self.search_service.close()


__all__ = [
    "ArticleTool"
]