"""
autosearch_mcp/server.py

AutoSearch V6.5

MCP-4.4

功能：
    建立 AutoSearch MCP Server。
    並註冊：

        1. MCP Search Tool
        2. MCP Article Retrieval Tool

目前階段：
    MCP-4 Advanced Search
    Server Registration

Flow：

    MCP Client / AI Agent
            |
            v
        MCP Server
        /         \
       v           v
 Search Tool   Article Tool
       |           |
       v           v
 SearchService  SearchService
       |           |
       v           v
 ArticleRepository
            |
            v
          articles


本階段原則：

    1. MCP 使用專用 Search Tool。
    2. MCP 使用專用 Article Tool。
    3. MCP 使用專用 SearchService。
    4. MCP 使用專用 ArticleRepository。
    5. 搜尋與 Article Retrieval 資料來源為 articles。
    6. Search Tool 支援 Advanced Search。
    7. 支援 Date Filter。
    8. 支援 Category Filter。
    9. 支援 Sort。
   10. 支援 Pagination。
   11. Source Parameter 保留。
   12. Source Filter 目前不啟用。
   13. 不使用 SearchIndexRepository。
   14. 不使用 search_index。
   15. 不使用 SearchRankingService。
   16. 不修改既有 services/search_service.py。
   17. MCP Server 只負責 Tool Registration。
"""


import sys
from pathlib import Path

from mcp.server import MCPServer


# ============================================================
# Project Root
# ============================================================

PROJECT_ROOT = Path(
    __file__
).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(PROJECT_ROOT)
    )


# ============================================================
# AutoSearch MCP Tools
# ============================================================

from autosearch_mcp.tools.search import (
    SearchTool
)

from autosearch_mcp.tools.article import (
    ArticleTool
)


# ============================================================
# MCP Server
# ============================================================

mcp = MCPServer(
    "AutoSearch MCP"
)


# ============================================================
# Search Tool
# ============================================================

search_tool = SearchTool()


@mcp.tool(
    name="search",
    description=(
        "Search AutoSearch articles with keyword, "
        "date, category, sorting, and pagination filters."
    )
)
def search(
    query: str,
    limit: int = 20,
    source: str | None = None,
    category: str | None = None,
    published_from: str | None = None,
    published_to: str | None = None,
    sort_by: str = "latest",
    page: int = 1
) -> dict:
    """
    執行 AutoSearch Advanced Article Search。

    Parameters:
        query:
            Search keyword or query。

        limit:
            每頁結果數量。
            Default: 20。

        source:
            Source Filter。

            目前保留此參數，
            但 Source Filter 尚未啟用。

        category:
            Article Category Filter。

        published_from:
            Published Date 起始日期。

        published_to:
            Published Date 結束日期。

        sort_by:
            排序方式。

            支援：
                latest
                oldest
                published
                published_oldest
                crawl_time
                crawl_time_oldest
                importance

        page:
            Pagination Page。
            Default: 1。

    Returns:
        JSON-compatible search result。

    Flow:

        MCP Client / AI Agent
            ↓
        MCP Server
            ↓
        MCP Search Tool
            ↓
        MCP SearchService
            ↓
        MCP ArticleRepository
            ↓
        articles
    """

    results = search_tool.search(
        query=query,
        limit=limit,
        source=source,
        category=category,
        published_from=published_from,
        published_to=published_to,
        sort_by=sort_by,
        page=page
    )

    return {
        "query": query,
        "count": (
            len(results)
            if isinstance(results, list)
            else 0
        ),
        "data": results
    }


# ============================================================
# Article Tool
# ============================================================

article_tool = ArticleTool()


# ============================================================
# Get Article By Document ID
# ============================================================

@mcp.tool(
    name="get_article_by_document_id",
    description=(
        "Retrieve an AutoSearch article by "
        "document ID."
    )
)
def get_article_by_document_id(
    document_id: str
) -> dict:
    """
    依 Document ID 取得 Article。

    Parameters:
        document_id:
            AutoSearch Article Document ID。

    Returns:
        JSON-compatible article data。
    """

    article = article_tool.get_by_document_id(
        document_id
    )

    if article is None:
        return {
            "document_id": document_id,
            "data": None
        }

    return {
        "document_id": document_id,
        "data": article
    }


# ============================================================
# Get Article By URL
# ============================================================

@mcp.tool(
    name="get_article_by_url",
    description=(
        "Retrieve an AutoSearch article by "
        "article URL."
    )
)
def get_article_by_url(
    url: str
) -> dict:
    """
    依 Article URL 取得 Article。

    Parameters:
        url:
            Article URL。

    Returns:
        JSON-compatible article data。
    """

    article = article_tool.get_by_url(
        url
    )

    if article is None:
        return {
            "url": url,
            "data": None
        }

    return {
        "url": url,
        "data": article
    }


# ============================================================
# Main
# ============================================================

def main():
    """
    啟動 AutoSearch MCP Server。
    """

    mcp.run()


if __name__ == "__main__":
    main()