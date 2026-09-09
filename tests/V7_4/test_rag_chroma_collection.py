"""
tests/V7_4/test_rag_chroma_collection.py

AutoSearch V7

RAG-4.3

ChromaDB Collection Test

驗證：

    1. Collection initialization
    2. Collection creation
    3. Collection retrieval
    4. Collection name
    5. Distance metric
    6. Client integration
    7. Get-or-create behavior
    8. Custom collection name
    9. Custom distance metric
    10. Invalid collection name validation
    11. Invalid distance metric validation

本測試不負責：

    1. Document Index
    2. Embedding
    3. MySQL
    4. Full Indexing
    5. Incremental Indexing
"""


import tempfile

from rag.chroma.client import (
    ChromaDBClient
)

from rag.chroma.collection import (
    ChromaCollection
)

from rag.chroma.config import (
    CHROMA_COLLECTION_NAME,
    CHROMA_DISTANCE_METRIC,
    SUPPORTED_DISTANCE_METRICS,
)


# ============================================================
# Shared Collection
# ============================================================

_COLLECTION = None


def create_collection():
    """
    建立共用 ChromaDB Collection。
    """

    global _COLLECTION

    if _COLLECTION is None:

        _COLLECTION = ChromaCollection()

    return _COLLECTION


# ============================================================
# Test 1
# ============================================================

def test_collection_initialization():
    """
    驗證 Collection 初始化。
    """

    collection = create_collection()

    assert isinstance(
        collection,
        ChromaCollection
    )

    print(
        "PASS: ChromaDB Collection initialization"
    )


# ============================================================
# Test 2
# ============================================================

def test_collection_creation():
    """
    驗證 Collection 已成功建立或取得。
    """

    collection = create_collection()

    chroma_collection = (
        collection.get_collection()
    )

    assert (
        chroma_collection
        is not None
    )

    print(
        "PASS: ChromaDB Collection creation"
    )


# ============================================================
# Test 3
# ============================================================

def test_collection_retrieval():
    """
    驗證 get_collection()。
    """

    collection = create_collection()

    chroma_collection = (
        collection.get_collection()
    )

    assert (
        chroma_collection
        is collection.get_collection()
    )

    assert hasattr(
        chroma_collection,
        "add"
    )

    assert hasattr(
        chroma_collection,
        "get"
    )

    assert hasattr(
        chroma_collection,
        "query"
    )

    print(
        "PASS: ChromaDB Collection retrieval"
    )


# ============================================================
# Test 4
# ============================================================

def test_collection_name():
    """
    驗證 Collection Name。
    """

    collection = create_collection()

    assert (
        collection.get_collection_name()
        == CHROMA_COLLECTION_NAME
    )

    assert (
        collection.get_collection_name()
        != ""
    )

    print(
        "PASS: Collection name"
    )

    print(
        f"      Collection: "
        f"{collection.get_collection_name()}"
    )


# ============================================================
# Test 5
# ============================================================

def test_distance_metric():
    """
    驗證 Distance Metric。
    """

    collection = create_collection()

    assert (
        collection.get_distance_metric()
        == CHROMA_DISTANCE_METRIC
    )

    assert (
        collection.get_distance_metric()
        in SUPPORTED_DISTANCE_METRICS
    )

    print(
        "PASS: Collection distance metric"
    )

    print(
        f"      Metric: "
        f"{collection.get_distance_metric()}"
    )


# ============================================================
# Test 6
# ============================================================

def test_client_integration():
    """
    驗證 Collection 使用 RAG-4.2 Client。
    """

    collection = create_collection()

    client = collection.get_client()

    assert (
        client
        is not None
    )

    assert hasattr(
        client,
        "get_or_create_collection"
    )

    print(
        "PASS: Collection / Client integration"
    )


# ============================================================
# Test 7
# ============================================================

def test_get_or_create_behavior():
    """
    驗證同名 Collection
    可以重複取得，而不是產生錯誤。
    """

    first = ChromaCollection()

    second = ChromaCollection()

    assert (
        first.get_collection_name()
        == second.get_collection_name()
    )

    assert (
        first.get_collection()
        is not None
    )

    assert (
        second.get_collection()
        is not None
    )

    print(
        "PASS: Get-or-create Collection behavior"
    )


