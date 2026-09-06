"""
autosearch_mcp/tools/search.py

AutoSearch V6.5

MCP-4.3

MCP Search Tool

用途：

    將 MCP SearchService
    暴露為 MCP Search Tool。

Flow：

    MCP Client / AI Agent
            ↓
        MCP SearchTool
            ↓
        MCP SearchService
            ↓
    MCP ArticleRepository
            ↓
          articles

本階段原則：

    1. MCP Tool 不直接操作 SQL。
    2. MCP Tool 不直接操作 Database。
    3. MCP Tool 不直接使用 Repository。
    4. MCP Tool 只呼叫 MCP SearchService。
    5. 支援 Article Search。
    6. 支援 Date Filter。
    7. 支援 Category Filter。
    8. 支援 Sort。
    9. 支援 Pagination。
    10. Source Parameter 保留。
    11. Source Filter 目前不啟用。
    12. 不使用 search_index。
    13. 不使用 SearchIndexRepository。
    14. 不使用 SearchRankingService。
    15. 不修改既有 services/search_service.py。
"""


from autosearch_mcp.services.search_service import (
    SearchService
)


class SearchTool:
    """
    AutoSearch MCP Search Tool。

    負責：

        MCP Search Request
        Search Parameter Handling
        呼叫 MCP SearchService

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
        service=None
    ):
        self.service = (
            service
            if service is not None
            else SearchService()
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

        Parameters
        ----------
        query : str
            搜尋關鍵字。

        limit : int
            每頁結果數量。

        source : str | None
            Source Filter。

            目前保留此參數，
            但 Source Filter 尚未啟用。

        category : str | None
            Article Category Filter。

        published_from : str | None
            Published Date 起始日期。

        published_to : str | None
            Published Date 結束日期。

        sort_by : str
            排序方式。

        page : int
            Pagination Page。

        Returns
        -------
        list[dict]
            Article Search Results。
        """

        return self.service.search(
            query=query,
            limit=limit,
            source=source,
            category=category,
            published_from=published_from,
            published_to=published_to,
            sort_by=sort_by,
            page=page
        )

    # ==================================================
    # Close
    # ==================================================

    def close(
        self
    ):
        """
        關閉 SearchService。
        """

        if self.service is not None:

            self.service.close()


__all__ = [
    "SearchTool"
]