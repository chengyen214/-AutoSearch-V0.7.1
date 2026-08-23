"""
tests/V5-6/test_search_execution_bridge.py

AutoSearch V5

P5.6.3

SearchExecutionBridge Integration Test

測試：

    Source Definition
        ↓
    SourceResolutionBridge
        ↓
    GoogleNewsProvider
        ↓
    ProviderSearchAdapter
        ↓
    SearchExecutionBridge
        ↓
    SearchResult[]

本測試只驗證：

    P5.6.2 Source Resolution
        +
    P5.6.3 Search Execution

不測試：

    - Article
    - Crawler
    - Parser
    - Archive
    - AI
    - Database
"""


# ==================================================
#
# Project Root
#
# ==================================================

import sys
from pathlib import Path


PROJECT_ROOT = (
    Path(__file__).resolve().parents[2]
)


if str(PROJECT_ROOT) not in sys.path:

    sys.path.insert(
        0,
        str(PROJECT_ROOT),
    )


# ==================================================
#
# Imports
#
# ==================================================

from models.search_result import (
    SearchResult,
)

from services.source_resolution_bridge import (
    SourceResolutionBridge,
)

from services.search_execution_bridge import (
    SearchExecutionBridge,
)


# ==================================================
#
# Test Configuration
#
# ==================================================

TEST_KEYWORD = "semiconductor"


# ==================================================
#
# Helpers
#
# ==================================================

def print_separator():
    print(
        "\n"
        + "=" * 70
    )


def print_result(
    index,
    result,
):
    print(
        f"[{index}]"
    )

    print(
        f"    title        : "
        f"{result.title}"
    )

    print(
        f"    url          : "
        f"{result.url}"
    )

    print(
        f"    source       : "
        f"{result.source}"
    )

    print(
        f"    search_source: "
        f"{result.search_source}"
    )

    print(
        f"    keyword      : "
        f"{result.keyword}"
    )

    print(
        f"    rank         : "
        f"{result.rank}"
    )


# ==================================================
#
# Test 1
#
# Source Resolution
#
# ==================================================

def test_source_resolution():
    """
    驗證 P5.6.2：

        Source Definition
            ↓
        SourceResolutionBridge
            ↓
        Provider
            ↓
        ProviderSearchAdapter
    """

    print_separator()

    print(
        "TEST 1: Source Resolution"
    )

    print_separator()

    source_definition = {

        "source_type":
            "search",

        "keyword":
            TEST_KEYWORD,

        "provider":
            "google_news",
    }

    print(
        "Source Definition:"
    )

    print(
        source_definition
    )

    bridge = (
        SourceResolutionBridge()
    )

    resolved_source = (
        bridge.resolve(
            source_definition
        )
    )

    print(
        "\nResolved Source:"
    )

    print(
        resolved_source
    )

    # ------------------------------------------
    # Assertions
    # ------------------------------------------

    assert isinstance(
        resolved_source,
        dict,
    )

    assert (
        resolved_source.get(
            "source_type"
        )
        == "search"
    )

    assert (
        resolved_source.get(
            "keyword"
        )
        == TEST_KEYWORD
    )

    assert (
        resolved_source.get(
            "provider"
        )
        == "google_news"
    )

    assert (
        resolved_source.get(
            "provider_instance"
        )
        is not None
    )

    adapter = (
        resolved_source.get(
            "adapter"
        )
    )

    assert adapter is not None

    assert callable(
        getattr(
            adapter,
            "search",
            None,
        )
    )

    print(
        "\nPASS: "
        "SourceResolutionBridge"
    )

    return resolved_source


# ==================================================
#
# Test 2
#
# Search Execution
#
# ==================================================

def test_search_execution(
    resolved_source,
):
    """
    驗證 P5.6.3：

        Resolved Source
            ↓
        SearchExecutionBridge
            ↓
        adapter.search()
            ↓
        SearchResult[]
    """

    print_separator()

    print(
        "TEST 2: Search Execution"
    )

    print_separator()

    bridge = (
        SearchExecutionBridge()
    )

    results = (
        bridge.execute(
            resolved_source
        )
    )

    print(
        f"Search Result Count: "
        f"{len(results)}"
    )

    # ------------------------------------------
    # Result Type
    # ------------------------------------------

    assert isinstance(
        results,
        list,
    )

    # ------------------------------------------
    # Print Results
    # ------------------------------------------

    for index, result in enumerate(
        results,
        start=1,
    ):

        print_result(
            index,
            result,
        )

    # ------------------------------------------
    # Search Result Validation
    # ------------------------------------------

    for result in results:

        assert isinstance(
            result,
            SearchResult,
        )

        assert result.url

        assert (
            result.keyword
            == TEST_KEYWORD
        )

        assert result.rank > 0

    # ------------------------------------------
    # Rank Validation
    # ------------------------------------------

    for expected_rank, result in enumerate(
        results,
        start=1,
    ):

        assert (
            result.rank
            == expected_rank
        )

    print(
        "\nPASS: "
        "SearchExecutionBridge"
    )

    return results


