"""
tests/V7_5/test_rag_retrieval_result_real.py

AutoSearch V7

RAG-5.5

Real Retrieval Result Integration Test

完整實機流程：

    User Query
        ↓
    RAG-5.2 Query Embedding
        ↓
    Qwen/Qwen3-Embedding-0.6B
        ↓
    1024D Query Vector
        ↓
    RAG-5.3 ChromaDB Candidate Retrieval
        ↓
    Candidate-K = 20
        ↓
    RAG-5.4 Final Top-K
        ↓
    Top-K = 5
        ↓
    RAG-5.5 Retrieval Result
        ↓
    List[RetrievalResult]

驗證：

    1. Real ChromaDB
    2. Real Qwen Query Embedding
    3. RAG-5.3 Candidate Retrieval
    4. RAG-5.4 Final Top-K
    5. RAG-5.5 RetrievalResultBuilder
    6. Chunk
    7. Distance
    8. document_id
    9. chunk_index
    10. Metadata
    11. Record ID consistency
    12. Result count
    13. Result alignment
"""


# ============================================================
# Imports
# ============================================================

import math


from rag.chroma.client import (
    ChromaDBClient
)

from rag.chroma.collection import (
    ChromaCollection
)

from rag.retriever.config import (
    CANDIDATE_K,
    TOP_K,
    EMBEDDING_DIMENSION,
)

from rag.retriever.query_embedding import (
    QueryEmbedding
)

from rag.retriever.chroma_retrieval import (
    ChromaDBRetrieval
)

from rag.retriever.top_k import (
    TopKRetrieval
)

from rag.retriever.retrieval_result import (
    RetrievalResult,
    RetrievalResultBuilder,
)


# ============================================================
# Test Constants
# ============================================================

TEST_QUERY = (
    "台灣半導體產業未來發展趨勢"
)


# ============================================================
# Main Test
# ============================================================

