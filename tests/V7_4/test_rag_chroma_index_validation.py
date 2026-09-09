"""
tests/V7_4/test_rag_chroma_index_validation.py

AutoSearch V7

RAG-4.5

ChromaDB Index Validation Test

測試範圍：

    RAG-4.5 Index Validation

核心驗證：

    1. Count
    2. Dimension
    3. Metadata
    4. Stored Vector

資料流程：

    RAG-3 EmbeddingPipeline
            ↓
    RAG-3 Mapping
            ↓
    RAG-4.4 ChromaIndexer
            ↓
    ChromaDB
            ↓
    RAG-4.5 Index Validation

正式 Metadata Schema：

    RAG-1.3 Metadata

        1. document_id
        2. title
        3. url
        4. keyword
        5. source
        6. crawl_time
        7. ai_summary
        8. ai_category
        9. ai_keywords
        10. ai_importance
        11. ai_confidence

本測試不負責：

    1. MySQL
    2. MCP
    3. RAG-1 Document Preparation implementation
    4. RAG-2 Chunking implementation
    5. RAG-3 Embedding implementation
    6. RAG-4.1 Configuration
    7. RAG-4.2 Client implementation
    8. RAG-4.3 Collection implementation
    9. RAG-4.4 Indexer implementation
    10. RAG-5 Retriever
"""


import math


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


from rag.chroma.indexer import (
    ChromaIndexer
)


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
    "rag_4_5_index_validation_test"
)


# ============================================================
# Expected Embedding Dimension
# ============================================================

EXPECTED_DIMENSION = 1024


# ============================================================
# RAG-1.3 Metadata Schema
# ============================================================

