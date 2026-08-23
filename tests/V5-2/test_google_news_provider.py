"""
tests/V5-2/test_google_news_provider.py

AutoSearch V5

V5.2 P2.3

Google News API / Provider Tests

測試：

    - Provider Name
    - Default Result Limit
    - Constructor
    - Empty Keyword
    - None Keyword
    - Invalid Result Limit
    - Zero Result Limit
    - Negative Result Limit
    - Google News Search
    - SearchResult Validation
    - Search Source Normalization
    - Rank Normalization
"""


from unittest.mock import patch

from models.search_result import SearchResult
from search.google_news_provider import (
    GoogleNewsProvider,
)


# ==================================
# Provider Name
# ==================================


def test_provider_name():

    provider = GoogleNewsProvider()

    assert provider.provider_name == "google_news"


# ==================================
# Default Result Limit
# ==================================


def test_default_max_results():

    provider = GoogleNewsProvider()

    assert provider.max_results == 20


# ==================================
# Constructor
# ==================================


def test_constructor():

    provider = GoogleNewsProvider(
        timeout=10
    )

    assert provider.timeout == 10


# ==================================
# Empty Keyword
# ==================================


def test_empty_keyword():

    provider = GoogleNewsProvider()

    results = provider.search(
        ""
    )

    assert results == []


# ==================================
# None Keyword
# ==================================


def test_none_keyword():

    provider = GoogleNewsProvider()

    results = provider.search(
        None
    )

    assert results == []


# ==================================
# Invalid Result Limit
# ==================================


def test_invalid_max_results():

    provider = GoogleNewsProvider()

    with patch(
        "search.google_news_provider.google_news_search"
    ) as mock_search:

        mock_search.return_value = []

        results = provider.search(
            "semiconductor",
            max_results="invalid",
        )

    assert results == []

    mock_search.assert_called_once_with(
        "semiconductor",
        max_results=20,
    )


# ==================================
# Zero Result Limit
# ==================================


def test_zero_max_results():

    provider = GoogleNewsProvider()

    results = provider.search(
        "semiconductor",
        max_results=0,
    )

    assert results == []


# ==================================
# Negative Result Limit
# ==================================


def test_negative_max_results():

    provider = GoogleNewsProvider()

    results = provider.search(
        "semiconductor",
        max_results=-1,
    )

    assert results == []


# ==================================
# Google News Search
# ==================================


def test_google_news_search():

    provider = GoogleNewsProvider()

    source_results = [

        SearchResult(
            keyword="semiconductor",
            title="Article One",
            url="https://example.com/1",
            source="Example",
            published=None,
            search_source="google_news",
            rank=1,
        ),

        SearchResult(
            keyword="semiconductor",
            title="Article Two",
            url="https://example.com/2",
            source="Example",
            published=None,
            search_source="google_news",
            rank=2,
        ),

    ]

    with patch(
        "search.google_news_provider.google_news_search"
    ) as mock_search:

        mock_search.return_value = (
            source_results
        )

        results = provider.search(
            "semiconductor",
            max_results=2,
        )

    assert len(results) == 2

    assert isinstance(
        results[0],
        SearchResult,
    )

    assert isinstance(
        results[1],
        SearchResult,
    )


# ==================================
# SearchResult Validation
# ==================================


def test_search_result_validation():

    provider = GoogleNewsProvider()

    source_results = [

        SearchResult(
            keyword="AI",
            title="AI News",
            url="https://example.com/ai",
            source="Example",
            search_source="google_news",
            rank=1,
        )

    ]

    with patch(
        "search.google_news_provider.google_news_search"
    ) as mock_search:

        mock_search.return_value = (
            source_results
        )

        results = provider.search(
            "AI"
        )

    assert provider.validate_results(
        results
    ) is True


# ==================================
# Search Source Normalization
# ==================================


def test_search_source_normalization():

    provider = GoogleNewsProvider()

    source_results = [

        SearchResult(
            keyword="AI",
            title="AI News",
            url="https://example.com/ai",
            source="Example",
            search_source="wrong_source",
            rank=99,
        )

    ]

    with patch(
        "search.google_news_provider.google_news_search"
    ) as mock_search:

        mock_search.return_value = (
            source_results
        )

        results = provider.search(
            "AI"
        )

    assert results[0].search_source == (
        "google_news"
    )


# ==================================
# Rank Normalization
# ==================================


def test_rank_normalization():

    provider = GoogleNewsProvider()

    source_results = [

        SearchResult(
            keyword="AI",
            title="Article One",
            url="https://example.com/1",
            search_source="google_news",
            rank=99,
        ),

        SearchResult(
            keyword="AI",
            title="Article Two",
            url="https://example.com/2",
            search_source="google_news",
            rank=88,
        ),

    ]

    with patch(
        "search.google_news_provider.google_news_search"
    ) as mock_search:

        mock_search.return_value = (
            source_results
        )

        results = provider.search(
            "AI"
        )

    assert results[0].rank == 1

    assert results[1].rank == 2