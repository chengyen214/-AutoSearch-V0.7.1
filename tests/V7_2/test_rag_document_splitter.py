"""
tests/V7_2/test_rag_document_splitter.py

AutoSearch V7

RAG-2.2

Document Splitter Test

測試內容：

    1. 透過 DocumentPreparation 取得真實 Prepared Document
    2. Document → Chunks
    3. Chunk 是否為 LangChain Document
    4. Chunk 是否有 page_content
    5. Chunk 數量是否大於 0
    6. Chunk 長度是否符合設定
    7. 每個 Chunk 是否保留 Metadata
    8. 單一 Document Split
    9. 多 Documents Split
    10. Invalid Document validation

實際資料流程：

    MCP
      ↓
    ArticleSource
      ↓
    Article
      ↓
    ArticleDocument
      ↓
    ContentCleaner
      ↓
    Prepared Document
      ↓
    DocumentSplitter
      ↓
    Chunks

目前設定：

    CHUNK_SPLITTER = recursive
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200

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

from rag.chunking.splitter import (
    DocumentSplitter
)

from rag.chunking.config import (
    CHUNK_SIZE,
    CHUNK_OVERLAP,
)


# ============================================================
# Test Article Identifier
# ============================================================

TEST_DOCUMENT_ID = (
    "d9ce4740c3f0b6f1d260c094c0549f68727187b0a2b57c94f6308b4df9fd9d13"
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
# Create Splitter
# ============================================================

def create_splitter():
    """
    建立 DocumentSplitter。
    """

    return DocumentSplitter()


# ============================================================
# Test Splitter Initialization
# ============================================================

def test_splitter_initialization():
    """
    確認 DocumentSplitter
    正確載入目前設定。
    """

    splitter = create_splitter()

    assert splitter is not None

    assert (
        splitter.chunk_size
        == CHUNK_SIZE
    )

    assert (
        splitter.chunk_overlap
        == CHUNK_OVERLAP
    )

    assert splitter.splitter is not None

    print(
        "PASS: DocumentSplitter initialization"
    )

    print(
        f"      Chunk Size: "
        f"{splitter.chunk_size}"
    )

    print(
        f"      Chunk Overlap: "
        f"{splitter.chunk_overlap}"
    )


# ============================================================
# Test Single Document Split
# ============================================================

def test_split_document():
    """
    測試單一 Prepared Document
    是否可以成功切割。
    """

    document = create_prepared_document()

    splitter = create_splitter()

    chunks = splitter.split_document(
        document
    )

    assert chunks is not None

    assert isinstance(
        chunks,
        list
    )

    assert len(chunks) > 0

    print(
        "PASS: Single Document splitting"
    )

    print(
        f"      Chunk count: "
        f"{len(chunks)}"
    )


# ============================================================
# Test Chunk Document Type
# ============================================================

def test_chunk_document_type():
    """
    確認所有 Chunk
    都是 LangChain Document。
    """

    document = create_prepared_document()

    splitter = create_splitter()

    chunks = splitter.split_document(
        document
    )

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

    splitter = create_splitter()

    chunks = splitter.split_document(
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
            "is not str."
        )

        assert chunk.page_content.strip(), (
            f"Chunk {index} page_content is empty."
        )

    print(
        "PASS: Chunk page_content"
    )


# ============================================================
# Test Chunk Length
# ============================================================

def test_chunk_length():
    """
    確認 Chunk 長度不應超過
    CHUNK_SIZE。

    注意：

        RecursiveCharacterTextSplitter
        會依分隔符號進行切割，
        因此實際 Chunk 長度可能小於 CHUNK_SIZE。
    """

    document = create_prepared_document()

    splitter = create_splitter()

    chunks = splitter.split_document(
        document
    )

    for index, chunk in enumerate(
        chunks
    ):

        assert len(
            chunk.page_content
        ) <= CHUNK_SIZE, (
            f"Chunk {index} exceeds CHUNK_SIZE: "
            f"{len(chunk.page_content)} > {CHUNK_SIZE}"
        )

    print(
        "PASS: Chunk length validation"
    )

    for index, chunk in enumerate(
        chunks
    ):

        print(
            f"      Chunk {index + 1}: "
            f"{len(chunk.page_content)} characters"
        )


# ============================================================
# Test Metadata Preservation
# ============================================================

def test_metadata_preservation():
    """
    確認 Splitter 產生的 Chunk
    保留原始 Document metadata。
    """

    document = create_prepared_document()

    splitter = create_splitter()

    chunks = splitter.split_document(
        document
    )

    assert len(chunks) > 0

    for index, chunk in enumerate(
        chunks
    ):

        assert chunk.metadata is not None

        assert (
            chunk.metadata
            == document.metadata
        ), (
            f"Chunk {index} metadata "
            "does not match source document metadata."
        )

    print(
        "PASS: Metadata preservation"
    )


# ============================================================
# Test Document ID Preservation
# ============================================================

def test_document_id_preservation():
    """
    確認每個 Chunk
    保留原始 document_id。
    """

    document = create_prepared_document()

    splitter = create_splitter()

    chunks = splitter.split_document(
        document
    )

    for index, chunk in enumerate(
        chunks
    ):

        assert (
            chunk.metadata["document_id"]
            == document.metadata["document_id"]
        ), (
            f"Chunk {index} document_id mismatch."
        )

    print(
        "PASS: Document ID preservation"
    )


# ============================================================
# Test Multiple Documents Split
# ============================================================

def test_split_documents():
    """
    測試多個 Prepared Documents
    是否可以成功切割。

    使用同一篇真實文章建立兩份 Document
    只驗證 API 的多 Documents 行為。
    """

    document = create_prepared_document()

    documents = [
        document,
        document,
    ]

    splitter = create_splitter()

    chunks = splitter.split_documents(
        documents
    )

    assert chunks is not None

    assert isinstance(
        chunks,
        list
    )

    assert len(chunks) > 0

    print(
        "PASS: Multiple Documents splitting"
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
# Test None Document
# ============================================================

def test_none_document():
    """
    測試 Document=None。
    """

    splitter = create_splitter()

    try:

        splitter.split_document(
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
# Test Invalid Documents Type
# ============================================================

def test_invalid_documents_type():
    """
    測試 split_documents()
    接收到非 list。
    """

    splitter = create_splitter()

    try:

        splitter.split_documents(
            "invalid"
        )

    except TypeError:

        print(
            "PASS: Documents type validation"
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
    測試空 Documents list。
    """

    splitter = create_splitter()

    try:

        splitter.split_documents(
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
# Test Invalid Chunk Configuration
# ============================================================

def test_invalid_chunk_configuration():
    """
    測試無效 Chunk Configuration。
    """

    try:

        DocumentSplitter(
            chunk_size=0,
            chunk_overlap=0
        )

    except ValueError:

        print(
            "PASS: Invalid chunk_size validation"
        )

    else:

        raise AssertionError(
            "chunk_size=0 should raise ValueError."
        )

    try:

        DocumentSplitter(
            chunk_size=100,
            chunk_overlap=100
        )

    except ValueError:

        print(
            "PASS: Invalid chunk_overlap validation"
        )

    else:

        raise AssertionError(
            "chunk_overlap >= chunk_size "
            "should raise ValueError."
        )


# ============================================================
# Test Real Article Chunking
# ============================================================

def test_real_article_chunking():
    """
    使用目前真實文章
    執行完整 Chunking。

    目前文章長度約 821 characters，
    小於 CHUNK_SIZE 1000，
    因此預期通常只會產生 1 個 Chunk。

    這裡不硬性要求 Chunk 數量，
    只確認至少產生一個有效 Chunk。
    """

    document = create_prepared_document()

    splitter = create_splitter()

    chunks = splitter.split_document(
        document
    )

    assert len(chunks) >= 1

    total_length = sum(
        len(chunk.page_content)
        for chunk in chunks
    )

    assert total_length > 0

    print(
        "PASS: Real Article Chunking"
    )

    print(
        f"      Source length: "
        f"{len(document.page_content)}"
    )

    print(
        f"      Chunk count: "
        f"{len(chunks)}"
    )

    print(
        f"      Total chunk content length: "
        f"{total_length}"
    )


# ============================================================
# Main
# ============================================================

def main():
    """
    執行 RAG-2.2 Document Splitter Test。
    """

    print("=" * 60)
    print(
        "RAG-2.2 Document Splitter Test"
    )
    print("=" * 60)

    print()

    print(
        "Testing real RAG-1 Prepared Document..."
    )

    print()

    test_splitter_initialization()

    test_split_document()

    test_chunk_document_type()

    test_chunk_content()

    test_chunk_length()

    test_metadata_preservation()

    test_document_id_preservation()

    test_split_documents()

    test_real_article_chunking()

    test_none_document()

    test_invalid_documents_type()

    test_empty_documents()

    test_invalid_chunk_configuration()

    print()

    print("=" * 60)
    print(
        "ALL RAG-2.2 DOCUMENT SPLITTER TESTS PASSED"
    )
    print("=" * 60)


if __name__ == "__main__":
    main()