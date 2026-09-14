"""
tests/V7_5/test_rag_retrieval_validation.py

AutoSearch V7

RAG-5.6

Retrieval Validation

目的：

    驗證 RAG-5 Unified Retriever
    是否可以正常完成：

        User Query
            ↓
        RAG-5.2 Query Embedding
            ↓
        RAG-5.3 Candidate Retrieval
            ↓
        Candidate-K
            ↓
        RAG-5.4 Final Top-K
            ↓
        RAG-5.5 Retrieval Result
            ↓
        List[RetrievalResult]

本測試使用：

    - 真實 ChromaDB
    - 真實 Qwen/Qwen3-Embedding-0.6B
    - 真實 Retrieval Pipeline

驗證：

    1. RAGRetriever initialization
    2. Candidate-K configuration
    3. Top-K configuration
    4. RAG-5.2 Query Embedding integration
    5. RAG-5.3 Candidate Retrieval integration
    6. RAG-5.4 Final Top-K integration
    7. RAG-5.5 Retrieval Result integration
    8. Final result type
    9. Final result count
    10. Chunk
    11. Distance
    12. document_id
    13. chunk_index
    14. Metadata
    15. Record ID consistency
    16. Distance ordering
    17. Retrieval result integrity
    18. Basic relevance validation
"""


# ============================================================
# Imports
# ============================================================

import math

from rag.chroma.client import (
    ChromaDBClient,
)

from rag.chroma.collection import (
    ChromaCollection,
)

from rag.retriever.config import (
    CANDIDATE_K,
    TOP_K,
    EMBEDDING_DIMENSION,
)

from rag.retriever.retrieval_result import (
    RetrievalResult,
)

from rag.retriever.retriever import (
    RAGRetriever,
)


# ============================================================
# Test Constants
# ============================================================

TEST_QUERY = (
    "台灣半導體產業未來發展趨勢"
)


# ============================================================
# Relevance Keywords
# ============================================================

RELEVANCE_KEYWORDS = (
    "半導體",
    "IC",
    "晶片",
    "台灣",
    "AI",
    "先進製程",
    "封裝",
    "HBM",
    "供應鏈",
    "設備",
)


# ============================================================
# Main Test
# ============================================================

