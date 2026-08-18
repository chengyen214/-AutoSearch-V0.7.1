"""
search/search_adapter.py

AutoSearch V4

P4.1 / P4.2 / P4.3 / P4.4 / P4.7 Data Sources
Search Adapter

功能:

1. Google News Search Adapter
2. TSMC Search Adapter
3. Intel Newsroom Search Adapter
4. 統一 Search Adapter Interface
5. Search Source 數量控制
6. Multi-Source Search
7. URL Deduplication
8. Global Rank
9. 統一回傳 SearchResult
10. SearchResult → Article
11. P4.7 Keyword / Language Source Strategy Integration

架構:

                    SearchAdapterBase
                           │
              ┌────────────┼────────────┐
              ↓            ↓            ↓
      GoogleNewsAdapter  TSMCNewsAdapter  IntelNewsAdapter
              │            │            │
              ↓            ↓            ↓
        Google News RSS  TSMC Press    Intel Newsroom
                          Center
              │            │            │
              └────────────┼────────────┘
                           ↓
                SearchAdapterManager
                           │
                           ↓
                  KeywordStrategy
                           │
             ┌─────────────┼─────────────┐
             ↓             ↓             ↓
        google_news      tsmc          intel
           auto           zh             en
             │             │             │
             └─────────────┼─────────────┘
                           ↓
                  Multi-Source Search
                           ↓
                  URL Deduplication
                           ↓
                     Global Rank
                           ↓
                     SearchResult
                           ↓
                        Article
                           ↓
                    ArticleService
                           ↓
                   Download / Parser
                           ↓
                      Archive / AI


P4.1:

Google News
    ↓
GoogleNewsAdapter
    ↓
search_engine.py
    ↓
SearchResult


P4.2:

Google News RSS
    ↓
search_engine.py
    ↓
SearchResult
    ↓
GoogleNewsAdapter
    ↓
SearchAdapterManager


P4.3:

TSMC Press Center
    ↓
TSMCNewsAdapter
    ↓
SearchResult
    ↓
SearchAdapterManager


P4.4:

Intel Newsroom
    ↓
IntelNewsAdapter
    ↓
SearchResult
    ↓
SearchAdapterManager


P4.7:

User Keyword
    ↓
SearchAdapterManager
    ↓
KeywordStrategy
    ↓
Source-specific Keyword
    │
    ├── Google News → auto
    ├── TSMC       → zh
    └── Intel      → en
    ↓
SearchAdapter
    ↓
SearchResult


注意:

本模組不負責:

- HTML Download
- Parser
- Article Archive
- AI Analysis
- AI Worker
- Database Storage
- Keyword Translation

P4.7 第一階段:

KeywordStrategy 只負責:

- Keyword Normalize
- Source Language Identity
- Source-specific Keyword Strategy

目前不進行自動翻譯。
"""


# ==================================================
#
# Configuration
#
# ==================================================


