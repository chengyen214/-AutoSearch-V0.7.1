"""
tests/V7_5/test_rag_retrieval_result.py

AutoSearch V7

RAG-5.5

Retrieval Result Integration Test

測試：

    RAG-5.4 Final Top-K
            ↓
    Raw Retrieval Result
            ↓
    RetrievalResultBuilder
            ↓
    List[RetrievalResult]

驗證：

    1. RetrievalResult initialization
    2. RetrievalResult field integrity
    3. RetrievalResult getters
    4. RetrievalResultBuilder initialization
    5. Raw retrieval result validation
    6. Record ID parsing
    7. document_id extraction
    8. chunk_index extraction
    9. Metadata validation
    10. Distance validation
    11. Similarity handling
    12. Single result building
    13. Multiple result building
    14. Result count
    15. Result ordering
    16. Result field alignment
    17. Invalid input validation
"""


# ============================================================
# Imports
# ============================================================

import math

from rag.retriever.retrieval_result import (
    RetrievalResult,
    RetrievalResultBuilder,
)


# ============================================================
# Test Constants
# ============================================================

TEST_DOCUMENT_ID_1 = (
    "82b6c57a03fedc1968c08f5e21fd7dcc9d94dba77fde87e4d83162163ce574db"
)

TEST_DOCUMENT_ID_2 = (
    "02164dbe74744033d0abbc57aecb7f6d28312449cca8457198b13bd9ea477e8a"
)

TEST_CHUNK_0 = (
    "台灣半導體產業持續受到 AI 與先進製程需求帶動。"
)

TEST_CHUNK_1 = (
    "先進封裝與高頻寬記憶體成為產業重要發展方向。"
)


# ============================================================
# Fake Raw Retrieval Result
# ============================================================

def create_raw_result():
    """
    建立模擬 RAG-5.4 Raw Top-K Retrieval Result。
    """

    return {
        "ids": [
            f"{TEST_DOCUMENT_ID_1}::chunk_0",
            f"{TEST_DOCUMENT_ID_1}::chunk_1",
            f"{TEST_DOCUMENT_ID_2}::chunk_0",
        ],
        "documents": [
            TEST_CHUNK_0,
            TEST_CHUNK_1,
            "AI、高效運算與先進封裝持續推升半導體投資。",
        ],
        "metadatas": [
            {
                "document_id": TEST_DOCUMENT_ID_1,
                "title": "全球產業數據 - Research - DIGITIMES",
                "url": "https://example.com/digitimes",
                "keyword": "IC semiconductor",
                "source": "",
                "crawl_time": "2026-09-02T14:52:12",
                "ai_summary": "半導體產業資料。",
                "ai_category": "Semiconductor",
                "ai_keywords": "半導體, AI",
                "ai_importance": 7,
                "ai_confidence": 0.8,
            },
            {
                "document_id": TEST_DOCUMENT_ID_1,
                "title": "全球產業數據 - Research - DIGITIMES",
                "url": "https://example.com/digitimes",
                "keyword": "IC semiconductor",
                "source": "",
                "crawl_time": "2026-09-02T14:52:12",
                "ai_summary": "半導體產業資料。",
                "ai_category": "Semiconductor",
                "ai_keywords": "半導體, AI",
                "ai_importance": 7,
                "ai_confidence": 0.8,
            },
            {
                "document_id": TEST_DOCUMENT_ID_2,
                "title": "科技網 - DIGITIMES",
                "url": "https://example.com/tech",
                "keyword": "IC semiconductor",
                "source": "",
                "crawl_time": "2026-09-08T11:34:22",
                "ai_summary": "AI 與 HPC 推動半導體設備需求。",
                "ai_category": "Equipment",
                "ai_keywords": "AI, HPC, HBM",
                "ai_importance": 6,
                "ai_confidence": 0.8,
            },
        ],
        "distances": [
            0.3552568554878235,
            0.38492822647094727,
            0.36375892162323,
        ],
    }


# ============================================================
# Main Test
# ============================================================

