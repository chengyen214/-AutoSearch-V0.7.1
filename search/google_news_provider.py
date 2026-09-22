"""
search/google_news_provider.py

AutoSearch V5

V5.2 P2.3

Google News Search Provider

用途：

    將 V4 既有 Google News RSS Search
    包裝成 V5 SearchProvider。

架構：

    User Keyword
        ↓
    GoogleNewsProvider
        ↓
    V4 Google News Search Engine
        ↓
    30 Candidate SearchResult[]
        ↓
    Target crawler_url Exclusion
        ↓
    Database URL Priority
        ↓
    10 Valid SearchResult[]
        ↓
    ProviderSearchAdapter
        ↓
    SearchExecutionBridge
        ↓
    SearchResult[]

設計原則：

    V5 P2.3 不重新實作 Google News RSS。

    直接沿用：

        search/search_engine.py

    已有能力：

        - Google News RSS
        - URL Encode
        - RSS Parsing
        - Google News URL Decode
        - URL Deduplication
        - SearchResult 建立

本模組只負責：

    - Google News Provider
    - Provider Identity
    - Keyword Validation
    - Result Limit
    - 取得全部 Target crawler_url
    - 呼叫 V4 Google News Search
    - 近 7 天搜尋條件
    - Target Source Exclusion
    - articles.url Database Priority
    - SearchResult Validation
    - SearchResult Normalization

本模組不負責：

    - ProviderSearchAdapter 建立
    - SearchAdapter
    - SearchAdapterManager
    - SearchExecutionBridge
    - Crawler
    - Parser
    - Article
    - Archive
    - AI
    - Target INSERT / UPDATE
"""


# ==================================================
#
# V4 Google News Search Engine
#
# ==================================================

from search.search_engine import (
    search as google_news_search,
)


# ==================================================
#
# V5 Search Provider Base
#
# ==================================================

from search.search_provider import (
    SearchProvider,
)


# ==================================================
#
# Search Result
#
# ==================================================

from models.search_result import (
    SearchResult,
)


# ==================================================
#
# URL Source Grouping Service
#
# ==================================================

from services.url_source_grouping_service import (
    URLSourceGroupingService,
)


# ==================================================
#
# Database
#
# ==================================================

from database.connection import (
    get_connection,
)


# ==================================================
#
# Logger
#
# ==================================================

from utils.logger import (
    logger,
)