# ==================================================
#
# Test 3
#
# Search Source Identity
#
# ==================================================

def test_search_source_identity(
    results,
):
    """
    驗證 SearchResult
    是否保留 Google News Source Identity。
    """

    print_separator()

    print(
        "TEST 3: Search Source Identity"
    )

    print_separator()

    if not results:

        print(
            "WARNING: "
            "No search results returned."
        )

        print(
            "Source identity test skipped."
        )

        return

    for result in results:

        print(
            f"rank={result.rank}, "
            f"search_source="
            f"{result.search_source}"
        )

        assert (
            result.search_source
            == "google_news"
        )

    print(
        "\nPASS: "
        "SearchResult Source Identity"
    )


# ==================================================
#
# Test 4
#
# Adapter Result Limit
#
# ==================================================

def test_result_limit(
    resolved_source,
):
    """
    驗證 SearchExecutionBridge
    能正確傳遞 max_results。
    """

    print_separator()

    print(
        "TEST 4: Result Limit"
    )

    print_separator()

    bridge = (
        SearchExecutionBridge()
    )

    limit = 5

    results = (
        bridge.execute(
            resolved_source,
            max_results=limit,
        )
    )

    print(
        f"Requested Limit: "
        f"{limit}"
    )

    print(
        f"Actual Results: "
        f"{len(results)}"
    )

    assert isinstance(
        results,
        list,
    )

    assert (
        len(results)
        <= limit
    )

    for expected_rank, result in enumerate(
        results,
        start=1,
    ):

        assert (
            result.rank
            == expected_rank
        )

    print(
        "\nPASS: "
        "Result Limit"
    )


# ==================================================
#
# Main
#
# ==================================================

def main():
    """
    執行完整 P5.6.3 Integration Test。
    """

    print_separator()

    print(
        "AutoSearch V5"
    )

    print(
        "P5.6.3 SearchExecutionBridge"
    )

    print(
        "Integration Test"
    )

    print_separator()

    print(
        f"Project Root: "
        f"{PROJECT_ROOT}"
    )

    print(
        f"Test Keyword: "
        f"{TEST_KEYWORD}"
    )

    try:

        # --------------------------------------
        # P5.6.2
        # --------------------------------------

        resolved_source = (
            test_source_resolution()
        )

        # --------------------------------------
        # P5.6.3
        # --------------------------------------

        results = (
            test_search_execution(
                resolved_source
            )
        )

        # --------------------------------------
        # SearchResult
        # --------------------------------------

        test_search_source_identity(
            results
        )

        # --------------------------------------
        # Result Limit
        # --------------------------------------

        test_result_limit(
            resolved_source
        )

        # --------------------------------------
        # Final
        # --------------------------------------

        print_separator()

        print(
            "ALL TESTS PASSED"
        )

        print_separator()

        print(
            "P5.6.2"
            " Source Resolution"
            " -> PASS"
        )

        print(
            "P5.6.3"
            " Search Execution"
            " -> PASS"
        )

        print(
            "ProviderSearchAdapter"
            " -> PASS"
        )

        print(
            "GoogleNewsProvider"
            " -> PASS"
        )

        print(
            "SearchResult"
            " -> PASS"
        )

        print_separator()

        return 0

    except AssertionError as e:

        print_separator()

        print(
            "TEST FAILED"
        )

        print(
            f"AssertionError: {e}"
        )

        print_separator()

        return 1

    except Exception as e:

        print_separator()

        print(
            "TEST FAILED"
        )

        print(
            f"{type(e).__name__}: {e}"
        )

        print_separator()

        return 1


# ==================================================
#
# Entry Point
#
# ==================================================

if __name__ == "__main__":

    raise SystemExit(
        main()
    )
