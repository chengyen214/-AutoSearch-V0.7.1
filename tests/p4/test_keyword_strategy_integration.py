"""
tests/p4/test_keyword_strategy_integration.py

AutoSearch V4

P4.7 Keyword / Language Source Strategy Integration Tests

測試:

1. SearchAdapterManager 正確建立 KeywordStrategy
2. KeywordStrategy 正確整合至 SearchAdapterManager
3. Google News 使用 auto strategy
4. TSMC 使用 zh strategy
5. Intel 使用 en strategy
6. Keyword Normalize
7. Source-specific Keyword
8. Adapter 實際收到 Strategy 處理後的 keyword
9. SearchResult 正常回傳
10. URL Deduplication 正常
11. Global Rank 正常
12. Custom KeywordStrategy Injection
13. Unknown Source 使用 auto strategy

注意:

本測試不進行真實 HTTP Search。

使用 Mock Adapter 驗證:

    SearchAdapterManager
        ↓
    KeywordStrategy
        ↓
    Adapter
        ↓
    SearchResult
"""


import pytest


from models.search_result import (
    SearchResult,
)


from search.search_adapter import (
    SearchAdapterManager,
)


from search.search_adapter_base import (
    SearchAdapter,
)


from search.keyword_strategy import (
    KeywordStrategy,
    SourceLanguage,
)


# ==================================================
#
# Mock Adapter
#
# ==================================================


class MockSearchAdapter(SearchAdapter):
    """
    測試用 Search Adapter。

    用來確認 SearchAdapterManager
    是否真的把 KeywordStrategy
    處理後的 keyword 傳入 Adapter。
    """

    def __init__(
        self,
        search_source,
        max_results=5,
        results=None,
    ):

        self.search_source = (
            search_source
        )

        self.max_results = (
            max_results
        )

        self.results = (
            results or []
        )

        self.received_keywords = []

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

        self.received_keywords.append(
            keyword
        )

        results = []

        limit = (
            max_results
            if max_results is not None
            else self.max_results
        )

        for item in self.results[:limit]:

            results.append(
                SearchResult(

                    keyword=keyword,

                    title=item.get(
                        "title",
                        "",
                    ),

                    url=item.get(
                        "url",
                        "",
                    ),

                    source=item.get(
                        "source",
                        self.search_source,
                    ),

                    published=item.get(
                        "published",
                        None,
                    ),

                    search_source=(
                        self.search_source
                    ),

                    rank=len(results) + 1,
                )
            )

        return results


# ==================================================
#
# Test Helper
#
# ==================================================


def create_result(
    url,
    title="Test Article",
    source="Test Source",
):
    """
    建立測試 Search Result Data。
    """

    return {
        "url": url,
        "title": title,
        "source": source,
    }


# ==================================================
#
# P4.7 Manager Initialization
#
# ==================================================


def test_manager_creates_default_keyword_strategy():
    """
    SearchAdapterManager
    應自動建立 KeywordStrategy。
    """

    manager = (
        SearchAdapterManager(
            adapters=[]
        )
    )

    assert manager.keyword_strategy is not None

    assert isinstance(
        manager.keyword_strategy,
        KeywordStrategy,
    )


# ==================================================
#
# P4.7 Source Language
#
# ==================================================


def test_google_news_uses_auto_strategy():
    """
    Google News:

        language = auto
    """

    strategy = KeywordStrategy()

    assert (
        strategy.get_language(
            "google_news"
        )
        == SourceLanguage.AUTO
    )


def test_tsmc_uses_zh_strategy():
    """
    TSMC:

        language = zh
    """

    strategy = KeywordStrategy()

    assert (
        strategy.get_language(
            "tsmc"
        )
        == SourceLanguage.ZH
    )


def test_intel_uses_en_strategy():
    """
    Intel:

        language = en
    """

    strategy = KeywordStrategy()

    assert (
        strategy.get_language(
            "intel"
        )
        == SourceLanguage.EN
    )


# ==================================================
#
# P4.7 Keyword Normalize Integration
#
# ==================================================


def test_manager_normalizes_keyword_before_search():
    """
    Manager 應透過 KeywordStrategy
    將 keyword normalize 後
    再傳給 Adapter。
    """

    adapter = MockSearchAdapter(
        search_source="google_news",
        results=[
            create_result(
                "https://example.com/1"
            )
        ],
    )

    manager = SearchAdapterManager(
        adapters=[adapter]
    )

    results = manager.search(
        "   IC    semiconductor   "
    )

    assert (
        adapter.received_keywords
        == [
            "IC semiconductor"
        ]
    )

    assert len(results) == 1

    assert (
        results[0].keyword
        == "IC semiconductor"
    )


# ==================================================
#
# P4.7 Google Integration
#
# ==================================================


