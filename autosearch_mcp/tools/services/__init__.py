"""
autosearch_mcp/services/search_service.py

AutoSearch V6.4

MCP Search Service

功能：

    1. Keyword Search
    2. Entity Search
    3. Full Search
    4. Hybrid Search
    5. Search Ranking
    6. Final Search Score
    7. Result Sorting
    8. Pagination
    9. Get All Search Index

Flow：

    MCP Search Tool
            |
            v
    MCP SearchService
            |
            +-----------------------------+
            |                             |
            v                             v
    SearchIndexRepository      SearchRankingService
            |                             |
            v                             v
      Search Candidates        KnowledgeSearchScore
                                          |
                                          v
                                    final_score
                                          |
                                          v
                                    Final Ranking


本 Service 定位：

    MCP 專用 Search Service。

本 Service 負責：

    - MCP Search Domain Logic
    - Query Normalize
    - Keyword Search
    - Entity Search
    - Full Search
    - Hybrid Search
    - Search Ranking
    - Result Sorting
    - Pagination
    - Search Index Retrieval


本 Service 不負責：

    - MCP Server
    - MCP Tool Registration
    - MCP Protocol
    - Database SQL
    - Database Connection
    - SearchIndexRepository implementation
    - SearchRankingService implementation
    - Search Engine
    - Search Provider
    - Crawler
    - Parser
    - Article
    - Archive
    - AI Analysis
"""


# ============================================================
# Existing Repository
# ============================================================

from database.search_index_repository import (
    SearchIndexRepository
)


# ============================================================
# Existing Ranking Service
# ============================================================

from services.search_ranking_service import (
    SearchRankingService
)


