"""
tests/V7/test_rag_document_model.py

AutoSearch V7

RAG-1.1
RAG-1.2
RAG-1.3

Article Source + Document Model + Metadata Test

測試內容：

    1. 透過 MCP ArticleSource 真正取得 Article
    2. Article → LangChain Document
    3. page_content mapping
    4. Document type
    5. RAG Metadata Schema
    6. Core Metadata mapping
    7. AI Metadata mapping
    8. Article → Document 完整資料流
    9. Invalid Article validation

實際資料流程：

    MCP Server
        ↓
    ArticleSource
        ↓
    Article dict
        ↓
    ArticleDocument
        ↓
    LangChain Document

測試資料：

    Document ID：

        d9ce4740c3f0b6f1d260c094c0549f68727187b0a2b57c94f6308b4df9fd9d13

    URL：

        https://finance.technews.tw/2026/02/26/
        navitas-semiconductor-announces-fourth-quarter-and-full-year-2025-financial-results/

本測試不負責：

    1. Chunking
    2. Embedding
    3. ChromaDB
    4. Retriever
    5. LLM
"""


from langchain_core.documents import Document

from rag.article_source import (
    ArticleSource
)

from rag.document_model import (
    ArticleDocument
)


# ============================================================
# Test Article Identifier
# ============================================================

TEST_DOCUMENT_ID = (
    "d9ce4740c3f0b6f1d260c094c0549f68727187b0a2b57c94f6308b4df9fd9d13"
)

TEST_URL = (
    "https://finance.technews.tw/2026/02/26/"
    "navitas-semiconductor-announces-fourth-quarter-and-full-year-2025-financial-results/"
)


# ============================================================
# Expected Metadata Schema
# ============================================================

EXPECTED_METADATA_FIELDS = (
    # Core Article Metadata
    "document_id",
    "title",
    "url",
    "keyword",
    "source",
    "crawl_time",

    # AI Knowledge Metadata
    "ai_summary",
    "ai_category",
    "ai_keywords",
    "ai_importance",
    "ai_confidence",
)


# ============================================================
# Get Real Article
# ============================================================

def get_real_article():
    """
    透過 MCP ArticleSource
    真正取得 Article。

    Returns:
        dict
    """

    source = ArticleSource()

    article = source.get_by_document_id(
        TEST_DOCUMENT_ID
    )

    assert article is not None, (
        "MCP ArticleSource returned no Article."
    )

    assert isinstance(
        article,
        dict
    ), (
        "MCP ArticleSource must return dict."
    )

    return article


# ============================================================
# Create Real Document
# ============================================================

def create_document():
    """
    透過 MCP 取得真實 Article，
    再轉換成 LangChain Document。
    """

    article = get_real_article()

    document = ArticleDocument.from_article(
        article
    )

    return article, document


# ============================================================
# Test Real MCP Article Retrieval
# ============================================================

def test_real_article_retrieval():
    """
    確認測試資料確實來自 MCP。
    """

    article = get_real_article()

    assert (
        article["document_id"]
        == TEST_DOCUMENT_ID
    )

    assert (
        article["url"]
        == TEST_URL
    )

    assert article.get(
        "title"
    )

    assert article.get(
        "content"
    )

    print(
        "PASS: Real MCP Article retrieval"
    )

    print(
        f"      Document ID: "
        f"{article['document_id']}"
    )

    print(
        f"      Title: "
        f"{article['title']}"
    )

    print(
        f"      Content length: "
        f"{len(article['content'])}"
    )


# ============================================================
# Test Document Creation
# ============================================================

def test_article_to_document():
    """
    測試：

        MCP Article
            ↓
        LangChain Document
    """

    article, document = create_document()

    assert document is not None

    print(
        "PASS: Document creation"
    )


# ============================================================
# Test Page Content
# ============================================================

def test_page_content():
    """
    確認：

        Article.content
            ↓
        Document.page_content
    """

    article, document = create_document()

    assert (
        document.page_content
        == article["content"]
    )

    assert document.page_content

    print(
        "PASS: page_content mapping"
    )

    print(
        f"      Page content length: "
        f"{len(document.page_content)}"
    )


# ============================================================
# Test Document Type
# ============================================================

def test_document_type():
    """
    確認結果確實為 LangChain Document。
    """

    _, document = create_document()

    assert isinstance(
        document,
        Document
    )

    print(
        "PASS: LangChain Document type"
    )


# ============================================================
# Test Metadata Fields
# ============================================================

def test_metadata_fields():
    """
    確認 RAG Metadata Schema
    包含全部正式欄位。
    """

    _, document = create_document()

    metadata = document.metadata

    for field in EXPECTED_METADATA_FIELDS:

        assert field in metadata, (
            f"Metadata field "
            f"'{field}' is missing."
        )

    assert (
        len(metadata)
        == len(EXPECTED_METADATA_FIELDS)
    ), (
        "Unexpected metadata fields detected."
    )

    print(
        "PASS: Metadata schema"
    )

    print(
        f"      Metadata fields: "
        f"{len(metadata)}"
    )


# ============================================================
# Test Core Metadata
# ============================================================

