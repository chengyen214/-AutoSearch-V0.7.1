"""
services/historical_search_service.py

AutoSearch V4

P2.3.5

Historical Search Service

功能:

1. Historical Search
2. Article Historical Search
3. Version Search
4. Source Search
5. Date Range Search
6. Article History
7. Latest Version
8. Search Result Count
9. Historical Search Result Normalization

Architecture:

Historical Search
        ↓
HistoricalSearchService
        ↓
HistoricalSearchRepository
        ↓
archive_versions
        ↓
raw_documents
        ↓
articles

用途:

    P2.3.5 Historical Search
    P3 Historical Search API
"""

from database.historical_search_repository import (
    HistoricalSearchRepository
)

from utils.logger import logger


class HistoricalSearchService:
    """
    Historical Search Service

    負責：

        Historical Search
        Historical Version Query
        Historical Timeline Query

    不直接操作 Database。
    """

    # ==================================
    # Initialize
    # ==================================

    def __init__(
        self,
        repository=None
    ):
        """
        初始化 Historical Search Service。

        Parameters
        ----------
        repository :
            HistoricalSearchRepository

            支援 Dependency Injection。
        """

        if repository is None:

            repository = (
                HistoricalSearchRepository()
            )

        self.repository = repository

    # ==================================
    # Search
    # ==================================

    def search(
        self,
        keyword=None,
        article_id=None,
        source=None,
        start_date=None,
        end_date=None,
        version_number=None,
        limit=50,
        offset=0
    ):
        """
        搜尋 Historical Archive。

        支援：

            Keyword
            Article
            Source
            Date Range
            Version

        Returns
        -------

        dict

        {
            "results": [...],
            "count": ...,
            "limit": ...,
            "offset": ...
        }
        """

        try:

            # ==================================
            # Normalize Pagination
            # ==================================

            if limit is None:
                limit = 50

            if limit <= 0:
                limit = 50

            if offset is None:
                offset = 0

            if offset < 0:
                offset = 0

            # ==================================
            # Search
            # ==================================

            results = (
                self.repository.search(

                    keyword=keyword,

                    article_id=article_id,

                    source=source,

                    start_date=start_date,

                    end_date=end_date,

                    version_number=version_number,

                    limit=limit,

                    offset=offset

                )
            )

            # ==================================
            # Count
            # ==================================

            count = (
                self.repository.count(

                    keyword=keyword,

                    article_id=article_id,

                    source=source,

                    start_date=start_date,

                    end_date=end_date,

                    version_number=version_number

                )
            )

            return {

                "results": results,

                "count": count,

                "limit": limit,

                "offset": offset

            }

        except Exception as e:

            logger.exception(
                f"Historical search error: {e}"
            )

            return {

                "results": [],

                "count": 0,

                "limit": limit,

                "offset": offset

            }

    # ==================================
    # Search By Keyword
    # ==================================

    def search_by_keyword(
        self,
        keyword,
        limit=50,
        offset=0
    ):
        """
        依關鍵字搜尋 Historical Archive。
        """

        if not keyword:

            return {

                "results": [],

                "count": 0,

                "limit": limit,

                "offset": offset

            }

        return self.search(

            keyword=keyword,

            limit=limit,

            offset=offset

        )

    # ==================================
    # Search By Article
    # ==================================

    def search_by_article(
        self,
        article_id,
        keyword=None,
        limit=50,
        offset=0
    ):
        """
        搜尋指定 Article 的歷史資料。

        如果 keyword 為 None：

            回傳 Article 所有歷史版本。

        如果有 keyword：

            搜尋指定 Article 的歷史版本。
        """

        if article_id is None:

            return {

                "results": [],

                "count": 0,

                "limit": limit,

                "offset": offset

            }

        try:

            if keyword:

                results = (
                    self.repository.search(

                        keyword=keyword,

                        article_id=article_id,

                        limit=limit,

                        offset=offset

                    )
                )

                count = (
                    self.repository.count(

                        keyword=keyword,

                        article_id=article_id

                    )
                )

            else:

                results = (
                    self.repository
                    .get_by_article_id(
                        article_id
                    )
                )

                # ==================================
                # Pagination
                # ==================================

                total = len(results)

                results = results[
                    offset:
                    offset + limit
                ]

                count = total

            return {

                "results": results,

                "count": count,

                "limit": limit,

                "offset": offset

            }

        except Exception as e:

            logger.exception(
                "Historical article search error: "
                f"{e}"
            )

            return {

                "results": [],

                "count": 0,

                "limit": limit,

                "offset": offset

            }

    # ==================================
    # Get History
    # ==================================

    def get_history(
        self,
        article_id
    ):
        """
        取得 Article 完整歷史版本。
        """

        if article_id is None:

            return []

        try:

            return (
                self.repository
                .get_by_article_id(
                    article_id
                )
            )

        except Exception as e:

            logger.exception(
                "Get historical history error: "
                f"{e}"
            )

            return []

    # ==================================
    # Get Version
    # ==================================

    def get_version(
        self,
        article_id,
        version_number
    ):
        """
        取得指定 Article Version。
        """

        if article_id is None:

            return None

        if version_number is None:

            return None

        try:

            return (
                self.repository
                .get_version(

                    article_id,

                    version_number

                )
            )

        except Exception as e:

            logger.exception(
                "Get historical version error: "
                f"{e}"
            )

            return None

    # ==================================
    # Get Latest Version
    # ==================================

    def get_latest_version(
        self,
        article_id
    ):
        """
        取得 Article 最新歷史版本。
        """

        if article_id is None:

            return None

        try:

            return (
                self.repository
                .get_latest_version(
                    article_id
                )
            )

        except Exception as e:

            logger.exception(
                "Get latest historical version error: "
                f"{e}"
            )

            return None

    # ==================================
    # Search By Source
    # ==================================

    def search_by_source(
        self,
        source,
        limit=50,
        offset=0
    ):
        """
        搜尋指定 Source 的 Historical Archive。
        """

        if not source:

            return {

                "results": [],

                "count": 0,

                "limit": limit,

                "offset": offset

            }

        try:

            results = (
                self.repository
                .search_by_source(

                    source,

                    limit=limit,

                    offset=offset

                )
            )

            count = (
                self.repository.count(
                    source=source
                )
            )

            return {

                "results": results,

                "count": count,

                "limit": limit,

                "offset": offset

            }

        except Exception as e:

            logger.exception(
                "Historical source search error: "
                f"{e}"
            )

            return {

                "results": [],

                "count": 0,

                "limit": limit,

                "offset": offset

            }

    # ==================================
    # Search By Date
    # ==================================

    def search_by_date(
        self,
        start_date,
        end_date,
        limit=50,
        offset=0
    ):
        """
        依日期範圍搜尋 Historical Archive。
        """

        if start_date is None:
            return {

                "results": [],

                "count": 0,

                "limit": limit,

                "offset": offset

            }

        if end_date is None:
            return {

                "results": [],

                "count": 0,

                "limit": limit,

                "offset": offset

            }

        try:

            results = (
                self.repository
                .search_by_date(

                    start_date,

                    end_date,

                    limit=limit,

                    offset=offset

                )
            )

            count = (
                self.repository.count(

                    start_date=start_date,

                    end_date=end_date

                )
            )

            return {

                "results": results,

                "count": count,

                "limit": limit,

                "offset": offset

            }

        except Exception as e:

            logger.exception(
                "Historical date search error: "
                f"{e}"
            )

            return {

                "results": [],

                "count": 0,

                "limit": limit,

                "offset": offset

            }

    # ==================================
    # Search By Version
    # ==================================

    def search_by_version(
        self,
        version_number,
        limit=50,
        offset=0
    ):
        """
        搜尋指定 Version Number 的所有 Article。
        """

        if version_number is None:

            return {

                "results": [],

                "count": 0,

                "limit": limit,

                "offset": offset

            }

        return self.search(

            version_number=version_number,

            limit=limit,

            offset=offset

        )

    # ==================================
    # Count
    # ==================================

    def count(
        self,
        keyword=None,
        article_id=None,
        source=None,
        start_date=None,
        end_date=None,
        version_number=None
    ):
        """
        計算 Historical Search 結果數量。
        """

        try:

            return self.repository.count(

                keyword=keyword,

                article_id=article_id,

                source=source,

                start_date=start_date,

                end_date=end_date,

                version_number=version_number

            )

        except Exception as e:

            logger.exception(
                "Historical search count error: "
                f"{e}"
            )

            return 0

    # ==================================
    # Exists
    # ==================================

    def exists(
        self,
        article_id,
        version_number
    ):
        """
        檢查指定歷史版本是否存在。
        """

        if article_id is None:
            return False

        if version_number is None:
            return False

        try:

            return (
                self.repository.exists(

                    article_id,

                    version_number

                )
            )

        except Exception as e:

            logger.exception(
                "Historical version exists error: "
                f"{e}"
            )

            return False

    # ==================================
    # Search All History
    # ==================================

    def get_all_history(
        self,
        limit=50,
        offset=0
    ):
        """
        取得所有 Article 的歷史版本。

        用於：

            Archive Browser
            Historical Search
            Knowledge History
        """

        return self.search(

            limit=limit,

            offset=offset

        )

    # ==================================
    # Repr
    # ==================================

    def __repr__(self):

        return (
            "HistoricalSearchService("
            f"repository="
            f"{self.repository!r}"
            ")"
        )