# ============================================================
# Test 8
# ============================================================

def test_custom_collection_name():
    """
    驗證可以使用自訂 Collection Name。
    """

    temp_dir = tempfile.mkdtemp()

    try:

        client = ChromaDBClient(
            persist_directory=temp_dir
        )

        collection = ChromaCollection(
            chroma_client=client,
            collection_name="test_collection"
        )

        assert (
            collection.get_collection_name()
            == "test_collection"
        )

        assert (
            collection.get_collection()
            is not None
        )

    finally:

        # Chroma Client object will be released
        # when leaving scope.

        pass

    print(
        "PASS: Custom Collection name"
    )


# ============================================================
# Test 9
# ============================================================

def test_custom_distance_metric():
    """
    驗證可以使用支援的 Distance Metric。
    """

    for metric in SUPPORTED_DISTANCE_METRICS:

        temp_dir = tempfile.mkdtemp()

        client = ChromaDBClient(
            persist_directory=temp_dir
        )

        collection = ChromaCollection(
            chroma_client=client,
            collection_name=(
                f"test_collection_{metric}"
            ),
            distance_metric=metric
        )

        assert (
            collection.get_distance_metric()
            == metric
        )

        assert (
            collection.get_collection()
            is not None
        )

    print(
        "PASS: Custom distance metric"
    )


# ============================================================
# Test 10
# ============================================================

def test_empty_collection_name():
    """
    空 Collection Name 必須拒絕。
    """

    try:

        ChromaCollection(
            collection_name="   "
        )

    except ValueError:

        print(
            "PASS: Empty Collection name validation"
        )

        return

    raise AssertionError(
        "Empty Collection name "
        "should raise ValueError."
    )


# ============================================================
# Test 11
# ============================================================

def test_empty_distance_metric():
    """
    空 Distance Metric 必須拒絕。
    """

    try:

        ChromaCollection(
            distance_metric="   "
        )

    except ValueError:

        print(
            "PASS: Empty distance metric validation"
        )

        return

    raise AssertionError(
        "Empty distance metric "
        "should raise ValueError."
    )


# ============================================================
# Test 12
# ============================================================

def test_invalid_distance_metric():
    """
    不支援的 Distance Metric 必須拒絕。

    ChromaCollection 會交給
    ChromaDB API 處理不支援值，
    因此這裡接受 ChromaDB 原生例外。
    """

    try:

        ChromaCollection(
            distance_metric="invalid_metric"
        )

    except Exception:

        print(
            "PASS: Invalid distance metric validation"
        )

        return

    raise AssertionError(
        "Invalid distance metric "
        "should raise an exception."
    )


# ============================================================
# Test 13
# ============================================================

def test_collection_api():
    """
    驗證 Collection 已具備後續
    RAG-4.4 Index Document 所需要的 API。
    """

    collection = create_collection()

    chroma_collection = (
        collection.get_collection()
    )

    required_methods = [
        "add",
        "upsert",
        "get",
        "query",
        "count",
        "delete",
    ]

    for method_name in required_methods:

        assert hasattr(
            chroma_collection,
            method_name
        ), (
            f"Collection missing "
            f"required method: {method_name}"
        )

    print(
        "PASS: ChromaDB Collection API"
    )


# ============================================================
# Main
# ============================================================

def main():
    """
    執行 RAG-4.3 ChromaDB Collection Test。
    """

    print("=" * 60)

    print(
        "RAG-4.3 ChromaDB Collection Test"
    )

    print("=" * 60)

    print()

    test_collection_initialization()

    test_collection_creation()

    test_collection_retrieval()

    test_collection_name()

    test_distance_metric()

    test_client_integration()

    test_get_or_create_behavior()

    test_custom_collection_name()

    test_custom_distance_metric()

    test_empty_collection_name()

    test_empty_distance_metric()

    test_invalid_distance_metric()

    test_collection_api()

    print()

    print("=" * 60)

    print(
        "ALL RAG-4.3 CHROMADB COLLECTION TESTS PASSED"
    )

    print("=" * 60)


if __name__ == "__main__":
    main()