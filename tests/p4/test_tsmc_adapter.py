"""
tests/p4/test_tsmc_adapter.py

AutoSearch V4

P4.3 TSMC Website Search Source

測試:

1. TSMCNewsAdapter 建立
2. SearchResult 型別
3. search_source
4. TSMC URL
5. Keyword Matching
6. Result Limit
7. URL Deduplication
8. 實際 TSMC 搜尋
"""


from search.tsmc_adapter import (
    TSMCNewsAdapter,
)

from models.search_result import (
    SearchResult,
)


# ==================================================
#
# Adapter Creation
#
# ==================================================


def test_tsmc_adapter_creation():

    adapter = TSMCNewsAdapter()

    assert adapter is not None


# ==================================================
#
# Search Source
#
# ==================================================


def test_tsmc_search_source():

    adapter = TSMCNewsAdapter()

    assert adapter.search_source == "tsmc"


# ==================================================
#
# Result Limit
#
# ==================================================


def test_tsmc_result_limit():

    adapter = TSMCNewsAdapter()

    results = adapter.search(
        "TSMC",
        max_results=2,
    )

    assert len(results) <= 2


# ==================================================
#
# SearchResult
#
# ==================================================


def test_tsmc_search_result_type():

    adapter = TSMCNewsAdapter()

    results = adapter.search(
        "TSMC",
        max_results=5,
    )

    for result in results:

        assert isinstance(
            result,
            SearchResult,
        )


# ==================================================
#
# TSMC URL
#
# ==================================================


def test_tsmc_url():

    adapter = TSMCNewsAdapter()

    results = adapter.search(
        "TSMC",
        max_results=5,
    )

    for result in results:

        assert result.url.startswith(
            "https://pr.tsmc.com/"
        )


# ==================================================
#
# Search Source Normalization
#
# ==================================================


def test_tsmc_result_source():

    adapter = TSMCNewsAdapter()

    results = adapter.search(
        "TSMC",
        max_results=5,
    )

    for result in results:

        assert result.search_source == "tsmc"


# ==================================================
#
# Keyword
#
# ==================================================


def test_tsmc_keyword():

    adapter = TSMCNewsAdapter()

    keyword = "TSMC"

    results = adapter.search(
        keyword,
        max_results=5,
    )

    for result in results:

        assert result.keyword == keyword


# ==================================================
#
# Rank
#
# ==================================================


def test_tsmc_rank():

    adapter = TSMCNewsAdapter()

    results = adapter.search(
        "TSMC",
        max_results=5,
    )

    for index, result in enumerate(
        results,
        start=1,
    ):

        assert result.rank == index


# ==================================================
#
# URL Deduplication
#
# ==================================================


def test_tsmc_url_deduplication():

    adapter = TSMCNewsAdapter()

    results = adapter.search(
        "TSMC",
        max_results=20,
    )

    urls = [
        result.url
        for result in results
    ]

    assert len(urls) == len(
        set(urls)
    )


# ==================================================
#
# Empty Keyword
#
# ==================================================


def test_tsmc_empty_keyword():

    adapter = TSMCNewsAdapter()

    results = adapter.search(
        "",
    )

    assert results == []


# ==================================================
#
# Invalid Result Limit
#
# ==================================================


def test_tsmc_invalid_result_limit():

    adapter = TSMCNewsAdapter()

    results = adapter.search(
        "TSMC",
        max_results=0,
    )

    assert results == []


# ==================================================
#
# Actual Search
#
# ==================================================


def test_tsmc_actual_search():

    adapter = TSMCNewsAdapter()

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

        assert result.url

        assert result.search_source == "tsmc"

        assert result.source == "TSMC"


# ==================================================
#
# Main
#
# ==================================================


if __name__ == "__main__":

    adapter = TSMCNewsAdapter()

    results = adapter.search(
        "IC semiconductor",
        max_results=5,
    )

    print()
    print("=" * 60)
    print("P4.3 TSMC Adapter Test")
    print("=" * 60)

    print(
        "Adapter:",
        adapter.__class__.__name__,
    )

    print(
        "Source:",
        adapter.search_source,
    )

    print(
        "Results:",
        len(results),
    )

    for result in results:

        print(
            result.rank,
            result.search_source,
            result.source,
            result.title,
            result.url,
        )