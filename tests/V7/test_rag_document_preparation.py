"""
tests/V7/test_rag_document_preparation.py

AutoSearch V7

RAG-1.5

Document Preparation Test

功能：

    測試 RAG-1 Document Preparation
    主控流程。

完整流程：

    Document ID
        ↓
    DocumentPreparation
        ↓
    ArticleSource
        ↓
    MCP
        ↓
    Article
        ↓
    ArticleDocument
        ↓
    LangChain Document
        ↓
    ContentCleaner
        ↓
    Prepared Document

測試內容：

    1. Document ID → Prepared Document
    2. URL → Prepared Document
    3. Document type
    4. page_content
    5. Metadata
    6. Content Cleaning
    7. RAG-2 Chunking readiness
    8. Invalid identifier validation
    9. Article not found validation

本測試不負責：

    1. Chunking
    2. Embedding
    3. ChromaDB
    4. Retriever
    5. Context Builder
    6. LLM
"""


from langchain_core.documents import Document

from rag.document_preparation import (
    DocumentPreparation
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
    "document_id",
    "title",
    "url",
    "keyword",
    "source",
    "crawl_time",
    "ai_summary",
    "ai_category",
    "ai_keywords",
    "ai_importance",
    "ai_confidence",
)


# ============================================================
# Create Preparation
# ============================================================

def create_preparation():
    """
    建立 DocumentPreparation。
    """

    return DocumentPreparation()


# ============================================================
# Test Document ID Preparation
# ============================================================

def test_prepare_by_document_id():
    """
    測試：

        Document ID
            ↓
        Prepared Document
    """

    preparation = create_preparation()

    document = preparation.prepare_by_document_id(
        TEST_DOCUMENT_ID
    )

    assert isinstance(
        document,
        Document
    )

    assert document.page_content

    print(
        "PASS: Document ID preparation"
    )

    print(
        f"      Document ID: "
        f"{document.metadata['document_id']}"
    )


# ============================================================
# Test URL Preparation
# ============================================================

def test_prepare_by_url():
    """
    測試：

        URL
            ↓
        Prepared Document
    """

    preparation = create_preparation()

    document = preparation.prepare_by_url(
        TEST_URL
    )

    assert isinstance(
        document,
        Document
    )

    assert document.page_content

    assert (
        document.metadata["url"]
        == TEST_URL
    )

    print(
        "PASS: URL preparation"
    )

    print(
        f"      URL: "
        f"{document.metadata['url']}"
    )


# ============================================================
# Test Page Content
# ============================================================

def test_page_content():
    """
    確認 Prepared Document
    有有效的 page_content。
    """

    preparation = create_preparation()

    document = preparation.prepare_by_document_id(
        TEST_DOCUMENT_ID
    )

    assert isinstance(
        document.page_content,
        str
    )

    assert document.page_content.strip()

    assert (
        document.page_content
        == document.page_content.strip()
    )

    assert "\r" not in document.page_content

    assert "\n\n\n" not in document.page_content

    print(
        "PASS: Prepared page_content"
    )

    print(
        f"      Content length: "
        f"{len(document.page_content)}"
    )


# ============================================================
# Test Metadata Schema
# ============================================================

def test_metadata_schema():
    """
    確認 Prepared Document
    包含正式 RAG Metadata Schema。
    """

    preparation = create_preparation()

    document = preparation.prepare_by_document_id(
        TEST_DOCUMENT_ID
    )

    metadata = document.metadata

    for field in EXPECTED_METADATA_FIELDS:

        assert field in metadata, (
            f"Metadata field "
            f"'{field}' is missing."
        )

    assert (
        set(metadata.keys())
        == set(EXPECTED_METADATA_FIELDS)
    ), (
        "Prepared Document metadata does not "
        "match the expected RAG schema."
    )

    print(
        "PASS: Metadata schema"
    )

    print(
        f"      Metadata fields: "
        f"{len(metadata)}"
    )


# ============================================================
# Test Core Metadata Values
# ============================================================

def test_core_metadata():
    """
    確認 Core Article Metadata。
    """

    preparation = create_preparation()

    document = preparation.prepare_by_document_id(
        TEST_DOCUMENT_ID
    )

    metadata = document.metadata

    assert (
        metadata["document_id"]
        == TEST_DOCUMENT_ID
    )

    assert metadata["title"]

    assert (
        metadata["url"]
        == TEST_URL
    )

    assert metadata["keyword"]

    assert (
        "source"
        in metadata
    )

    assert metadata["crawl_time"]

    print(
        "PASS: Core metadata"
    )


# ============================================================
# Test AI Metadata Values
# ============================================================