from config.settings import (
    GOOGLE_NEWS_RESULTS,
    TSMC_RESULTS,
    INTEL_RESULTS,
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
# Search Adapter Base
#
# ==================================================


from search.search_adapter_base import (
    SearchAdapter,
)


# ==================================================
#
# Google News
#
# ==================================================


from search.search_engine import (
    search as google_news_search,
)


# ==================================================
#
# TSMC
#
# ==================================================


from search.tsmc_adapter import (
    TSMCNewsAdapter,
)


# ==================================================
#
# Intel
#
# ==================================================


from search.intel_adapter import (
    IntelNewsAdapter,
)


# ==================================================
#
# P4.7 Keyword Strategy
#
# ==================================================


from search.keyword_strategy import (
    KeywordStrategy,
)


# ==================================================
#
# Google News Adapter
#
# ==================================================


class GoogleNewsAdapter(SearchAdapter):
    """
    Google News RSS Search Adapter。

    P4.1 / P4.2

    使用:

        search/search_engine.py

    作為 Google News RSS 搜尋底層。

    search_engine.py 負責:

        - Google News RSS
        - RSS URL 建立
        - Google News URL Decode
        - RSS Parsing
        - URL Deduplication
        - SearchResult 建立
        - Result Limit

    GoogleNewsAdapter 負責:

        - SearchAdapter Interface
        - Google News Source Identity
        - SearchResult 驗證
        - Source Rank 正規化
    """

    # ==================================================
    #
    # Result Limit
    #
    # ==================================================

    max_results = GOOGLE_NEWS_RESULTS

    # ==================================================
    #
    # Search Source
    #
    # ==================================================

    search_source = "google_news"

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

        Returns
        -------

        list[SearchResult]
        """

        # ------------------------------------------
        # Result Limit
        # ------------------------------------------

        if max_results is None:

            max_results = (
                self.max_results
            )

        try:

            max_results = int(
                max_results
            )

        except (
            TypeError,
            ValueError,
        ):

            max_results = (
                self.max_results
            )

        if max_results <= 0:

            return []

        # ------------------------------------------
        # Google News Search
        # ------------------------------------------

        try:

            source_results = (
                google_news_search(
                    keyword,
                    max_results=max_results,
                )
            )

        except Exception as e:

            print(
                "Google News Adapter failed:",
                e,
            )

            return []

        # ------------------------------------------
        # Empty Result
        # ------------------------------------------

        if not source_results:

            return []

        # ------------------------------------------
        # Normalize SearchResult
        # ------------------------------------------

        results = []

        for item in source_results:

            # --------------------------------------
            # SearchResult
            # --------------------------------------

            if isinstance(
                item,
                SearchResult,
            ):

                result = item

            # --------------------------------------
            # Backward Compatibility
            #
            # 如果 search_engine.py
            # 未來又回傳 Article，
            # Adapter 可以轉換。
            # --------------------------------------

            else:

                result = SearchResult(

                    keyword=keyword,

                    title=getattr(
                        item,
                        "title",
                        "",
                    ),

                    url=getattr(
                        item,
                        "url",
                        "",
                    ),

                    source=getattr(
                        item,
                        "source",
                        "",
                    ),

                    published=getattr(
                        item,
                        "published",
                        None,
                    ),

                    search_source=(
                        self.search_source
                    ),

                    rank=len(results) + 1,
                )

            # --------------------------------------
            # URL 必須存在
            # --------------------------------------

            if not result.url:

                continue

            # --------------------------------------
            # Normalize Keyword
            # --------------------------------------

            result.keyword = keyword

            # --------------------------------------
            # Normalize Search Source
            # --------------------------------------

            result.search_source = (
                self.search_source
            )

            results.append(
                result
            )

            # --------------------------------------
            # Source Result Limit
            # --------------------------------------

            if len(results) >= max_results:

                break

        # ------------------------------------------
        # Source Rank
        # ------------------------------------------

        for rank, result in enumerate(
            results,
            start=1,
        ):

            result.rank = rank

        return results


# ==================================================
#
# TSMC Adapter
#
# ==================================================


class TSMCSearchAdapter(TSMCNewsAdapter):
    """
    TSMC Website Search Adapter。

    P4.3

    實際搜尋邏輯位於:

        search/tsmc_adapter.py

    Base:

        TSMCNewsAdapter

    Source:

        TSMC Press Center
        Latest News

    Result Limit:

        TSMC_RESULTS
    """

    # ==================================================
    #
    # Result Limit
    #
    # ==================================================

    max_results = TSMC_RESULTS

    # ==================================================
    #
    # Search Source
    #
    # ==================================================

    search_source = "tsmc"


# ==================================================
#
# Intel Adapter
#
# ==================================================


class IntelSearchAdapter(IntelNewsAdapter):
    """
    Intel Website Search Adapter。

    P4.4

    實際搜尋邏輯位於:

        search/intel_adapter.py

    Base:

        IntelNewsAdapter

    Source:

        Intel Newsroom

    Result Limit:

        INTEL_RESULTS
    """

    # ==================================================
    #
    # Result Limit
    #
    # ==================================================

    max_results = INTEL_RESULTS

    # ==================================================
    #
    # Search Source
    #
    # ==================================================

    search_source = "intel"


# ==================================================
#
# Search Adapter Manager
#
# ==================================================


class SearchAdapterManager:
    """
    Search Adapter Manager。

    P4.1 / P4.2 / P4.3 / P4.4 / P4.7

    統一管理多個 Search Source。

    Current Sources:

        Google News = GOOGLE_NEWS_RESULTS

        TSMC = TSMC_RESULTS

        Intel = INTEL_RESULTS

    Keyword Strategy:

        Google News = auto

        TSMC = zh

        Intel = en

    Manager 負責:

        1. Multi-Source Search
        2. Keyword Strategy
        3. URL Deduplication
        4. Global Rank

    Adapter 負責:

        1. Source Search
        2. Source Result Limit
        3. Source Rank
        4. SearchResult

    KeywordStrategy 負責:

        1. Keyword Normalize
        2. Source Language Identity
        3. Source-specific Keyword Strategy
    """

    def __init__(
        self,
        adapters=None,
        keyword_strategy=None,
    ):
        """
        Parameters
        ----------

        adapters:
            Search Adapter List

        keyword_strategy:
            Keyword / Language Strategy

        若未指定:

            GoogleNewsAdapter
            TSMCSearchAdapter
            IntelSearchAdapter

            +
            
            KeywordStrategy
        """

        # ==================================================
        #
        # Default Adapters
        #
        # ==================================================

        if adapters is None:

            adapters = [

                GoogleNewsAdapter(),

                TSMCSearchAdapter(),

                IntelSearchAdapter(),

            ]

        self.adapters = adapters

        # ==================================================
        #
        # Keyword Strategy
        #
        # ==================================================

        if keyword_strategy is None:

            keyword_strategy = (
                KeywordStrategy()
            )

        self.keyword_strategy = (
            keyword_strategy
        )

    # ==================================================
    #
    # Search
    #
    # ==================================================

    def search(
        self,
        keyword,
    ):
        """
        執行 Multi-Source Search。

        P4.7 Integration Pipeline:

            User Keyword
                ↓
            KeywordStrategy
                ↓
            Source Keyword
                │
                ├───────────────┐
                ↓               ↓
             Google           TSMC
                │               │
                ↓               ↓
             Intel         Source Adapter
                │               │
                └───────┬───────┘
                        ↓
                  Merge Results
                        ↓
                URL Deduplication
                        ↓
                   Global Rank
                        ↓
                  SearchResult

        理論最大:

            Google News = 40
            TSMC        = 20
            Intel       = 20

            Total = 80

        注意:

            80 是理論最大值。

            實際結果數量取決於
            各 Search Source 實際搜尋結果。
        """

        results = []

        # ==================================================
        #
        # Search Every Adapter
        #
        # ==================================================

        for adapter in self.adapters:

            try:

                # ------------------------------------------
                # Adapter Result Limit
                # ------------------------------------------

                max_results = getattr(
                    adapter,
                    "max_results",
                    10,
                )

                # ------------------------------------------
                # Search Source
                # ------------------------------------------

                search_source = getattr(
                    adapter,
                    "search_source",
                    "",
                )

                # ==================================================
                #
                # P4.7 Keyword Strategy
                #
                # ==================================================

                source_keyword = (
                    self.keyword_strategy.get_keyword(
                        keyword,
                        search_source,
                    )
                )

                # ------------------------------------------
                # Empty Keyword
                # ------------------------------------------

                if not source_keyword:

                    continue

                # ==================================================
                #
                # Execute Source Search
                #
                # ==================================================

                source_results = (
                    adapter.search(
                        source_keyword,
                        max_results=max_results,
                    )
                )

                # ------------------------------------------
                # Empty Result
                # ------------------------------------------

                if not source_results:

                    continue

                # ------------------------------------------
                # Validate Results
                # ------------------------------------------

                for result in source_results:

                    if not isinstance(
                        result,
                        SearchResult,
                    ):

                        continue

                    if not result.url:

                        continue

                    # --------------------------------------
                    # Normalize Keyword
                    #
                    # 保留 Source Strategy 最終 Keyword
                    # --------------------------------------

                    result.keyword = (
                        source_keyword
                    )

                    # --------------------------------------
                    # Normalize Search Source
                    # --------------------------------------

                    if not result.search_source:

                        result.search_source = (
                            search_source
                        )

                    results.append(
                        result
                    )

            except Exception as e:

                print(
                    "Search Adapter failed:",
                    adapter.__class__.__name__,
                    e,
                )

        # ==================================================
        #
        # URL Deduplication
        #
        # ==================================================

        unique_results = []

        url_set = set()

        for result in results:

            url = getattr(
                result,
                "url",
                "",
            )

            # ------------------------------------------
            # Empty URL
            # ------------------------------------------

            if not url:

                continue

            # ------------------------------------------
            # Duplicate URL
            # ------------------------------------------

            if url in url_set:

                continue

            url_set.add(
                url
            )

            unique_results.append(
                result
            )

        # ==================================================
        #
        # Global Rank
        #
        # ==================================================

        for rank, result in enumerate(
            unique_results,
            start=1,
        ):

            result.rank = rank

        return unique_results


# ==================================================
#
# Search Result → Article
#
# ==================================================


def search_articles(
    keyword,
):
    """
    執行 Multi-Source Search。

    Search Flow:

        Search Source
            ↓
        SearchAdapter
            ↓
        KeywordStrategy
            ↓
        SearchResult
            ↓
        SearchResult.to_article()
            ↓
        Article

    Returns
    -------

    list[Article]

    注意:

        SearchAdapterManager
        標準回傳 SearchResult。

        此函式負責將 SearchResult
        轉換成 Article，
        保持既有 ArticleService
        Pipeline 相容。
    """

    manager = (
        SearchAdapterManager()
    )

    results = (
        manager.search(
            keyword
        )
    )

    # ==================================================
    #
    # SearchResult → Article
    #
    # ==================================================

    articles = []

    for result in results:

        article = (
            result.to_article()
        )

        articles.append(
            article
        )

    return articles


# ==================================================
#
# Default Search API
#
# ==================================================


def search(
    keyword,
):
    """
    P4 統一 Search API。

    ArticleService 應使用:

        search(keyword)

    不應直接依賴:

        search_engine.search()

    Returns
    -------

    list[Article]

    Pipeline:

        Search Source
            ↓
        SearchAdapter
            ↓
        KeywordStrategy
            ↓
        SearchResult
            ↓
        Article
            ↓
        ArticleService
            ↓
        Download
            ↓
        Parser
            ↓
        Archive
            ↓
        AI Task
    """

    return search_articles(
        keyword
    )


# ==================================================
#
# Export
#
# ==================================================


__all__ = [
    "SearchAdapter",
    "GoogleNewsAdapter",
    "TSMCSearchAdapter",
    "IntelSearchAdapter",
    "SearchAdapterManager",
    "search",
    "search_articles",
]
