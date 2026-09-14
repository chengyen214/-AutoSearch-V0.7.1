"""
tests/V7_5/test_rag_chroma_retrieval_real.py

AutoSearch V7

RAG-5.3
Real ChromaDB Candidate Retrieval Integration Test

目的：

    使用真正的：

        RAG-5.2 QueryEmbedding
        Qwen/Qwen3-Embedding-0.6B
        ChromaDB Persistent Collection

    驗證：

        Query
            ↓
        Query Embedding
            ↓
        ChromaDB Similarity Search
            ↓
        Candidate Retrieval Results

本測試：

    RAG-5.3
        負責取得 Candidate Results

    RAG-5.4
        負責 Final Top-K Selection

因此本測試不使用 TOP_K，
而使用 CANDIDATE_K。
"""


from rag.retriever.chroma_retrieval import (
    ChromaDBRetrieval,
)

from rag.retriever.query_embedding import (
    QueryEmbedding,
)

from rag.chroma.client import (
    ChromaDBClient,
)

from rag.chroma.collection import (
    ChromaCollection,
)

from rag.retriever.config import (
    CANDIDATE_K,
    EMBEDDING_DIMENSION,
)


# ============================================================
# Test Query
# ============================================================

TEST_QUERY = (
    "台灣半導體產業未來發展趨勢"
)


# ============================================================
# Assertion
# ============================================================

def check(
    condition,
    message,
):

    if not condition:
        raise AssertionError(
            message
        )

    print(
        f"PASS: {message}"
    )


# ============================================================
# Main
# ============================================================

