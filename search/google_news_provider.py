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
    SearchResult[]
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
        - Result Limit

本模組只負責：

    - Google News Provider
    - Provider Identity
    - Keyword Validation
    - Result Limit
    - 呼叫 V4 Google News Search
    - SearchResult Validation
    - SearchResult Normalization

本模組不負責：

    - ProviderSearchAdapter 建立
    - SearchAdapter
    - SearchAdapterManager
    - SearchExecutionBridge
    - URL Deduplication
    - Crawler
    - Parser
    - Article
    - Archive
    - AI
    - Database
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

    Provider 只負責：

        keyword
            ↓
        V4 Google News Search
            ↓
        SearchResult[]
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
            V4 search_engine.search()
                ↓
            SearchResult[]
                ↓
            Validate / Normalize
                ↓
            SearchResult[]

        Parameters
        ----------
        keyword :
            Search Keyword。

        max_results :
            最大搜尋結果數量。

            None：
                使用 Provider max_results。

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
        # V4 Google News Search
        #
        # ==================================================

        source_results = (
            google_news_search(
                keyword,
                max_results=max_results,
            )
        )

        # ==================================================
        #
        # Normalize Results
        #
        # ==================================================

        return self._normalize_results(
            source_results,
            keyword,
            max_results,
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

        return value

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
    ):
        """
        Validate / Normalize V4 Search Results。

        本方法不重新建立 SearchResult。

        只處理：

            - None
            - list validation
            - SearchResult validation
            - URL validation
            - keyword normalization
            - search_source normalization
            - rank normalization
            - result limit

        URL Deduplication：

            由 V4 search_engine.py 負責。

        本 Provider 不重複執行 URL Deduplication。
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

            results.append(
                item
            )

            # ------------------------------------------
            # Result Limit
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