def test_core_metadata():
    """
    測試 Core Article Metadata。

    Mapping：

        document_id → document_id
        title       → title
        url         → url
        keyword     → keyword
        source      → source
        crawl_time  → crawl_time
    """

    article, document = create_document()

    metadata = document.metadata

    assert (
        metadata["document_id"]
        == article["document_id"]
    )

    assert (
        metadata["title"]
        == article["title"]
    )

    assert (
        metadata["url"]
        == article["url"]
    )

    assert (
        metadata["keyword"]
        == article.get("keyword")
    )

    assert (
        metadata["source"]
        == article.get("source")
    )

    assert (
        metadata["crawl_time"]
        == article.get("crawl_time")
    )

    print(
        "PASS: Core metadata mapping"
    )


# ============================================================
# Test AI Metadata
# ============================================================

def test_ai_metadata():
    """
    測試 AI Knowledge Metadata。

    Mapping：

        ai_summary
        ai_category
        ai_keywords
        ai_importance
        ai_confidence
    """

    article, document = create_document()

    metadata = document.metadata

    assert (
        metadata["ai_summary"]
        == article.get("ai_summary")
    )

    assert (
        metadata["ai_category"]
        == article.get("ai_category")
    )

    assert (
        metadata["ai_keywords"]
        == article.get("ai_keywords")
    )

    assert (
        metadata["ai_importance"]
        == article.get("ai_importance")
    )

    assert (
        metadata["ai_confidence"]
        == article.get("ai_confidence")
    )

    print(
        "PASS: AI metadata mapping"
    )


# ============================================================
# Test Metadata Values
# ============================================================

def test_metadata_values():
    """
    額外確認實際 MCP Article 的
    重要 Metadata 有正確資料。
    """

    article, document = create_document()

    metadata = document.metadata

    assert metadata["document_id"]

    assert metadata["title"]

    assert metadata["url"]

    assert metadata["keyword"]

    assert metadata["crawl_time"]

    assert metadata["ai_summary"]

    assert metadata["ai_category"]

    assert metadata["ai_keywords"]

    assert metadata["ai_importance"] is not None

    assert metadata["ai_confidence"] is not None

    print(
        "PASS: Metadata values"
    )

    print(
        f"      Keyword: "
        f"{metadata['keyword']}"
    )

    print(
        f"      AI Category: "
        f"{metadata['ai_category']}"
    )

    print(
        f"      AI Importance: "
        f"{metadata['ai_importance']}"
    )

    print(
        f"      AI Confidence: "
        f"{metadata['ai_confidence']}"
    )


# ============================================================
# Test No Unexpected Metadata
# ============================================================

def test_no_unexpected_metadata():
    """
    確認 Document metadata
    完全符合正式 RAG Metadata Schema。
    """

    _, document = create_document()

    metadata_fields = set(
        document.metadata.keys()
    )

    expected_fields = set(
        EXPECTED_METADATA_FIELDS
    )

    assert (
        metadata_fields
        == expected_fields
    ), (
        "Document metadata schema does not "
        "match the expected RAG schema."
    )

    print(
        "PASS: No unexpected metadata"
    )


# ============================================================
# Test Full Data Flow
# ============================================================

def test_full_data_flow():
    """
    驗證完整資料流：

        MCP
        ↓
        Article
        ↓
        Document
    """

    article, document = create_document()

    assert (
        document.metadata["document_id"]
        == article["document_id"]
    )

    assert (
        document.metadata["title"]
        == article["title"]
    )

    assert (
        document.metadata["url"]
        == article["url"]
    )

    assert (
        document.page_content
        == article["content"]
    )

    print(
        "PASS: MCP Article → Document full data flow"
    )


# ============================================================
# Test Invalid Article
# ============================================================

def test_invalid_article():
    """
    測試必要欄位驗證。
    """

    invalid_article = {
        "document_id": "test"
    }

    try:

        ArticleDocument.from_article(
            invalid_article
        )

    except ValueError:

        print(
            "PASS: Invalid Article validation"
        )

        return

    raise AssertionError(
        "Invalid Article should raise ValueError."
    )


# ============================================================
# Test None Article
# ============================================================

def test_none_article():
    """
    測試 Article=None。
    """

    try:

        ArticleDocument.from_article(
            None
        )

    except ValueError:

        print(
            "PASS: None Article validation"
        )

        return

    raise AssertionError(
        "None Article should raise ValueError."
    )


# ============================================================
# Test Invalid Article Type
# ============================================================

def test_invalid_article_type():
    """
    測試 Article 不是 dict。
    """

    try:

        ArticleDocument.from_article(
            "invalid article"
        )

    except TypeError:

        print(
            "PASS: Article type validation"
        )

        return

    raise AssertionError(
        "Non-dict Article should raise TypeError."
    )


# ============================================================
# Main
# ============================================================

def main():
    """
    執行 RAG-1.1 / RAG-1.2 / RAG-1.3
    Article Source + Document Model + Metadata Test。
    """

    print("=" * 60)
    print(
        "RAG-1.1 / RAG-1.2 / RAG-1.3 "
        "Document Preparation Test"
    )
    print("=" * 60)

    print()

    print(
        "Testing real MCP Article data..."
    )

    print()

    test_real_article_retrieval()

    print()

    test_article_to_document()

    test_page_content()

    test_document_type()

    test_metadata_fields()

    test_core_metadata()

    test_ai_metadata()

    test_metadata_values()

    test_no_unexpected_metadata()

    test_full_data_flow()

    test_invalid_article()

    test_none_article()

    test_invalid_article_type()

    print()

    print("=" * 60)
    print(
        "ALL RAG-1.1 / RAG-1.2 / RAG-1.3 "
        "DOCUMENT PREPARATION TESTS PASSED"
    )
    print("=" * 60)


if __name__ == "__main__":
    main()