REQUIRED_METADATA_FIELDS = {
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
# Create Prepared Document
# ============================================================

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


# ============================================================
# Create Chunks
# ============================================================

def create_chunks():
    """
    建立真實 RAG-2 Chunks。
    """

    global _CHUNKS

    if _CHUNKS is None:

        document = create_document()

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


# ============================================================
# Create Embedding Pipeline
# ============================================================

def create_embedding_pipeline():
    """
    建立共用 RAG-3 EmbeddingPipeline。

    Qwen Model 只初始化一次。
    """

    global _EMBEDDING_PIPELINE

    if _EMBEDDING_PIPELINE is None:

        _EMBEDDING_PIPELINE = (
            EmbeddingPipeline()
        )

    return _EMBEDDING_PIPELINE


# ============================================================
# Create RAG-3 Mappings
# ============================================================

def create_rag3_mappings():
    """
    建立真實 RAG-3 Embedding Mapping。

    正式 Mapping 結構：

        {
            "document": Document,
            "embedding": list[float]
        }
    """

    global _RAG3_MAPPINGS

    if _RAG3_MAPPINGS is None:

        chunks = create_chunks()

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

    for mapping in _RAG3_MAPPINGS:

        assert isinstance(
            mapping,
            dict
        )

        assert (
            "document"
            in mapping
        )

        assert (
            "embedding"
            in mapping
        )

        assert isinstance(
            mapping["document"],
            Document
        )

        assert isinstance(
            mapping["embedding"],
            list
        )

        assert (
            len(
                mapping["embedding"]
            )
            == EXPECTED_DIMENSION
        )

    return _RAG3_MAPPINGS


# ============================================================
# Create Chroma Client
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


# ============================================================
# Create Test Collection
# ============================================================

def create_chroma_collection():
    """
    建立 RAG-4.5 專用測試 Collection。

    完全沿用 RAG-4.4
    已驗證成功的 Collection API。
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
                distance_metric="cosine"
            )
        )

    return _CHROMA_COLLECTION


# ============================================================
# Create Indexer
# ============================================================

def create_indexer():
    """
    建立共用 ChromaIndexer。

    完全沿用 RAG-4.4
    已驗證成功的 Indexer API。
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


# ============================================================
# Prepare Index
# ============================================================

def prepare_index():
    """
    建立 RAG-4.5 Index Validation 所需的 ChromaDB Index。

    RAG-3 Mapping
            ↓
    ChromaIndexer
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

    return (
        indexer,
        mappings,
        ids
    )


# ============================================================
# RAG-4.5.1
# Count Validation
# ============================================================

def test_count_validation():
    """
    驗證：

        Indexed Mapping Count
                =
        ChromaDB Record Count
    """

    indexer, mappings, ids = (
        prepare_index()
    )

    count = (
        indexer.count()
    )

    assert (
        count
        >= len(ids)
    )

    print(
        "PASS: Count validation"
    )

    print(
        f"      Expected records: "
        f"{len(ids)}"
    )

    print(
        f"      ChromaDB count: "
        f"{count}"
    )


# ============================================================
# RAG-4.5.2
# Dimension Validation
# ============================================================

def test_dimension_validation():
    """
    驗證：

        Stored Vector Dimension
                =
        RAG-3 Embedding Dimension
                =
                 1024
    """

    indexer, mappings, ids = (
        prepare_index()
    )

    for record_id in ids:

        result = (
            indexer.get_record(
                record_id
            )
        )

        embeddings = (
            result[
                "embeddings"
            ]
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

    print(
        "PASS: Dimension validation"
    )

    print(
        f"      Expected dimension: "
        f"{EXPECTED_DIMENSION}"
    )

    print(
        f"      Validated records: "
        f"{len(ids)}"
    )


# ============================================================
# RAG-4.5.3
# Metadata Validation
# ============================================================

def test_metadata_validation():
    """
    驗證：

        RAG-1.3 Metadata
                ↓
        ChromaDB Metadata

    正式 Schema：

        document_id
        title
        url
        keyword
        source
        crawl_time
        ai_summary
        ai_category
        ai_keywords
        ai_importance
        ai_confidence
    """

    indexer, mappings, ids = (
        prepare_index()
    )

    assert (
        len(mappings)
        == len(ids)
    )

    for index, record_id in enumerate(
        ids
    ):

        result = (
            indexer.get_record(
                record_id
            )
        )

        metadatas = (
            result[
                "metadatas"
            ]
        )

        assert (
            metadatas
            is not None
        )

        assert (
            len(metadatas)
            == 1
        )

        stored_metadata = (
            metadatas[0]
        )

        assert isinstance(
            stored_metadata,
            dict
        )

        # ----------------------------------------------------
        # Metadata Schema
        # ----------------------------------------------------

        assert (
            set(
                stored_metadata.keys()
            )
            == REQUIRED_METADATA_FIELDS
        )

        # ----------------------------------------------------
        # Source Document
        # ----------------------------------------------------

        source_document = (
            mappings[index][
                "document"
            ]
        )

        source_metadata = (
            source_document.metadata
        )

        # ----------------------------------------------------
        # document_id
        # ----------------------------------------------------

        assert (
            stored_metadata[
                "document_id"
            ]
            == source_metadata[
                "document_id"
            ]
        )

        # ----------------------------------------------------
        # All 11 Metadata Fields
        # ----------------------------------------------------

        for field in (
            REQUIRED_METADATA_FIELDS
        ):

            source_value = (
                source_metadata.get(
                    field
                )
            )

            stored_value = (
                stored_metadata.get(
                    field
                )
            )

            if source_value is None:

                assert (
                    stored_value
                    == ""
                )

            elif isinstance(
                source_value,
                (str, int, float, bool)
            ):

                assert (
                    stored_value
                    == source_value
                )

            else:

                assert (
                    stored_value
                    == str(
                        source_value
                    )
                )

    print(
        "PASS: Metadata validation"
    )

    print(
        f"      Metadata fields: "
        f"{len(REQUIRED_METADATA_FIELDS)}"
    )

    print(
        f"      Validated records: "
        f"{len(ids)}"
    )


# ============================================================
# RAG-4.5.4
# Stored Vector Validation
# ============================================================

def test_stored_vector_validation():
    """
    驗證 Stored Vector：

        1. Vector 存在
        2. Vector Dimension = 1024
        3. Vector 不是全 0
        4. Vector 所有值都是有限數值
    """

    indexer, mappings, ids = (
        prepare_index()
    )

    for record_id in ids:

        result = (
            indexer.get_record(
                record_id
            )
        )

        embeddings = (
            result[
                "embeddings"
            ]
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

        # ----------------------------------------------------
        # Numeric Validation
        # ----------------------------------------------------

        for value in vector:

            numeric_value = float(
                value
            )

            assert math.isfinite(
                numeric_value
            )

        # ----------------------------------------------------
        # Non-zero Validation
        # ----------------------------------------------------

        non_zero_count = sum(
            1
            for value in vector
            if float(value) != 0.0
        )

        assert (
            non_zero_count
            > 0
        )

    print(
        "PASS: Stored vector validation"
    )

    print(
        f"      Dimension: "
        f"{EXPECTED_DIMENSION}"
    )

    print(
        f"      Validated records: "
        f"{len(ids)}"
    )


# ============================================================
# Cross Validation
# ============================================================

def test_index_validation_consistency():
    """
    驗證：

        RAG-3 Mapping
             ↓
        ChromaDB Record

    確認：

        Document
        Embedding
        Metadata
        Chroma Record ID

    四者保持一致。
    """

    indexer, mappings, ids = (
        prepare_index()
    )

    for index, mapping in enumerate(
        mappings
    ):

        record_id = (
            ids[index]
        )

        document = (
            mapping[
                "document"
            ]
        )

        embedding = (
            mapping[
                "embedding"
            ]
        )

        result = (
            indexer.get_record(
                record_id
            )
        )

        # ----------------------------------------------------
        # Document
        # ----------------------------------------------------

        assert (
            result[
                "documents"
            ][0]
            == document.page_content
        )

        # ----------------------------------------------------
        # Embedding
        # ----------------------------------------------------

        stored_embedding = (
            result[
                "embeddings"
            ][0]
        )

        assert (
            len(stored_embedding)
            == len(embedding)
        )

        assert (
            len(stored_embedding)
            == EXPECTED_DIMENSION
        )

        # ----------------------------------------------------
        # Metadata
        # ----------------------------------------------------

        stored_metadata = (
            result[
                "metadatas"
            ][0]
        )

        assert (
            set(
                stored_metadata.keys()
            )
            == REQUIRED_METADATA_FIELDS
        )

        assert (
            stored_metadata[
                "document_id"
            ]
            == document.metadata[
                "document_id"
            ]
        )

        # ----------------------------------------------------
        # Record ID
        # ----------------------------------------------------

        parsed = (
            indexer.parse_record_id(
                record_id
            )
        )

        assert (
            parsed[
                "document_id"
            ]
            == document.metadata[
                "document_id"
            ]
        )

        assert (
            parsed[
                "chunk_index"
            ]
            == index
        )

    print(
        "PASS: Index validation consistency"
    )


# ============================================================
# Read Validation
# ============================================================

def test_read_validation():
    """
    驗證 ChromaDB Read 回傳
    RAG-4.5 所需要的資料。
    """

    indexer, mappings, ids = (
        prepare_index()
    )

    result = (
        indexer.get_record(
            ids[0]
        )
    )

    assert (
        result
        is not None
    )

    assert (
        result["ids"]
        is not None
    )

    assert (
        len(result["ids"])
        == 1
    )

    assert (
        result["documents"]
        is not None
    )

    assert (
        result["embeddings"]
        is not None
    )

    assert (
        result["metadatas"]
        is not None
    )

    print(
        "PASS: Read validation"
    )

    print(
        f"      Record ID: "
        f"{result['ids'][0]}"
    )


# ============================================================
# Missing Record Validation
# ============================================================

def test_missing_record_validation():
    """
    驗證不存在的 Record。
    """

    indexer = (
        create_indexer()
    )

    missing_id = (
        "non_existing_document::chunk_999"
    )

    result = (
        indexer.get_record(
            missing_id
        )
    )

    assert (
        result
        is not None
    )

    ids = result.get(
        "ids"
    )

    assert (
        ids
        is not None
    )

    assert (
        len(ids)
        == 0
    )

    print(
        "PASS: Missing record validation"
    )


# ============================================================
# Main
# ============================================================

def main():
    """
    執行 RAG-4.5 Index Validation Test。
    """

    print(
        "=" * 60
    )

    print(
        "RAG-4.5 ChromaDB Index Validation Test"
    )

    print(
        "=" * 60
    )

    print()

    print(
        "Testing:"
    )

    print(
        "Count"
    )

    print(
        "Dimension"
    )

    print(
        "Metadata"
    )

    print(
        "Stored Vector"
    )

    print()

    # --------------------------------------------------------
    # RAG-4.5.1 Count
    # --------------------------------------------------------

    test_count_validation()

    # --------------------------------------------------------
    # RAG-4.5.2 Dimension
    # --------------------------------------------------------

    test_dimension_validation()

    # --------------------------------------------------------
    # RAG-4.5.3 Metadata
    # --------------------------------------------------------

    test_metadata_validation()

    # --------------------------------------------------------
    # RAG-4.5.4 Stored Vector
    # --------------------------------------------------------

    test_stored_vector_validation()

    # --------------------------------------------------------
    # Cross Validation
    # --------------------------------------------------------

    test_index_validation_consistency()

    # --------------------------------------------------------
    # Read Validation
    # --------------------------------------------------------

    test_read_validation()

    # --------------------------------------------------------
    # Missing Record
    # --------------------------------------------------------

    test_missing_record_validation()

    print()

    print(
        "=" * 60
    )

    print(
        "ALL RAG-4.5 CHROMADB INDEX "
        "VALIDATION TESTS PASSED"
    )

    print(
        "=" * 60
    )


if __name__ == "__main__":
    main()