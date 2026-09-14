"""
tests/V7_5/test_rag_query_embedding.py

AutoSearch V7

RAG-5.2

Query Embedding Integration Test

測試：

    User Query
        ↓
    QueryEmbedding
        ↓
    RAG-3 Embedder
        ↓
    Qwen/Qwen3-Embedding-0.6B
        ↓
    1024 維 Query Vector

驗證：

    1. QueryEmbedding initialization
    2. RAG-3 Embedder integration
    3. Query validation
    4. Query embedding generation
    5. Embedding type
    6. Embedding dimension
    7. Embedding value validity
    8. Query normalization
    9. Dimension API
"""


# ============================================================
# Imports
# ============================================================

import math

from rag.retriever.query_embedding import (
    QueryEmbedding
)

from rag.retriever.config import (
    EMBEDDING_DIMENSION
)


# ============================================================
# Test Constants
# ============================================================

TEST_QUERY = (
    "台灣半導體產業未來發展趨勢"
)


# ============================================================
# Fake Embedder
# ============================================================

class FakeEmbedder:
    """
    Fake RAG-3 Embedder。

    用於驗證 RAG-5.2
    是否正確呼叫既有 Embedder API。

    不載入 Qwen Model。
    """

    DIMENSION = EMBEDDING_DIMENSION

    def __init__(self):
        self.received_query = None

    def get_dimension(
        self
    ):
        return self.DIMENSION

    def embed_text(
        self,
        text
    ):
        self.received_query = text

        return [
            0.1
            for _ in range(
                self.DIMENSION
            )
        ]


# ============================================================
# Main Test
# ============================================================

