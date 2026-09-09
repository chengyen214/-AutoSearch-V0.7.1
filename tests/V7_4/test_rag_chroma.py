"""
tests/V7_4/test_rag_chroma.py

AutoSearch V7

RAG-4.6

ChromaDB Integration Test

測試範圍：

    RAG-4 ChromaDB 整體整合

功能：

    1. RAG-4.1 Configuration integration
    2. RAG-4.2 Client integration
    3. RAG-4.3 Collection integration
    4. RAG-4.4 Indexer integration
    5. RAG-4.5 Index Validation integration
    6. ChromaDB persistence verification

完整資料流程：

    RAG-1 Document Preparation
            ↓
    RAG-2 Chunking
            ↓
    RAG-3 Embedding
            ↓
    RAG-3 Mapping
            ↓
    RAG-4.1 Configuration
            ↓
    RAG-4.2 Client
            ↓
    RAG-4.3 Collection
            ↓
    RAG-4.4 Indexer
            ↓
    ChromaDB
            ↓
    RAG-4.5 Validation

本測試不負責：

    1. MySQL
    2. MCP implementation
    3. RAG-1 implementation
    4. RAG-2 implementation
    5. RAG-3 implementation
    6. RAG-4.4 Indexer implementation details
    7. RAG-5 Retriever
    8. Full Indexing Pipeline
    9. Incremental Indexing Pipeline
"""


# ============================================================
# Imports
# ============================================================

from langchain_core.documents import (
    Document
)


from rag.document_preparation import (
    DocumentPreparation
)


from rag.chunking.document_chunking import (
    DocumentChunking
)


from rag.embedding.embedding_pipeline import (
    EmbeddingPipeline
)


from rag.chroma.client import (
    ChromaDBClient
)


from rag.chroma.collection import (
    ChromaCollection
)


from rag.chroma.config import (
    CHROMA_PERSIST_DIRECTORY,
    CHROMA_COLLECTION_NAME,
    CHROMA_DISTANCE_METRIC,
    EMBEDDING_DIMENSION,
    SUPPORTED_DISTANCE_METRICS,
)


from rag.chroma.indexer import (
    ChromaIndexer
)
import math

# ============================================================
# Test Article
# ============================================================

TEST_DOCUMENT_ID = (
    "d9ce4740c3f0b6f1d260c094c0549f68727187b0a2b57c94f6308b4df9fd9d13"
)


# ============================================================
# Test Collection
# ============================================================

TEST_COLLECTION_NAME = (
    "rag_4_6_chroma_integration_test"
)


# ============================================================
# Expected Dimension
# ============================================================

EXPECTED_DIMENSION = (
    EMBEDDING_DIMENSION
)


# ============================================================
# Expected Metadata
# ============================================================

EXPECTED_METADATA_FIELDS = {
    "document_id",
    "title",
    "url",
    "keyword",
    "source",
    "crawl_time",
    "ai_summary",
    "ai_category",
    "ai_keywords",
    "ai_importance",
    "ai_confidence",
}


# ============================================================
# Shared Objects
# ============================================================

_DOCUMENT = None
_CHUNKS = None
_EMBEDDING_PIPELINE = None
_RAG3_MAPPINGS = None

_CHROMA_CLIENT = None
_CHROMA_COLLECTION = None
_INDEXER = None


# ============================================================
# RAG-4.1
# Configuration Integration
# ============================================================

def test_configuration_integration():
    """
    驗證 RAG-4.1 Configuration
    可以被 RAG-4 ChromaDB Layer 正常使用。
    """

    assert isinstance(
        CHROMA_PERSIST_DIRECTORY,
        str
    )

    assert (
        CHROMA_PERSIST_DIRECTORY.strip()
        != ""
    )

    assert isinstance(
        CHROMA_COLLECTION_NAME,
        str
    )

    assert (
        CHROMA_COLLECTION_NAME.strip()
        != ""
    )

    assert (
        CHROMA_DISTANCE_METRIC
        in SUPPORTED_DISTANCE_METRICS
    )

    assert (
        EMBEDDING_DIMENSION
        > 0
    )

    print(
        "PASS: RAG-4.1 Configuration integration"
    )

    print(
        f"      Persist Directory: "
        f"{CHROMA_PERSIST_DIRECTORY}"
    )

    print(
        f"      Collection: "
        f"{CHROMA_COLLECTION_NAME}"
    )

    print(
        f"      Distance Metric: "
        f"{CHROMA_DISTANCE_METRIC}"
    )

    print(
        f"      Embedding Dimension: "
        f"{EMBEDDING_DIMENSION}"
    )


# ============================================================
# RAG-4.2
# Client Integration
# ============================================================

