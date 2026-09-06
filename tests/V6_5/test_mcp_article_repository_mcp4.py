"""
tests/V6_5/test_mcp_article_repository_mcp4.py

AutoSearch V6.5

MCP-4

MCP Article Repository Test

測試：

    1. Basic Search
    2. Date Filter - From
    3. Date Filter - To
    4. Date Filter - Range
    5. Category Filter
    6. Source Parameter
       - 目前 source 暫不啟用 SQL Filter
    7. Sort - latest
    8. Sort - oldest
    9. Pagination - page 1
    10. Pagination - page 2
    11. Invalid Sort
    12. Invalid Page
    13. Invalid Limit
    14. Find By Document ID
    15. Find By URL
    16. Count
"""


from autosearch_mcp.repositories.article_repository import (
    ArticleRepository
)


# ==================================================
# Test Data
# ==================================================

TEST_QUERY = "IC semiconductor"

TEST_DOCUMENT_ID = (
    "8b02b05cf5e248204397c17778877590"
    "bf7e450702553f2df65a58e24e515414"
)

TEST_URL = (
    "https://www.tsmc.com/english/dedicatedFoundry"
)


# ==================================================
# Test Runner
# ==================================================

passed = 0
failed = 0


def test(
    name,
    condition
):
    global passed
    global failed

    if condition:

        print(
            f"  PASS - {name}"
        )

        passed += 1

    else:

        print(
            f"  FAIL - {name}"
        )

        failed += 1


# ==================================================
# Main
# ==================================================

