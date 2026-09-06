"""
tests/V6_5/test_mcp_article_repository.py

AutoSearch V6.4 / V6.5

Test：
    MCP ArticleRepository

Flow：

    Test
      ↓
    MCP ArticleRepository
      ↓
    articles

測試範圍：

    1. Search
    2. Title Search
    3. Content Search
    4. AI Field Search
    5. Empty Query
    6. Invalid Limit
    7. Find By ID
    8. Find By Document ID
    9. Count

注意：

    本測試直接使用目前 AutoSearch Database。

    不測：

        MCP Server
        SearchTool
        SearchService
        search_index
        SearchRankingService
"""


from autosearch_mcp.repositories.article_repository import (
    ArticleRepository
)


# ============================================================
# Test Configuration
# ============================================================

TEST_QUERY = "IC semiconductor"

EXPECTED_ARTICLE_ID = 103

EXPECTED_DOCUMENT_ID = (
    "8b02b05cf5e248204397c17778877590bf7e450702553f2df65a58e24e515414"
)


# ============================================================
# Helpers
# ============================================================

def print_result(
    name,
    result
):
    """
    顯示測試結果。
    """

    print(
        f"\n{'=' * 60}"
    )

    print(
        name
    )

    print(
        f"{'=' * 60}"
    )

    print(
        result
    )


# ============================================================
# Test Search
# ============================================================

def test_search():
    """
    測試 MCP ArticleRepository.search()。

    不要求指定 Article ID 一定出現在前 20 筆。

    原因：

        search() 預設 LIMIT 20。

    本測試只確認：

        1. Search 可以正常執行
        2. 有搜尋結果
        3. 回傳資料具有 Article 基本欄位
    """

    repository = ArticleRepository()

    try:

        results = repository.search(
            TEST_QUERY
        )

        print_result(
            "TEST 1 - Search",
            f"count = {len(results)}"
        )

        assert isinstance(
            results,
            list
        )

        assert len(results) > 0, (
            "Expected at least one article "
            f"for query: {TEST_QUERY}"
        )

        required_fields = [
            "id",
            "document_id",
            "keyword",
            "title",
            "url",
            "content",
            "crawl_time",
            "status",
            "ai_summary",
            "ai_category",
            "ai_keywords",
            "ai_importance",
            "ai_model",
            "ai_version",
            "ai_analyze_time",
            "ai_confidence",
            "ai_status"
        ]

        for row in results:

            assert isinstance(
                row,
                dict
            )

            for field in required_fields:

                assert field in row, (
                    f"Missing Article field: "
                    f"{field}"
                )

        assert len(results) <= 20

        print(
            "PASS"
        )

    finally:

        repository.close()


# ============================================================
# Test Title Search
# ============================================================

def test_title_search():
    """
    測試 title 搜尋。
    """

    repository = ArticleRepository()

    try:

        query = (
            "Dedicated IC Foundry"
        )

        results = repository.search(
            query
        )

        print_result(
            "TEST 2 - Title Search",
            f"count = {len(results)}"
        )

        assert isinstance(
            results,
            list
        )

        assert len(results) > 0

        matched = False

        for row in results:

            title = row.get(
                "title"
            )

            if title and query.lower() in title.lower():

                matched = True

                break

        assert matched, (
            "Expected title match was not found."
        )

        print(
            "PASS"
        )

    finally:

        repository.close()


# ============================================================
# Test Content Search
# ============================================================

def test_content_search():
    """
    測試 content 搜尋。
    """

    repository = ArticleRepository()

    try:

        query = (
            "Established in 1987"
        )

        results = repository.search(
            query
        )

        print_result(
            "TEST 3 - Content Search",
            f"count = {len(results)}"
        )

        assert isinstance(
            results,
            list
        )

        assert len(results) > 0

        matched = False

        for row in results:

            content = row.get(
                "content"
            )

            if content and query.lower() in content.lower():

                matched = True

                break

        assert matched, (
            "Expected content match was not found."
        )

        print(
            "PASS"
        )

    finally:

        repository.close()


# ============================================================
# Test AI Field Search
# ============================================================