def create_chroma_client():
    """
    建立共用 RAG-4.2 Client。
    """

    global _CHROMA_CLIENT

    if _CHROMA_CLIENT is None:

        _CHROMA_CLIENT = (
            ChromaDBClient()
        )

    return _CHROMA_CLIENT


def test_client_integration():
    """
    驗證 RAG-4.2 Client。
    """

    client = (
        create_chroma_client()
    )

    assert isinstance(
        client,
        ChromaDBClient
    )

    assert (
        client.get_client()
        is not None
    )

    assert (
        client.get_persist_directory()
        == CHROMA_PERSIST_DIRECTORY
    )

    assert hasattr(
        client.get_client(),
        "get_or_create_collection"
    )

    print(
        "PASS: RAG-4.2 Client integration"
    )

    print(
        f"      Persist Directory: "
        f"{client.get_persist_directory()}"
    )


# ============================================================
# RAG-4.3
# Collection Integration
# ============================================================

def create_chroma_collection():
    """
    建立 RAG-4.6 專用測試 Collection。
    """

    global _CHROMA_COLLECTION

    if _CHROMA_COLLECTION is None:

        _CHROMA_COLLECTION = (
            ChromaCollection(
                chroma_client=(
                    create_chroma_client()
                ),
                collection_name=(
                    TEST_COLLECTION_NAME
                ),
                distance_metric=(
                    CHROMA_DISTANCE_METRIC
                )
            )
        )

    return _CHROMA_COLLECTION


def test_collection_integration():
    """
    驗證 RAG-4.3 Collection。
    """

    collection = (
        create_chroma_collection()
    )

    assert isinstance(
        collection,
        ChromaCollection
    )

    assert (
        collection.get_collection()
        is not None
    )

    assert (
        collection.get_collection_name()
        == TEST_COLLECTION_NAME
    )

    assert (
        collection.get_distance_metric()
        == CHROMA_DISTANCE_METRIC
    )

    chroma_collection = (
        collection.get_collection()
    )

    required_methods = [
        "get",
        "upsert",
        "count",
        "delete",
    ]

    for method_name in required_methods:

        assert hasattr(
            chroma_collection,
            method_name
        )

    print(
        "PASS: RAG-4.3 Collection integration"
    )

    print(
        f"      Collection: "
        f"{collection.get_collection_name()}"
    )

    print(
        f"      Distance Metric: "
        f"{collection.get_distance_metric()}"
    )


# ============================================================
# RAG-4.4
# Indexer Integration
# ============================================================

def create_indexer():
    """
    建立共用 ChromaIndexer。
    """

    global _INDEXER

    if _INDEXER is None:

        _INDEXER = (
            ChromaIndexer(
                chroma_collection=(
                    create_chroma_collection()
                )
            )
        )

    return _INDEXER


def create_document():
    """
    建立真實 RAG-1 Prepared Document。
    """

    global _DOCUMENT

    if _DOCUMENT is None:

        preparation = (
            DocumentPreparation()
        )

        _DOCUMENT = (
            preparation.prepare_by_document_id(
                TEST_DOCUMENT_ID
            )
        )

    assert isinstance(
        _DOCUMENT,
        Document
    )

    assert (
        _DOCUMENT.metadata[
            "document_id"
        ]
        == TEST_DOCUMENT_ID
    )

    return _DOCUMENT


def create_chunks():
    """
    建立真實 RAG-2 Chunks。
    """

    global _CHUNKS

    if _CHUNKS is None:

        document = (
            create_document()
        )

        chunking = (
            DocumentChunking()
        )

        _CHUNKS = (
            chunking.chunk(
                document
            )
        )

    assert isinstance(
        _CHUNKS,
        list
    )

    assert (
        len(_CHUNKS)
        > 0
    )

    return _CHUNKS


def create_embedding_pipeline():
    """
    建立共用 RAG-3 EmbeddingPipeline。
    """

    global _EMBEDDING_PIPELINE

    if _EMBEDDING_PIPELINE is None:

        _EMBEDDING_PIPELINE = (
            EmbeddingPipeline()
        )

    return _EMBEDDING_PIPELINE


def create_rag3_mappings():
    """
    建立真實 RAG-3 Mapping。

    正式 Mapping：

        {
            "document": Document,
            "embedding": list[float]
        }
    """

    global _RAG3_MAPPINGS

    if _RAG3_MAPPINGS is None:

        chunks = (
            create_chunks()
        )

        pipeline = (
            create_embedding_pipeline()
        )

        result = (
            pipeline.process_chunks(
                chunks
            )
        )

        _RAG3_MAPPINGS = (
            result["mappings"]
        )

    assert isinstance(
        _RAG3_MAPPINGS,
        list
    )

    assert (
        len(_RAG3_MAPPINGS)
        == len(create_chunks())
    )

    return _RAG3_MAPPINGS


# ============================================================
# RAG-4.4 Indexer Integration Test
# ============================================================