def test_ai_metadata():
    """
    確認 AI Knowledge Metadata。
    """

    preparation = create_preparation()

    document = preparation.prepare_by_document_id(
        TEST_DOCUMENT_ID
    )

    metadata = document.metadata

    assert metadata["ai_summary"]

    assert metadata["ai_category"]

    assert metadata["ai_keywords"]

    assert (
        metadata["ai_importance"]
        is not None
    )

    assert (
        metadata["ai_confidence"]
        is not None
    )

    print(
        "PASS: AI metadata"
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
# Test Document Type
# ============================================================

def test_document_type():
    """
    確認最終結果為 LangChain Document。
    """

    preparation = create_preparation()

    document = preparation.prepare_by_document_id(
        TEST_DOCUMENT_ID
    )

    assert isinstance(
        document,
        Document
    )

    print(
        "PASS: Prepared Document type"
    )


# ============================================================
# Test Content Cleaning
# ============================================================

def test_content_cleaning():
    """
    確認最終 page_content
    已經經過 ContentCleaner。
    """

    preparation = create_preparation()

    document = preparation.prepare_by_document_id(
        TEST_DOCUMENT_ID
    )

    assert (
        document.page_content
        == document.page_content.strip()
    )

    assert "\r" not in document.page_content

    assert "\n\n\n" not in document.page_content

    print(
        "PASS: Content cleaning"
    )


# ============================================================
# Test RAG-2 Readiness
# ============================================================

def test_rag2_readiness():
    """
    確認 Prepared Document
    可以直接交給 RAG-2 Chunking。

    本測試不執行 Chunking。
    """

    preparation = create_preparation()

    document = preparation.prepare_by_document_id(
        TEST_DOCUMENT_ID
    )

    assert isinstance(
        document,
        Document
    )

    assert isinstance(
        document.page_content,
        str
    )

    assert document.page_content.strip()

    assert isinstance(
        document.metadata,
        dict
    )

    for field in EXPECTED_METADATA_FIELDS:

        assert field in document.metadata

    print(
        "PASS: RAG-2 Chunking readiness"
    )


# ============================================================
# Test Data Integrity
# ============================================================

def test_data_integrity():
    """
    確認 Document Preparation
    沒有遺失重要 Article 資料。
    """

    preparation = create_preparation()

    document = preparation.prepare_by_document_id(
        TEST_DOCUMENT_ID
    )

    # ----------------------------------------------
    # Core Identifier
    # ----------------------------------------------

    assert (
        document.metadata["document_id"]
        == TEST_DOCUMENT_ID
    )

    assert (
        document.metadata["url"]
        == TEST_URL
    )

    # ----------------------------------------------
    # Required Article Information
    # ----------------------------------------------

    assert document.metadata["title"]

    assert document.metadata["keyword"]

    assert document.page_content

    # ----------------------------------------------
    # AI Information
    # ----------------------------------------------

    assert document.metadata["ai_summary"]

    assert document.metadata["ai_category"]

    assert document.metadata["ai_keywords"]

    print(
        "PASS: Document data integrity"
    )


# ============================================================
# Test Empty Document ID
# ============================================================

def test_empty_document_id():
    """
    測試空 Document ID。
    """

    preparation = create_preparation()

    try:

        preparation.prepare_by_document_id(
            ""
        )

    except ValueError:

        print(
            "PASS: Empty Document ID validation"
        )

        return

    raise AssertionError(
        "Empty Document ID should raise ValueError."
    )


# ============================================================
# Test None Document ID
# ============================================================

def test_none_document_id():
    """
    測試 None Document ID。
    """

    preparation = create_preparation()

    try:

        preparation.prepare_by_document_id(
            None
        )

    except ValueError:

        print(
            "PASS: None Document ID validation"
        )

        return

    raise AssertionError(
        "None Document ID should raise ValueError."
    )


# ============================================================
# Test Empty URL
# ============================================================

def test_empty_url():
    """
    測試空 URL。
    """

    preparation = create_preparation()

    try:

        preparation.prepare_by_url(
            ""
        )

    except ValueError:

        print(
            "PASS: Empty URL validation"
        )

        return

    raise AssertionError(
        "Empty URL should raise ValueError."
    )


# ============================================================
# Test None URL
# ============================================================

def test_none_url():
    """
    測試 None URL。
    """

    preparation = create_preparation()

    try:

        preparation.prepare_by_url(
            None
        )

    except ValueError:

        print(
            "PASS: None URL validation"
        )

        return

    raise AssertionError(
        "None URL should raise ValueError."
    )


# ============================================================
# Test Article Not Found
# ============================================================

def test_article_not_found():
    """
    測試不存在的 Document ID。
    """

    preparation = create_preparation()

    invalid_document_id = (
        "000000000000000000000000000000000000"
    )

    try:

        preparation.prepare_by_document_id(
            invalid_document_id
        )

    except ValueError:

        print(
            "PASS: Article not found validation"
        )

        return

    raise AssertionError(
        "Unknown Document ID should raise ValueError."
    )


# ============================================================
# Main
# ============================================================

def main():
    """
    執行 RAG-1.5 Document Preparation Test。
    """

    print("=" * 60)
    print(
        "RAG-1.5 Document Preparation Test"
    )
    print("=" * 60)

    print()

    print(
        "Testing complete RAG-1 Document Preparation..."
    )

    print()

    test_prepare_by_document_id()

    print()

    test_prepare_by_url()

    print()

    test_page_content()

    test_document_type()

    test_metadata_schema()

    test_core_metadata()

    test_ai_metadata()

    test_content_cleaning()

    test_rag2_readiness()

    test_data_integrity()

    test_empty_document_id()

    test_none_document_id()

    test_empty_url()

    test_none_url()

    test_article_not_found()

    print()

    print("=" * 60)
    print(
        "ALL RAG-1 DOCUMENT PREPARATION TESTS PASSED"
    )
    print("=" * 60)


if __name__ == "__main__":
    main()