"""
tests/V5-2/test_search_result_normalization.py

AutoSearch V5

V5.2 P2.5

SearchResult Normalization Tests

測試：

    - Google Search Provider → SearchResult
    - Google News Provider → SearchResult
    - Keyword Normalization
    - Search Source Normalization
    - Title Normalization
    - URL Normalization
    - Source Normalization
    - Rank Normalization
    - Result Limit
    - SearchResult Validation
    - SearchResult Dictionary
"""


from models.search_result import (
    SearchResult,
)

from search.google_search_provider import (
    GoogleSearchProvider,
)

from search.google_news_provider import (
    GoogleNewsProvider,
)


# ==================================
# Google Search
# ==================================


def test_google_search_result_type(
    monkeypatch,
):
    """
    Google Search Provider
    必須回傳 SearchResult。
    """

    def fake_search(
        keyword,
        max_results=10,
    ):

        return [

            SearchResult(
                keyword=keyword,
                title="Google Result",
                url="https://example.com/google",
                source="example.com",
                search_source="google_search",
                rank=1,
            ),

        ]



    provider = GoogleSearchProvider(
        api_key="test-key",
        search_engine_id="test-engine",
    )

    # 直接測試 Provider 的
    # SearchResult normalization。
    #
    # 如果實際 API 尚未接 mock，
    # 使用假的 requests response。

    class FakeResponse:

        def raise_for_status(self):
            pass

        def json(self):

            return {
                "items": [
                    {
                        "title": "Google Result",
                        "link": "https://example.com/google",
                        "displayLink": "example.com",
                        "snippet": "Test",
                    }
                ]
            }

    def fake_get(
        *args,
        **kwargs,
    ):

        return FakeResponse()

    monkeypatch.setattr(
        "search.google_search_provider.requests.get",
        fake_get,
    )

    results = provider.search(
        "test keyword",
        max_results=10,
    )

    assert len(results) == 1

    assert isinstance(
        results[0],
        SearchResult,
    )


# ==================================
# Google Search Fields
# ==================================


def test_google_search_normalization(
    monkeypatch,
):

    class FakeResponse:

        def raise_for_status(self):
            pass

        def json(self):

            return {
                "items": [
                    {
                        "title": "Google Result",
                        "link": "https://example.com/google",
                        "displayLink": "example.com",
                        "snippet": "Test",
                    }
                ]
            }

    monkeypatch.setattr(
        "search.google_search_provider.requests.get",
        lambda *args, **kwargs: FakeResponse(),
    )

    provider = GoogleSearchProvider(
        api_key="test-key",
        search_engine_id="test-engine",
    )

    results = provider.search(
        "  semiconductor  ",
        max_results=10,
    )

    result = results[0]

    assert result.keyword == "semiconductor"

    assert result.title == "Google Result"

    assert (
        result.url
        == "https://example.com/google"
    )

    assert result.source == "example.com"

    assert (
        result.search_source
        == "google_search"
    )

    assert result.rank == 1


# ==================================
# Google News
# ==================================


def test_google_news_result_type(
    monkeypatch,
):

    def fake_google_news_search(
        keyword,
        max_results=10,
    ):

        return [

            SearchResult(
                keyword=keyword,
                title="News Result",
                url="https://example.com/news",
                source="Example News",
                search_source="google_news",
                rank=1,
            ),

        ]

    monkeypatch.setattr(
        "search.google_news_provider.google_news_search",
        fake_google_news_search,
    )

    provider = GoogleNewsProvider()

    results = provider.search(
        "test keyword",
        max_results=10,
    )

    assert len(results) == 1

    assert isinstance(
        results[0],
        SearchResult,
    )


# ==================================
# Google News Normalization
# ==================================


def test_google_news_normalization(
    monkeypatch,
):

    def fake_google_news_search(
        keyword,
        max_results=10,
    ):

        return [

            SearchResult(
                keyword="old keyword",
                title="News Result",
                url="https://example.com/news",
                source="Example News",
                search_source="old_source",
                rank=99,
            ),

        ]

    monkeypatch.setattr(
        "search.google_news_provider.google_news_search",
        fake_google_news_search,
    )

    provider = GoogleNewsProvider()

    results = provider.search(
        "  semiconductor  ",
        max_results=10,
    )

    result = results[0]

    assert result.keyword == "semiconductor"

    assert result.title == "News Result"

    assert (
        result.url
        == "https://example.com/news"
    )

    assert result.source == "Example News"

    assert (
        result.search_source
        == "google_news"
    )

    assert result.rank == 1


# ==================================
# Rank Normalization
# ==================================


def test_google_news_rank_normalization(
    monkeypatch,
):

    def fake_google_news_search(
        keyword,
        max_results=10,
    ):

        return [

            SearchResult(
                keyword=keyword,
                title="Result 1",
                url="https://example.com/1",
                rank=10,
            ),

            SearchResult(
                keyword=keyword,
                title="Result 2",
                url="https://example.com/2",
                rank=20,
            ),

            SearchResult(
                keyword=keyword,
                title="Result 3",
                url="https://example.com/3",
                rank=30,
            ),

        ]

    monkeypatch.setattr(
        "search.google_news_provider.google_news_search",
        fake_google_news_search,
    )

    provider = GoogleNewsProvider()

    results = provider.search(
        "test",
        max_results=3,
    )

    assert results[0].rank == 1

    assert results[1].rank == 2

    assert results[2].rank == 3


# ==================================
# Result Limit
# ==================================


def test_google_news_result_limit(
    monkeypatch,
):

    def fake_google_news_search(
        keyword,
        max_results=10,
    ):

        return [

            SearchResult(
                keyword=keyword,
                title=f"Result {i}",
                url=f"https://example.com/{i}",
                rank=i,
            )

            for i in range(1, 11)

        ]

    monkeypatch.setattr(
        "search.google_news_provider.google_news_search",
        fake_google_news_search,
    )

    provider = GoogleNewsProvider()

    results = provider.search(
        "test",
        max_results=3,
    )

    assert len(results) == 3


# ==================================
# SearchResult Validation
# ==================================


def test_search_result_validation(
    monkeypatch,
):

    def fake_google_news_search(
        keyword,
        max_results=10,
    ):

        return [

            SearchResult(
                keyword=keyword,
                title="Valid",
                url="https://example.com/valid",
                search_source="google_news",
                rank=1,
            ),

        ]

    monkeypatch.setattr(
        "search.google_news_provider.google_news_search",
        fake_google_news_search,
    )

    provider = GoogleNewsProvider()

    results = provider.search(
        "test",
    )

    assert provider.validate_results(
        results
    ) is True


# ==================================
# SearchResult Dictionary
# ==================================


def test_search_result_to_dict(
    monkeypatch,
):

    def fake_google_news_search(
        keyword,
        max_results=10,
    ):

        return [

            SearchResult(
                keyword=keyword,
                title="Test",
                url="https://example.com/test",
                source="Example",
                search_source="google_news",
                rank=1,
            ),

        ]

    monkeypatch.setattr(
        "search.google_news_provider.google_news_search",
        fake_google_news_search,
    )

    provider = GoogleNewsProvider()

    results = provider.search(
        "test",
    )

    data = results[0].to_dict()

    assert data["keyword"] == "test"

    assert data["title"] == "Test"

    assert (
        data["url"]
        == "https://example.com/test"
    )

    assert data["source"] == "Example"

    assert (
        data["search_source"]
        == "google_news"
    )

    assert data["rank"] == 1