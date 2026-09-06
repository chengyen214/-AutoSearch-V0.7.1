"""
autosearch_mcp/tools/search.py

AutoSearch V6.5

MCP-4.3

MCP Search Tool

用途：

    將 MCP SearchService
    暴露為 MCP Tool。

Flow：

    MCP Client / AI Agent
            |
            v
        SearchTool
            |
            v
        MCP SearchService
            |
            v
    MCP ArticleRepository
            |
            v
          articles

Important:

    1. 不重新實作 Search。
    2. 不直接操作 Database。
    3. 不直接操作 SQL。
    4. 不直接操作 Repository。
    5. 只使用 MCP SearchService。
    6. 支援 Article Search。
    7. 支援 Date Filter。
    8. 支援 Category Filter。
    9. 支援 Sort。
    10. 支援 Pagination。
    11. Source Parameter 保留。
    12. Source Filter 目前不啟用。
    13. 將 SearchService 回傳的 Python Object
        轉換成 MCP 可以傳輸的 JSON-compatible data。
    14. 不使用 search_index。
    15. 不使用 SearchIndexRepository。
    16. 不使用 SearchRankingService。
    17. 不修改既有 services/search_service.py。
"""


from autosearch_mcp.services.search_service import (
    SearchService
)


class SearchTool:
    """
    MCP Search Tool。

    負責：

        MCP Search Request
            ↓
        SearchService.search()
            ↓
        Result Serialization

    不負責：

        SQL
        Database
        Repository
        Search Index
        Search Ranking
        AI Analysis
        Archive
    """

    DEFAULT_LIMIT = 20

    # ==================================================
    # Initialize
    # ==================================================

    def __init__(
        self,
        search_service=None
    ):
        """
        初始化 Search Tool。

        Parameters:
            search_service:
                可注入 MCP SearchService。
                如果沒有提供，則建立新的 MCP SearchService。
        """

        # ==========================================
        # Search Service
        # ==========================================

        self.search_service = (

            search_service

            if search_service is not None

            else SearchService()

        )

    # ==================================================
    # Normalize Query
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
    # Serialize Object
    # ==================================================

    def _serialize_value(
        self,
        value
    ):
        """
        將 SearchService 回傳的 Python Object
        轉換成 JSON-compatible value。

        支援：

            None
            str
            int
            float
            bool
            list
            tuple
            dict
            dataclass-like object
            object.__dict__
        """

        # ==========================================
        # None
        # ==========================================

        if value is None:

            return None

        # ==========================================
        # Primitive
        # ==========================================

        if isinstance(
            value,
            (
                str,
                int,
                float,
                bool
            )
        ):

            return value

        # ==========================================
        # List / Tuple
        # ==========================================

        if isinstance(
            value,
            (
                list,
                tuple
            )
        ):

            return [

                self._serialize_value(
                    item
                )

                for item in value

            ]

        # ==========================================
        # Dictionary
        # ==========================================

        if isinstance(
            value,
            dict
        ):

            return {

                str(key):
                    self._serialize_value(
                        item
                    )

                for key, item
                in value.items()

            }

        # ==========================================
        # Object
        # ==========================================

        if hasattr(
            value,
            "__dict__"
        ):

            return {

                str(key):
                    self._serialize_value(
                        item
                    )

                for key, item
                in vars(value).items()

                if not key.startswith(
                    "_"
                )

            }

        # ==========================================
        # Fallback
        # ==========================================

        return str(
            value
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
        執行 MCP Article Search。

        Parameters:
            query:
                搜尋關鍵字。

            limit:
                每頁結果數量。

            source:
                Source Parameter。

                目前保留介面，
                但 Source Filter 尚未啟用。

            category:
                Article Category Filter。

            published_from:
                Published Date 起始日期。

            published_to:
                Published Date 結束日期。

            sort_by:
                排序方式。

            page:
                Pagination Page。

        Returns:
            dict

            {
                "query": str,
                "count": int,
                "data": list
            }
        """

        # ==========================================
        # Normalize Query
        # ==========================================

        query = self._normalize_query(
            query
        )

        # ==========================================
        # Empty Query
        # ==========================================

        if not query:

            return {

                "query":
                    "",

                "count":
                    0,

                "data":
                    []

            }

        # ==========================================
        # Search Service
        # ==========================================

        results = self.search_service.search(
            query=query,
            limit=limit,
            source=source,
            category=category,
            published_from=published_from,
            published_to=published_to,
            sort_by=sort_by,
            page=page
        )

        # ==========================================
        # Serialize Results
        # ==========================================

        data = self._serialize_value(
            results
        )

        # ==========================================
        # MCP Result
        # ==========================================

        return {

            "query":
                query,

            "count":
                len(results)
                if isinstance(
                    results,
                    list
                )
                else 0,

            "data":
                data

        }

    # ==================================================
    # Close
    # ==================================================

    def close(
        self
    ):
        """
        關閉 SearchService。
        """

        if self.search_service is not None:

            self.search_service.close()


# ==================================================
# Factory
# ==================================================

def create_search_tool(
    search_service=None
):
    """
    建立 SearchTool。

    可由 MCP Server 使用。

    Parameters:
        search_service:
            Optional MCP SearchService。

    Returns:
        SearchTool
    """

    return SearchTool(
        search_service=search_service
    )


__all__ = [
    "SearchTool",
    "create_search_tool"
]