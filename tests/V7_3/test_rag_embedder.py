"""
tests/V7_3/test_rag_embedder.py

AutoSearch V7

RAG-3.3

Chunk → Embedding Test

功能：

    測試 RAG-3.3 Embedder
    是否可以將 RAG-2 Chunks
    轉換成 Embedding Vectors。

完整資料流程：

    MCP
      ↓
    RAG-1 Document Preparation
      ↓
    Prepared Document
      ↓
    RAG-2 Document Chunking
      ↓
    Chunk Documents
      ↓
    RAG-3.3 Embedder
      ↓
    RAG-3.2 EmbeddingModel
      ↓
    Qwen/Qwen3-Embedding-0.6B
      ↓
    1024 維 Embedding Vectors

測試內容：

    1. Embedder initialization
    2. Embedding dimension
    3. Real RAG-2 Chunk retrieval
    4. Single Document → Embedding
    5. Single text → Embedding
    6. Multiple Documents → Embeddings
    7. Embedding count validation
    8. Embedding dimension validation
    9. Vector type validation
    10. Document embedding consistency
    11. Real Article embedding
    12. Empty / invalid input validation

注意：

    本測試會真正載入 Qwen Embedding Model
    並產生 Embedding。

    為避免重複載入模型，
    所有測試共用同一個 Embedder instance。

    這是 RAG-3.3 的正式測試。

本測試不負責：

    1. ChromaDB
    2. Retriever
    3. Context Builder
    4. LLM
"""


from langchain_core.documents import Document

from rag.document_preparation import (
    DocumentPreparation
)

from rag.chunking.document_chunking import (
    DocumentChunking
)

from rag.embedding.embedder import (
    Embedder
)

from rag.embedding.config import (
    EMBEDDING_MODEL,
    EMBEDDING_DIMENSION,
)


# ============================================================
# Test Article Identifier
# ============================================================

TEST_DOCUMENT_ID = (
    "d9ce4740c3f0b6f1d260c094c0549f68727187b0a2b57c94f6308b4df9fd9d13"
)


# ============================================================
# Shared Objects
# ============================================================

_EMBEDDER = None
_CHUNKS = None
_PREPARED_DOCUMENT = None


def get_embedder():
    """
    取得共用 Embedder。

    整個測試只建立一次，
    避免每個 test 重複載入 Qwen Model。
    """

    global _EMBEDDER

    if _EMBEDDER is None:

        _EMBEDDER = Embedder()

    return _EMBEDDER


# ============================================================
# Create Prepared Document
# ============================================================

def create_prepared_document():
    """
    透過 RAG-1 DocumentPreparation
    取得真實 Prepared Document。

    整個測試只建立一次。
    """

    global _PREPARED_DOCUMENT

    if _PREPARED_DOCUMENT is None:

        preparation = DocumentPreparation()

        _PREPARED_DOCUMENT = (
            preparation.prepare_by_document_id(
                TEST_DOCUMENT_ID
            )
        )

        assert _PREPARED_DOCUMENT is not None

        assert isinstance(
            _PREPARED_DOCUMENT,
            Document
        )

        assert _PREPARED_DOCUMENT.page_content

    return _PREPARED_DOCUMENT


# ============================================================
# Create Real Chunks
# ============================================================

def create_chunks():
    """
    透過 RAG-2 DocumentChunking
    取得真實 Chunk Documents。

    整個測試只建立一次。
    """

    global _CHUNKS

    if _CHUNKS is None:

        document = create_prepared_document()

        chunking = DocumentChunking()

        _CHUNKS = chunking.chunk(
            document
        )

        assert _CHUNKS is not None

        assert isinstance(
            _CHUNKS,
            list
        )

        assert len(_CHUNKS) > 0

    return _CHUNKS


# ============================================================
# Test Initialization
# ============================================================

def test_initialization():
    """
    測試 Embedder 是否正常初始化。
    """

    embedder = get_embedder()

    assert embedder is not None

    assert (
        embedder.embedding_model
        is not None
    )

    assert (
        embedder.model
        is not None
    )

    print(
        "PASS: Embedder initialization"
    )


# ============================================================
# Test Embedding Model Name
# ============================================================

def test_embedding_model_name():
    """
    確認 Embedding Model。
    """

    embedder = get_embedder()

    assert (
        embedder.embedding_model.model_name
        == EMBEDDING_MODEL
    )

    print(
        "PASS: Embedding model name"
    )

    print(
        f"      Model: "
        f"{embedder.embedding_model.model_name}"
    )


# ============================================================
# Test Embedding Dimension
# ============================================================