def main():

    print(
        "=" * 60
    )

    print(
        "RAG-5.3 Real ChromaDB Candidate Retrieval "
        "Integration Test"
    )

    print(
        "=" * 60
    )

    print()

    print(
        f"Query: {TEST_QUERY}"
    )

    print()

    # --------------------------------------------------------
    # RAG-4 ChromaDB Client
    # --------------------------------------------------------

    chroma_client = (
        ChromaDBClient()
    )

    check(
        chroma_client is not None,
        "RAG-4 ChromaDB client initialization",
    )

    # --------------------------------------------------------
    # RAG-4 ChromaDB Collection
    # --------------------------------------------------------

    chroma_collection = (
        ChromaCollection(
            chroma_client=chroma_client
        )
    )

    check(
        chroma_collection is not None,
        "RAG-4 ChromaDB collection initialization",
    )

    collection = (
        chroma_collection.get_collection()
    )

    check(
        collection is not None,
        "Real ChromaDB collection available",
    )

    # --------------------------------------------------------
    # Collection Count
    # --------------------------------------------------------

    collection_count = (
        collection.count()
    )

    print()

    print(
        f"ChromaDB Count: {collection_count}"
    )

    check(
        collection_count > 0,
        "ChromaDB contains indexed records",
    )

    # --------------------------------------------------------
    # RAG-5.2 Query Embedding
    # --------------------------------------------------------

    query_embedding = (
        QueryEmbedding()
    )

    check(
        query_embedding is not None,
        "Real RAG-5.2 QueryEmbedding initialization",
    )

    dimension = (
        query_embedding.get_dimension()
    )

    check(
        dimension
        == EMBEDDING_DIMENSION,
        "Real query embedding dimension",
    )

    print(
        f"Embedding Dimension: {dimension}"
    )

    # --------------------------------------------------------
    # Generate Real Query Embedding
    # --------------------------------------------------------

    vector = (
        query_embedding.embed(
            TEST_QUERY
        )
    )

    check(
        vector is not None,
        "Real query embedding generated",
    )

    check(
        isinstance(
            vector,
            list,
        ),
        "Real query embedding type",
    )

    check(
        len(vector)
        == EMBEDDING_DIMENSION,
        "Real query embedding dimension validation",
    )

    # --------------------------------------------------------
    # RAG-5.3 Candidate Retrieval
    # --------------------------------------------------------

    retriever = (
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

    check(
        retriever is not None,
        "Real ChromaDBRetrieval initialization",
    )

    check(
        retriever.get_candidate_k()
        == CANDIDATE_K,
        "Candidate-K configuration",
    )

    print(
        f"Candidate-K: {retriever.get_candidate_k()}"
    )

    result = (
        retriever.retrieve(
            TEST_QUERY
        )
    )

    check(
        result is not None,
        "Real ChromaDB candidate retrieval result",
    )

    check(
        isinstance(
            result,
            dict,
        ),
        "Real candidate retrieval result type",
    )

    # --------------------------------------------------------
    # Result Fields
    # --------------------------------------------------------

    required_fields = [
        "ids",
        "documents",
        "metadatas",
        "distances",
    ]

    for field in required_fields:

        check(
            field in result,
            f"Real retrieval contains {field}",
        )

    # --------------------------------------------------------
    # Result Group
    # --------------------------------------------------------

    ids = result["ids"][0]
    documents = result["documents"][0]
    metadatas = result["metadatas"][0]
    distances = result["distances"][0]

    # --------------------------------------------------------
    # Candidate Result Count
    # --------------------------------------------------------

    result_count = len(ids)

    print()

    print(
        f"Candidate Retrieved Count: "
        f"{result_count}"
    )

    check(
        result_count > 0,
        "Real candidate retrieval returned results",
    )

    check(
        result_count
        <= CANDIDATE_K,
        "Candidate retrieval count respects Candidate-K",
    )

    # --------------------------------------------------------
    # Candidate Count Behavior
    # --------------------------------------------------------

    expected_count = min(
        collection_count,
        CANDIDATE_K,
    )

    check(
        result_count
        == expected_count,
        "Candidate retrieval count matches expected count",
    )

    # --------------------------------------------------------
    # Result Consistency
    # --------------------------------------------------------

    check(
        len(ids)
        == len(documents)
        == len(metadatas)
        == len(distances),
        "Real candidate retrieval result count consistency",
    )

    # --------------------------------------------------------
    # Result Detail
    # --------------------------------------------------------

    print()

    print(
        "-" * 60
    )

    print(
        "REAL CANDIDATE RETRIEVAL RESULTS"
    )

    print(
        "-" * 60
    )

    for index in range(
        result_count
    ):

        print()

        print(
            f"[Candidate {index + 1}]"
        )

        print(
            f"ID: {ids[index]}"
        )

        print(
            f"Distance: {distances[index]}"
        )

        print(
            f"Metadata: {metadatas[index]}"
        )

        document = documents[index]

        if document is None:
            document = ""

        preview = (
            str(document)
            .replace(
                "\n",
                " ",
            )
        )

        if len(preview) > 200:
            preview = (
                preview[:200]
                + "..."
            )

        print(
            f"Document: {preview}"
        )

    # --------------------------------------------------------
    # Distance
    # --------------------------------------------------------

    check(
        all(
            distance is not None
            for distance in distances
        ),
        "Real retrieval distances available",
    )

    # --------------------------------------------------------
    # Distance Ordering
    # --------------------------------------------------------
    #
    # ChromaDB cosine distance：
    #
    # smaller distance
    #     =
    # more similar
    #
    # ChromaDB should return results
    # ordered by distance.
    #

    if len(distances) >= 2:

        check(
            all(
                distances[index]
                <= distances[index + 1]
                for index in range(
                    len(distances) - 1
                )
            ),
            "Real retrieval distance ordering",
        )

    # --------------------------------------------------------
    # Metadata Validation
    # --------------------------------------------------------

    for index, metadata in enumerate(
        metadatas
    ):

        check(
            isinstance(
                metadata,
                dict,
            ),
            f"Real metadata type {index + 1}",
        )

        check(
            "document_id" in metadata,
            f"Real metadata document_id {index + 1}",
        )

    # --------------------------------------------------------
    # ID / Metadata Consistency
    # --------------------------------------------------------

    for index in range(
        result_count
    ):

        record_id = (
            ids[index]
        )

        metadata_document_id = (
            metadatas[index]
            .get(
                "document_id"
            )
        )

        check(
            isinstance(
                record_id,
                str,
            ),
            f"Real record ID type {index + 1}",
        )

        check(
            isinstance(
                metadata_document_id,
                str,
            ),
            f"Real document_id type {index + 1}",
        )

        check(
            metadata_document_id
            == record_id.split(
                "::chunk_"
            )[0],
            f"Record ID / document_id consistency "
            f"{index + 1}",
        )

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    print()

    print(
        "=" * 60
    )

    print(
        "REAL RAG-5.3 CANDIDATE RETRIEVAL "
        "TEST SUMMARY"
    )

    print(
        "=" * 60
    )

    print(
        f"Query: {TEST_QUERY}"
    )

    print(
        f"ChromaDB Count: {collection_count}"
    )

    print(
        f"Candidate-K: {CANDIDATE_K}"
    )

    print(
        f"Candidate Retrieved Count: "
        f"{result_count}"
    )

    print(
        f"Embedding Dimension: {dimension}"
    )

    print()

    print(
        "Flow:"
    )

    print(
        "  Query"
    )

    print(
        "    ↓"
    )

    print(
        "  RAG-5.2 Query Embedding"
    )

    print(
        "    ↓"
    )

    print(
        "  RAG-5.3 ChromaDB Candidate Retrieval"
    )

    print(
        f"    ↓ ({result_count} candidates)"
    )

    print(
        "  RAG-5.4 Final Top-K"
    )

    print(
        "    ↓"
    )

    print(
        "  Final Retrieval Results"
    )

    print()

    print(
        "=" * 60
    )

    print(
        "REAL RAG-5.3 CHROMADB CANDIDATE "
        "RETRIEVAL INTEGRATION TEST PASSED"
    )

    print(
        "=" * 60
    )


if __name__ == "__main__":
    main()