def test_google_news_keyword_strategy_integration():
    """
    Google News:

        Source = google_news
        Language = auto
        Keyword = normalized keyword
    """

    adapter = MockSearchAdapter(
        search_source="google_news",
        results=[
            create_result(
                "https://example.com/google"
            )
        ],
    )

    manager = SearchAdapterManager(
        adapters=[adapter]
    )

    results = manager.search(
        "  AI    semiconductor  "
    )

    assert (
        adapter.received_keywords
        == [
            "AI semiconductor"
        ]
    )

    assert len(results) == 1

    assert (
        results[0].search_source
        == "google_news"
    )

    assert (
        results[0].keyword
        == "AI semiconductor"
    )


# ==================================================
#
# P4.7 TSMC Integration
#
# ==================================================


def test_tsmc_keyword_strategy_integration():
    """
    TSMC:

        Source = tsmc
        Language = zh
        Keyword = normalized keyword

    第一階段不翻譯 keyword。
    """

    adapter = MockSearchAdapter(
        search_source="tsmc",
        results=[
            create_result(
                "https://example.com/tsmc"
            )
        ],
    )

    manager = SearchAdapterManager(
        adapters=[adapter]
    )

    results = manager.search(
        "  台積電    semiconductor  "
    )

    assert (
        adapter.received_keywords
        == [
            "台積電 semiconductor"
        ]
    )

    assert len(results) == 1

    assert (
        results[0].search_source
        == "tsmc"
    )

    assert (
        results[0].keyword
        == "台積電 semiconductor"
    )


# ==================================================
#
# P4.7 Intel Integration
#
# ==================================================


def test_intel_keyword_strategy_integration():
    """
    Intel:

        Source = intel
        Language = en
        Keyword = normalized keyword

    第一階段不翻譯 keyword。
    """

    adapter = MockSearchAdapter(
        search_source="intel",
        results=[
            create_result(
                "https://example.com/intel"
            )
        ],
    )

    manager = SearchAdapterManager(
        adapters=[adapter]
    )

    results = manager.search(
        "  AI    semiconductor  "
    )

    assert (
        adapter.received_keywords
        == [
            "AI semiconductor"
        ]
    )

    assert len(results) == 1

    assert (
        results[0].search_source
        == "intel"
    )

    assert (
        results[0].keyword
        == "AI semiconductor"
    )


# ==================================================
#
# P4.7 Multi-Source Integration
#
# ==================================================


def test_multi_source_keyword_strategy_integration():
    """
    三個 Source 同時搜尋。

    確認每個 Adapter
    都收到 normalize 後的 keyword。
    """

    google_adapter = MockSearchAdapter(
        search_source="google_news",
        results=[
            create_result(
                "https://example.com/google"
            )
        ],
    )

    tsmc_adapter = MockSearchAdapter(
        search_source="tsmc",
        results=[
            create_result(
                "https://example.com/tsmc"
            )
        ],
    )

    intel_adapter = MockSearchAdapter(
        search_source="intel",
        results=[
            create_result(
                "https://example.com/intel"
            )
        ],
    )

    manager = SearchAdapterManager(
        adapters=[
            google_adapter,
            tsmc_adapter,
            intel_adapter,
        ]
    )

    results = manager.search(
        "   IC     semiconductor   "
    )

    # ------------------------------------------
    # Every Source receives normalized keyword
    # ------------------------------------------

    assert (
        google_adapter.received_keywords
        == [
            "IC semiconductor"
        ]
    )

    assert (
        tsmc_adapter.received_keywords
        == [
            "IC semiconductor"
        ]
    )

    assert (
        intel_adapter.received_keywords
        == [
            "IC semiconductor"
        ]
    )

    # ------------------------------------------
    # Result Count
    # ------------------------------------------

    assert len(results) == 3


# ==================================================
#
# P4.7 SearchResult Preservation
#
# ==================================================


def test_keyword_strategy_does_not_break_search_result():
    """
    KeywordStrategy 整合後，
    SearchResult 結構仍然正常。
    """

    adapter = MockSearchAdapter(
        search_source="intel",
        results=[
            create_result(
                "https://example.com/article",
                title="Intel Article",
                source="Intel",
            )
        ],
    )

    manager = SearchAdapterManager(
        adapters=[adapter]
    )

    results = manager.search(
        "  Intel   AI  "
    )

    assert len(results) == 1

    result = results[0]

    assert isinstance(
        result,
        SearchResult,
    )

    assert (
        result.title
        == "Intel Article"
    )

    assert (
        result.url
        == "https://example.com/article"
    )

    assert (
        result.source
        == "Intel"
    )

    assert (
        result.search_source
        == "intel"
    )

    assert (
        result.keyword
        == "Intel AI"
    )


# ==================================================
#
# P4.7 URL Deduplication
#
# ==================================================


