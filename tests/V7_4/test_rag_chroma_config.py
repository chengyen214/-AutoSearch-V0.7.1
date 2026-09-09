"""
tests/V7_4/test_rag_chroma_config.py

AutoSearch V7

RAG-4.1

ChromaDB Configuration Test

驗證：

    1. Persist Directory
    2. Collection Name
    3. Distance Metric
    4. Embedding Dimension
    5. Distance Metric Validation
"""


from rag.chroma.config import (
    CHROMA_PERSIST_DIRECTORY,
    CHROMA_COLLECTION_NAME,
    CHROMA_DISTANCE_METRIC,
    EMBEDDING_DIMENSION,
    SUPPORTED_DISTANCE_METRICS,
)


# ============================================================
# Test Persist Directory
# ============================================================

def test_persist_directory():
    """
    驗證 ChromaDB Persist Directory。
    """

    assert isinstance(
        CHROMA_PERSIST_DIRECTORY,
        str
    )

    assert (
        CHROMA_PERSIST_DIRECTORY
        != ""
    )

    print(
        "PASS: ChromaDB persist directory"
    )

    print(
        f"      Directory: "
        f"{CHROMA_PERSIST_DIRECTORY}"
    )


# ============================================================
# Test Collection Name
# ============================================================

def test_collection_name():
    """
    驗證 ChromaDB Collection Name。
    """

    assert isinstance(
        CHROMA_COLLECTION_NAME,
        str
    )

    assert (
        CHROMA_COLLECTION_NAME
        != ""
    )

    print(
        "PASS: ChromaDB collection name"
    )

    print(
        f"      Collection: "
        f"{CHROMA_COLLECTION_NAME}"
    )


# ============================================================
# Test Distance Metric
# ============================================================

def test_distance_metric():
    """
    驗證 Distance Metric。
    """

    assert (
        CHROMA_DISTANCE_METRIC
        in SUPPORTED_DISTANCE_METRICS
    )

    print(
        "PASS: ChromaDB distance metric"
    )

    print(
        f"      Metric: "
        f"{CHROMA_DISTANCE_METRIC}"
    )


# ============================================================
# Test Supported Metrics
# ============================================================

def test_supported_distance_metrics():
    """
    驗證支援的 Distance Metrics。
    """

    assert (
        "cosine"
        in SUPPORTED_DISTANCE_METRICS
    )

    assert (
        "l2"
        in SUPPORTED_DISTANCE_METRICS
    )

    assert (
        "ip"
        in SUPPORTED_DISTANCE_METRICS
    )

    print(
        "PASS: Supported distance metrics"
    )


# ============================================================
# Test Embedding Dimension
# ============================================================

def test_embedding_dimension():
    """
    驗證 ChromaDB 使用的 Embedding Dimension
    與 RAG-3 一致。
    """

    assert (
        EMBEDDING_DIMENSION
        == 1024
    )

    assert (
        EMBEDDING_DIMENSION
        > 0
    )

    print(
        "PASS: Embedding dimension"
    )

    print(
        f"      Dimension: "
        f"{EMBEDDING_DIMENSION}"
    )


# ============================================================
# Test Cosine Configuration
# ============================================================

def test_default_cosine_configuration():
    """
    確認目前正式設定使用 cosine。
    """

    assert (
        CHROMA_DISTANCE_METRIC
        == "cosine"
    )

    print(
        "PASS: Default cosine configuration"
    )


# ============================================================
# Main
# ============================================================

def main():
    """
    執行 RAG-4.1 ChromaDB Configuration Test。
    """

    print("=" * 60)

    print(
        "RAG-4.1 ChromaDB Configuration Test"
    )

    print("=" * 60)

    print()

    test_persist_directory()

    test_collection_name()

    test_distance_metric()

    test_supported_distance_metrics()

    test_embedding_dimension()

    test_default_cosine_configuration()

    print()

    print("=" * 60)

    print(
        "ALL RAG-4.1 CHROMADB CONFIGURATION TESTS PASSED"
    )

    print("=" * 60)


if __name__ == "__main__":
    main()