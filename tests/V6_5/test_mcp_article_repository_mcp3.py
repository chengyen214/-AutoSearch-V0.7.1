"""
tests/V6_5/test_mcp_article_repository_mcp3.py

AutoSearch V6.5

MCP-3.1

Test MCP ArticleRepository
Article Retrieval

測試：

    1. Find By Document ID
    2. Find By URL
    3. Invalid URL
    4. Empty URL

目前 MCP-3：

    Article Retrieval
        ├── Get by Document ID
        └── Get by URL
"""


from autosearch_mcp.repositories.article_repository import (
    ArticleRepository
)


# ============================================================
# Test Data
# ============================================================

DOCUMENT_ID = (
    "8b02b05cf5e248204397c17778877590bf7e450702553f2df65a58e24e515414"
)

ARTICLE_URL = (
    "https://www.tsmc.com/english/dedicatedFoundry"
)


# ============================================================
# Test Runner
# ============================================================

def run_tests():

    repository = ArticleRepository()

    passed = 0
    failed = 0

    # ========================================================
    # TEST 1 - Find By Document ID
    # ========================================================

    print(
        "TEST 1 - Find By Document ID"
    )

    article = repository.find_by_document_id(
        DOCUMENT_ID
    )

    if (
        article is not None
        and article.get("document_id") == DOCUMENT_ID
    ):
        print(
            "  PASS"
        )
        passed += 1

    else:
        print(
            "  FAIL"
        )
        failed += 1

    # ========================================================
    # TEST 2 - Find By URL
    # ========================================================

    print(
        "TEST 2 - Find By URL"
    )

    article = repository.find_by_url(
        ARTICLE_URL
    )

    if (
        article is not None
        and article.get("url") == ARTICLE_URL
    ):
        print(
            "  PASS"
        )
        passed += 1

    else:
        print(
            "  FAIL"
        )
        failed += 1

    # ========================================================
    # TEST 3 - Invalid URL
    # ========================================================

    print(
        "TEST 3 - Invalid URL"
    )

    article = repository.find_by_url(
        "https://invalid.example.com/not-found"
    )

    if article is None:
        print(
            "  PASS"
        )
        passed += 1

    else:
        print(
            "  FAIL"
        )
        failed += 1

    # ========================================================
    # TEST 4 - Empty URL
    # ========================================================

    print(
        "TEST 4 - Empty URL"
    )

    article = repository.find_by_url(
        ""
    )

    if article is None:
        print(
            "  PASS"
        )
        passed += 1

    else:
        print(
            "  FAIL"
        )
        failed += 1

    # ========================================================
    # Close
    # ========================================================

    repository.close()

    # ========================================================
    # Result
    # ========================================================

    print(
        "Passed : "
        f"{passed}"
    )

    print(
        "Failed : "
        f"{failed}"
    )

    if failed == 0:

        print(
            "ALL MCP ARTICLE REPOSITORY "
            "MCP-3 TESTS PASSED"
        )

    else:

        print(
            "MCP ARTICLE REPOSITORY "
            "MCP-3 TESTS FAILED"
        )


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":

    run_tests()