"""
tests/V5-2/test_google_search_provider.py

AutoSearch V5

V5.2 P2.2

Google Search API Provider Tests
"""


from unittest.mock import Mock

import pytest

from models.search_result import SearchResult

from search.google_search_provider import (
    GoogleSearchProvider,
)


# ==================================
# Default
# ==================================


def test_default_provider():

    provider = GoogleSearchProvider(
        api_key="test-key",
        search_engine_id="test-engine",
    )

    assert (
        provider.provider_name
        == "google_search"
    )

    assert provider.max_results == 20


# ==================================
# Configuration
# ==================================


def test_configured():

    provider = GoogleSearchProvider(
        api_key="test-key",
        search_engine_id="test-engine",
    )

    assert provider.is_configured() is True


def test_not_configured():

    provider = GoogleSearchProvider(
        api_key=None,
        search_engine_id=None,
    )

    assert provider.is_configured() is False


# ==================================
# Keyword Validation
# ==================================


def test_empty_keyword():

    provider = GoogleSearchProvider(
        api_key="test-key",
        search_engine_id="test-engine",
    )

    assert provider.search("") == []


def test_none_keyword():

    provider = GoogleSearchProvider(
        api_key="test-key",
        search_engine_id="test-engine",
    )

    assert provider.search(None) == []


# ==================================
# Result Limit
# ==================================


def test_invalid_result_limit():

    provider = GoogleSearchProvider(
        api_key="test-key",
        search_engine_id="test-engine",
    )

    assert (
        provider.search(
            "AI",
            max_results=0,
        )
        == []
    )


# ==================================
# API Request
# ==================================


def test_search(
    monkeypatch,
):

    provider = GoogleSearchProvider(

        api_key="test-key",

        search_engine_id="test-engine",

    )

    response = Mock()

    response.raise_for_status.return_value = None

    response.json.return_value = {

        "items": [

            {
                "title": "AI Article",

                "link":
                    "https://example.com/ai",

                "snippet":
                    "AI technology",

                "displayLink":
                    "example.com",
            },

            {
                "title": "Semiconductor Article",

                "link":
                    "https://example.com/chip",

                "snippet":
                    "Semiconductor",

                "displayLink":
                    "example.com",
            },

        ]

    }

    def mock_get(
        *args,
        **kwargs,
    ):

        return response

    monkeypatch.setattr(
        "search.google_search_provider.requests.get",
        mock_get,
    )

    results = provider.search(
        "AI",
        max_results=2,
    )

    assert len(results) == 2

    assert all(
        isinstance(
            result,
            SearchResult,
        )
        for result in results
    )

    assert (
        results[0].title
        == "AI Article"
    )

    assert (
        results[0].url
        == "https://example.com/ai"
    )

    assert (
        results[0].search_source
        == "google_search"
    )

    assert results[0].rank == 1

    assert results[1].rank == 2


# ==================================
# Result Limit
# ==================================


def test_search_result_limit(
    monkeypatch,
):

    provider = GoogleSearchProvider(

        api_key="test-key",

        search_engine_id="test-engine",

    )

    response = Mock()

    response.raise_for_status.return_value = None

    response.json.return_value = {

        "items": [

            {
                "title": "Result 1",
                "link":
                    "https://example.com/1",
            },

            {
                "title": "Result 2",
                "link":
                    "https://example.com/2",
            },

            {
                "title": "Result 3",
                "link":
                    "https://example.com/3",
            },

        ]

    }

    monkeypatch.setattr(

        "search.google_search_provider.requests.get",

        lambda *args, **kwargs: response,

    )

    results = provider.search(
        "AI",
        max_results=2,
    )

    assert len(results) == 2


# ==================================
# Missing Items
# ==================================


def test_empty_api_result(
    monkeypatch,
):

    provider = GoogleSearchProvider(

        api_key="test-key",

        search_engine_id="test-engine",

    )

    response = Mock()

    response.raise_for_status.return_value = None

    response.json.return_value = {}

    monkeypatch.setattr(

        "search.google_search_provider.requests.get",

        lambda *args, **kwargs: response,

    )

    results = provider.search(
        "AI"
    )

    assert results == []


# ==================================
# API Error
# ==================================


def test_api_error(
    monkeypatch,
):

    provider = GoogleSearchProvider(

        api_key="test-key",

        search_engine_id="test-engine",

    )

    def mock_get(
        *args,
        **kwargs,
    ):

        raise RuntimeError(
            "API failed"
        )

    monkeypatch.setattr(

        "search.google_search_provider.requests.get",

        mock_get,

    )

    with pytest.raises(
        RuntimeError
    ):

        provider.search(
            "AI"
        )