def test_embedding_dimension():
    """
    確認 Embedder 使用正確的
    Embedding Dimension。
    """

    embedder = get_embedder()

    assert (
        embedder.get_dimension()
        == EMBEDDING_DIMENSION
    )

    assert (
        embedder.get_dimension()
        == 1024
    )

    print(
        "PASS: Embedding dimension"
    )

    print(
        f"      Dimension: "
        f"{embedder.get_dimension()}"
    )


# ============================================================
# Test Real Chunk Retrieval
# ============================================================

def test_real_chunk_retrieval():
    """
    確認 RAG-3.3 的輸入
    確實來自 RAG-2 真實 Chunk。
    """

    document = create_prepared_document()

    chunks = create_chunks()

    assert len(chunks) > 0

    for index, chunk in enumerate(
        chunks
    ):

        assert isinstance(
            chunk,
            Document
        ), (
            f"Chunk {index} is not "
            "a LangChain Document."
        )

        assert chunk.page_content

        assert (
            chunk.metadata["document_id"]
            == document.metadata["document_id"]
        )

    print(
        "PASS: Real RAG-2 Chunk retrieval"
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
# Test Single Text Embedding
# ============================================================

def test_embed_text():
    """
    測試單一文字 → Embedding。
    """

    embedder = get_embedder()

    text = (
        "第三代半導體氮化鎵與 AI 資料中心需求持續成長。"
    )

    vector = embedder.embed_text(
        text
    )

    assert vector is not None

    assert isinstance(
        vector,
        list
    )

    assert len(
        vector
    ) == EMBEDDING_DIMENSION

    for value in vector:

        assert isinstance(
            value,
            (float, int)
        )

    print(
        "PASS: Text → Embedding"
    )

    print(
        f"      Vector dimension: "
        f"{len(vector)}"
    )


# ============================================================
# Test Single Document Embedding
# ============================================================

def test_embed_document():
    """
    測試單一 Chunk Document
    → Embedding。
    """

    chunks = create_chunks()

    embedder = get_embedder()

    document = chunks[0]

    vector = embedder.embed_document(
        document
    )

    assert vector is not None

    assert isinstance(
        vector,
        list
    )

    assert (
        len(vector)
        == EMBEDDING_DIMENSION
    )

    print(
        "PASS: Document → Embedding"
    )

    print(
        f"      Vector dimension: "
        f"{len(vector)}"
    )


# ============================================================
# Test Multiple Documents Embedding
# ============================================================

def test_embed_documents():
    """
    測試多個 Chunk Documents
    → Embedding Vectors。
    """

    chunks = create_chunks()

    embedder = get_embedder()

    vectors = embedder.embed_documents(
        chunks
    )

    assert vectors is not None

    assert isinstance(
        vectors,
        list
    )

    assert (
        len(vectors)
        == len(chunks)
    )

    for index, vector in enumerate(
        vectors
    ):

        assert isinstance(
            vector,
            list
        ), (
            f"Vector {index} is not list."
        )

        assert (
            len(vector)
            == EMBEDDING_DIMENSION
        ), (
            f"Vector {index} dimension mismatch."
        )

    print(
        "PASS: Multiple Documents → Embeddings"
    )

    print(
        f"      Documents: "
        f"{len(chunks)}"
    )

    print(
        f"      Embeddings: "
        f"{len(vectors)}"
    )


# ============================================================
# Test Embedding Count
# ============================================================

def test_embedding_count():
    """
    確認：

        1 Chunk
            ↓
        1 Embedding

    N Chunks
            ↓
        N Embeddings
    """

    chunks = create_chunks()

    embedder = get_embedder()

    vectors = embedder.embed_documents(
        chunks
    )

    assert (
        len(vectors)
        == len(chunks)
    )

    print(
        "PASS: Embedding count"
    )


# ============================================================
# Test Embedding Vector Dimension
# ============================================================

def test_embedding_vector_dimension():
    """
    確認所有 Embedding
    都是 1024 維。
    """

    chunks = create_chunks()

    embedder = get_embedder()

    vectors = embedder.embed_documents(
        chunks
    )

    for index, vector in enumerate(
        vectors
    ):

        assert (
            len(vector)
            == EMBEDDING_DIMENSION
        ), (
            f"Embedding {index} dimension "
            "does not equal "
            f"{EMBEDDING_DIMENSION}."
        )

    print(
        "PASS: All embedding vector dimensions"
    )


# ============================================================
# Test Vector Values
# ============================================================

def test_vector_values():
    """
    確認 Embedding Vector
    每個元素都是 numeric。
    """

    chunks = create_chunks()

    embedder = get_embedder()

    vectors = embedder.embed_documents(
        chunks
    )

    for index, vector in enumerate(
        vectors
    ):

        for value in vector:

            assert isinstance(
                value,
                (float, int)
            ), (
                f"Embedding {index} "
                "contains non-numeric value."
            )

    print(
        "PASS: Embedding vector values"
    )


# ============================================================
# Test Document Embedding Consistency
# ============================================================

def test_document_embedding_consistency():
    """
    確認同一個 Document
    重複 Embedding 後結果一致。
    """

    chunks = create_chunks()

    embedder = get_embedder()

    document = chunks[0]

    vector_1 = embedder.embed_document(
        document
    )

    vector_2 = embedder.embed_document(
        document
    )

    assert len(vector_1) == len(vector_2)

    assert (
        vector_1
        == vector_2
    )

    print(
        "PASS: Document embedding consistency"
    )


# ============================================================
# Test Real Article Embedding
# ============================================================

def test_real_article_embedding():
    """
    使用目前真實 Article 的 Chunk
    執行正式 Embedding。
    """

    document = create_prepared_document()

    chunks = create_chunks()

    embedder = get_embedder()

    vectors = embedder.embed_documents(
        chunks
    )

    assert len(vectors) == len(chunks)

    assert (
        document.metadata["document_id"]
        == TEST_DOCUMENT_ID
    )

    for index, vector in enumerate(
        vectors
    ):

        assert len(
            vector
        ) == EMBEDDING_DIMENSION

        assert any(
            value != 0
            for value in vector
        ), (
            f"Embedding {index} "
            "contains only zero values."
        )

    print(
        "PASS: Real Article → Embedding"
    )

    print(
        f"      Document ID: "
        f"{TEST_DOCUMENT_ID}"
    )

    print(
        f"      Chunk count: "
        f"{len(chunks)}"
    )

    print(
        f"      Embedding count: "
        f"{len(vectors)}"
    )


# ============================================================
# Test None Text
# ============================================================

def test_none_text():
    """
    測試 text=None。

    不需要重新載入模型；
    Embedder 應在輸入驗證階段直接拒絕。
    """

    embedder = get_embedder()

    try:

        embedder.embed_text(
            None
        )

    except ValueError:

        print(
            "PASS: None text validation"
        )

        return

    raise AssertionError(
        "None text should raise ValueError."
    )


# ============================================================
# Test Invalid Text Type
# ============================================================

def test_invalid_text_type():
    """
    測試 text 不是 str。
    """

    embedder = get_embedder()

    try:

        embedder.embed_text(
            12345
        )

    except TypeError:

        print(
            "PASS: Invalid text type validation"
        )

        return

    raise AssertionError(
        "Non-string text should raise TypeError."
    )


# ============================================================
# Test Empty Text
# ============================================================

def test_empty_text():
    """
    測試空文字。
    """

    embedder = get_embedder()

    try:

        embedder.embed_text(
            "   "
        )

    except ValueError:

        print(
            "PASS: Empty text validation"
        )

        return

    raise AssertionError(
        "Empty text should raise ValueError."
    )


# ============================================================
# Test None Document
# ============================================================

def test_none_document():
    """
    測試 Document=None。
    """

    embedder = get_embedder()

    try:

        embedder.embed_document(
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
    測試非 LangChain Document。
    """

    embedder = get_embedder()

    try:

        embedder.embed_document(
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
# Test None Documents
# ============================================================

def test_none_documents():
    """
    測試 documents=None。
    """

    embedder = get_embedder()

    try:

        embedder.embed_documents(
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

    embedder = get_embedder()

    try:

        embedder.embed_documents(
            "invalid documents"
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

    embedder = get_embedder()

    try:

        embedder.embed_documents(
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
# Main
# ============================================================

def main():
    """
    執行 RAG-3.3 Embedder Test。
    """

    print("=" * 60)
    print(
        "RAG-3.3 Chunk → Embedding Test"
    )
    print("=" * 60)

    print()

    print(
        "Testing real RAG-2 Chunks..."
    )

    print()

    test_initialization()

    test_embedding_model_name()

    test_embedding_dimension()

    test_real_chunk_retrieval()

    print()

    print(
        "Testing Embedding generation..."
    )

    print()

    test_embed_text()

    test_embed_document()

    test_embed_documents()

    test_embedding_count()

    test_embedding_vector_dimension()

    test_vector_values()

    test_document_embedding_consistency()

    test_real_article_embedding()

    print()

    print(
        "Testing input validation..."
    )

    print()

    test_none_text()

    test_invalid_text_type()

    test_empty_text()

    test_none_document()

    test_invalid_document_type()

    test_none_documents()

    test_invalid_documents_type()

    test_empty_documents()

    print()

    print("=" * 60)
    print(
        "ALL RAG-3.3 EMBEDDER TESTS PASSED"
    )
    print("=" * 60)


if __name__ == "__main__":
    main()