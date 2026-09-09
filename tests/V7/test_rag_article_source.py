"""
tests/V7/test_rag_article_source.py

AutoSearch V7

RAG-1.1

Article Source Test

功能：

    測試 RAG ArticleSource
    是否可以透過 MCP Client
    取得 AutoSearch Article。

測試流程：

    Test
        ↓
    ArticleSource
        ↓
    MCP Client
        ↓
    STDIO
        ↓
    AutoSearch MCP Server
        ↓
    MCP ArticleTool
        ↓
    MCP SearchService
        ↓
    MCP ArticleRepository
        ↓
    MySQL articles

測試內容：

    1. Document ID Retrieval
    2. URL Retrieval
    3. Article Data Validation

本階段原則：

    1. 不建立 LangChain Document。
    2. 不執行 Embedding。
    3. 不使用 ChromaDB。
    4. 不執行 Chunking。
    5. 不執行 RAG Query。
    6. 不修改 MCP Server。
    7. 不直接操作 MySQL。
"""


from rag.article_source import (
    ArticleSource
)


# ============================================================
# Test Article
# ============================================================

TEST_DOCUMENT_ID = (
    "d9ce4740c3f0b6f1d260c094c0549f68727187b0a2b57c94f6308b4df9fd9d13"
)

TEST_URL = (
    "https://finance.technews.tw/2026/02/26/"
    "navitas-semiconductor-announces-fourth-quarter-and-full-year-2025-financial-results/"
)


# ============================================================
# Validate Article
# ============================================================

def validate_article(
    article
):
    """
    驗證 Article 基本資料。
    """

    assert article is not None, (
        "Article retrieval returned None."
    )

    assert isinstance(
        article,
        dict
    ), (
        "Article must be returned as dict."
    )

    assert article.get(
        "document_id"
    ), (
        "Article document_id is missing."
    )

    assert article.get(
        "title"
    ), (
        "Article title is missing."
    )

    assert article.get(
        "url"
    ), (
        "Article URL is missing."
    )

    assert article.get(
        "content"
    ), (
        "Article content is missing."
    )


# ============================================================
# Document ID Test
# ============================================================

def test_get_by_document_id():
    """
    測試透過 Document ID
    從 MCP 取得 Article。
    """

    source = ArticleSource()

    article = source.get_by_document_id(
        TEST_DOCUMENT_ID
    )

    validate_article(
        article
    )

    assert (
        article["document_id"]
        == TEST_DOCUMENT_ID
    )

    print(
        "PASS: Document ID Article Retrieval"
    )

    print(
        f"      Document ID: "
        f"{article['document_id']}"
    )

    print(
        f"      Title: "
        f"{article['title']}"
    )


# ============================================================
# URL Test
# ============================================================

def test_get_by_url():
    """
    測試透過 URL
    從 MCP 取得 Article。
    """

    source = ArticleSource()

    article = source.get_by_url(
        TEST_URL
    )

    validate_article(
        article
    )

    assert (
        article["url"]
        == TEST_URL
    )

    print(
        "PASS: URL Article Retrieval"
    )

    print(
        f"      URL: "
        f"{article['url']}"
    )

    print(
        f"      Document ID: "
        f"{article['document_id']}"
    )


# ============================================================
# Main
# ============================================================

def main():
    """
    執行 RAG-1.1 Article Source Test。
    """

    print("=" * 60)
    print(
        "RAG-1.1 Article Source Test"
    )
    print("=" * 60)

    print()

    print(
        "Testing MCP Article Retrieval..."
    )

    print()

    test_get_by_document_id()

    print()

    test_get_by_url()

    print()

    print("=" * 60)
    print(
        "ALL RAG-1.1 ARTICLE SOURCE TESTS PASSED"
    )
    print("=" * 60)


if __name__ == "__main__":
    main()