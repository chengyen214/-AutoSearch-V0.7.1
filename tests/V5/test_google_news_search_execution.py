"""
tests/V5/test_google_news_search_execution.py

AutoSearch V5

Test:

    Google News Provider
        ↓
    ProviderSearchAdapter
        ↓
    SearchExecutionBridge
        ↓
    SearchResult[]

目前只測 Search Layer。

不測:

    Crawl
    Parser
    Article
    Archive
    AI
"""



from search.google_news_provider import (
    GoogleNewsProvider,
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



def test_google_news_search_execution():

    # ==========================================
    #
    # Google News Provider
    #
    # ==========================================

    provider = (
        GoogleNewsProvider()
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
    # ==========================================

    resolved_source = {

        "source_type":
            "search",


        "keyword":
            "TSMC",


        "provider":
            "google_news",


        "adapter":
            adapter,

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


        assert result.keyword == "TSMC"


        assert result.rank > 0



if __name__ == "__main__":

    test_google_news_search_execution()

    print(
        "Google News SearchExecution test passed"
    )