class SearchService:
    """
    AutoSearch MCP 專用 Search Service。

    負責整合：

        SearchIndexRepository
        SearchRankingService

    建立 MCP 使用的完整 Knowledge Search Pipeline。

    注意：

        這個 Service 是 MCP 專用入口。

        但底層仍然重用 AutoSearch 已完成的：

            SearchIndexRepository
            SearchRankingService

        不重新實作既有 SQL 與 Ranking Logic。
    """

    # ========================================================
    # Initialization
    # ========================================================

    def __init__(
        self,
        repository=None,
        ranking_service=None
    ):
        """
        初始化 MCP SearchService。

        Parameters
        ----------
        repository:
            可注入 SearchIndexRepository。

        ranking_service:
            可注入 SearchRankingService。
        """

        # ====================================================
        # Search Index Repository
        # ====================================================

        self.repository = (
            repository
            if repository is not None
            else SearchIndexRepository()
        )

        # ====================================================
        # Search Ranking Service
        # ====================================================

        self.ranking_service = (
            ranking_service
            if ranking_service is not None
            else SearchRankingService()
        )

    # ========================================================
    # Normalize Query
    # ========================================================

    def _normalize_query(
        self,
        query
    ):
        """
        Normalize MCP Search Query。

        行為：

            None
                ↓
            ""

            其他
                ↓
            str()
                ↓
            strip()
        """

        if query is None:
            return ""

        return str(
            query
        ).strip()

    # ========================================================
    # Keyword Search
    # ========================================================

    def search_keyword(
        self,
        query
    ):
        """
        Keyword Search。

        搜尋：

            search_text
            keywords

        實際搜尋交由：

            SearchIndexRepository.search_keyword()
        """

        query = self._normalize_query(
            query
        )

        if not query:
            return []

        return self.repository.search_keyword(
            query
        )

    # ========================================================
    # Entity Search
    # ========================================================

    def search_entity(
        self,
        query
    ):
        """
        Entity Search。

        實際搜尋交由：

            SearchIndexRepository.search_entity()
        """

        query = self._normalize_query(
            query
        )

        if not query:
            return []

        return self.repository.search_entity(
            query
        )

    # ========================================================
    # Build Ranked Results
    # ========================================================

    def _build_ranked_results(
        self,
        query,
        search_indexes
    ):
        """
        對 Search Index 建立 Ranking。

        每筆結果：

            SearchIndex
                +
            KnowledgeSearchScore

        Flow：

            SearchIndex
                ↓
            SearchRankingService
                ↓
            KnowledgeSearchScore
                ↓
            final_score
                ↓
            Sort DESC
        """

        results = []

        if not search_indexes:
            return results

        for search_index in search_indexes:

            score = (
                self.ranking_service.build_search_score(
                    query,
                    search_index
                )
            )

            results.append(
                {
                    "search_index":
                        search_index,

                    "score":
                        score
                }
            )

        # ====================================================
        # Final Search Score Ranking
        # ====================================================

        results.sort(
            key=lambda item:
                item["score"].final_score,
            reverse=True
        )

        return results

    # ========================================================
    # Full Search
    # ========================================================

    def search(
        self,
        query
    ):
        """
        完整 Knowledge Search。

        Flow：

            Query
              ↓
            Normalize
              ↓
            Keyword Search
              ↓
            Search Index
              ↓
            Search Ranking
              ↓
            Final Search Score
              ↓
            Sort DESC
        """

        query = self._normalize_query(
            query
        )

        if not query:
            return []

        # ====================================================
        # Search Candidates
        # ====================================================

        candidates = (
            self.repository.search_keyword(
                query
            )
        )

        # ====================================================
        # Ranking
        # ====================================================

        return self._build_ranked_results(
            query,
            candidates
        )

    # ========================================================
    # Hybrid Search
    # ========================================================

    def hybrid_search(
        self,
        query
    ):
        """
        Hybrid Search。

        Keyword Search
                +
        Entity Search
                ↓
              Merge
                ↓
             Ranking
                ↓
             Sort DESC
        """

        query = self._normalize_query(
            query
        )

        if not query:
            return []

        # ====================================================
        # Keyword Search
        # ====================================================

        keyword_results = (
            self.repository.search_keyword(
                query
            )
        )

        # ====================================================
        # Entity Search
        # ====================================================

        entity_results = (
            self.repository.search_entity(
                query
            )
        )

        # ====================================================
        # Merge
        # ====================================================

        merged = {}

        for item in keyword_results:

            key = self._get_result_key(
                item
            )

            merged[key] = item

        for item in entity_results:

            key = self._get_result_key(
                item
            )

            merged[key] = item

        # ====================================================
        # Ranking
        # ====================================================

        return self._build_ranked_results(
            query,
            list(
                merged.values()
            )
        )

    # ========================================================
    # Result Key
    # ========================================================

    def _get_result_key(
        self,
        search_index
    ):
        """
        取得 Search Result 唯一 Key。

        優先：

            id

        fallback：

            knowledge_id
        """

        if search_index.id is not None:

            return (
                "id",
                search_index.id
            )

        return (
            "knowledge_id",
            search_index.knowledge_id
        )

    # ========================================================
    # Normalize Pagination
    # ========================================================

    def _normalize_pagination(
        self,
        page=1,
        page_size=20
    ):
        """
        Normalize Pagination Parameters。

        Returns：

            (
                page,
                page_size
            )
        """

        try:
            page = int(
                page
            )

        except (
            TypeError,
            ValueError
        ):
            page = 1

        try:
            page_size = int(
                page_size
            )

        except (
            TypeError,
            ValueError
        ):
            page_size = 20

        if page < 1:
            page = 1

        if page_size < 1:
            page_size = 20

        return (
            page,
            page_size
        )

    # ========================================================
    # Apply Pagination
    # ========================================================

    def _apply_pagination(
        self,
        results,
        page,
        page_size
    ):
        """
        對搜尋結果進行 Pagination。
        """

        start = (
            (page - 1)
            * page_size
        )

        end = (
            start
            + page_size
        )

        return results[
            start:end
        ]

    # ========================================================
    # Search With Pagination
    # ========================================================

    def search_paginated(
        self,
        query,
        page=1,
        page_size=20
    ):
        """
        Search + Ranking + Pagination。

        Returns：

        {
            "query": query,
            "page": page,
            "page_size": page_size,
            "total": total,
            "count": count,
            "data": [...]
        }
        """

        query = self._normalize_query(
            query
        )

        (
            page,
            page_size
        ) = self._normalize_pagination(
            page,
            page_size
        )

        # ====================================================
        # Empty Query
        # ====================================================

        if not query:

            return {
                "query":
                    query,

                "page":
                    page,

                "page_size":
                    page_size,

                "total":
                    0,

                "count":
                    0,

                "data":
                    []
            }

        # ====================================================
        # Search
        # ====================================================

        results = self.search(
            query
        )

        total = len(
            results
        )

        # ====================================================
        # Pagination
        # ====================================================

        data = self._apply_pagination(
            results,
            page,
            page_size
        )

        return {
            "query":
                query,

            "page":
                page,

            "page_size":
                page_size,

            "total":
                total,

            "count":
                len(data),

            "data":
                data
        }

    # ========================================================
    # Hybrid Search With Pagination
    # ========================================================

    def hybrid_search_paginated(
        self,
        query,
        page=1,
        page_size=20
    ):
        """
        Hybrid Search + Ranking + Pagination。

        Returns：

        {
            "query": query,
            "page": page,
            "page_size": page_size,
            "total": total,
            "count": count,
            "data": [...]
        }
        """

        query = self._normalize_query(
            query
        )

        (
            page,
            page_size
        ) = self._normalize_pagination(
            page,
            page_size
        )

        # ====================================================
        # Empty Query
        # ====================================================

        if not query:

            return {
                "query":
                    query,

                "page":
                    page,

                "page_size":
                    page_size,

                "total":
                    0,

                "count":
                    0,

                "data":
                    []
            }

        # ====================================================
        # Hybrid Search
        # ====================================================

        results = self.hybrid_search(
            query
        )

        total = len(
            results
        )

        # ====================================================
        # Pagination
        # ====================================================

        data = self._apply_pagination(
            results,
            page,
            page_size
        )

        return {
            "query":
                query,

            "page":
                page,

            "page_size":
                page_size,

            "total":
                total,

            "count":
                len(data),

            "data":
                data
        }

    # ========================================================
    # Get All Search Index
    # ========================================================

    def get_all(
        self
    ):
        """
        取得所有 Search Index。

        主要用途：

            MCP Management
            MCP Debug
            MCP Testing

        實際資料取得交由：

            SearchIndexRepository.get_all()
        """

        return self.repository.get_all()


# ============================================================
# Public API
# ============================================================

__all__ = [
    "SearchService"
]