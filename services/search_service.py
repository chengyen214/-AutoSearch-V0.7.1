"""
services/search_service.py

AutoSearch V4

P3.8

Search Service

Purpose:

    統一處理 Knowledge Search。

Responsibilities:

    1. Keyword Search
    2. Entity Search
    3. Hybrid Search
    4. Search Ranking
    5. Final Search Score
    6. Result Sorting
    7. Pagination

Flow:

    Search API
        |
        v
    SearchService
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
"""


from database.search_index_repository import (
    SearchIndexRepository
)

from services.search_ranking_service import (
    SearchRankingService
)


class SearchService:
    """
    P3.8 Search Service。

    負責整合：

        SearchIndexRepository
        SearchRankingService

    建立完整 Search Pipeline。
    """

    def __init__(
        self,
        repository=None,
        ranking_service=None
    ):

        # ==================================
        # Repository
        # ==================================

        self.repository = (

            repository

            if repository is not None

            else SearchIndexRepository()

        )

        # ==================================
        # Ranking Service
        # ==================================

        self.ranking_service = (

            ranking_service

            if ranking_service is not None

            else SearchRankingService()

        )

    # ==================================
    # Normalize Query
    # ==================================

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

    # ==================================
    # Keyword Search
    # ==================================

    def search_keyword(
        self,
        query
    ):
        """
        Keyword Search。

        搜尋：

            search_text
            keywords
        """

        query = self._normalize_query(
            query
        )

        if not query:

            return []

        return self.repository.search_keyword(
            query
        )

    # ==================================
    # Entity Search
    # ==================================

    def search_entity(
        self,
        query
    ):
        """
        Entity Search。
        """

        query = self._normalize_query(
            query
        )

        if not query:

            return []

        return self.repository.search_entity(
            query
        )

    # ==================================
    # Build Ranked Results
    # ==================================

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
        """

        results = []

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

        # ==================================
        # Final Search Score Ranking
        # ==================================

        results.sort(

            key=lambda item:
                item["score"].final_score,

            reverse=True

        )

        return results

    # ==================================
    # Full Search
    # ==================================

    def search(
        self,
        query
    ):
        """
        完整 Search。

        Flow:

            Query
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

        candidates = (

            self.repository.search_keyword(

                query

            )

        )

        return self._build_ranked_results(

            query,

            candidates

        )

    # ==================================
    # Hybrid Search
    # ==================================

    def hybrid_search(
        self,
        query
    ):
        """
        Hybrid Search。

        Keyword + Entity

        流程：

            Keyword Search
                    +
            Entity Search
                    ↓
                Merge
                    ↓
                Ranking
                    ↓
                Sort
        """

        query = self._normalize_query(
            query
        )

        if not query:

            return []

        keyword_results = (

            self.repository.search_keyword(

                query

            )

        )

        entity_results = (

            self.repository.search_entity(

                query

            )

        )

        # ==================================
        # Merge
        # ==================================

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

        return self._build_ranked_results(

            query,

            list(
                merged.values()
            )

        )

    # ==================================
    # Result Key
    # ==================================

    def _get_result_key(
        self,
        search_index
    ):
        """
        取得 Search Result 唯一 Key。

        優先使用：

            id

        如果不存在：

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

    # ==================================
    # Search With Pagination
    # ==================================

    def search_paginated(
        self,
        query,
        page=1,
        page_size=20
    ):
        """
        Search + Ranking + Pagination。
        """

        query = self._normalize_query(
            query
        )

        # ==================================
        # Normalize Pagination
        # ==================================

        try:

            page = int(page)

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

        # ==================================
        # Search
        # ==================================

        results = self.search(
            query
        )

        total = len(
            results
        )

        # ==================================
        # Pagination
        # ==================================

        start = (

            (page - 1)
            * page_size

        )

        end = (

            start
            + page_size

        )

        data = results[
            start:end
        ]

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

    # ==================================
    # Hybrid Search With Pagination
    # ==================================

    def hybrid_search_paginated(
        self,
        query,
        page=1,
        page_size=20
    ):
        """
        Hybrid Search + Ranking + Pagination。
        """

        query = self._normalize_query(
            query
        )

        try:

            page = int(page)

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

        # ==================================
        # Hybrid Search
        # ==================================

        results = self.hybrid_search(
            query
        )

        total = len(
            results
        )

        # ==================================
        # Pagination
        # ==================================

        start = (

            (page - 1)
            * page_size

        )

        end = (

            start
            + page_size

        )

        data = results[
            start:end
        ]

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

    # ==================================
    # Get All Search Index
    # ==================================

    def get_all(
        self
    ):
        """
        取得所有 Search Index。

        主要供：

            Management
            Debug
            Testing

        使用。
        """

        return self.repository.get_all()
