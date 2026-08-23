"""
tests/V5-2/test_search_provider.py

AutoSearch V5

V5.2 P2.1

Search Provider Interface Tests
"""


import pytest

from models.search_result import SearchResult

from search.search_provider import (
    SearchProvider,
)


# ==================================
# Default
# ==================================


def test_default_provider():

    provider = SearchProvider()

    assert provider.provider_name == ""

    assert provider.max_results == 20


# ==================================
# Search Interface
# ==================================


def test_search_not_implemented():

    provider = SearchProvider()

    with pytest.raises(
        NotImplementedError
    ):

        provider.search(
            "semiconductor"
        )


# ==================================
# Validate Results
# ==================================


def test_validate_results_empty():

    assert (
        SearchProvider.validate_results([])
        is True
    )


def test_validate_results():

    results = [

        SearchResult(
            keyword="semiconductor",
            title="Test",
            url="https://example.com",
            search_source="google",
            rank=1,
        )

    ]

    assert (
        SearchProvider.validate_results(
            results
        )
        is True
    )


def test_validate_results_invalid_item():

    results = [
        "invalid"
    ]

    assert (
        SearchProvider.validate_results(
            results
        )
        is False
    )


def test_validate_results_invalid_type():

    assert (
        SearchProvider.validate_results(
            None
        )
        is False
    )


def test_validate_results_non_list():

    assert (
        SearchProvider.validate_results(
            SearchResult()
        )
        is False
    )


# ==================================
# Custom Provider
# ==================================


class DummySearchProvider(
    SearchProvider
):

    provider_name = "dummy"

    def search(
        self,
        keyword,
        max_results=None,
    ):

        if max_results is None:

            max_results = self.max_results

        return [

            SearchResult(
                keyword=keyword,
                title="Dummy Result",
                url="https://example.com",
                search_source=self.provider_name,
                rank=1,
            )

        ][:max_results]


def test_custom_provider():

    provider = DummySearchProvider()

    results = provider.search(
        "AI",
        max_results=10,
    )

    assert len(results) == 1

    assert isinstance(
        results[0],
        SearchResult,
    )

    assert results[0].keyword == "AI"

    assert (
        results[0].search_source
        == "dummy"
    )


def test_custom_provider_name():

    provider = DummySearchProvider()

    assert (
        provider.provider_name
        == "dummy"
    )


def test_custom_provider_limit():

    provider = DummySearchProvider()

    results = provider.search(
        "AI",
        max_results=0,
    )

    assert results == []