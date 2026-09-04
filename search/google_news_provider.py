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
    60 Candidate SearchResult[]
        ↓
    Target crawler_url Exclusion
        ↓
    20 Valid SearchResult[]
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
    - Target Source Exclusion
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
        60 Candidate Results
            ↓
        排除所有 Target Source
            ↓
        20 Valid Results
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

    max_results = 20

    # ==================================================
    #
    # Candidate Result Limit
    #
    # ==================================================

    candidate_results = 60

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

        注意：

            真正 RSS Request Timeout
            尚未由本 Provider 注入
            V4 search_engine.py。
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
            targets
                ↓
            取得全部 crawler_url
                ↓
            V4 search_engine.search()
                ↓
            60 Candidate Results
                ↓
            排除所有 Target Source
                ↓
            Validate / Normalize
                ↓
            最多 20 Valid Results

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

        Returns
        -------
        list[SearchResult]
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
        # V4 Google News Search
        #
        # 先取得 60 筆候選結果。
        #
        # ==================================================

        source_results = (
            google_news_search(
                keyword,
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

            20
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
            - 所有 Target crawler_url exclusion
            - keyword normalization
            - search_source normalization
            - rank normalization
            - result limit

        流程：

            60 Candidate Results
                    ↓
            ALL Target crawler_url exclusion
                    ↓
            Valid Results
                    ↓
            最多 20 筆

        URL Deduplication：

            V4 search_engine.py
            已經負責 URL Deduplication。

            Provider 不重新實作
            V4 Search Engine 的 Deduplication。
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

        results = []

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
            # Target crawler_url Exclusion
            #
            # 只要符合任何一個 Target crawler_url
            # 就排除。
            #
            # 注意：
            #
            # crawler_urls 來自：
            #
            #     targets
            #
            # 的全部 crawler_url。
            #
            # 不限制 keyword。
            #
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

            # ------------------------------------------
            # Normalize URL
            # ------------------------------------------

            try:

                item.url = url

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
                    len(results) + 1
                )

            except AttributeError:

                pass

            # ------------------------------------------
            # Append Valid Result
            # ------------------------------------------

            results.append(
                item
            )

            # ------------------------------------------
            # Result Limit
            #
            # 最多回傳 20 筆。
            #
            # ------------------------------------------

            if len(results) >= max_results:

                break

        return results


# ==================================================
#
# Public API
#
# ==================================================

__all__ = [
    "GoogleNewsProvider",
]