def main():

    print(
        "=" * 60
    )

    print(
        "RAG-5.5 Retrieval Result Integration Test"
    )

    print(
        "=" * 60
    )

    print()

    # ========================================================
    # Raw Result
    # ========================================================

    raw_result = (
        create_raw_result()
    )

    # ========================================================
    # Builder Initialization
    # ========================================================

    builder = (
        RetrievalResultBuilder()
    )

    assert (
        builder
        is not None
    )

    print(
        "PASS: RetrievalResultBuilder initialization"
    )

    # ========================================================
    # Build Results
    # ========================================================

    results = (
        builder.build(
            raw_result
        )
    )

    assert isinstance(
        results,
        list
    )

    print(
        "PASS: RetrievalResultBuilder result type"
    )

    # ========================================================
    # Result Count
    # ========================================================

    assert (
        len(results)
        == 3
    )

    print(
        "PASS: Retrieval result count"
    )

    print(
        f"      Result Count: "
        f"{len(results)}"
    )

    # ========================================================
    # RetrievalResult Type
    # ========================================================

    for index, result in enumerate(
        results,
        start=1
    ):

        assert isinstance(
            result,
            RetrievalResult
        )

        print(
            f"PASS: RetrievalResult type {index}"
        )

    # ========================================================
    # First Result
    # ========================================================

    first = results[0]

    assert (
        first.chunk
        == TEST_CHUNK_0
    )

    print(
        "PASS: First result chunk"
    )

    assert (
        first.distance
        == 0.3552568554878235
    )

    print(
        "PASS: First result distance"
    )

    assert (
        first.document_id
        == TEST_DOCUMENT_ID_1
    )

    print(
        "PASS: First result document_id"
    )

    assert (
        first.chunk_index
        == 0
    )

    print(
        "PASS: First result chunk_index"
    )

    assert isinstance(
        first.metadata,
        dict
    )

    print(
        "PASS: First result metadata"
    )

    assert (
        first.similarity
        is None
    )

    print(
        "PASS: First result similarity default"
    )

    # ========================================================
    # Getter Tests
    # ========================================================

    assert (
        first.get_chunk()
        == first.chunk
    )

    print(
        "PASS: get_chunk()"
    )

    assert (
        first.get_distance()
        == first.distance
    )

    print(
        "PASS: get_distance()"
    )

    assert (
        first.get_similarity()
        == first.similarity
    )

    print(
        "PASS: get_similarity()"
    )

    assert (
        first.get_document_id()
        == first.document_id
    )

    print(
        "PASS: get_document_id()"
    )

    assert (
        first.get_chunk_index()
        == first.chunk_index
    )

    print(
        "PASS: get_chunk_index()"
    )

    assert (
        first.get_metadata()
        == first.metadata
    )

    print(
        "PASS: get_metadata()"
    )

    # ========================================================
    # Record ID Parsing
    # ========================================================

    (
        document_id,
        chunk_index
    ) = builder._parse_record_id(
        f"{TEST_DOCUMENT_ID_2}::chunk_7"
    )

    assert (
        document_id
        == TEST_DOCUMENT_ID_2
    )

    print(
        "PASS: Record ID document_id parsing"
    )

    assert (
        chunk_index
        == 7
    )

    print(
        "PASS: Record ID chunk_index parsing"
    )

    # ========================================================
    # Single Result Build
    # ========================================================

    single_result = (
        builder.build_one(
            record_id=(
                f"{TEST_DOCUMENT_ID_2}::chunk_3"
            ),
            chunk="Single test chunk",
            metadata={
                "document_id": TEST_DOCUMENT_ID_2,
                "title": "Single Test",
            },
            distance=0.42,
        )
    )

    assert isinstance(
        single_result,
        RetrievalResult
    )

    print(
        "PASS: Single RetrievalResult build"
    )

    assert (
        single_result.document_id
        == TEST_DOCUMENT_ID_2
    )

    print(
        "PASS: Single result document_id"
    )

    assert (
        single_result.chunk_index
        == 3
    )

    print(
        "PASS: Single result chunk_index"
    )

    # ========================================================
    # Similarity Input
    # ========================================================

    similarity_result = (
        builder.build_one(
            record_id=(
                f"{TEST_DOCUMENT_ID_1}::chunk_5"
            ),
            chunk="Similarity test",
            metadata={
                "document_id": TEST_DOCUMENT_ID_1,
            },
            distance=0.25,
            similarity=0.75,
        )
    )

    assert (
        similarity_result.similarity
        == 0.75
    )

    print(
        "PASS: Similarity value handling"
    )

    # ========================================================
    # Result Count API
    # ========================================================

    assert (
        builder.count(
            results
        )
        == 3
    )

    print(
        "PASS: Result count API"
    )

    # ========================================================
    # Result Ordering
    # ========================================================

    assert (
        results[0].distance
        == raw_result["distances"][0]
    )

    assert (
        results[1].distance
        == raw_result["distances"][1]
    )

    assert (
        results[2].distance
        == raw_result["distances"][2]
    )

    print(
        "PASS: Result ordering"
    )

    # ========================================================
    # Field Alignment
    # ========================================================

    for index in range(
        len(results)
    ):

        result = results[index]

        assert (
            result.chunk
            == raw_result["documents"][index]
        )

        assert (
            result.distance
            == raw_result["distances"][index]
        )

        assert (
            result.metadata
            == raw_result["metadatas"][index]
        )

    print(
        "PASS: Result field alignment"
    )

    # ========================================================
    # Document ID Alignment
    # ========================================================

    for index, result in enumerate(
        results
    ):

        record_id = (
            raw_result["ids"][index]
        )

        expected_document_id = (
            record_id.split(
                "::chunk_",
                1
            )[0]
        )

        assert (
            result.document_id
            == expected_document_id
        )

        print(
            f"PASS: document_id alignment {index + 1}"
        )

    # ========================================================
    # Chunk Index Alignment
    # ========================================================

    for index, result in enumerate(
        results
    ):

        record_id = (
            raw_result["ids"][index]
        )

        expected_chunk_index = int(
            record_id.split(
                "::chunk_",
                1
            )[1]
        )

        assert (
            result.chunk_index
            == expected_chunk_index
        )

        print(
            f"PASS: chunk_index alignment {index + 1}"
        )

    # ========================================================
    # Metadata document_id
    # ========================================================

    for index, result in enumerate(
        results
    ):

        assert (
            result.metadata["document_id"]
            == result.document_id
        )

        print(
            f"PASS: Metadata document_id "
            f"integrity {index + 1}"
        )

    # ========================================================
    # Distance Values
    # ========================================================

    for index, result in enumerate(
        results
    ):

        assert isinstance(
            result.distance,
            (int, float)
        )

        assert math.isfinite(
            float(
                result.distance
            )
        )

        print(
            f"PASS: Distance validity {index + 1}"
        )

    # ========================================================
    # None Raw Result
    # ========================================================

    try:

        builder.build(
            None
        )

        raise AssertionError(
            "Expected ValueError"
        )

    except ValueError:

        print(
            "PASS: None raw result validation"
        )

    # ========================================================
    # Non-dict Raw Result
    # ========================================================

    try:

        builder.build(
            "invalid"
        )

        raise AssertionError(
            "Expected TypeError"
        )

    except TypeError:

        print(
            "PASS: Non-dict raw result validation"
        )

    # ========================================================
    # Missing Field
    # ========================================================

    try:

        builder.build(
            {
                "ids": [],
                "documents": [],
                "metadatas": [],
            }
        )

        raise AssertionError(
            "Expected ValueError"
        )

    except ValueError:

        print(
            "PASS: Missing retrieval field validation"
        )

    # ========================================================
    # Unequal Field Length
    # ========================================================

    try:

        builder.build(
            {
                "ids": [
                    "doc::chunk_0"
                ],
                "documents": [
                    "test"
                ],
                "metadatas": [
                    {
                        "document_id": "doc"
                    }
                ],
                "distances": [],
            }
        )

        raise AssertionError(
            "Expected ValueError"
        )

    except ValueError:

        print(
            "PASS: Retrieval field length validation"
        )

    # ========================================================
    # Invalid Record ID
    # ========================================================

    try:

        builder.build_one(
            record_id="invalid_record_id",
            chunk="test",
            metadata={},
            distance=0.5,
        )

        raise AssertionError(
            "Expected ValueError"
        )

    except ValueError:

        print(
            "PASS: Invalid record ID validation"
        )

    # ========================================================
    # Invalid Chunk
    # ========================================================

    try:

        RetrievalResult(
            chunk="",
            distance=0.5,
            similarity=None,
            document_id="doc",
            chunk_index=0,
            metadata={},
        )

        raise AssertionError(
            "Expected ValueError"
        )

    except ValueError:

        print(
            "PASS: Empty chunk validation"
        )

    # ========================================================
    # Invalid Distance
    # ========================================================

    try:

        RetrievalResult(
            chunk="test",
            distance=float("nan"),
            similarity=None,
            document_id="doc",
            chunk_index=0,
            metadata={},
        )

        raise AssertionError(
            "Expected ValueError"
        )

    except ValueError:

        print(
            "PASS: Invalid distance validation"
        )

    # ========================================================
    # Invalid Document ID
    # ========================================================

    try:

        RetrievalResult(
            chunk="test",
            distance=0.5,
            similarity=None,
            document_id="",
            chunk_index=0,
            metadata={},
        )

        raise AssertionError(
            "Expected ValueError"
        )

    except ValueError:

        print(
            "PASS: Empty document_id validation"
        )

    # ========================================================
    # Invalid Chunk Index
    # ========================================================

    try:

        RetrievalResult(
            chunk="test",
            distance=0.5,
            similarity=None,
            document_id="doc",
            chunk_index=-1,
            metadata={},
        )

        raise AssertionError(
            "Expected ValueError"
        )

    except ValueError:

        print(
            "PASS: Invalid chunk_index validation"
        )

    # ========================================================
    # Invalid Metadata
    # ========================================================

    try:

        RetrievalResult(
            chunk="test",
            distance=0.5,
            similarity=None,
            document_id="doc",
            chunk_index=0,
            metadata="invalid",
        )

        raise AssertionError(
            "Expected TypeError"
        )

    except TypeError:

        print(
            "PASS: Invalid metadata validation"
        )

    # ========================================================
    # Metadata document_id Mismatch
    # ========================================================

    try:

        RetrievalResult(
            chunk="test",
            distance=0.5,
            similarity=None,
            document_id="doc_A",
            chunk_index=0,
            metadata={
                "document_id": "doc_B"
            },
        )

        raise AssertionError(
            "Expected ValueError"
        )

    except ValueError:

        print(
            "PASS: Metadata document_id mismatch validation"
        )

    # ========================================================
    # Invalid Similarity
    # ========================================================

    try:

        RetrievalResult(
            chunk="test",
            distance=0.5,
            similarity=float("nan"),
            document_id="doc",
            chunk_index=0,
            metadata={},
        )

        raise AssertionError(
            "Expected ValueError"
        )

    except ValueError:

        print(
            "PASS: Invalid similarity validation"
        )

    # ========================================================
    # Frozen Model Validation
    # ========================================================

    try:

        first.chunk = (
            "modified"
        )

        raise AssertionError(
            "Expected FrozenInstanceError"
        )

    except Exception:

        print(
            "PASS: RetrievalResult immutability"
        )

    # ========================================================
    # Final Integrity
    # ========================================================

    assert (
        len(results)
        == builder.count(
            results
        )
    )

    assert all(
        isinstance(
            result,
            RetrievalResult
        )
        for result in results
    )

    print(
        "PASS: Final retrieval result integrity"
    )

    # ========================================================
    # Final
    # ========================================================

    print()

    print(
        "=" * 60
    )

    print(
        "ALL RAG-5.5 RETRIEVAL RESULT "
        "INTEGRATION TESTS PASSED"
    )

    print(
        "=" * 60
    )


# ============================================================
# Entry Point
# ============================================================

if __name__ == "__main__":
    main()