def test_keyword_strategy_does_not_break_url_deduplication():
    """
    Strategy 整合後，
    URL Deduplication 仍然正常。
    """

    adapter_1 = MockSearchAdapter(
        search_source="google_news",
        results=[
            create_result(
                "https://example.com/same"
            ),
            create_result(
                "https://example.com/google-only"
            ),
        ],
    )

    adapter_2 = MockSearchAdapter(
        search_source="tsmc",
        results=[
            create_result(
                "https://example.com/same"
            ),
            create_result(
                "https://example.com/tsmc-only"
            ),
        ],
    )

    manager = SearchAdapterManager(
        adapters=[
            adapter_1,
            adapter_2,
        ]
    )

    results = manager.search(
        "  semiconductor   "
    )

    urls = [
        result.url
        for result in results
    ]

    assert len(results) == 3

    assert (
        "https://example.com/same"
        in urls
    )

    assert (
        urls.count(
            "https://example.com/same"
        )
        == 1
    )


# ==================================================
#
# P4.7 Global Rank
#
# ==================================================


def test_keyword_strategy_does_not_break_global_rank():
    """
    Strategy 整合後，
    Global Rank 應重新從 1 開始。
    """

    adapter = MockSearchAdapter(
        search_source="google_news",
        results=[
            create_result(
                "https://example.com/1"
            ),
            create_result(
                "https://example.com/2"
            ),
            create_result(
                "https://example.com/3"
            ),
        ],
    )

    manager = SearchAdapterManager(
        adapters=[adapter]
    )

    results = manager.search(
        "  semiconductor  "
    )

    ranks = [
        result.rank
        for result in results
    ]

    assert ranks == [
        1,
        2,
        3,
    ]


# ==================================================
#
# P4.7 Custom Strategy Injection
#
# ==================================================


class RecordingKeywordStrategy:
    """
    測試用自訂 KeywordStrategy。

    用來確認 Manager
    真的使用注入的 Strategy。
    """

    def __init__(self):

        self.calls = []

    def get_keyword(
        self,
        keyword,
        search_source,
    ):

        self.calls.append(
            (
                keyword,
                search_source,
            )
        )

        return (
            f"{keyword}|{search_source}"
        )


def test_manager_accepts_custom_keyword_strategy():
    """
    SearchAdapterManager
    應支援注入自訂 Strategy。
    """

    strategy = (
        RecordingKeywordStrategy()
    )

    adapter = MockSearchAdapter(
        search_source="intel",
        results=[
            create_result(
                "https://example.com/intel"
            )
        ],
    )

    manager = SearchAdapterManager(
        adapters=[adapter],
        keyword_strategy=strategy,
    )

    results = manager.search(
        "AI semiconductor"
    )

    assert (
        strategy.calls
        == [
            (
                "AI semiconductor",
                "intel",
            )
        ]
    )

    assert (
        adapter.received_keywords
        == [
            "AI semiconductor|intel"
        ]
    )

    assert len(results) == 1


# ==================================================
#
# P4.7 Unknown Source
#
# ==================================================


def test_unknown_source_uses_auto_strategy():
    """
    未知 Search Source:

        language = auto
    """

    strategy = KeywordStrategy()

    assert (
        strategy.get_language(
            "unknown_source"
        )
        == SourceLanguage.AUTO
    )


def test_unknown_source_keyword_is_normalized():
    """
    未知 Source 仍然使用
    normalize keyword。
    """

    strategy = KeywordStrategy()

    keyword = (
        strategy.get_keyword(
            "  IC    semiconductor  ",
            "unknown_source",
        )
    )

    assert (
        keyword
        == "IC semiconductor"
    )


# ==================================================
#
# P4.7 Empty Keyword
#
# ==================================================


def test_empty_keyword_does_not_call_adapter():
    """
    Empty Keyword 不應執行 Search。
    """

    adapter = MockSearchAdapter(
        search_source="google_news",
        results=[
            create_result(
                "https://example.com/article"
            )
        ],
    )

    manager = SearchAdapterManager(
        adapters=[adapter]
    )

    results = manager.search(
        "     "
    )

    assert results == []

    assert (
        adapter.received_keywords
        == []
    )


# ==================================================
#
# P4.7 Keyword Strategy Source Separation
#
# ==================================================


def test_each_source_gets_independent_strategy_call():
    """
    每一個 Search Source
    都應獨立呼叫 KeywordStrategy。
    """

    strategy = (
        RecordingKeywordStrategy()
    )

    google_adapter = MockSearchAdapter(
        search_source="google_news",
        results=[
            create_result(
                "https://example.com/google"
            )
        ],
    )

    tsmc_adapter = MockSearchAdapter(
        search_source="tsmc",
        results=[
            create_result(
                "https://example.com/tsmc"
            )
        ],
    )

    intel_adapter = MockSearchAdapter(
        search_source="intel",
        results=[
            create_result(
                "https://example.com/intel"
            )
        ],
    )

    manager = SearchAdapterManager(
        adapters=[
            google_adapter,
            tsmc_adapter,
            intel_adapter,
        ],
        keyword_strategy=strategy,
    )

    manager.search(
        "IC semiconductor"
    )

    assert strategy.calls == [
        (
            "IC semiconductor",
            "google_news",
        ),
        (
            "IC semiconductor",
            "tsmc",
        ),
        (
            "IC semiconductor",
            "intel",
        ),
    ]
