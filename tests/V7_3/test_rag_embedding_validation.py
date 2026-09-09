"""
tests/V7_3/test_rag_embedding_validation.py

AutoSearch V7

RAG-3.5

Embedding Validation Test

功能：

    驗證 RAG-3 Embedding 是否為有效向量。

資料流程：

    MCP
      ↓
    RAG-1 Document Preparation
      ↓
    RAG-2 Document Chunking
      ↓
    RAG-3.2 Qwen Embedding Model
      ↓
    RAG-3.3 Embedder
      ↓
    RAG-3.5 Embedding Validation

本測試不負責：

    1. ChromaDB
    2. Retriever
    3. Context Builder
    4. LLM
"""


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
    EMBEDDING_DIMENSION,
)


# ============================================================
# Test Article
# ============================================================

TEST_DOCUMENT_ID = (
    "d9ce4740c3f0b6f1d260c094c0549f68727187b0a2b57c94f6308b4df9fd9d13"
)


# ============================================================
# Shared Test Objects
# ============================================================

_PREPARED_DOCUMENT = None
_CHUNKS = None
_EMBEDDER = None
_EMBEDDINGS = None


# ============================================================
# Create Prepared Document
# ============================================================

def create_prepared_document():
    """
    建立真實 Prepared Document。

    只建立一次。
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

    return _PREPARED_DOCUMENT


# ============================================================
# Create Chunks
# ============================================================

def create_chunks():
    """
    建立真實 RAG-2 Chunks。

    只建立一次。
    """

    global _CHUNKS

    if _CHUNKS is None:

        document = (
            create_prepared_document()
        )

        chunking = DocumentChunking()

        _CHUNKS = chunking.chunk(
            document
        )

    assert _CHUNKS is not None
    assert len(_CHUNKS) > 0

    return _CHUNKS


# ============================================================
# Create Embedder
# ============================================================

def create_embedder():
    """
    建立並共用 Embedder。

    Qwen Model 只載入一次。
    """

    global _EMBEDDER

    if _EMBEDDER is None:

        _EMBEDDER = Embedder()

    return _EMBEDDER


# ============================================================
# Create Embeddings
# ============================================================

def create_embeddings():
    """
    建立真實 Embeddings。

    只執行一次。
    """

    global _EMBEDDINGS

    if _EMBEDDINGS is None:

        chunks = create_chunks()
        embedder = create_embedder()

        _EMBEDDINGS = (
            embedder.embed_documents(
                chunks
            )
        )

    assert _EMBEDDINGS is not None
    assert len(_EMBEDDINGS) > 0

    return _EMBEDDINGS


# ============================================================
# Test Single Embedding Validation
# ============================================================

def test_single_embedding_validation():
    """
    驗證單一 Embedding。
    """

    embedder = create_embedder()
    embeddings = create_embeddings()

    embedding = embeddings[0]

    assert (
        embedder.validate_embedding(
            embedding
        )
        is True
    )

    print(
        "PASS: Single embedding validation"
    )


# ============================================================
# Test Embedding Type
# ============================================================

def test_embedding_type_validation():
    """
    驗證 Embedding 必須為 list。
    """

    embedder = create_embedder()

    try:

        embedder.validate_embedding(
            "invalid"
        )

    except TypeError:

        print(
            "PASS: Invalid embedding type validation"
        )

        return

    raise AssertionError(
        "Invalid embedding type "
        "should raise TypeError."
    )


# ============================================================
# Test Empty Embedding
# ============================================================

def test_empty_embedding_validation():
    """
    驗證 Embedding 不可為空。
    """

    embedder = create_embedder()

    try:

        embedder.validate_embedding(
            []
        )

    except ValueError:

        print(
            "PASS: Empty embedding validation"
        )

        return

    raise AssertionError(
        "Empty embedding should raise ValueError."
    )


# ============================================================
# Test Embedding Dimension
# ============================================================

def test_embedding_dimension_validation():
    """
    驗證 Embedding 維度必須等於 1024。
    """

    embedder = create_embedder()

    invalid_embedding = [
        0.1
    ] * (
        EMBEDDING_DIMENSION - 1
    )

    try:

        embedder.validate_embedding(
            invalid_embedding
        )

    except ValueError:

        print(
            "PASS: Embedding dimension validation"
        )

        return

    raise AssertionError(
        "Wrong embedding dimension "
        "should raise ValueError."
    )


# ============================================================
# Test Numeric Values
# ============================================================

def test_embedding_numeric_values():
    """
    驗證 Embedding 每個值都必須為 numeric。
    """

    embedder = create_embedder()

    invalid_embedding = [
        0.1
    ] * EMBEDDING_DIMENSION

    invalid_embedding[0] = "invalid"

    try:

        embedder.validate_embedding(
            invalid_embedding
        )

    except TypeError:

        print(
            "PASS: Embedding numeric value validation"
        )

        return

    raise AssertionError(
        "Non-numeric embedding value "
        "should raise TypeError."
    )


# ============================================================
# Test Finite Values
# ============================================================

def test_embedding_finite_values():
    """
    驗證 Embedding 不可包含：

        NaN
        +Infinity
        -Infinity
    """

    embedder = create_embedder()

    invalid_embedding = [
        0.1
    ] * EMBEDDING_DIMENSION

    invalid_embedding[0] = float(
        "nan"
    )

    try:

        embedder.validate_embedding(
            invalid_embedding
        )

    except ValueError:

        print(
            "PASS: Embedding finite value validation"
        )

        return

    raise AssertionError(
        "NaN embedding value "
        "should raise ValueError."
    )


# ============================================================
# Test Non-zero Embedding
# ============================================================

def test_embedding_non_zero_validation():
    """
    驗證 Embedding 不可為全零向量。
    """

    embedder = create_embedder()

    zero_embedding = [
        0.0
    ] * EMBEDDING_DIMENSION

    try:

        embedder.validate_embedding(
            zero_embedding
        )

    except ValueError:

        print(
            "PASS: All-zero embedding validation"
        )

        return

    raise AssertionError(
        "All-zero embedding "
        "should raise ValueError."
    )


# ============================================================
# Test Multiple Embeddings
# ============================================================

def test_multiple_embeddings_validation():
    """
    驗證多個 Embeddings。
    """

    embedder = create_embedder()
    embeddings = create_embeddings()

    assert (
        embedder.validate_embeddings(
            embeddings
        )
        is True
    )

    print(
        "PASS: Multiple embeddings validation"
    )


# ============================================================
# Test Multiple Embeddings Count
# ============================================================

def test_multiple_embeddings_count():
    """
    驗證 Embedding 數量
    與真實 Chunks 數量一致。
    """

    chunks = create_chunks()
    embeddings = create_embeddings()

    assert (
        len(embeddings)
        == len(chunks)
    )

    print(
        "PASS: Embedding count validation"
    )

    print(
        f"      Chunks: "
        f"{len(chunks)}"
    )

    print(
        f"      Embeddings: "
        f"{len(embeddings)}"
    )


# ============================================================
# Test Multiple Embedding Dimensions
# ============================================================

def test_multiple_embedding_dimensions():
    """
    驗證所有 Embeddings
    都是 1024 維。
    """

    embeddings = create_embeddings()

    for index, embedding in enumerate(
        embeddings
    ):

        assert (
            len(embedding)
            == EMBEDDING_DIMENSION
        ), (
            f"Embedding {index} "
            "dimension mismatch."
        )

    print(
        "PASS: Multiple embedding dimensions"
    )


# ============================================================
# Test None Embedding
# ============================================================

def test_none_embedding_validation():
    """
    驗證 None Embedding。
    """

    embedder = create_embedder()

    try:

        embedder.validate_embedding(
            None
        )

    except TypeError:

        print(
            "PASS: None embedding validation"
        )

        return

    raise AssertionError(
        "None embedding "
        "should raise TypeError."
    )


# ============================================================
# Test None Embeddings
# ============================================================

def test_none_embeddings_validation():
    """
    驗證 None Embeddings。
    """

    embedder = create_embedder()

    try:

        embedder.validate_embeddings(
            None
        )

    except TypeError:

        print(
            "PASS: None embeddings validation"
        )

        return

    raise AssertionError(
        "None embeddings "
        "should raise TypeError."
    )


# ============================================================
# Test Empty Embeddings
# ============================================================

def test_empty_embeddings_validation():
    """
    驗證空 Embeddings list。
    """

    embedder = create_embedder()

    try:

        embedder.validate_embeddings(
            []
        )

    except ValueError:

        print(
            "PASS: Empty embeddings validation"
        )

        return

    raise AssertionError(
        "Empty embeddings "
        "should raise ValueError."
    )


# ============================================================
# Test Real Qwen Embedding
# ============================================================

def test_real_qwen_embedding_validation():
    """
    使用真實 Qwen Embedding
    完成 RAG-3.5 驗證。
    """

    embedder = create_embedder()
    chunks = create_chunks()
    embeddings = create_embeddings()

    assert (
        len(embeddings)
        == len(chunks)
    )

    assert (
        embedder.validate_embeddings(
            embeddings
        )
        is True
    )

    for index, embedding in enumerate(
        embeddings
    ):

        assert isinstance(
            embedding,
            list
        )

        assert (
            len(embedding)
            == EMBEDDING_DIMENSION
        )

        assert any(
            value != 0
            for value in embedding
        )

    print(
        "PASS: Real Qwen embedding validation"
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
        f"{len(embeddings)}"
    )

    print(
        f"      Embedding dimension: "
        f"{EMBEDDING_DIMENSION}"
    )


# ============================================================
# Main
# ============================================================

def main():
    """
    執行 RAG-3.5 Embedding Validation Test。
    """

    print("=" * 60)

    print(
        "RAG-3.5 Embedding Validation Test"
    )

    print("=" * 60)

    print()

    print(
        "Testing real RAG-3 Embeddings..."
    )

    print()

    test_single_embedding_validation()

    test_embedding_type_validation()

    test_empty_embedding_validation()

    test_embedding_dimension_validation()

    test_embedding_numeric_values()

    test_embedding_finite_values()

    test_embedding_non_zero_validation()

    test_multiple_embeddings_validation()

    test_multiple_embeddings_count()

    test_multiple_embedding_dimensions()

    test_none_embedding_validation()

    test_none_embeddings_validation()

    test_empty_embeddings_validation()

    test_real_qwen_embedding_validation()

    print()

    print("=" * 60)

    print(
        "ALL RAG-3.5 EMBEDDING VALIDATION TESTS PASSED"
    )

    print("=" * 60)


if __name__ == "__main__":
    main()