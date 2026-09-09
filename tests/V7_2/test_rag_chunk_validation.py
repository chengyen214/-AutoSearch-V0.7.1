"""
tests/V7_2/test_rag_chunk_validation.py

AutoSearch V7

RAG-2.4

Chunk Validation Test

功能：

    驗證 RAG-2.2 DocumentSplitter
    產生的 Chunk 是否符合正式要求。

資料流程：

    RAG-1.5
    Prepared LangChain Document
            ↓
    RAG-2.2
    DocumentSplitter
            ↓
    Chunks
            ↓
    RAG-2.3
    Metadata Preservation
            ↓
    RAG-2.4
    Chunk Validation

正式 RAG Metadata Schema：

    1. document_id
    2. title
    3. url
    4. keyword
    5. source
    6. crawl_time
    7. ai_summary
    8. ai_category
    9. ai_keywords
    10. ai_importance
    11. ai_confidence

本測試不負責：

    1. MCP Server
    2. Database
    3. SQL
    4. Content Cleaning
    5. Embedding
    6. Qwen Embedding
    7. ChromaDB
    8. Retriever
    9. Context Builder
    10. LLM
"""


from langchain_core.documents import Document

from rag.document_preparation import (
    DocumentPreparation
)

from rag.chunking.splitter import (
    DocumentSplitter
)

from rag.chunking.config import (
    CHUNK_SIZE,
)


# ============================================================
# Test Article Identifier
# ============================================================

