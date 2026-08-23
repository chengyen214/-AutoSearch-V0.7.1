"""
tests/V5/test_google_search_execution.py

AutoSearch V5

Test:

    Google Search Provider
        ↓
    ProviderSearchAdapter
        ↓
    SearchExecutionBridge
        ↓
    Google Custom Search API
        ↓
    SearchResult[]

目前只測 Search Layer。

測試：

    keyword + url

例如：

    keyword:
        IC semiconductor

    url:
        https://www.intel.com/

不測：

    Crawl
    Parser
    Article
    Archive
    AI
"""


from search.google_search_provider import (
    GoogleSearchProvider,
)


from search.provider_adapter import (
    ProviderSearchAdapter,
)


from services.search_execution_bridge import (
    SearchExecutionBridge,
)


from models.search_result import (
    SearchResult,
)


def test_google_search_execution():

    # ==========================================
    #
    # Google Search Provider
    #
    # ==========================================

    provider = (
        GoogleSearchProvider()
    )


    # ==========================================
    #
    # Existing Adapter
    #
    # ==========================================

    adapter = (
        ProviderSearchAdapter(
            provider=provider,
        )
    )


    # ==========================================
    #
    # Resolved Source
    #
    # 模擬 SourceResolutionBridge 結果
    #
    # URL + Keyword
    #
    # ==========================================

    resolved_source = {

        "source_type":
            "search",

        "keyword":
            "IC semiconductor",

        "provider":
            "google_search",

        "adapter":
            adapter,

        "url":
            "https://www.intel.com/",
    }


    # ==========================================
    #
    # Search Execution
    #
    # ==========================================

    bridge = (
        SearchExecutionBridge()
    )


    results = (
        bridge.execute(
            resolved_source,
            max_results=5,
        )
    )


    # ==========================================
    #
    # Validation
    #
    # ==========================================

    assert isinstance(
        results,
        list,
    )


    for result in results:

        assert isinstance(
            result,
            SearchResult,
        )


        assert result.url


        assert result.keyword == (
            "IC semiconductor"
        )


        assert result.rank > 0


        # Intel site result
        #
        # Google siteSearch 應該限制
        # 結果來自 Intel 網站。

        assert (
            "intel.com"
            in result.url.lower()
        )


if __name__ == "__main__":

    test_google_search_execution()

    print(
        "Google Search SearchExecution test passed"
    )