def main():

    print(
        "=" * 60
    )

    print(
        "RAG-5.5 Real Retrieval Result Integration Test"
    )

    print(
        "=" * 60
    )

    print()

    # ========================================================
    # RAG-4 ChromaDB
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
    # RAG-5.2 Real Query Embedding
    # ========================================================

    query_embedding = (
        QueryEmbedding()
    )

    assert (
        query_embedding
        is not None
    )

    print(
        "PASS: Real RAG-5.2 QueryEmbedding initialization"
    )

    assert (
        query_embedding.get_dimension()
        == EMBEDDING_DIMENSION
    )

    print(
        "PASS: Real query embedding dimension"
    )

    print(
        f"Embedding Dimension: "
        f"{query_embedding.get_dimension()}"
    )

    query_vector = (
        query_embedding.embed(
            TEST_QUERY
        )
    )

    assert isinstance(
        query_vector,
        list
    )

    print(
        "PASS: Real query embedding generated"
    )

    assert (
        len(query_vector)
        == EMBEDDING_DIMENSION
    )

    print(
        "PASS: Real query embedding dimension validation"
    )

    # ========================================================
    # RAG-5.3 Candidate Retrieval
    # ========================================================

    candidate_retrieval = (
        ChromaDBRetrieval(
            chroma_collection=(
                chroma_collection
            ),
            query_embedding=(
                query_embedding
            ),
            candidate_k=CANDIDATE_K,
        )
    )

    assert (
        candidate_retrieval
        is not None
    )

    print(
        "PASS: Real ChromaDBRetrieval initialization"
    )

    assert (
        candidate_retrieval.get_candidate_k()
        == CANDIDATE_K
    )

    print(
        "PASS: Candidate-K configuration"
    )

    print(
        f"Candidate-K: "
        f"{candidate_retrieval.get_candidate_k()}"
    )

    candidate_result = (
        candidate_retrieval.retrieve(
            TEST_QUERY
        )
    )

    assert (
        isinstance(
            candidate_result,
            dict
        )
    )

    print(
        "PASS: Real ChromaDB candidate retrieval result"
    )

    # ========================================================
    # Candidate Result Fields
    # ========================================================

    required_fields = (
        "ids",
        "documents",
        "metadatas",
        "distances",
    )

    for field in required_fields:

        assert (
            field in candidate_result
        )

        print(
            f"PASS: Candidate result contains {field}"
        )

    # ========================================================
    # Candidate Count
    # ========================================================

    candidate_ids = (
        candidate_result["ids"][0]
    )

    candidate_documents = (
        candidate_result["documents"][0]
    )

    candidate_metadatas = (
        candidate_result["metadatas"][0]
    )

    candidate_distances = (
        candidate_result["distances"][0]
    )

    candidate_count = (
        len(candidate_ids)
    )

    print()

    print(
        f"Candidate Retrieved Count: "
        f"{candidate_count}"
    )

    expected_candidate_count = min(
        collection_count,
        CANDIDATE_K
    )

    assert (
        candidate_count
        == expected_candidate_count
    )

    print(
        "PASS: Candidate retrieval count"
    )

    # ========================================================
    # RAG-5.4 Final Top-K
    # ========================================================

    top_k_retrieval = (
        TopKRetrieval(
            top_k=TOP_K
        )
    )

    assert (
        top_k_retrieval
        is not None
    )

    print(
        "PASS: RAG-5.4 TopKRetrieval initialization"
    )

    assert (
        top_k_retrieval.get_top_k()
        == TOP_K
    )

    print(
        "PASS: RAG-5.4 Top-K configuration"
    )

    print(
        f"Top-K: "
        f"{top_k_retrieval.get_top_k()}"
    )

    final_result = (
        top_k_retrieval.select(
            candidate_result
        )
    )

    assert (
        isinstance(
            final_result,
            dict
        )
    )

    print(
        "PASS: RAG-5.4 final Top-K result"
    )

    # ========================================================
    # Final Top-K Count
    #
    # RAG-5.4 returns flat lists:
    #
    #     ids
    #     documents
    #     metadatas
    #     distances
    #
    # Unlike raw ChromaDB:
    #
    #     ids[0]
    #     documents[0]
    #     metadatas[0]
    #     distances[0]
    # ========================================================

    final_ids = (
        final_result["ids"]
    )

    final_documents = (
        final_result["documents"]
    )

    final_metadatas = (
        final_result["metadatas"]
    )

    final_distances = (
        final_result["distances"]
    )

    final_count = (
        len(final_ids)
    )

    print()

    print(
        f"Final Top-K Count: "
        f"{final_count}"
    )

    expected_final_count = min(
        candidate_count,
        TOP_K
    )

    assert (
        final_count
        == expected_final_count
    )

    print(
        "PASS: Final Top-K count"
    )

    # ========================================================
    # Final Top-K Field Count Consistency
    # ========================================================

    assert (
        len(final_ids)
        == len(final_documents)
        == len(final_metadatas)
        == len(final_distances)
    )

    print(
        "PASS: Final Top-K field count consistency"
    )

    # ========================================================
    # RAG-5.5 Result Builder
    # ========================================================

    builder = (
        RetrievalResultBuilder()
    )

    assert (
        builder
        is not None
    )

    print(
        "PASS: RAG-5.5 RetrievalResultBuilder initialization"
    )

    # ========================================================
    # Build Retrieval Results
    # ========================================================

    retrieval_results = (
        builder.build(
            final_result
        )
    )

    assert isinstance(
        retrieval_results,
        list
    )

    print(
        "PASS: RAG-5.5 RetrievalResult result type"
    )

    assert (
        len(retrieval_results)
        == final_count
    )

    print(
        "PASS: RAG-5.5 retrieval result count"
    )

    # ========================================================
    # Real Retrieval Results
    # ========================================================

    print()

    print(
        "-" * 60
    )

    print(
        "REAL RAG-5.5 RETRIEVAL RESULTS"
    )

    print(
        "-" * 60
    )

    print()

    for index, result in enumerate(
        retrieval_results,
        start=1
    ):

        assert isinstance(
            result,
            RetrievalResult
        )

        # ----------------------------------------------------
        # Chunk
        # ----------------------------------------------------

        assert (
            result.chunk
            == final_documents[index - 1]
        )

        # ----------------------------------------------------
        # Distance
        # ----------------------------------------------------

        assert (
            result.distance
            == final_distances[index - 1]
        )

        # ----------------------------------------------------
        # Metadata
        # ----------------------------------------------------

        assert (
            result.metadata
            == final_metadatas[index - 1]
        )

        # ----------------------------------------------------
        # Record ID
        # ----------------------------------------------------

        record_id = (
            final_ids[index - 1]
        )

        (
            expected_document_id,
            expected_chunk_index,
        ) = builder._parse_record_id(
            record_id
        )

        # ----------------------------------------------------
        # document_id
        # ----------------------------------------------------

        assert (
            result.document_id
            == expected_document_id
        )

        # ----------------------------------------------------
        # chunk_index
        # ----------------------------------------------------

        assert (
            result.chunk_index
            == expected_chunk_index
        )

        # ----------------------------------------------------
        # Metadata document_id
        # ----------------------------------------------------

        metadata_document_id = (
            result.metadata.get(
                "document_id"
            )
        )

        assert (
            metadata_document_id
            == result.document_id
        )

        # ----------------------------------------------------
        # Output
        # ----------------------------------------------------

        print(
            f"[Result {index}]"
        )

        print(
            f"ID: {record_id}"
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
            f"Metadata: "
            f"{result.metadata}"
        )

        print(
            f"Chunk: "
            f"{result.chunk[:200]}"
        )

        print()

    # ========================================================
    # Chunk Validation
    # ========================================================

    for index, result in enumerate(
        retrieval_results,
        start=1
    ):

        assert isinstance(
            result.chunk,
            str
        )

        assert (
            result.chunk.strip()
        )

        print(
            f"PASS: Real chunk validation {index}"
        )

    # ========================================================
    # Distance Validation
    # ========================================================

    for index, result in enumerate(
        retrieval_results,
        start=1
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
            f"PASS: Real distance validation {index}"
        )

    # ========================================================
    # Document ID Validation
    # ========================================================

    for index, result in enumerate(
        retrieval_results,
        start=1
    ):

        assert isinstance(
            result.document_id,
            str
        )

        assert (
            result.document_id.strip()
        )

        print(
            f"PASS: Real document_id validation {index}"
        )

    # ========================================================
    # Chunk Index Validation
    # ========================================================

    for index, result in enumerate(
        retrieval_results,
        start=1
    ):

        assert isinstance(
            result.chunk_index,
            int
        )

        assert (
            result.chunk_index
            >= 0
        )

        print(
            f"PASS: Real chunk_index validation {index}"
        )

    # ========================================================
    # Metadata Validation
    # ========================================================

    for index, result in enumerate(
        retrieval_results,
        start=1
    ):

        assert isinstance(
            result.metadata,
            dict
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
            f"PASS: Real metadata validation {index}"
        )

    # ========================================================
    # Result Alignment
    # ========================================================

    assert (
        len(final_ids)
        == len(final_documents)
        == len(final_metadatas)
        == len(final_distances)
        == len(retrieval_results)
    )

    print(
        "PASS: Real result field count alignment"
    )

    # ========================================================
    # Record ID Consistency
    # ========================================================

    for index, result in enumerate(
        retrieval_results
    ):

        record_id = (
            final_ids[index]
        )

        expected_prefix = (
            f"{result.document_id}::chunk_"
        )

        assert (
            record_id.startswith(
                expected_prefix
            )
        )

        print(
            f"PASS: Real record ID consistency "
            f"{index + 1}"
        )

    # ========================================================
    # Distance Ordering
    # ========================================================

    for index in range(
        len(retrieval_results) - 1
    ):

        assert (
            retrieval_results[index].distance
            <=
            retrieval_results[index + 1].distance
        )

    print(
        "PASS: Real final Top-K distance ordering"
    )

    # ========================================================
    # Similarity Handling
    # ========================================================

    for index, result in enumerate(
        retrieval_results,
        start=1
    ):

        assert (
            result.similarity
            is None
        )

        print(
            f"PASS: Similarity handling {index}"
        )

    # ========================================================
    # Final Result Count
    # ========================================================

    assert (
        builder.count(
            retrieval_results
        )
        == expected_final_count
    )

    print(
        "PASS: Final retrieval result count consistency"
    )

    # ========================================================
    # Final
    # ========================================================

    print()

    print(
        "=" * 60
    )

    print(
        "REAL RAG-5.5 RETRIEVAL RESULT "
        "INTEGRATION TEST PASSED"
    )

    print(
        "=" * 60
    )


# ============================================================
# Entry Point
# ============================================================

if __name__ == "__main__":
    main()