def main():

    print(
        "=" * 60
    )

    print(
        "RAG-5.2 Query Embedding Integration Test"
    )

    print(
        "=" * 60
    )

    print()

    # ========================================================
    # Fake Embedder
    # ========================================================

    fake_embedder = (
        FakeEmbedder()
    )

    query_embedding = (
        QueryEmbedding(
            embedder=fake_embedder
        )
    )

    # ========================================================
    # Initialization
    # ========================================================

    assert (
        query_embedding
        is not None
    )

    print(
        "PASS: QueryEmbedding initialization"
    )

    # ========================================================
    # RAG-3 Embedder Integration
    # ========================================================

    assert (
        query_embedding.embedder
        is fake_embedder
    )

    print(
        "PASS: RAG-3 Embedder integration"
    )

    # ========================================================
    # Dimension
    # ========================================================

    assert (
        query_embedding.get_dimension()
        == EMBEDDING_DIMENSION
    )

    print(
        "PASS: QueryEmbedding dimension configuration"
    )

    print(
        f"      Dimension: "
        f"{query_embedding.get_dimension()}"
    )

    # ========================================================
    # Query Embedding
    # ========================================================

    embedding = (
        query_embedding.embed(
            TEST_QUERY
        )
    )

    print(
        "PASS: Query embedding generation"
    )

    # ========================================================
    # Embedder Received Query
    # ========================================================

    assert (
        fake_embedder.received_query
        == TEST_QUERY
    )

    print(
        "PASS: Query passed to RAG-3 Embedder"
    )

    # ========================================================
    # Embedding Type
    # ========================================================

    assert isinstance(
        embedding,
        list
    )

    print(
        "PASS: Query embedding type"
    )

    # ========================================================
    # Embedding Count
    # ========================================================

    assert (
        len(embedding)
        == EMBEDDING_DIMENSION
    )

    print(
        "PASS: Query embedding dimension"
    )

    print(
        f"      Vector Dimension: "
        f"{len(embedding)}"
    )

    # ========================================================
    # Embedding Values
    # ========================================================

    for value in embedding:

        assert isinstance(
            value,
            (int, float)
        )

        assert math.isfinite(
            float(value)
        )

    print(
        "PASS: Query embedding values"
    )

    # ========================================================
    # Query Normalization
    # ========================================================

    normalized_embedding = (
        query_embedding.embed(
            "   "
            + TEST_QUERY
            + "   "
        )
    )

    assert (
        fake_embedder.received_query
        == TEST_QUERY
    )

    assert (
        normalized_embedding
        == embedding
    )

    print(
        "PASS: Query normalization"
    )

    # ========================================================
    # None Query Validation
    # ========================================================

    try:

        query_embedding.embed(
            None
        )

        raise AssertionError(
            "Expected ValueError"
        )

    except ValueError:

        print(
            "PASS: None query validation"
        )

    # ========================================================
    # Empty Query Validation
    # ========================================================

    try:

        query_embedding.embed(
            ""
        )

        raise AssertionError(
            "Expected ValueError"
        )

    except ValueError:

        print(
            "PASS: Empty query validation"
        )

    # ========================================================
    # Whitespace Query Validation
    # ========================================================

    try:

        query_embedding.embed(
            "   "
        )

        raise AssertionError(
            "Expected ValueError"
        )

    except ValueError:

        print(
            "PASS: Whitespace query validation"
        )

    # ========================================================
    # Non-string Query Validation
    # ========================================================

    try:

        query_embedding.embed(
            123
        )

        raise AssertionError(
            "Expected TypeError"
        )

    except TypeError:

        print(
            "PASS: Non-string query validation"
        )

    # ========================================================
    # Invalid Embedder Dimension
    # ========================================================

    class InvalidDimensionEmbedder:
        """
        測試 Dimension mismatch。
        """

        def get_dimension(
            self
        ):
            return (
                EMBEDDING_DIMENSION
                + 1
            )

        def embed_text(
            self,
            text
        ):
            return [
                0.1
                for _ in range(
                    EMBEDDING_DIMENSION
                    + 1
                )
            ]

    try:

        QueryEmbedding(
            embedder=(
                InvalidDimensionEmbedder()
            )
        )

        raise AssertionError(
            "Expected ValueError"
        )

    except ValueError:

        print(
            "PASS: Embedding dimension validation"
        )

    # ========================================================
    # Invalid Embedding Type
    # ========================================================

    class InvalidTypeEmbedder:
        """
        回傳錯誤 Embedding type。
        """

        def get_dimension(
            self
        ):
            return EMBEDDING_DIMENSION

        def embed_text(
            self,
            text
        ):
            return "invalid"

    invalid_type_embedding = (
        QueryEmbedding(
            embedder=(
                InvalidTypeEmbedder()
            )
        )
    )

    try:

        invalid_type_embedding.embed(
            TEST_QUERY
        )

        raise AssertionError(
            "Expected TypeError"
        )

    except TypeError:

        print(
            "PASS: Invalid embedding type validation"
        )

    # ========================================================
    # Invalid Embedding Length
    # ========================================================

    class InvalidLengthEmbedder:
        """
        回傳錯誤 Embedding dimension。
        """

        def get_dimension(
            self
        ):
            return EMBEDDING_DIMENSION

        def embed_text(
            self,
            text
        ):
            return [
                0.1
                for _ in range(
                    EMBEDDING_DIMENSION - 1
                )
            ]

    invalid_length_embedding = (
        QueryEmbedding(
            embedder=(
                InvalidLengthEmbedder()
            )
        )
    )

    try:

        invalid_length_embedding.embed(
            TEST_QUERY
        )

        raise AssertionError(
            "Expected ValueError"
        )

    except ValueError:

        print(
            "PASS: Invalid embedding length validation"
        )

    # ========================================================
    # Result Integrity
    # ========================================================

    assert (
        isinstance(
            embedding,
            list
        )
    )

    assert (
        len(embedding)
        == EMBEDDING_DIMENSION
    )

    assert all(
        isinstance(
            value,
            (int, float)
        )
        for value in embedding
    )

    print(
        "PASS: Query embedding result integrity"
    )

    # ========================================================
    # Final
    # ========================================================

    print()

    print(
        "=" * 60
    )

    print(
        "ALL RAG-5.2 QUERY EMBEDDING "
        "INTEGRATION TESTS PASSED"
    )

    print(
        "=" * 60
    )


if __name__ == "__main__":
    main()