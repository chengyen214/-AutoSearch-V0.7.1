"""
tests/V6_5/test_mcp_article_tool_mcp3.py

AutoSearch V6.5

MCP-3.3

Test MCP ArticleTool

測試：

    1. Get By Document ID
    2. Get By URL
    3. Invalid Document ID
    4. Invalid URL
    5. Empty Document ID
    6. Empty URL
"""


from autosearch_mcp.tools.article import (
    ArticleTool
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

    tool = ArticleTool()

    passed = 0
    failed = 0

    # ========================================================
    # TEST 1 - Get By Document ID
    # ========================================================

    print(
        "TEST 1 - Get By Document ID"
    )

    article = tool.get_by_document_id(
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
    # TEST 2 - Get By URL
    # ========================================================

    print(
        "TEST 2 - Get By URL"
    )

    article = tool.get_by_url(
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
    # TEST 3 - Invalid Document ID
    # ========================================================

    print(
        "TEST 3 - Invalid Document ID"
    )

    article = tool.get_by_document_id(
        "invalid-document-id"
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
    # TEST 4 - Invalid URL
    # ========================================================

    print(
        "TEST 4 - Invalid URL"
    )

    article = tool.get_by_url(
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
    # TEST 5 - Empty Document ID
    # ========================================================

    print(
        "TEST 5 - Empty Document ID"
    )

    article = tool.get_by_document_id(
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
    # TEST 6 - Empty URL
    # ========================================================

    print(
        "TEST 6 - Empty URL"
    )

    article = tool.get_by_url(
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

    tool.close()

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
            "ALL MCP ARTICLE TOOL "
            "MCP-3.3 TESTS PASSED"
        )

    else:

        print(
            "MCP ARTICLE TOOL "
            "MCP-3.3 TESTS FAILED"
        )


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":

    run_tests()