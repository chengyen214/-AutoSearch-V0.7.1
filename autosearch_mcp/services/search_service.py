"""
autosearch_mcp/services/search_service.py

AutoSearch V6.5

MCP Search Service

用途：

    專門提供 AutoSearch MCP Search
    所需要的 Search Service。

Flow：

    MCP SearchTool
          ↓
    MCP SearchService
          ↓
    MCP ArticleRepository
          ↓
        articles

本 Service 與：

    services/search_service.py

    分離。

原本的 SearchService：

    負責 V4 Knowledge Search
    SearchIndex
    Search Ranking
    Hybrid Search

MCP SearchService：

    只負責 MCP Article Search
    與 Article Retrieval。

本階段原則：

    1. MCP 使用專用 SearchService。
    2. 搜尋資料來源為 articles。
    3. 使用 MCP ArticleRepository。
    4. 支援 Article Search。
    5. 支援 Document ID Retrieval。
    6. 支援 URL Retrieval。
    7. 支援 Date Filter。
    8. 支援 Category Filter。
    9. 支援 Sort。
    10. 支援 Pagination。
    11. Source Parameter 保留，但目前不啟用 Source Filter。
    12. 不使用 search_index。
    13. 不使用 SearchIndexRepository。
    14. 不使用 SearchRankingService。
    15. 不修改既有 services/search_service.py。
    16. 不直接操作 SQL。
    17. 不直接操作 Database。
"""


from autosearch_mcp.repositories.article_repository import (
    ArticleRepository
)


class SearchService:
    """
    AutoSearch MCP 專用 Search Service。

    負責：

        Query Normalize
        Query Validation
        Article Search
        Result Limit
        Date Filter
        Category Filter
        Sort
        Pagination
        Article Retrieval

    支援：

        Search
        Find By ID
        Find By Document ID
        Find By URL
        Count

    不負責：

        Database Connection
        SQL
        Search Index
        Search Ranking
        AI Analysis
        Archive
    """

    DEFAULT_LIMIT = 20
    MAX_LIMIT = 100

    # ==================================================
    # Initialize
    # ==================================================

    def __init__(
        self,
        repository=None
    ):
        self.repository = (
            repository
            if repository is not None
            else ArticleRepository()
        )

    # ==================================================
    # Query Normalize
    # ==================================================

    def _normalize_query(
        self,
        query
    ):
        """
        Normalize Search Query。
        """

        if query is None:
            return ""

        return str(
            query
        ).strip()

    # ==================================================
    # Query Validation
    # ==================================================

    def _validate_query(
        self,
        query
    ):
        """
        Validate Search Query。
        """

        if not query:
            return (
                False,
                "Search query cannot be empty."
            )

        return (
            True,
            ""
        )

    # ==================================================
    # Limit Normalize
    # ==================================================

    def _normalize_limit(
        self,
        limit
    ):
        """
        Normalize Search Result Limit。
        """

        try:
            limit = int(
                limit
            )

        except (
            TypeError,
            ValueError
        ):
            limit = self.DEFAULT_LIMIT

        if limit <= 0:
            limit = self.DEFAULT_LIMIT

        return min(
            limit,
            self.MAX_LIMIT
        )

    # ==================================================
    # Search
    # ==================================================

    def search(
        self,
        query,
        limit=DEFAULT_LIMIT,
        source=None,
        category=None,
        published_from=None,
        published_to=None,
        sort_by="latest",
        page=1
    ):
        """
        Search AutoSearch Articles。

        搜尋來源：

            articles

        支援：

            Date Filter
            Category Filter
            Sort
            Pagination

        Source：

            保留 source 參數。

            目前 articles.source
            尚未有實際資料，

            因此 Source Filter
            暫不啟用。

        回傳：

            list[dict]
        """

        query = self._normalize_query(
            query
        )

        is_valid, error_message = (
            self._validate_query(
                query
            )
        )

        if not is_valid:
            return []

        limit = self._normalize_limit(
            limit
        )

        # ==================================================
        # Normalize Page
        # ==================================================

        try:
            page = int(
                page
            )

        except (
            TypeError,
            ValueError
        ):
            page = 1

        if page <= 0:
            page = 1

        # ==================================================
        # Source
        # ==================================================

        # Source Filter 目前保留介面，
        # 但因 articles.source 尚未有實際資料，
        # 暫時不啟用 Source SQL Filter。
        #
        # 明確保留此參數，避免未來 API 介面變動。

        _ = source

        # ==================================================
        # Repository Search
        # ==================================================

        return self.repository.search(
            query=query,
            limit=limit,
            category=category,
            published_from=published_from,
            published_to=published_to,
            sort_by=sort_by,
            page=page
        )

    # ==================================================
    # Count
    # ==================================================

    def count(
        self
    ):
        """
        取得目前 articles 總數。
        """

        return self.repository.count()

    # ==================================================
    # Find By ID
    # ==================================================

    def find_by_id(
        self,
        article_id
    ):
        """
        依 Article ID 查詢。

        主要供內部 Article Retrieval 使用。
        """

        return self.repository.find_by_id(
            article_id
        )

    # ==================================================
    # Find By Document ID
    # ==================================================

    def find_by_document_id(
        self,
        document_id
    ):
        """
        依 Document ID 查詢。

        Document ID 是 MCP Article
        Retrieval 的主要識別方式之一。
        """

        return self.repository.find_by_document_id(
            document_id
        )

    # ==================================================
    # Find By URL
    # ==================================================

    def find_by_url(
        self,
        url
    ):
        """
        依 Article URL 查詢。

        URL 是 MCP Article Retrieval
        的主要識別方式之一。
        """

        return self.repository.find_by_url(
            url
        )

    # ==================================================
    # Close
    # ==================================================

    def close(
        self
    ):
        """
        關閉 Repository。
        """

        if self.repository is not None:

            self.repository.close()


__all__ = [
    "SearchService"
]