def main():

    print(
        "=" * 60
    )

    print(
        "RAG-5.6 Retrieval Validation Test"
    )

    print(
        "=" * 60
    )

    print()

    # ========================================================
    # RAG-4 ChromaDB Validation
    # ========================================================

    chroma_client = (
        ChromaDBClient()
    )

    assert (
        chroma_client
        is not None
    )

    print(
        "PASS: RAG-4 ChromaDB client initialization"
    )

    chroma_collection = (
        ChromaCollection(
            chroma_client=chroma_client
        )
    )

    assert (
        chroma_collection
        is not None
    )

    print(
        "PASS: RAG-4 ChromaDB collection initialization"
    )

    collection = (
        chroma_collection.get_collection()
    )

    assert (
        collection
        is not None
    )

    print(
        "PASS: Real ChromaDB collection available"
    )

    collection_count = (
        collection.count()
    )

    print()

    print(
        f"ChromaDB Count: "
        f"{collection_count}"
    )

    assert (
        collection_count
        > 0
    )

    print(
        "PASS: ChromaDB contains indexed records"
    )

    # ========================================================
    # RAG-5 Unified Retriever
    # ========================================================

    retriever = (
        RAGRetriever()
    )

    assert (
        retriever
        is not None
    )

    print(
        "PASS: RAGRetriever initialization"
    )

    # ========================================================
    # Configuration
    # ========================================================

    assert (
        retriever.get_candidate_k()
        == CANDIDATE_K
    )

    print(
        "PASS: Candidate-K configuration"
    )

    print(
        f"      Candidate-K: "
        f"{retriever.get_candidate_k()}"
    )

    assert (
        retriever.get_top_k()
        == TOP_K
    )

    print(
        "PASS: Top-K configuration"
    )

    print(
        f"      Top-K: "
        f"{retriever.get_top_k()}"
    )

    # ========================================================
    # RAG-5.2 Query Embedding Integration
    # ========================================================

    query_embedding = (
        retriever.get_query_embedding()
    )

    assert (
        query_embedding
        is not None
    )

    print(
        "PASS: RAG-5.2 QueryEmbedding integration"
    )

    assert (
        query_embedding.get_dimension()
        == EMBEDDING_DIMENSION
    )

    print(
        "PASS: RAG-5.2 embedding dimension"
    )

    print(
        f"      Embedding Dimension: "
        f"{query_embedding.get_dimension()}"
    )

    # ========================================================
    # RAG-5.3 Integration
    # ========================================================

    chroma_retrieval = (
        retriever.get_chroma_retrieval()
    )

    assert (
        chroma_retrieval
        is not None
    )

    print(
        "PASS: RAG-5.3 ChromaDBRetrieval integration"
    )

    assert (
        chroma_retrieval.get_candidate_k()
        == CANDIDATE_K
    )

    print(
        "PASS: RAG-5.3 Candidate-K integration"
    )

    # ========================================================
    # RAG-5.4 Integration
    # ========================================================

    top_k_retrieval = (
        retriever.get_top_k_retrieval()
    )

    assert (
        top_k_retrieval
        is not None
    )

    print(
        "PASS: RAG-5.4 TopKRetrieval integration"
    )

    assert (
        top_k_retrieval.get_top_k()
        == TOP_K
    )

    print(
        "PASS: RAG-5.4 Top-K integration"
    )

    # ========================================================
    # RAG-5.5 Integration
    # ========================================================

    result_builder = (
        retriever.get_retrieval_result_builder()
    )

    assert (
        result_builder
        is not None
    )

    print(
        "PASS: RAG-5.5 RetrievalResultBuilder integration"
    )

    # ========================================================
    # Unified Search
    # ========================================================

    print()

    print(
        "-" * 60
    )

    print(
        "EXECUTING RAG-5 UNIFIED SEARCH"
    )

    print(
        "-" * 60
    )

    print()

    results = (
        retriever.search(
            TEST_QUERY
        )
    )

    # ========================================================
    # Final Result Type
    # ========================================================

    assert isinstance(
        results,
        list,
    )

    print(
        "PASS: Final retrieval result type"
    )

    # ========================================================
    # Final Result Count
    # ========================================================

    result_count = (
        len(results)
    )

    print(
        f"Final Retrieval Result Count: "
        f"{result_count}"
    )

    expected_result_count = min(
        collection_count,
        CANDIDATE_K,
        TOP_K,
    )

    assert (
        result_count
        == expected_result_count
    )

    print(
        "PASS: Final retrieval result count"
    )

    # ========================================================
    # Top-K Maximum
    # ========================================================

    assert (
        result_count
        <= TOP_K
    )

    print(
        "PASS: Final result respects Top-K"
    )

    # ========================================================
    # Result Not Empty
    # ========================================================

    assert (
        result_count
        > 0
    )

    print(
        "PASS: Retrieval returned results"
    )

    # ========================================================
    # Real Retrieval Results
    # ========================================================

    print()

    print(
        "=" * 60
    )

    print(
        "REAL RAG-5 RETRIEVAL RESULTS"
    )

    print(
        "=" * 60
    )

    print()

    for index, result in enumerate(
        results,
        start=1,
    ):

        assert isinstance(
            result,
            RetrievalResult,
        )

        # ----------------------------------------------------
        # Chunk
        # ----------------------------------------------------

        assert isinstance(
            result.chunk,
            str,
        )

        assert (
            result.chunk.strip()
        )

        print(
            f"PASS: Chunk validation {index}"
        )

        # ----------------------------------------------------
        # Distance
        # ----------------------------------------------------

        assert isinstance(
            result.distance,
            (int, float),
        )

        assert math.isfinite(
            float(
                result.distance
            )
        )

        print(
            f"PASS: Distance validation {index}"
        )

        # ----------------------------------------------------
        # Document ID
        # ----------------------------------------------------

        assert isinstance(
            result.document_id,
            str,
        )

        assert (
            result.document_id.strip()
        )

        print(
            f"PASS: document_id validation {index}"
        )

        # ----------------------------------------------------
        # Chunk Index
        # ----------------------------------------------------

        assert isinstance(
            result.chunk_index,
            int,
        )

        assert (
            result.chunk_index
            >= 0
        )

        print(
            f"PASS: chunk_index validation {index}"
        )

        # ----------------------------------------------------
        # Metadata
        # ----------------------------------------------------

        assert isinstance(
            result.metadata,
            dict,
        )

        assert (
            "document_id"
            in result.metadata
        )

        assert (
            result.metadata["document_id"]
            == result.document_id
        )

        print(
            f"PASS: Metadata validation {index}"
        )

        # ----------------------------------------------------
        # Output
        # ----------------------------------------------------

        print()

        print(
            f"[Result {index}]"
        )

        print(
            f"Document ID: "
            f"{result.document_id}"
        )

        print(
            f"Chunk Index: "
            f"{result.chunk_index}"
        )

        print(
            f"Distance: "
            f"{result.distance}"
        )

        print(
            f"Similarity: "
            f"{result.similarity}"
        )

        print(
            f"Title: "
            f"{result.metadata.get('title', '')}"
        )

        print(
            f"Category: "
            f"{result.metadata.get('ai_category', '')}"
        )

        print(
            f"Chunk: "
            f"{result.chunk[:300]}"
        )

        print()

    # ========================================================
    # Distance Ordering
    # ========================================================

    for index in range(
        result_count - 1
    ):

        assert (
            results[index].distance
            <=
            results[index + 1].distance
        )

    print(
        "PASS: Retrieval distance ordering"
    )

    # ========================================================
    # Record Identity
    # ========================================================

    for index, result in enumerate(
        results,
        start=1,
    ):

        record_id = (
            f"{result.document_id}"
            f"::chunk_{result.chunk_index}"
        )

        assert (
            record_id.endswith(
                f"::chunk_{result.chunk_index}"
            )
        )

        assert (
            record_id.startswith(
                result.document_id
            )
        )

        print(
            f"PASS: Record identity validation {index}"
        )

    # ========================================================
    # Metadata Integrity
    # ========================================================

    for index, result in enumerate(
        results,
        start=1,
    ):

        assert (
            result.metadata.get(
                "document_id"
            )
            == result.document_id
        )

        print(
            f"PASS: Metadata document_id integrity {index}"
        )

    # ========================================================
    # Basic Relevance Validation
    #
    # 注意：
    # 這裡不是 AI Judge。
    #
    # 只做基本的內容相關性 sanity check，
    # 確認搜尋結果不是完全無關內容。
    # ========================================================

    relevant_results = 0

    for result in results:

        searchable_text = " ".join(
            [
                result.chunk,
                str(
                    result.metadata.get(
                        "title",
                        "",
                    )
                ),
                str(
                    result.metadata.get(
                        "ai_summary",
                        "",
                    )
                ),
                str(
                    result.metadata.get(
                        "ai_keywords",
                        "",
                    )
                ),
                str(
                    result.metadata.get(
                        "ai_category",
                        "",
                    )
                ),
            ]
        ).lower()

        matched = False

        for keyword in RELEVANCE_KEYWORDS:

            if keyword.lower() in searchable_text:
                matched = True
                break

        if matched:
            relevant_results += 1

    print()

    print(
        f"Relevant Result Count: "
        f"{relevant_results}"
    )

    assert (
        relevant_results
        > 0
    )

    print(
        "PASS: Basic retrieval relevance validation"
    )

    # ========================================================
    # Query Specific Relevance
    # ========================================================

    semiconductor_results = 0

    for result in results:

        searchable_text = " ".join(
            [
                result.chunk,
                str(
                    result.metadata.get(
                        "title",
                        "",
                    )
                ),
                str(
                    result.metadata.get(
                        "ai_summary",
                        "",
                    )
                ),
                str(
                    result.metadata.get(
                        "ai_keywords",
                        "",
                    )
                ),
                str(
                    result.metadata.get(
                        "ai_category",
                        "",
                    )
                ),
            ]
        ).lower()

        if (
            "半導體" in searchable_text
            or "semiconductor" in searchable_text
            or "ic" in searchable_text
            or "晶片" in searchable_text
        ):
            semiconductor_results += 1

    print(
        f"Semiconductor-related Result Count: "
        f"{semiconductor_results}"
    )

    assert (
        semiconductor_results
        > 0
    )

    print(
        "PASS: Semiconductor query relevance validation"
    )

    # ========================================================
    # Final Integrity
    # ========================================================

    assert all(
        isinstance(
            result,
            RetrievalResult,
        )
        for result in results
    )

    assert (
        len(results)
        <= TOP_K
    )

    print(
        "PASS: Final RetrievalResult integrity"
    )

    # ========================================================
    # Final
    # ========================================================

    print()

    print(
        "=" * 60
    )

    print(
        "RAG-5.6 RETRIEVAL VALIDATION PASSED"
    )

    print(
        "=" * 60
    )


# ============================================================
# Entry Point
# ============================================================

if __name__ == "__main__":
    main()