def test_indexer_integration():
    """
    驗證：

        RAG-3 Mapping
              ↓
        RAG-4.4 Indexer
              ↓
        ChromaDB
    """

    mappings = (
        create_rag3_mappings()
    )

    indexer = (
        create_indexer()
    )

    ids = (
        indexer.index_mappings(
            mappings
        )
    )

    assert isinstance(
        ids,
        list
    )

    assert (
        len(ids)
        == len(mappings)
    )

    for index, record_id in enumerate(
        ids
    ):

        expected_id = (
            f"{TEST_DOCUMENT_ID}"
            f"::chunk_{index}"
        )

        assert (
            record_id
            == expected_id
        )

    print(
        "PASS: RAG-4.4 Indexer integration"
    )

    print(
        f"      Mappings: "
        f"{len(mappings)}"
    )

    print(
        f"      Indexed Records: "
        f"{len(ids)}"
    )


# ============================================================
# RAG-4.5
# Index Validation Integration
# ============================================================

def test_index_validation_integration():
    """
    驗證：

        Count
        Dimension
        Metadata
        Stored Vector
    """

    mappings = (
        create_rag3_mappings()
    )

    indexer = (
        create_indexer()
    )

    ids = (
        indexer.index_mappings(
            mappings
        )
    )

    # --------------------------------------------------------
    # Count
    # --------------------------------------------------------

    count = (
        indexer.count()
    )

    assert (
        count
        >= len(ids)
    )

    # --------------------------------------------------------
    # Every Record
    # --------------------------------------------------------

    for index, record_id in enumerate(
        ids
    ):

        result = (
            indexer.get_record(
                record_id
            )
        )

        assert (
            result["ids"]
            is not None
        )

        assert (
            len(result["ids"])
            == 1
        )

        # ----------------------------------------------------
        # Document
        # ----------------------------------------------------

        documents = (
            result["documents"]
        )

        assert (
            documents
            is not None
        )

        assert (
            len(documents)
            == 1
        )

        assert (
            documents[0]
            == mappings[index][
                "document"
            ].page_content
        )

        # ----------------------------------------------------
        # Metadata
        # ----------------------------------------------------

        metadatas = (
            result["metadatas"]
        )

        assert (
            metadatas
            is not None
        )

        assert (
            len(metadatas)
            == 1
        )

        metadata = (
            metadatas[0]
        )

        assert (
            set(metadata.keys())
            == EXPECTED_METADATA_FIELDS
        )

        assert (
            metadata["document_id"]
            == mappings[index][
                "document"
            ].metadata[
                "document_id"
            ]
        )

        # ----------------------------------------------------
        # Embedding
        # ----------------------------------------------------

        embeddings = (
            result["embeddings"]
        )

        assert (
            embeddings
            is not None
        )

        assert (
            len(embeddings)
            == 1
        )

        vector = (
            embeddings[0]
        )

        assert (
            vector
            is not None
        )

        assert (
            len(vector)
            == EXPECTED_DIMENSION
        )

        for value in vector:

            assert math.isfinite(
                float(value)
            )

    print(
        "PASS: RAG-4.5 Index Validation integration"
    )

    print(
        f"      Count: {count}"
    )

    print(
        f"      Dimension: "
        f"{EXPECTED_DIMENSION}"
    )

    print(
        f"      Metadata fields: "
        f"{len(EXPECTED_METADATA_FIELDS)}"
    )


# ============================================================
# Persistence Verification
# ============================================================

def test_persistence():
    """
    驗證 PersistentClient。

    流程：

        Client A
            ↓
        Collection
            ↓
        Index Record
            ↓
        Client A 結束
            ↓
        Client B
            ↓
        同一 Persist Directory
            ↓
        Record 仍存在
    """

    mappings = (
        create_rag3_mappings()
    )

    first_client = (
        ChromaDBClient()
    )

    first_collection = (
        ChromaCollection(
            chroma_client=first_client,
            collection_name=(
                TEST_COLLECTION_NAME
            ),
            distance_metric=(
                CHROMA_DISTANCE_METRIC
            )
        )
    )

    first_indexer = (
        ChromaIndexer(
            chroma_collection=first_collection
        )
    )

    ids = (
        first_indexer.index_mappings(
            mappings
        )
    )

    assert (
        len(ids)
        == len(mappings)
    )

    first_count = (
        first_indexer.count()
    )

    assert (
        first_count
        >= len(ids)
    )

    record_id = ids[0]

    first_result = (
        first_indexer.get_record(
            record_id
        )
    )

    assert (
        first_result["ids"]
        is not None
    )

    assert (
        len(first_result["ids"])
        == 1
    )

    # --------------------------------------------------------
    # 建立全新的 Client / Collection / Indexer
    # --------------------------------------------------------

    second_client = (
        ChromaDBClient()
    )

    assert (
        second_client.get_persist_directory()
        == first_client.get_persist_directory()
    )

    second_collection = (
        ChromaCollection(
            chroma_client=second_client,
            collection_name=(
                TEST_COLLECTION_NAME
            ),
            distance_metric=(
                CHROMA_DISTANCE_METRIC
            )
        )
    )

    second_indexer = (
        ChromaIndexer(
            chroma_collection=second_collection
        )
    )

    second_count = (
        second_indexer.count()
    )

    assert (
        second_count
        == first_count
    )

    second_result = (
        second_indexer.get_record(
            record_id
        )
    )

    assert (
        second_result["ids"]
        is not None
    )

    assert (
        len(second_result["ids"])
        == 1
    )

    assert (
        second_result["documents"][0]
        == first_result["documents"][0]
    )

    assert (
        second_result["metadatas"][0]
        == first_result["metadatas"][0]
    )

    assert (
        len(
            second_result[
                "embeddings"
            ][0]
        )
        == EXPECTED_DIMENSION
    )

    print(
        "PASS: ChromaDB persistence verification"
    )

    print(
        f"      Persist Directory: "
        f"{second_client.get_persist_directory()}"
    )

    print(
        f"      First Count: "
        f"{first_count}"
    )

    print(
        f"      Second Count: "
        f"{second_count}"
    )