class GoogleNewsProvider(SearchProvider):
    """
    V5 Google News Search Provider。

    P2.3

    使用 V4：

        search/search_engine.py

    作為 Google News RSS 的實際搜尋實作。

    Provider 本身：

        - 不建立 Adapter
        - 不執行 Crawler
        - 不執行 Parser
        - 不處理 Archive
        - 不處理 AI

    Provider 負責：

        keyword
            ↓
        取得全部 Target crawler_url
            ↓
        V4 Google News Search
            ↓
        近 7 天
            ↓
        30 Candidate Results
            ↓
        排除所有 Target Source
            ↓
        查 articles.url
            ↓
        New URL 優先
            ↓
        Existing URL 補足
            ↓
        10 Valid Results
    """

    # ==================================================
    #
    # Provider Identity
    #
    # ==================================================

    provider_name = "google_news"

    # ==================================================
    #
    # Default Result Limit
    #
    # ==================================================

    max_results = 10

    # ==================================================
    #
    # Candidate Result Limit
    #
    # ==================================================

    candidate_results = 30

    # ==================================================
    #
    # Search Time Range
    #
    # ==================================================

    search_time_range = "when:7d"

    # ==================================================
    #
    # Constructor
    #
    # ==================================================

    def __init__(
        self,
        timeout=7,
    ):
        """
        建立 GoogleNewsProvider。

        Parameters
        ----------
        timeout :
            Provider Timeout 設定。

            目前 V4 search_engine.py
            使用 feedparser.parse()
            建立 RSS Search。

            P2.3 不修改 V4 Search Engine，
            因此此 timeout 暫時只保留
            Provider Configuration Interface。
        """

        self.timeout = timeout

        # --------------------------------------------------
        # URL Source Grouping Service
        # --------------------------------------------------

        self.url_source_grouping_service = (
            URLSourceGroupingService()
        )

    # ==================================================
    #
    # Search
    #
    # ==================================================

    def search(
        self,
        keyword,
        max_results=None,
    ):
        """
        執行 Google News Search。

        Pipeline：

            keyword
                ↓
            取得全部 Target crawler_url
                ↓
            keyword + when:7d
                ↓
            V4 search_engine.search()
                ↓
            30 Candidate Results
                ↓
            Target crawler_url exclusion
                ↓
            articles.url Database Priority
                ↓
            New URL 優先
                ↓
            Existing URL 補足
                ↓
            最多 10 Valid Results

        Parameters
        ----------
        keyword :
            Search Keyword。

        max_results :
            最大回傳結果數量。

            None：
                使用 Provider max_results。

            注意：

                V4 Google News Search
                固定先取得 candidate_results
                筆候選結果。
        """

        # ==================================================
        #
        # Keyword Validation
        #
        # ==================================================

        keyword = self._normalize_keyword(
            keyword
        )

        if not keyword:

            return []

        # ==================================================
        #
        # Result Limit
        #
        # ==================================================

        max_results = (
            self._normalize_max_results(
                max_results
            )
        )

        if max_results <= 0:

            return []

        # ==================================================
        #
        # Fetch ALL Target crawler_urls
        #
        # 不限制 keyword。
        #
        # Google News 永遠排除
        # targets 裡所有 crawler_url。
        #
        # ==================================================

        crawler_urls = (
            self.url_source_grouping_service
            .fetch_crawler_urls()
        )

        # ==================================================
        #
        # Google News Search Query
        #
        # 近 7 天：
        #
        #     when:7d
        #
        # ==================================================

        search_keyword = (
            f"{keyword} "
            f"{self.search_time_range}"
        )

        # ==================================================
        #
        # V4 Google News Search
        #
        # 先取得 30 筆候選結果。
        #
        # ==================================================

        source_results = (
            google_news_search(
                search_keyword,
                max_results=self.candidate_results,
            )
        )

        # ==================================================
        #
        # Normalize / Filter Results
        #
        # ==================================================

        return self._normalize_results(
            source_results=source_results,
            keyword=keyword,
            max_results=max_results,
            crawler_urls=crawler_urls,
        )

    # ==================================================
    #
    # Normalize Keyword
    #
    # ==================================================

    @staticmethod
    def _normalize_keyword(
        keyword,
    ):
        """
        Normalize Search Keyword。

        None / Empty：

            回傳空字串。
        """

        if keyword is None:

            return ""

        keyword = str(
            keyword
        ).strip()

        return keyword

    # ==================================================
    #
    # Normalize Max Results
    #
    # ==================================================

    @classmethod
    def _normalize_max_results(
        cls,
        max_results,
    ):
        """
        Normalize Result Limit。

        None：

            使用 Provider max_results。

        Invalid：

            使用 Provider max_results。

        <= 0：

            保留為 <= 0，
            由 search() 判斷為空結果。

        最大回傳數：

            10
        """

        if max_results is None:

            return cls.max_results

        try:

            value = int(
                max_results
            )

        except (
            TypeError,
            ValueError,
        ):

            return cls.max_results

        return min(
            value,
            cls.max_results,
        )

    # ==================================================
    #
    # Normalize Results
    #
    # ==================================================

    @classmethod
    def _normalize_results(
        cls,
        source_results,
        keyword,
        max_results,
        crawler_urls=None,
    ):
        """
        Validate / Normalize V4 Search Results。

        本方法處理：

            - None
            - list validation
            - SearchResult validation
            - URL validation
            - Target crawler_url exclusion
            - articles.url Database Priority
            - keyword normalization
            - search_source normalization
            - rank normalization
            - result limit

        流程：

            30 Candidate Results
                    ↓
            Target crawler_url exclusion
                    ↓
            Valid Candidate URLs
                    ↓
            articles.url lookup
                    ↓
            New URLs
                    ↓
            Existing URLs
                    ↓
            New URLs 優先
                    ↓
            Existing URLs 補足
                    ↓
            最多 10 筆

        URL Deduplication：

            V4 search_engine.py
            已經負責 URL Deduplication。

            Provider 不重新實作
            V4 Search Engine 的
            Deduplication。
        """

        if source_results is None:

            return []

        if not isinstance(
            source_results,
            list,
        ):

            raise TypeError(
                "Google News Search "
                "must return a list"
            )

        if crawler_urls is None:

            crawler_urls = []

        # ==================================================
        #
        # First Stage:
        # Validate / Target Exclusion
        #
        # ==================================================

        candidates = []

        seen_urls = set()

        for item in source_results:

            # ------------------------------------------
            # SearchResult Validation
            # ------------------------------------------

            if not isinstance(
                item,
                SearchResult,
            ):

                continue

            # ------------------------------------------
            # URL Validation
            # ------------------------------------------

            url = getattr(
                item,
                "url",
                None,
            )

            if not url:

                continue

            url = str(
                url
            ).strip()

            if not url:

                continue

            # ------------------------------------------
            # Local Deduplication Safety
            #
            # V4 本身已負責 Deduplication，
            # 這裡只保護 Provider 自身
            # 不重複處理。
            # ------------------------------------------

            if url in seen_urls:

                continue

            # ------------------------------------------
            # Target crawler_url Exclusion
            #
            # 只要符合任何一個 Target crawler_url
            # 就排除。
            # ------------------------------------------

            excluded = False

            for crawler_url in crawler_urls:

                if (
                    URLSourceGroupingService
                    .is_excluded_by_crawler_url(
                        url,
                        crawler_url,
                    )
                ):

                    excluded = True
                    break

            if excluded:

                continue

            seen_urls.add(
                url
            )

            candidates.append(
                (
                    item,
                    url,
                )
            )

        # ==================================================
        #
        # No Candidates
        #
        # ==================================================

        if not candidates:

            return []

        # ==================================================
        #
        # Database Existing URL Lookup
        #
        # ==================================================

        candidate_urls = [
            url
            for _, url in candidates
        ]

        existing_url_set = (
            cls._get_existing_urls(
                candidate_urls
            )
        )

        # ==================================================
        #
        # Split New / Existing
        #
        # ==================================================

        new_results = []
        existing_results = []

        for item, url in candidates:

            if url in existing_url_set:

                existing_results.append(
                    item
                )

            else:

                new_results.append(
                    item
                )

        # ==================================================
        #
        # New URL Priority
        #
        # ==================================================

        results = []

        # ------------------------------------------
        #
        # First: New URLs
        #
        # ------------------------------------------

        for item in new_results:

            results.append(
                item
            )

            if len(results) >= max_results:

                break

        # ------------------------------------------
        #
        # Second: Existing URLs
        #
        # ------------------------------------------

        if len(results) < max_results:

            remaining = (
                max_results
                - len(results)
            )

            results.extend(
                existing_results[
                    :remaining
                ]
            )

        # ==================================================
        #
        # Final Normalize
        #
        # ==================================================

        normalized_results = []

        for item in results:

            # ------------------------------------------
            # Normalize URL
            # ------------------------------------------

            url = getattr(
                item,
                "url",
                None,
            )

            if not url:

                continue

            try:

                item.url = str(
                    url
                ).strip()

            except AttributeError:

                pass

            # ------------------------------------------
            # Normalize Keyword
            # ------------------------------------------

            try:

                item.keyword = keyword

            except AttributeError:

                pass

            # ------------------------------------------
            # Normalize Search Source
            # ------------------------------------------

            try:

                item.search_source = (
                    cls.provider_name
                )

            except AttributeError:

                pass

            # ------------------------------------------
            # Normalize Rank
            # ------------------------------------------

            try:

                item.rank = (
                    len(normalized_results)
                    + 1
                )

            except AttributeError:

                pass

            normalized_results.append(
                item
            )

        return normalized_results

    # ==================================================
    #
    # Existing URL Lookup
    #
    # ==================================================

    @staticmethod
    def _get_existing_urls(
        urls,
    ):
        """
        查詢 MySQL articles.url。

        Parameters
        ----------
        urls :
            Candidate URL list。

        Returns
        -------
        set[str]

            已存在於：

                articles.url

            的 URL 集合。

        SQL：

            SELECT url
            FROM articles
            WHERE url IN (...)
        """

        if not urls:

            return set()

        conn = None
        cursor = None

        try:

            # --------------------------------------------------
            # Connection
            # --------------------------------------------------

            conn = get_connection()

            if conn is None:

                logger.warning(
                    "SQL connection unavailable "
                    "during Google News URL lookup."
                )

                return set()

            # --------------------------------------------------
            # Cursor
            # --------------------------------------------------

            cursor = conn.cursor()

            # --------------------------------------------------
            # Placeholder
            # --------------------------------------------------

            placeholders = ", ".join(
                ["%s"] * len(urls)
            )

            # --------------------------------------------------
            # SQL
            # --------------------------------------------------

            query = f"""
                SELECT url
                FROM articles
                WHERE url IN ({placeholders})
            """

            cursor.execute(
                query,
                tuple(urls),
            )

            rows = cursor.fetchall()

            # --------------------------------------------------
            # Result
            # --------------------------------------------------

            existing_urls = set()

            for row in rows:

                if not row:

                    continue

                url = row[0]

                if url is None:

                    continue

                existing_urls.add(
                    str(url).strip()
                )

            return existing_urls

        except Exception as exc:

            logger.exception(
                "Failed to query existing "
                "Google News Article URLs: "
                f"error={exc}"
            )

            # SQL 查詢失敗：
            #
            # 不阻斷 Google News Search。
            #
            # 視為目前沒有確認到
            # 已存在的 URL。
            #
            # 因此全部視為 new URLs。

            return set()

        finally:

            # --------------------------------------------------
            # Close Cursor
            # --------------------------------------------------

            if cursor is not None:

                try:

                    cursor.close()

                except Exception:

                    pass

            # --------------------------------------------------
            # Close Connection
            # --------------------------------------------------

            if conn is not None:

                try:

                    conn.close()

                except Exception:

                    pass


# ==================================================
#
# Public API
#
# ==================================================

__all__ = [
    "GoogleNewsProvider",
]