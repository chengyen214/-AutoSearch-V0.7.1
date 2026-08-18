"""
tests/p4/test_intel_adapter.py

AutoSearch V4

P4.4 Intel Newsroom Search Source

測試:

1. IntelNewsAdapter 建立
2. SearchResult 型別
3. search_source
4. Intel Newsroom URL
5. Keyword Matching
6. Result Limit
7. URL Deduplication
8. 實際 Intel Newsroom 搜尋
"""


from search.intel_adapter import (
    IntelNewsAdapter,
)


from models.search_result import (
    SearchResult,
)


# ==================================================
#
# Adapter Creation
#
# ==================================================


def test_intel_adapter_creation():

    adapter = IntelNewsAdapter()

    assert adapter is not None


# ==================================================
#
# Search Source
#
# ==================================================


def test_intel_search_source():

    adapter = IntelNewsAdapter()

    assert adapter.search_source == "intel"


# ==================================================
#
# Result Limit
#
# ==================================================


def test_intel_result_limit():

    adapter = IntelNewsAdapter()

    results = adapter.search(
        "semiconductor",
        max_results=2,
    )

    assert len(results) <= 2


# ==================================================
#
# SearchResult
#
# ==================================================


def test_intel_search_result_type():

    adapter = IntelNewsAdapter()

    results = adapter.search(
        "semiconductor",
        max_results=5,
    )

    for result in results:

        assert isinstance(
            result,
            SearchResult,
        )


# ==================================================
#
# Intel URL
#
# ==================================================


def test_intel_url():

    adapter = IntelNewsAdapter()

    results = adapter.search(
        "semiconductor",
        max_results=5,
    )

    for result in results:

        assert result.url.startswith(
            "https://newsroom.intel.com/"
        )


# ==================================================
#
# Search Source Normalization
#
# ==================================================


def test_intel_result_source():

    adapter = IntelNewsAdapter()

    results = adapter.search(
        "semiconductor",
        max_results=5,
    )

    for result in results:

        assert result.search_source == "intel"


# ==================================================
#
# Keyword
#
# ==================================================


def test_intel_keyword():

    adapter = IntelNewsAdapter()

    keyword = "semiconductor"

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


def test_intel_rank():

    adapter = IntelNewsAdapter()

    results = adapter.search(
        "semiconductor",
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


def test_intel_url_deduplication():

    adapter = IntelNewsAdapter()

    results = adapter.search(
        "semiconductor",
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


def test_intel_empty_keyword():

    adapter = IntelNewsAdapter()

    results = adapter.search(
        "",
    )

    assert results == []


# ==================================================
#
# Invalid Result Limit
#
# ==================================================


def test_intel_invalid_result_limit():

    adapter = IntelNewsAdapter()

    results = adapter.search(
        "semiconductor",
        max_results=0,
    )

    assert results == []


# ==================================================
#
# Actual Search
#
# ==================================================


def test_intel_actual_search():

    adapter = IntelNewsAdapter()

    results = adapter.search(
        "IC semiconductor",
        max_results=10,
    )

    assert isinstance(
        results,
        list,
    )

    assert len(results) <= 10

    for result in results:

        assert isinstance(
            result,
            SearchResult,
        )

        assert result.url

        assert result.search_source == "intel"

        assert result.source == "Intel"


# ==================================================
#
# Main
#
# ==================================================


if __name__ == "__main__":

    adapter = IntelNewsAdapter()

    results = adapter.search(
        "IC semiconductor",
        max_results=10,
    )

    print()
    print("=" * 60)
    print("P4.4 Intel Newsroom Adapter Test")
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