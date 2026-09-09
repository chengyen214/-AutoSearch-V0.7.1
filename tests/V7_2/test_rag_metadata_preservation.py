"""
tests/V7_2/test_rag_metadata_preservation.py

AutoSearch V7

RAG-2.3

Metadata Preservation Test

功能：

    驗證 RAG-2.2 Document Splitter
    產生的每個 Chunk
    是否完整保留 RAG-1.3 Document Metadata。

資料流程：

    RAG-1.5
    Prepared LangChain Document
            ↓
    RAG-2.2
    DocumentSplitter
            ↓
    Chunk Documents
            ↓
    RAG-2.3
    Metadata Preservation Validation

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
    9. LLM
"""


from langchain_core.documents import Document

from rag.document_preparation import (
    DocumentPreparation
)

from rag.chunking.splitter import (
    DocumentSplitter
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

    assert isinstance(
        document.metadata,
        dict
    )

    return document


# ============================================================
# Create Chunks
# ============================================================

def create_chunks():
    """
    使用 RAG-2.2 DocumentSplitter
    將 Prepared Document 切成 Chunks。
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
# Test Source Metadata Schema
# ============================================================

def test_source_metadata_schema():
    """
    確認 RAG-1.5 Prepared Document
    使用正式的 11 個 Metadata 欄位。
    """

    document = create_prepared_document()

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
        "Source Document metadata schema "
        "does not match expected schema."
    )

    print(
        "PASS: Source metadata schema"
    )

    print(
        f"      Metadata fields: "
        f"{len(metadata_fields)}"
    )


# ============================================================
# Test Chunk Metadata Exists
# ============================================================

def test_chunk_metadata_exists():
    """
    確認每個 Chunk 都有 metadata。
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

        assert chunk.metadata is not None

        assert isinstance(
            chunk.metadata,
            dict
        )

    print(
        "PASS: Chunk metadata exists"
    )


# ============================================================
# Test Metadata Fields Preservation
# ============================================================

def test_metadata_fields_preserved():
    """
    確認每個 Chunk
    都包含完整 Metadata Schema。
    """

    _, chunks = create_chunks()

    for index, chunk in enumerate(
        chunks
    ):

        metadata_fields = set(
            chunk.metadata.keys()
        )

        expected_fields = set(
            EXPECTED_METADATA_FIELDS
        )

        assert (
            metadata_fields
            == expected_fields
        ), (
            f"Chunk {index} metadata schema "
            "does not match source schema."
        )

    print(
        "PASS: Chunk metadata schema preservation"
    )


# ============================================================
# Test Metadata Values Preservation
# ============================================================

def test_metadata_values_preserved():
    """
    確認每個 Chunk 的 Metadata value
    與原始 Prepared Document 完全一致。
    """

    document, chunks = create_chunks()

    source_metadata = document.metadata

    for index, chunk in enumerate(
        chunks
    ):

        for field in EXPECTED_METADATA_FIELDS:

            assert (
                chunk.metadata[field]
                == source_metadata[field]
            ), (
                f"Chunk {index} metadata field "
                f"'{field}' value was changed."
            )

    print(
        "PASS: Metadata values preservation"
    )


# ============================================================
# Test Document ID Preservation
# ============================================================

def test_document_id_preservation():
    """
    確認所有 Chunk
    保留相同 document_id。
    """

    document, chunks = create_chunks()

    source_document_id = document.metadata[
        "document_id"
    ]

    assert (
        source_document_id
        == TEST_DOCUMENT_ID
    )

    for index, chunk in enumerate(
        chunks
    ):

        assert (
            chunk.metadata["document_id"]
            == source_document_id
        ), (
            f"Chunk {index} document_id "
            "does not match source."
        )

    print(
        "PASS: document_id preservation"
    )


# ============================================================
# Test Article Identity Preservation
# ============================================================

def test_article_identity_preservation():
    """
    確認每個 Chunk
    仍然指向同一篇 Article。
    """

    document, chunks = create_chunks()

    source_metadata = document.metadata

    for index, chunk in enumerate(
        chunks
    ):

        assert (
            chunk.metadata["document_id"]
            == source_metadata["document_id"]
        )

        assert (
            chunk.metadata["title"]
            == source_metadata["title"]
        )

        assert (
            chunk.metadata["url"]
            == source_metadata["url"]
        )

    print(
        "PASS: Article identity preservation"
    )


# ============================================================
# Test AI Metadata Preservation
# ============================================================

def test_ai_metadata_preservation():
    """
    確認 AI Knowledge Metadata
    在 Chunking 後沒有遺失。
    """

    document, chunks = create_chunks()

    source_metadata = document.metadata

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

            assert (
                field in chunk.metadata
            ), (
                f"Chunk {index} is missing "
                f"AI metadata '{field}'."
            )

            assert (
                chunk.metadata[field]
                == source_metadata[field]
            ), (
                f"Chunk {index} AI metadata "
                f"'{field}' was changed."
            )

    print(
        "PASS: AI metadata preservation"
    )


# ============================================================
# Test No Metadata Mutation
# ============================================================

def test_no_metadata_mutation():
    """
    確認 Chunking 不會修改
    原始 Prepared Document metadata。
    """

    document = create_prepared_document()

    original_metadata = dict(
        document.metadata
    )

    splitter = DocumentSplitter()

    chunks = splitter.split_document(
        document
    )

    assert len(chunks) > 0

    assert (
        document.metadata
        == original_metadata
    ), (
        "Source Document metadata was mutated."
    )

    print(
        "PASS: Source metadata immutability"
    )


# ============================================================
# Test Metadata Consistency Across Chunks
# ============================================================

def test_metadata_consistency_across_chunks():
    """
    確認同一篇文章產生的所有 Chunk
    使用一致的 Metadata。
    """

    _, chunks = create_chunks()

    reference_metadata = chunks[
        0
    ].metadata

    for index, chunk in enumerate(
        chunks
    ):

        assert (
            chunk.metadata
            == reference_metadata
        ), (
            f"Chunk {index} metadata "
            "differs from other chunks."
        )

    print(
        "PASS: Metadata consistency across chunks"
    )


# ============================================================
# Test No Unexpected Metadata
# ============================================================

def test_no_unexpected_metadata():
    """
    確認 Chunk 沒有出現
    非正式 Schema 的 Metadata 欄位。
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
            f"Chunk {index} contains "
            "unexpected metadata fields."
        )

    print(
        "PASS: No unexpected chunk metadata"
    )


# ============================================================
# Test Real Article
# ============================================================

def test_real_article_metadata():
    """
    使用目前真實文章
    驗證 Metadata Preservation。
    """

    document, chunks = create_chunks()

    assert document.metadata[
        "document_id"
    ] == TEST_DOCUMENT_ID

    for index, chunk in enumerate(
        chunks
    ):

        assert (
            chunk.metadata["document_id"]
            == TEST_DOCUMENT_ID
        )

        assert (
            chunk.metadata["title"]
            == document.metadata["title"]
        )

        assert (
            chunk.metadata["url"]
            == document.metadata["url"]
        )

        assert (
            chunk.metadata["ai_category"]
            == "Semiconductor"
        )

    print(
        "PASS: Real Article metadata preservation"
    )

    print(
        f"      Chunk count: "
        f"{len(chunks)}"
    )

    print(
        f"      Document ID: "
        f"{TEST_DOCUMENT_ID}"
    )


# ============================================================
# Main
# ============================================================

def main():
    """
    執行 RAG-2.3 Metadata Preservation Test。
    """

    print("=" * 60)
    print(
        "RAG-2.3 Metadata Preservation Test"
    )
    print("=" * 60)

    print()

    print(
        "Testing real RAG-1 Prepared Document..."
    )

    print()

    test_source_metadata_schema()

    test_chunk_metadata_exists()

    test_metadata_fields_preserved()

    test_metadata_values_preserved()

    test_document_id_preservation()

    test_article_identity_preservation()

    test_ai_metadata_preservation()

    test_no_metadata_mutation()

    test_metadata_consistency_across_chunks()

    test_no_unexpected_metadata()

    test_real_article_metadata()

    print()

    print("=" * 60)
    print(
        "ALL RAG-2.3 METADATA PRESERVATION TESTS PASSED"
    )
    print("=" * 60)


if __name__ == "__main__":
    main()