TEST_DOCUMENT_ID = (
    "d9ce4740c3f0b6f1d260c094c0549f68727187b0a2b57c94f6308b4df9fd9d13"
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
# Create Prepared Document
# ============================================================

def create_prepared_document():
    """
    透過 RAG-1 DocumentPreparation
    取得真實 Prepared Document。
    """

    preparation = DocumentPreparation()

    document = preparation.prepare_by_document_id(
        TEST_DOCUMENT_ID
    )

    assert document is not None

    assert isinstance(
        document,
        Document
    )

    assert document.page_content

    return document


# ============================================================
# Create Chunks
# ============================================================

def create_chunks():
    """
    使用 RAG-2.2 DocumentSplitter
    建立真實 Chunk。
    """

    document = create_prepared_document()

    splitter = DocumentSplitter()

    chunks = splitter.split_document(
        document
    )

    assert chunks is not None

    assert isinstance(
        chunks,
        list
    )

    assert len(chunks) > 0

    return document, chunks


# ============================================================
# Test Chunk List
# ============================================================

def test_chunk_list():
    """
    驗證 Chunk 結果為有效 list。
    """

    _, chunks = create_chunks()

    assert isinstance(
        chunks,
        list
    )

    assert len(chunks) > 0

    print(
        "PASS: Chunk list validation"
    )

    print(
        f"      Chunk count: {len(chunks)}"
    )


# ============================================================
# Test Chunk Type
# ============================================================

def test_chunk_type():
    """
    確認所有 Chunk
    都是 LangChain Document。
    """

    _, chunks = create_chunks()

    for index, chunk in enumerate(
        chunks
    ):

        assert isinstance(
            chunk,
            Document
        ), (
            f"Chunk {index} is not LangChain Document."
        )

    print(
        "PASS: Chunk Document type validation"
    )


# ============================================================
# Test Chunk Content Type
# ============================================================

def test_chunk_content_type():
    """
    確認 Chunk.page_content
    是字串。
    """

    _, chunks = create_chunks()

    for index, chunk in enumerate(
        chunks
    ):

        assert isinstance(
            chunk.page_content,
            str
        ), (
            f"Chunk {index} page_content "
            "must be str."
        )

    print(
        "PASS: Chunk page_content type validation"
    )


# ============================================================
# Test Chunk Content Not Empty
# ============================================================

def test_chunk_content_not_empty():
    """
    確認 Chunk.page_content
    不是空內容。
    """

    _, chunks = create_chunks()

    for index, chunk in enumerate(
        chunks
    ):

        assert chunk.page_content.strip(), (
            f"Chunk {index} page_content is empty."
        )

    print(
        "PASS: Chunk content not empty"
    )


# ============================================================
# Test Chunk Length
# ============================================================

def test_chunk_length():
    """
    確認每個 Chunk
    不超過 CHUNK_SIZE。

    注意：

        最後一個 Chunk 可能明顯小於
        CHUNK_SIZE，這是正常行為。
    """

    _, chunks = create_chunks()

    for index, chunk in enumerate(
        chunks
    ):

        chunk_length = len(
            chunk.page_content
        )

        assert chunk_length <= CHUNK_SIZE, (
            f"Chunk {index} exceeds CHUNK_SIZE: "
            f"{chunk_length} > {CHUNK_SIZE}"
        )

    print(
        "PASS: Chunk length validation"
    )


# ============================================================
# Test Chunk Whitespace
# ============================================================

def test_chunk_whitespace():
    """
    確認 Chunk 不包含
    不必要的頭尾空白。
    """

    _, chunks = create_chunks()

    for index, chunk in enumerate(
        chunks
    ):

        assert (
            chunk.page_content
            == chunk.page_content.strip()
        ), (
            f"Chunk {index} contains "
            "leading or trailing whitespace."
        )

    print(
        "PASS: Chunk whitespace validation"
    )


# ============================================================
# Test Chunk Metadata
# ============================================================

def test_chunk_metadata():
    """
    確認每個 Chunk
    都具有 metadata。
    """

    _, chunks = create_chunks()

    for index, chunk in enumerate(
        chunks
    ):

        assert isinstance(
            chunk.metadata,
            dict
        ), (
            f"Chunk {index} metadata "
            "must be dict."
        )

    print(
        "PASS: Chunk metadata validation"
    )


# ============================================================
# Test Metadata Schema
# ============================================================

def test_metadata_schema():
    """
    確認每個 Chunk
    都包含完整的 RAG Metadata Schema。
    """

    _, chunks = create_chunks()

    expected_fields = set(
        EXPECTED_METADATA_FIELDS
    )

    for index, chunk in enumerate(
        chunks
    ):

        actual_fields = set(
            chunk.metadata.keys()
        )

        assert (
            actual_fields
            == expected_fields
        ), (
            f"Chunk {index} metadata schema "
            "does not match expected schema."
        )

    print(
        "PASS: Chunk metadata schema validation"
    )


# ============================================================
# Test Document ID
# ============================================================

def test_document_id():
    """
    確認每個 Chunk
    都具有有效 document_id。
    """

    _, chunks = create_chunks()

    for index, chunk in enumerate(
        chunks
    ):

        document_id = chunk.metadata.get(
            "document_id"
        )

        assert document_id, (
            f"Chunk {index} document_id is missing."
        )

        assert (
            document_id
            == TEST_DOCUMENT_ID
        ), (
            f"Chunk {index} document_id mismatch."
        )

    print(
        "PASS: Chunk document_id validation"
    )


# ============================================================
# Test Article Metadata
# ============================================================

def test_article_metadata():
    """
    確認每個 Chunk
    都具有文章識別資訊。
    """

    _, chunks = create_chunks()

    for index, chunk in enumerate(
        chunks
    ):

        assert chunk.metadata.get(
            "title"
        ), (
            f"Chunk {index} title is missing."
        )

        assert chunk.metadata.get(
            "url"
        ), (
            f"Chunk {index} url is missing."
        )

        assert chunk.metadata.get(
            "keyword"
        ), (
            f"Chunk {index} keyword is missing."
        )

        assert chunk.metadata.get(
            "crawl_time"
        ), (
            f"Chunk {index} crawl_time is missing."
        )

    print(
        "PASS: Chunk article metadata validation"
    )


# ============================================================
# Test AI Metadata
# ============================================================

def test_ai_metadata():
    """
    確認 AI Knowledge Metadata
    存在於每個 Chunk。
    """

    _, chunks = create_chunks()

    ai_fields = (
        "ai_summary",
        "ai_category",
        "ai_keywords",
        "ai_importance",
        "ai_confidence",
    )

    for index, chunk in enumerate(
        chunks
    ):

        for field in ai_fields:

            assert field in chunk.metadata, (
                f"Chunk {index} missing AI "
                f"metadata '{field}'."
            )

    print(
        "PASS: Chunk AI metadata validation"
    )


# ============================================================
# Test Chunk Consistency
# ============================================================

def test_chunk_consistency():
    """
    確認同一篇 Article 的所有 Chunk
    具有一致的 document_id、title、url。
    """

    _, chunks = create_chunks()

    reference = chunks[0].metadata

    for index, chunk in enumerate(
        chunks
    ):

        assert (
            chunk.metadata["document_id"]
            == reference["document_id"]
        ), (
            f"Chunk {index} document_id inconsistency."
        )

        assert (
            chunk.metadata["title"]
            == reference["title"]
        ), (
            f"Chunk {index} title inconsistency."
        )

        assert (
            chunk.metadata["url"]
            == reference["url"]
        ), (
            f"Chunk {index} URL inconsistency."
        )

    print(
        "PASS: Chunk metadata consistency"
    )


# ============================================================
# Test Chunk Content Integrity
# ============================================================

def test_chunk_content_integrity():
    """
    確認 Chunking 後仍然存在有效文章內容。

    本測試不要求：
        sum(chunk lengths) == source length

    因為 Chunk Overlap 會造成重複內容。
    """

    document, chunks = create_chunks()

    source_content = document.page_content

    assert source_content

    for index, chunk in enumerate(
        chunks
    ):

        assert chunk.page_content in source_content, (
            f"Chunk {index} contains content "
            "not found in source document."
        )

    print(
        "PASS: Chunk content integrity"
    )


# ============================================================
# Test Real Article Validation
# ============================================================

def test_real_article_validation():
    """
    使用真實文章完成完整 Chunk Validation。
    """

    document, chunks = create_chunks()

    assert (
        document.metadata["document_id"]
        == TEST_DOCUMENT_ID
    )

    assert len(chunks) > 0

    for index, chunk in enumerate(
        chunks
    ):

        assert isinstance(
            chunk,
            Document
        )

        assert chunk.page_content

        assert len(
            chunk.page_content
        ) <= CHUNK_SIZE

        assert (
            chunk.metadata["document_id"]
            == TEST_DOCUMENT_ID
        )

    print(
        "PASS: Real Article Chunk validation"
    )

    print(
        f"      Source length: "
        f"{len(document.page_content)}"
    )

    print(
        f"      Chunk count: "
        f"{len(chunks)}"
    )


# ============================================================
# Test Invalid Chunk Size
# ============================================================

def test_invalid_chunk_size():
    """
    測試超過 CHUNK_SIZE 的人工 Chunk
    可以被辨識為無效。

    注意：
        此測試只驗證 Validation 條件，
        不修改正式 DocumentSplitter。
    """

    invalid_chunk = Document(
        page_content="A" * (
            CHUNK_SIZE + 1
        ),
        metadata={
            "document_id": TEST_DOCUMENT_ID
        }
    )

    assert len(
        invalid_chunk.page_content
    ) > CHUNK_SIZE

    print(
        "PASS: Invalid chunk size detection"
    )


# ============================================================
# Test Invalid Chunk Content
# ============================================================

def test_invalid_chunk_content():
    """
    測試空 Chunk Content 可以被辨識。
    """

    invalid_chunk = Document(
        page_content="",
        metadata={
            "document_id": TEST_DOCUMENT_ID
        }
    )

    assert not invalid_chunk.page_content.strip()

    print(
        "PASS: Invalid chunk content detection"
    )


# ============================================================
# Main
# ============================================================

def main():
    """
    執行 RAG-2.4 Chunk Validation Test。
    """

    print("=" * 60)
    print(
        "RAG-2.4 Chunk Validation Test"
    )
    print("=" * 60)

    print()

    print(
        "Testing real RAG-2 Chunks..."
    )

    print()

    test_chunk_list()

    test_chunk_type()

    test_chunk_content_type()

    test_chunk_content_not_empty()

    test_chunk_length()

    test_chunk_whitespace()

    test_chunk_metadata()

    test_metadata_schema()

    test_document_id()

    test_article_metadata()

    test_ai_metadata()

    test_chunk_consistency()

    test_chunk_content_integrity()

    test_real_article_validation()

    test_invalid_chunk_size()

    test_invalid_chunk_content()

    print()

    print("=" * 60)
    print(
        "ALL RAG-2.4 CHUNK VALIDATION TESTS PASSED"
    )
    print("=" * 60)


if __name__ == "__main__":
    main()