def main():

    repository = ArticleRepository()

    try:

        # ==========================================
        # TEST 1
        # Basic Search
        # ==========================================

        print(
            "TEST 1 - Basic Search"
        )

        rows = repository.search(
            TEST_QUERY
        )

        test(
            "Basic search returns rows",
            isinstance(rows, list)
            and len(rows) > 0
        )

        test(
            "Default limit <= 20",
            len(rows) <= 20
        )

        # ==========================================
        # TEST 2
        # Date Filter - From
        # ==========================================

        print(
            "TEST 2 - Date Filter From"
        )

        rows = repository.search(
            TEST_QUERY,
            published_from="2026-01-01"
        )

        test(
            "Date from returns list",
            isinstance(rows, list)
        )

        # ==========================================
        # TEST 3
        # Date Filter - To
        # ==========================================

        print(
            "TEST 3 - Date Filter To"
        )

        rows = repository.search(
            TEST_QUERY,
            published_to="2026-12-31"
        )

        test(
            "Date to returns list",
            isinstance(rows, list)
        )

        # ==========================================
        # TEST 4
        # Date Filter - Range
        # ==========================================

        print(
            "TEST 4 - Date Filter Range"
        )

        rows = repository.search(
            TEST_QUERY,
            published_from="2026-01-01",
            published_to="2026-12-31"
        )

        test(
            "Date range returns list",
            isinstance(rows, list)
        )

        # ==========================================
        # TEST 5
        # Category Filter
        # ==========================================

        print(
            "TEST 5 - Category Filter"
        )

        rows = repository.search(
            TEST_QUERY,
            category="Semiconductor"
        )

        test(
            "Category filter returns list",
            isinstance(rows, list)
        )

        # ==========================================
        # TEST 6
        # Source Parameter
        # ==========================================

        print(
            "TEST 6 - Source Parameter"
        )

        rows_without_source = repository.search(
            TEST_QUERY
        )

        rows_with_source = repository.search(
            TEST_QUERY,
            source="TSMC"
        )

        test(
            "Source parameter accepted",
            isinstance(rows_with_source, list)
        )

        test(
            "Source filter currently inactive",
            rows_with_source == rows_without_source
        )

        # ==========================================
        # TEST 7
        # Sort - latest
        # ==========================================

        print(
            "TEST 7 - Sort Latest"
        )

        rows = repository.search(
            TEST_QUERY,
            limit=5,
            sort_by="latest"
        )

        test(
            "Latest sort returns list",
            isinstance(rows, list)
        )

        if len(rows) >= 2:

            test(
                "Latest sort is descending ID",
                rows[0]["id"] >= rows[-1]["id"]
            )

        # ==========================================
        # TEST 8
        # Sort - oldest
        # ==========================================

        print(
            "TEST 8 - Sort Oldest"
        )

        rows = repository.search(
            TEST_QUERY,
            limit=5,
            sort_by="oldest"
        )

        test(
            "Oldest sort returns list",
            isinstance(rows, list)
        )

        if len(rows) >= 2:

            test(
                "Oldest sort is ascending ID",
                rows[0]["id"] <= rows[-1]["id"]
            )

        # ==========================================
        # TEST 9
        # Pagination - Page 1
        # ==========================================

        print(
            "TEST 9 - Pagination Page 1"
        )

        page1 = repository.search(
            TEST_QUERY,
            limit=5,
            page=1,
            sort_by="latest"
        )

        test(
            "Page 1 returns list",
            isinstance(page1, list)
        )

        test(
            "Page 1 <= 5 rows",
            len(page1) <= 5
        )

        # ==========================================
        # TEST 10
        # Pagination - Page 2
        # ==========================================

        print(
            "TEST 10 - Pagination Page 2"
        )

        page2 = repository.search(
            TEST_QUERY,
            limit=5,
            page=2,
            sort_by="latest"
        )

        test(
            "Page 2 returns list",
            isinstance(page2, list)
        )

        test(
            "Page 2 <= 5 rows",
            len(page2) <= 5
        )

        if page1 and page2:

            page1_ids = {
                row["id"]
                for row in page1
            }

            page2_ids = {
                row["id"]
                for row in page2
            }

            test(
                "Page 1 and Page 2 do not overlap",
                page1_ids.isdisjoint(
                    page2_ids
                )
            )

        # ==========================================
        # TEST 11
        # Invalid Sort
        # ==========================================

        print(
            "TEST 11 - Invalid Sort"
        )

        rows = repository.search(
            TEST_QUERY,
            limit=5,
            sort_by="invalid_sort"
        )

        test(
            "Invalid sort falls back to default",
            isinstance(rows, list)
        )

        if len(rows) >= 2:

            test(
                "Invalid sort uses latest",
                rows[0]["id"] >= rows[-1]["id"]
            )

        # ==========================================
        # TEST 12
        # Invalid Page
        # ==========================================

        print(
            "TEST 12 - Invalid Page"
        )

        page_invalid = repository.search(
            TEST_QUERY,
            limit=5,
            page=0,
            sort_by="latest"
        )

        page_one = repository.search(
            TEST_QUERY,
            limit=5,
            page=1,
            sort_by="latest"
        )

        test(
            "Invalid page falls back to page 1",
            page_invalid == page_one
        )

        # ==========================================
        # TEST 13
        # Invalid Limit
        # ==========================================

        print(
            "TEST 13 - Invalid Limit"
        )

        rows = repository.search(
            TEST_QUERY,
            limit="invalid"
        )

        test(
            "Invalid limit falls back to 20",
            len(rows) <= 20
        )

        rows = repository.search(
            TEST_QUERY,
            limit=999
        )

        test(
            "Limit is capped at 100",
            len(rows) <= 100
        )

        rows = repository.search(
            TEST_QUERY,
            limit=0
        )

        test(
            "Zero limit falls back to default",
            len(rows) <= 20
        )

        # ==========================================
        # TEST 14
        # Find By Document ID
        # ==========================================

        print(
            "TEST 14 - Find By Document ID"
        )

        article = repository.find_by_document_id(
            TEST_DOCUMENT_ID
        )

        test(
            "Document ID returns article",
            article is not None
        )

        if article is not None:

            test(
                "Document ID matches",
                article["document_id"]
                == TEST_DOCUMENT_ID
            )

        # ==========================================
        # TEST 15
        # Find By URL
        # ==========================================

        print(
            "TEST 15 - Find By URL"
        )

        article = repository.find_by_url(
            TEST_URL
        )

        test(
            "URL returns article",
            article is not None
        )

        if article is not None:

            test(
                "URL matches",
                article["url"]
                == TEST_URL
            )

        # ==========================================
        # TEST 16
        # Count
        # ==========================================

        print(
            "TEST 16 - Count"
        )

        count = repository.count()

        test(
            "Count returns integer",
            isinstance(count, int)
        )

        test(
            "Article count > 0",
            count > 0
        )

    finally:

        repository.close()

    # ==================================================
    # Summary
    # ==================================================

    print()
    print(
        "=========================================="
    )
    print(
        "MCP-4 Article Repository Test Summary"
    )
    print(
        "=========================================="
    )

    print(
        f"Passed : {passed}"
    )

    print(
        f"Failed : {failed}"
    )

    if failed == 0:

        print(
            "ALL MCP ARTICLE REPOSITORY MCP-4 "
            "TESTS PASSED"
        )

    else:

        print(
            "MCP ARTICLE REPOSITORY MCP-4 "
            "TESTS FAILED"
        )


if __name__ == "__main__":

    main()