# ============================================================
# Cross Layer Integration
# ============================================================

def test_full_chroma_integration():
    """
    驗證完整 RAG-4 Layer。

        Configuration
              ↓
        Client
              ↓
        Collection
              ↓
        Indexer
              ↓
        ChromaDB
              ↓
        Validation
    """

    assert (
        create_chroma_client()
        .get_persist_directory()
        == CHROMA_PERSIST_DIRECTORY
    )

    collection = (
        create_chroma_collection()
    )

    assert (
        collection.get_collection_name()
        == TEST_COLLECTION_NAME
    )

    indexer = (
        create_indexer()
    )

    mappings = (
        create_rag3_mappings()
    )

    ids = (
        indexer.index_mappings(
            mappings
        )
    )

    assert (
        len(ids)
        == len(mappings)
    )

    count = (
        indexer.count()
    )

    assert (
        count
        >= len(ids)
    )

    for index, record_id in enumerate(
        ids
    ):

        result = (
            indexer.get_record(
                record_id
            )
        )

        assert (
            result["ids"][0]
            == record_id
        )

        assert (
            result["documents"][0]
            == mappings[index][
                "document"
            ].page_content
        )

        assert (
            result["metadatas"][0][
                "document_id"
            ]
            == TEST_DOCUMENT_ID
        )

        assert (
            len(
                result[
                    "embeddings"
                ][0]
            )
            == EXPECTED_DIMENSION
        )

    print(
        "PASS: Full RAG-4 ChromaDB integration"
    )

    print(
        f"      Document ID: "
        f"{TEST_DOCUMENT_ID}"
    )

    print(
        f"      Chunk count: "
        f"{len(mappings)}"
    )

    print(
        f"      ChromaDB count: "
        f"{count}"
    )


# ============================================================
# Main
# ============================================================

def main():
    """
    執行 RAG-4.6 ChromaDB Integration Test。
    """

    print(
        "=" * 60
    )

    print(
        "RAG-4.6 ChromaDB Integration Test"
    )

    print(
        "=" * 60
    )

    print()

    print(
        "Testing:"
    )

    print(
        "RAG-4.1 Configuration integration"
    )

    print(
        "RAG-4.2 Client integration"
    )

    print(
        "RAG-4.3 Collection integration"
    )

    print(
        "RAG-4.4 Indexer integration"
    )

    print(
        "RAG-4.5 Index Validation integration"
    )

    print(
        "ChromaDB persistence verification"
    )

    print()

    # --------------------------------------------------------
    # RAG-4.1
    # --------------------------------------------------------

    test_configuration_integration()

    # --------------------------------------------------------
    # RAG-4.2
    # --------------------------------------------------------

    test_client_integration()

    # --------------------------------------------------------
    # RAG-4.3
    # --------------------------------------------------------

    test_collection_integration()

    # --------------------------------------------------------
    # RAG-4.4
    # --------------------------------------------------------

    test_indexer_integration()

    # --------------------------------------------------------
    # RAG-4.5
    # --------------------------------------------------------

    test_index_validation_integration()

    # --------------------------------------------------------
    # Persistence
    # --------------------------------------------------------

    test_persistence()

    # --------------------------------------------------------
    # Full Integration
    # --------------------------------------------------------

    test_full_chroma_integration()

    print()

    print(
        "=" * 60
    )

    print(
        "ALL RAG-4.6 CHROMADB TESTS PASSED"
    )

    print(
        "=" * 60
    )


if __name__ == "__main__":
    main()