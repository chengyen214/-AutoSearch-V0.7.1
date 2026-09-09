"""
tests/V7_2/test_rag_chunking_config.py

AutoSearch V7

RAG-2.1

Chunking Configuration Test

測試內容：

    1. CHUNK_SPLITTER 是否正確載入
    2. CHUNK_SIZE 是否正確載入
    3. CHUNK_OVERLAP 是否正確載入
    4. Chunking Configuration 是否符合目前設定
    5. Configuration 邏輯是否合法

目前正式設定：

    CHUNK_SPLITTER = recursive
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200

本測試不負責：

    1. Article Source
    2. Document Model
    3. Content Cleaning
    4. Document Splitting
    5. Embedding
    6. ChromaDB
    7. Retriever
    8. LLM
"""


from rag.chunking.config import (
    CHUNK_SPLITTER,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
)


# ============================================================
# Expected Configuration
# ============================================================

EXPECTED_CHUNK_SPLITTER = "recursive"

EXPECTED_CHUNK_SIZE = 1000

EXPECTED_CHUNK_OVERLAP = 200


# ============================================================
# Test Splitter Configuration
# ============================================================

def test_chunk_splitter():
    """
    測試 Chunk Splitter 設定。
    """

    assert (
        CHUNK_SPLITTER
        == EXPECTED_CHUNK_SPLITTER
    )

    print(
        "PASS: CHUNK_SPLITTER"
    )

    print(
        f"      Splitter: {CHUNK_SPLITTER}"
    )


# ============================================================
# Test Chunk Size
# ============================================================

def test_chunk_size():
    """
    測試 Chunk Size。
    """

    assert (
        CHUNK_SIZE
        == EXPECTED_CHUNK_SIZE
    )

    assert CHUNK_SIZE > 0

    print(
        "PASS: CHUNK_SIZE"
    )

    print(
        f"      Chunk Size: {CHUNK_SIZE}"
    )


# ============================================================
# Test Chunk Overlap
# ============================================================

def test_chunk_overlap():
    """
    測試 Chunk Overlap。
    """

    assert (
        CHUNK_OVERLAP
        == EXPECTED_CHUNK_OVERLAP
    )

    assert CHUNK_OVERLAP >= 0

    print(
        "PASS: CHUNK_OVERLAP"
    )

    print(
        f"      Chunk Overlap: {CHUNK_OVERLAP}"
    )


# ============================================================
# Test Configuration Logic
# ============================================================

def test_configuration_logic():
    """
    確認 Chunking Configuration
    符合基本邏輯。

    必須：

        CHUNK_SIZE > 0

        CHUNK_OVERLAP >= 0

        CHUNK_OVERLAP < CHUNK_SIZE
    """

    assert CHUNK_SIZE > 0

    assert CHUNK_OVERLAP >= 0

    assert (
        CHUNK_OVERLAP
        < CHUNK_SIZE
    )

    print(
        "PASS: Chunking configuration logic"
    )


# ============================================================
# Test Configuration Types
# ============================================================

def test_configuration_types():
    """
    確認 Configuration 型別。
    """

    assert isinstance(
        CHUNK_SPLITTER,
        str
    )

    assert isinstance(
        CHUNK_SIZE,
        int
    )

    assert isinstance(
        CHUNK_OVERLAP,
        int
    )

    print(
        "PASS: Chunking configuration types"
    )


# ============================================================
# Test Final Configuration
# ============================================================

def test_final_configuration():
    """
    確認目前 RAG-2.1
    正式 Configuration。
    """

    assert (
        CHUNK_SPLITTER
        == "recursive"
    )

    assert (
        CHUNK_SIZE
        == 1000
    )

    assert (
        CHUNK_OVERLAP
        == 200
    )

    print(
        "PASS: Final RAG-2.1 configuration"
    )


# ============================================================
# Main
# ============================================================

def main():
    """
    執行 RAG-2.1 Chunking Configuration Test。
    """

    print("=" * 60)
    print(
        "RAG-2.1 Chunking Configuration Test"
    )
    print("=" * 60)

    print()

    test_chunk_splitter()

    test_chunk_size()

    test_chunk_overlap()

    test_configuration_logic()

    test_configuration_types()

    test_final_configuration()

    print()

    print("=" * 60)
    print(
        "ALL RAG-2.1 CHUNKING CONFIG TESTS PASSED"
    )
    print("=" * 60)


if __name__ == "__main__":
    main()