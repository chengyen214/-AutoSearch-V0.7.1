"""
tests/V7_2/test_rag_document_chunking.py

AutoSearch V7

RAG-2.5

Chunking Test

功能：

    測試 RAG-2 DocumentChunking 主控流程。

完整資料流程：

    MCP
      ↓
    ArticleSource
      ↓
    Article
      ↓
    DocumentPreparation
      ↓
    Prepared LangChain Document
      ↓
    DocumentChunking
      ↓
    DocumentSplitter
      ↓
    Chunk Documents
      ↓
    RAG-3 Embedding

測試內容：

    1. DocumentChunking initialization
    2. Prepared Document → Chunks
    3. Chunk type
    4. Chunk content
    5. Chunk length
    6. Chunk metadata
    7. Document ID preservation
    8. Multiple Documents chunking
    9. RAG-3 readiness
    10. Invalid Document validation
    11. Invalid Documents validation
    12. Real Article end-to-end Chunking

本測試不負責：

    1. Embedding
    2. Qwen Embedding
    3. ChromaDB
    4. Retriever
    5. Context Builder
    6. LLM
"""


from langchain_core.documents import Document

from rag.document_preparation import (
    DocumentPreparation
)

from rag.chunking.document_chunking import (
    DocumentChunking
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

    assert isinstance(
        document.metadata,
        dict
    )

    return document


# ============================================================
# Create DocumentChunking
# ============================================================

def create_document_chunking():
    """
    建立 RAG-2 DocumentChunking。
    """

    return DocumentChunking()


# ============================================================
# Test Initialization
# ============================================================

def test_initialization():
    """
    確認 DocumentChunking
    可以正常初始化。
    """

    chunking = create_document_chunking()

    assert chunking is not None

    assert (
        chunking.document_splitter
        is not None
    )

    print(
        "PASS: DocumentChunking initialization"
    )


# ============================================================
# Test Single Document Chunking
# ============================================================

def test_chunk():
    """
    測試：

        Prepared Document
            ↓
        DocumentChunking
            ↓
        Chunks
    """

    document = create_prepared_document()

    chunking = create_document_chunking()

    chunks = chunking.chunk(
        document
    )

    assert chunks is not None

    assert isinstance(
        chunks,
        list
    )

    assert len(chunks) > 0

    print(
        "PASS: DocumentChunking single document"
    )

    print(
        f"      Chunk count: "
        f"{len(chunks)}"
    )


# ============================================================
# Test Chunk Type
# ============================================================

def test_chunk_type():
    """
    確認所有 Chunk
    都是 LangChain Document。
    """

    document = create_prepared_document()

    chunking = create_document_chunking()

    chunks = chunking.chunk(
        document
    )

    for index, chunk in enumerate(
        chunks
    ):

        assert isinstance(
            chunk,
            Document
        ), (
            f"Chunk {index} is not "
            "LangChain Document."
        )

    print(
        "PASS: Chunk Document type"
    )


# ============================================================
# Test Chunk Content
# ============================================================

def test_chunk_content():
    """
    確認所有 Chunk
    都有有效 page_content。
    """

    document = create_prepared_document()

    chunking = create_document_chunking()

    chunks = chunking.chunk(
        document
    )

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

        assert chunk.page_content.strip(), (
            f"Chunk {index} page_content "
            "cannot be empty."
        )

    print(
        "PASS: Chunk content"
    )


# ============================================================
# Test Chunk Length
# ============================================================

def test_chunk_length():
    """
    確認每個 Chunk
    不超過 CHUNK_SIZE。
    """

    document = create_prepared_document()

    chunking = create_document_chunking()

    chunks = chunking.chunk(
        document
    )

    for index, chunk in enumerate(
        chunks
    ):

        chunk_length = len(
            chunk.page_content
        )

        assert chunk_length <= CHUNK_SIZE, (
            f"Chunk {index} exceeds "
            f"CHUNK_SIZE={CHUNK_SIZE}: "
            f"{chunk_length}"
        )

    print(
        "PASS: Chunk length"
    )

    for index, chunk in enumerate(
        chunks
    ):

        print(
            f"      Chunk {index + 1}: "
            f"{len(chunk.page_content)} characters"
        )


# ============================================================
# Test Chunk Metadata
# ============================================================

def test_chunk_metadata():
    """
    確認每個 Chunk
    都保留正式 RAG Metadata。
    """

    document = create_prepared_document()

    chunking = create_document_chunking()

    chunks = chunking.chunk(
        document
    )

    expected_fields = set(
        EXPECTED_METADATA_FIELDS
    )

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

        actual_fields = set(
            chunk.metadata.keys()
        )

        assert (
            actual_fields
            == expected_fields
        ), (
            f"Chunk {index} metadata "
            "schema mismatch."
        )

    print(
        "PASS: Chunk metadata"
    )


# ============================================================
# Test Document ID Preservation
# ============================================================

def test_document_id_preservation():
    """
    確認所有 Chunk
    保留原始 document_id。
    """

    document = create_prepared_document()

    chunking = create_document_chunking()

    chunks = chunking.chunk(
        document
    )

    for index, chunk in enumerate(
        chunks
    ):

        assert (
            chunk.metadata["document_id"]
            == TEST_DOCUMENT_ID
        ), (
            f"Chunk {index} document_id "
            "does not match source."
        )

    print(
        "PASS: Document ID preservation"
    )


# ============================================================
# Test Metadata Value Preservation
# ============================================================

def test_metadata_value_preservation():
    """
    確認 Chunk metadata values
    與 Prepared Document 完全一致。
    """

    document = create_prepared_document()

    chunking = create_document_chunking()

    chunks = chunking.chunk(
        document
    )

    for index, chunk in enumerate(
        chunks
    ):

        assert (
            chunk.metadata
            == document.metadata
        ), (
            f"Chunk {index} metadata values "
            "do not match source."
        )

    print(
        "PASS: Metadata value preservation"
    )


# ============================================================
# Test Multiple Documents
# ============================================================

def test_chunk_documents():
    """
    測試多個 Prepared Documents
    的 Chunking。
    """

    document = create_prepared_document()

    documents = [
        document,
        document,
    ]

    chunking = create_document_chunking()

    chunks = chunking.chunk_documents(
        documents
    )

    assert chunks is not None

    assert isinstance(
        chunks,
        list
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

        assert (
            chunk.metadata["document_id"]
            == TEST_DOCUMENT_ID
        )

    print(
        "PASS: Multiple Documents chunking"
    )

    print(
        f"      Input documents: "
        f"{len(documents)}"
    )

    print(
        f"      Output chunks: "
        f"{len(chunks)}"
    )


# ============================================================
# Test RAG-3 Readiness
# ============================================================

def test_rag3_readiness():
    """
    確認 Chunks 可以直接交給
    RAG-3 Embedding。

    本測試不執行 Embedding。
    """

    document = create_prepared_document()

    chunking = create_document_chunking()

    chunks = chunking.chunk(
        document
    )

    assert len(chunks) > 0

    for index, chunk in enumerate(
        chunks
    ):

        assert isinstance(
            chunk,
            Document
        )

        assert isinstance(
            chunk.page_content,
            str
        )

        assert chunk.page_content.strip()

        assert isinstance(
            chunk.metadata,
            dict
        )

        assert (
            chunk.metadata["document_id"]
            == document.metadata["document_id"]
        )

    print(
        "PASS: RAG-3 Embedding readiness"
    )


# ============================================================
# Test Source Document Integrity
# ============================================================

def test_source_document_integrity():
    """
    確認 Chunking 不會修改
    原始 Prepared Document。
    """

    document = create_prepared_document()

    original_content = (
        document.page_content
    )

    original_metadata = dict(
        document.metadata
    )

    chunking = create_document_chunking()

    chunks = chunking.chunk(
        document
    )

    assert len(chunks) > 0

    assert (
        document.page_content
        == original_content
    )

    assert (
        document.metadata
        == original_metadata
    )

    print(
        "PASS: Source Document integrity"
    )


# ============================================================
# Test None Document
# ============================================================

def test_none_document():
    """
    測試 Document=None。
    """

    chunking = create_document_chunking()

    try:

        chunking.chunk(
            None
        )

    except ValueError:

        print(
            "PASS: None Document validation"
        )

        return

    raise AssertionError(
        "None Document should raise ValueError."
    )


# ============================================================
# Test Invalid Document Type
# ============================================================

def test_invalid_document_type():
    """
    測試輸入不是 LangChain Document。
    """

    chunking = create_document_chunking()

    try:

        chunking.chunk(
            "invalid document"
        )

    except TypeError:

        print(
            "PASS: Invalid Document type validation"
        )

        return

    raise AssertionError(
        "Invalid Document type should raise TypeError."
    )


# ============================================================
# Test Empty Document Content
# ============================================================

def test_empty_document_content():
    """
    測試空 page_content。
    """

    document = Document(
        page_content="",
        metadata={}
    )

    chunking = create_document_chunking()

    try:

        chunking.chunk(
            document
        )

    except ValueError:

        print(
            "PASS: Empty Document content validation"
        )

        return

    raise AssertionError(
        "Empty Document content should raise ValueError."
    )


# ============================================================
# Test None Documents
# ============================================================

def test_none_documents():
    """
    測試 documents=None。
    """

    chunking = create_document_chunking()

    try:

        chunking.chunk_documents(
            None
        )

    except ValueError:

        print(
            "PASS: None Documents validation"
        )

        return

    raise AssertionError(
        "None Documents should raise ValueError."
    )


# ============================================================
# Test Invalid Documents Type
# ============================================================

def test_invalid_documents_type():
    """
    測試 documents 不是 list。
    """

    chunking = create_document_chunking()

    try:

        chunking.chunk_documents(
            "invalid"
        )

    except TypeError:

        print(
            "PASS: Invalid Documents type validation"
        )

        return

    raise AssertionError(
        "Non-list Documents should raise TypeError."
    )


# ============================================================
# Test Empty Documents
# ============================================================

def test_empty_documents():
    """
    測試空 documents list。
    """

    chunking = create_document_chunking()

    try:

        chunking.chunk_documents(
            []
        )

    except ValueError:

        print(
            "PASS: Empty Documents validation"
        )

        return

    raise AssertionError(
        "Empty Documents should raise ValueError."
    )


# ============================================================
# Test Real Article End-to-End
# ============================================================

def test_real_article_end_to_end():
    """
    真實 Article 完整執行：

        MCP
          ↓
        RAG-1 Document Preparation
          ↓
        Prepared Document
          ↓
        RAG-2 DocumentChunking
          ↓
        Chunks
    """

    document = create_prepared_document()

    chunking = create_document_chunking()

    chunks = chunking.chunk(
        document
    )

    assert len(chunks) >= 1

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
        "PASS: Real Article end-to-end Chunking"
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
# Main
# ============================================================

def main():
    """
    執行 RAG-2.5 Chunking Test。
    """

    print("=" * 60)
    print(
        "RAG-2.5 Chunking Test"
    )
    print("=" * 60)

    print()

    print(
        "Testing complete RAG-2 Chunking workflow..."
    )

    print()

    test_initialization()

    test_chunk()

    test_chunk_type()

    test_chunk_content()

    test_chunk_length()

    test_chunk_metadata()

    test_document_id_preservation()

    test_metadata_value_preservation()

    test_chunk_documents()

    test_rag3_readiness()

    test_source_document_integrity()

    test_none_document()

    test_invalid_document_type()

    test_empty_document_content()

    test_none_documents()

    test_invalid_documents_type()

    test_empty_documents()

    test_real_article_end_to_end()

    print()

    print("=" * 60)
    print(
        "ALL RAG-2 CHUNKING TESTS PASSED"
    )
    print("=" * 60)


if __name__ == "__main__":
    main()