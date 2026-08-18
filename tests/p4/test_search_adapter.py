"""
tests/p4/test_search_adapter.py

AutoSearch V4

P4.1 / P4.2 Data Sources

Search Adapter + Google News Integration Test
"""


import pytest


from models.search_result import (
    SearchResult,
)


from search.search_engine import (
    search as google_news_search,
)


from search.search_adapter import (
    GoogleNewsAdapter,
    SearchAdapterManager,
    search,
    search_articles,
)


# ==================================================
#
# Test SearchResult
#
# ==================================================


def test_search_result_to_article():

    result = SearchResult(
        keyword="IC semiconductor",
        title="Test Article",
        url="https://example.com/test",
        source="Test Source",
        published=None,
        search_source="google_news",
        rank=1,
    )

    article = result.to_article()

    assert article is not None

    assert article.keyword == (
        "IC semiconductor"
    )

    assert article.title == (
        "Test Article"
    )

    assert article.url == (
        "https://example.com/test"
    )

    assert article.source == (
        "Test Source"
    )


# ==================================================
#
# P4.2 Test Google News Search Engine
#
# ==================================================


@pytest.mark.slow
def test_google_news_search_engine():

    results = google_news_search(
        "IC semiconductor",
        max_results=5,
    )

    assert isinstance(
        results,
        list,
    )

    assert len(results) <= 5

    for result in results:

        # ------------------------------------------
        # P4.2 Search Engine 必須回傳 SearchResult
        # ------------------------------------------

        assert isinstance(
            result,
            SearchResult,
        )

        # ------------------------------------------
        # Keyword
        # ------------------------------------------

        assert result.keyword == (
            "IC semiconductor"
        )

        # ------------------------------------------
        # URL
        # ------------------------------------------

        assert result.url

        # ------------------------------------------
        # Search Source
        # ------------------------------------------

        assert result.search_source == (
            "google_news"
        )

        # ------------------------------------------
        # Rank
        # ------------------------------------------

        assert result.rank >= 1


# ==================================================
#
# P4.2 Test Google News Adapter
#
# ==================================================


@pytest.mark.slow
def test_google_news_adapter():

    adapter = GoogleNewsAdapter()

    results = adapter.search(
        "IC semiconductor",
        max_results=5,
    )

    assert isinstance(
        results,
        list,
    )

    assert len(results) <= 5

    for result in results:

        assert isinstance(
            result,
            SearchResult,
        )

        assert result.keyword == (
            "IC semiconductor"
        )

        assert result.url

        assert result.search_source == (
            "google_news"
        )

        assert result.rank >= 1


# ==================================================
#
# P4.1 / P4.2
# Test Search Adapter Manager
#
# ==================================================


@pytest.mark.slow
def test_search_adapter_manager():

    manager = SearchAdapterManager()

    results = manager.search(
        "IC semiconductor"
    )

    assert isinstance(
        results,
        list,
    )

    # ------------------------------------------
    # URL 不可以重複
    # ------------------------------------------

    urls = [
        result.url
        for result in results
    ]

    assert len(urls) == len(
        set(urls)
    )

    # ------------------------------------------
    # 必須全部是 SearchResult
    # ------------------------------------------

    for result in results:

        assert isinstance(
            result,
            SearchResult,
        )

    # ------------------------------------------
    # Rank 必須重新建立
    # ------------------------------------------

    for index, result in enumerate(
        results,
        start=1,
    ):

        assert result.rank == index


# ==================================================
#
# Test SearchResult → Article
#
# ==================================================


@pytest.mark.slow
def test_search_articles():

    articles = search_articles(
        "IC semiconductor"
    )

    assert isinstance(
        articles,
        list,
    )

    for article in articles:

        assert article is not None

        assert article.keyword == (
            "IC semiconductor"
        )

        assert article.url

        assert article.title


# ==================================================
#
# Test Default Search API
#
# ==================================================


@pytest.mark.slow
def test_search():

    results = search(
        "IC semiconductor"
    )

    assert isinstance(
        results,
        list,
    )

    for article in results:

        # ------------------------------------------
        # P4 最終 API
        #
        # 必須仍回傳 Article
        # ------------------------------------------

        assert article.__class__.__name__ == (
            "Article"
        )

        assert article.url

        assert article.title