def test_ai_field_search():
    """
    測試 AI 欄位搜尋：

        ai_summary
        ai_category
        ai_keywords
    """

    repository = ArticleRepository()

    try:

        queries = [
            "Semiconductor",
            "TSMC",
            "12-inch wafer"
        ]

        total_matches = 0

        for query in queries:

            results = repository.search(
                query
            )

            print(
                f"\nquery = {query}"
            )

            print(
                f"count = {len(results)}"
            )

            if results:

                total_matches += len(
                    results
                )

        assert total_matches > 0, (
            "Expected AI field search "
            "to return articles."
        )

        print(
            "PASS"
        )

    finally:

        repository.close()


# ============================================================
# Test Empty Query
# ============================================================

def test_empty_query():
    """
    空 Query 不應查詢 Database。
    """

    repository = ArticleRepository()

    try:

        results = repository.search(
            ""
        )

        print_result(
            "TEST 5 - Empty Query",
            results
        )

        assert results == []

        print(
            "PASS"
        )

    finally:

        repository.close()


# ============================================================
# Test Invalid Limit
# ============================================================

def test_invalid_limit():
    """
    測試非法 limit。
    """

    repository = ArticleRepository()

    try:

        results = repository.search(
            TEST_QUERY,
            limit="invalid"
        )

        print_result(
            "TEST 6 - Invalid Limit",
            f"count = {len(results)}"
        )

        assert isinstance(
            results,
            list
        )

        assert len(results) <= 20

        print(
            "PASS"
        )

    finally:

        repository.close()


# ============================================================
# Test Find By ID
# ============================================================

def test_find_by_id():
    """
    測試依 Article ID 查詢。
    """

    repository = ArticleRepository()

    try:

        article = repository.find_by_id(
            EXPECTED_ARTICLE_ID
        )

        print_result(
            "TEST 7 - Find By ID",
            article
        )

        assert article is not None

        assert article.get(
            "id"
        ) == EXPECTED_ARTICLE_ID

        assert article.get(
            "keyword"
        ) == TEST_QUERY

        print(
            "PASS"
        )

    finally:

        repository.close()


# ============================================================
# Test Find By Document ID
# ============================================================

def test_find_by_document_id():
    """
    測試依 Document ID 查詢。
    """

    repository = ArticleRepository()

    try:

        article = repository.find_by_document_id(
            EXPECTED_DOCUMENT_ID
        )

        print_result(
            "TEST 8 - Find By Document ID",
            article
        )

        assert article is not None

        assert article.get(
            "id"
        ) == EXPECTED_ARTICLE_ID

        assert article.get(
            "document_id"
        ) == EXPECTED_DOCUMENT_ID

        print(
            "PASS"
        )

    finally:

        repository.close()


# ============================================================
# Test Count
# ============================================================

def test_count():
    """
    測試 Article Count。
    """

    repository = ArticleRepository()

    try:

        count = repository.count()

        print_result(
            "TEST 9 - Count",
            f"count = {count}"
        )

        assert isinstance(
            count,
            int
        )

        assert count >= 0

        print(
            "PASS"
        )

    finally:

        repository.close()


# ============================================================
# Main
# ============================================================

def main():
    """
    執行所有 MCP ArticleRepository Tests。
    """

    print(
        "\n"
        "============================================================\n"
        "AutoSearch V6.5\n"
        "MCP ArticleRepository Test\n"
        "============================================================"
    )

    tests = [
        test_search,
        test_title_search,
        test_content_search,
        test_ai_field_search,
        test_empty_query,
        test_invalid_limit,
        test_find_by_id,
        test_find_by_document_id,
        test_count
    ]

    passed = 0
    failed = 0

    for test in tests:

        try:

            test()

            passed += 1

        except Exception as e:

            failed += 1

            print(
                f"\nFAIL: {test.__name__}"
            )

            print(
                f"Error: {e}"
            )

    print(
        "\n"
        "============================================================"
    )

    print(
        "TEST SUMMARY"
    )

    print(
        "============================================================"
    )

    print(
        f"Passed : {passed}"
    )

    print(
        f"Failed : {failed}"
    )

    print(
        "============================================================"
    )

    if failed > 0:

        raise SystemExit(
            1
        )

    print(
        "ALL MCP ARTICLE REPOSITORY TESTS PASSED"
    )


if __name__ == "__main__":
    main()