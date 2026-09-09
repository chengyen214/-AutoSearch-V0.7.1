"""
tests/V7_4/test_rag_chroma_indexer.py

AutoSearch V7

RAG-4.4

ChromaDB Indexer Test

測試範圍：

    RAG-4.4 ChromaDB Indexer

功能：

    1. Chunk + Embedding + Metadata → ChromaDB
    2. Chroma ID ↔ document_id / chunk
    3. Upsert
    4. Read
    5. Count

資料流程：

    RAG-3 EmbeddingPipeline
            ↓
    RAG-3 Mapping
            ↓
    ChromaIndexer
            ↓
    ChromaDB Collection

本測試不負責：

    1. MySQL
    2. MCP
    3. RAG-1 Document Preparation implementation
    4. RAG-2 Chunking implementation
    5. RAG-3 Embedding implementation
    6. RAG-4.1 Configuration
    7. RAG-4.2 Client implementation
    8. RAG-4.3 Collection implementation
    9. RAG-4.6 Index Validation
    10. RAG-5 Retriever
"""


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

    assert len(
        _CHUNKS
    ) > 0

    return _CHUNKS


# ============================================================
# Create RAG-3 Mapping
# ============================================================

def create_rag3_mappings():
    """
    建立真實 RAG-3 Embedding Mapping。

    整個測試只產生一次。
    """

    global _RAG3_MAPPINGS

    if _RAG3_MAPPINGS is None:

        chunks = create_chunks()

        if _EMBEDDING_PIPELINE is None:
            create_embedding_pipeline()

        result = (
            _EMBEDDING_PIPELINE
            .process_chunks(
                chunks
            )
        )

        _RAG3_MAPPINGS = result[
            "mappings"
        ]

    assert isinstance(
        _RAG3_MAPPINGS,
        list
    )

    assert len(
        _RAG3_MAPPINGS
    ) == len(
        create_chunks()
    )

    return _RAG3_MAPPINGS


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
    建立 RAG-4.4 專用測試 Collection。

    不使用正式 Collection，
    避免測試污染正式資料。
    """

    global _CHROMA_COLLECTION

    if _CHROMA_COLLECTION is None:

        _CHROMA_COLLECTION = (
            ChromaCollection(
                chroma_client=(
                    create_chroma_client()
                ),
                collection_name=(
                    "rag_4_4_indexer_test"
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
# Test 1
# ============================================================

def test_indexer_initialization():
    """
    驗證 ChromaIndexer 初始化。
    """

    indexer = create_indexer()

    assert isinstance(
        indexer,
        ChromaIndexer
    )

    assert (
        indexer.get_collection()
        is not None
    )

    print(
        "PASS: ChromaIndexer initialization"
    )


# ============================================================
# Test 2
# ============================================================

def test_rag3_mapping_input():
    """
    驗證 ChromaIndexer
    可以接受 RAG-3 Mapping。
    """

    mappings = (
        create_rag3_mappings()
    )

    indexer = create_indexer()

    for mapping in mappings:

        assert (
            indexer._validate_mapping(
                mapping
            )
            is True
        )

    print(
        "PASS: RAG-3 Mapping input"
    )


# ============================================================
# Test 3
# ============================================================

def test_record_id_generation():
    """
    驗證：

        document_id + chunk_index
                ↓
        Chroma Record ID
    """

    chunks = create_chunks()
    indexer = create_indexer()

    record_id = (
        indexer.create_record_id(
            chunks[0],
            0
        )
    )

    expected = (
        f"{TEST_DOCUMENT_ID}::chunk_0"
    )

    assert (
        record_id
        == expected
    )

    print(
        "PASS: Chroma ID generation"
    )

    print(
        f"      Record ID: {record_id}"
    )


# ============================================================
# Test 4
# ============================================================

def test_record_id_parsing():
    """
    驗證 Chroma Record ID
    可以反推出：

        document_id
        chunk_index
    """

    indexer = create_indexer()

    record_id = (
        f"{TEST_DOCUMENT_ID}::chunk_5"
    )

    parsed = (
        indexer.parse_record_id(
            record_id
        )
    )

    assert (
        parsed["document_id"]
        == TEST_DOCUMENT_ID
    )

    assert (
        parsed["chunk_index"]
        == 5
    )

    print(
        "PASS: Chroma ID parsing"
    )


# ============================================================
# Test 5
# ============================================================

def test_id_mapping_consistency():
    """
    驗證：

        Chroma ID
            ↕
        document_id
            ↕
        chunk_index
    """

    chunks = create_chunks()
    indexer = create_indexer()

    for index, chunk in enumerate(
        chunks
    ):

        record_id = (
            indexer.create_record_id(
                chunk,
                index
            )
        )

        parsed = (
            indexer.parse_record_id(
                record_id
            )
        )

        assert (
            parsed["document_id"]
            == chunk.metadata[
                "document_id"
            ]
        )

        assert (
            parsed["chunk_index"]
            == index
        )

    print(
        "PASS: Chroma ID ↔ document_id / chunk mapping"
    )


# ============================================================
# Test 6
# ============================================================

def test_metadata_mapping():
    """
    驗證：

        LangChain Document Metadata
                    ↓
              Chroma Metadata
    """

    chunks = create_chunks()
    indexer = create_indexer()

    metadata = (
        indexer.to_chroma_metadata(
            chunks[0].metadata
        )
    )

    assert isinstance(
        metadata,
        dict
    )

    for field in (
        indexer.METADATA_FIELDS
    ):

        assert field in metadata

    print(
        "PASS: Metadata mapping"
    )


# ============================================================
# Test 7
# ============================================================

def test_metadata_schema():
    """
    驗證正式 11-field Metadata Schema。
    """

    indexer = create_indexer()

    expected_fields = {
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

    assert (
        set(indexer.METADATA_FIELDS)
        == expected_fields
    )

    print(
        "PASS: Metadata schema"
    )


# ============================================================
# Test 8
# ============================================================

def test_single_mapping_index():
    """
    驗證：

        Chunk
        + Embedding
        + Metadata
              ↓
        ChromaDB
    """

    mappings = create_rag3_mappings()
    indexer = create_indexer()

    record_id = (
        indexer.index_mapping(
            mappings[0],
            chunk_index=0
        )
    )

    assert (
        record_id
        == (
            f"{TEST_DOCUMENT_ID}"
            "::chunk_0"
        )
    )

    assert (
        indexer.count()
        >= 1
    )

    print(
        "PASS: Single Mapping → ChromaDB"
    )

    print(
        f"      Record ID: {record_id}"
    )


# ============================================================
# Test 9
# ============================================================

def test_multiple_mapping_index():
    """
    驗證多筆 Mapping
    可以批次寫入 ChromaDB。
    """

    mappings = create_rag3_mappings()
    indexer = create_indexer()

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

    print(
        "PASS: Multiple Mapping → ChromaDB"
    )

    print(
        f"      Mappings: {len(mappings)}"
    )

    print(
        f"      Records: {len(ids)}"
    )


# ============================================================
# Test 10
# ============================================================

def test_stored_document():
    """
    驗證 ChromaDB 儲存 Chunk Document。
    """

    mappings = create_rag3_mappings()
    indexer = create_indexer()

    ids = (
        indexer.index_mappings(
            mappings
        )
    )

    result = (
        indexer.get_record(
            ids[0]
        )
    )

    assert (
        result["documents"]
        is not None
    )

    assert (
        len(
            result["documents"]
        )
        == 1
    )

    assert (
        result["documents"][0]
        == mappings[0][
            "document"
        ].page_content
    )

    print(
        "PASS: Stored Chunk document"
    )


# ============================================================
# Test 11
# ============================================================

def test_stored_embedding():
    """
    驗證 ChromaDB 儲存 Embedding。
    """

    mappings = create_rag3_mappings()
    indexer = create_indexer()

    ids = (
        indexer.index_mappings(
            mappings
        )
    )

    result = (
        indexer.get_record(
            ids[0]
        )
    )

    embedding = result[
        "embeddings"
    ][0]

    source_embedding = mappings[0][
        "embedding"
    ]

    assert embedding is not None

    assert (
        len(embedding)
        == 1024
    )

    assert (
        len(embedding)
        == len(source_embedding)
    )

    print(
        "PASS: Stored Embedding"
    )

    print(
        f"      Dimension: {len(embedding)}"
    )


# ============================================================
# Test 12
# ============================================================

def test_stored_metadata():
    """
    驗證 ChromaDB 儲存完整 Metadata。
    """

    mappings = create_rag3_mappings()
    indexer = create_indexer()

    ids = (
        indexer.index_mappings(
            mappings
        )
    )

    result = (
        indexer.get_record(
            ids[0]
        )
    )

    metadata = result[
        "metadatas"
    ][0]

    source_metadata = mappings[0][
        "document"
    ].metadata

    for field in (
        indexer.METADATA_FIELDS
    ):

        source_value = (
            source_metadata.get(
                field
            )
        )

        stored_value = (
            metadata.get(
                field
            )
        )

        if source_value is None:

            assert stored_value == ""

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
                == str(source_value)
            )

    print(
        "PASS: Stored Metadata"
    )


# ============================================================
# Test 13
# ============================================================

def test_document_id_metadata():
    """
    驗證 Chroma Metadata
    保留 Article document_id。
    """

    mappings = create_rag3_mappings()
    indexer = create_indexer()

    ids = (
        indexer.index_mappings(
            mappings
        )
    )

    result = (
        indexer.get_record(
            ids[0]
        )
    )

    metadata = result[
        "metadatas"
    ][0]

    assert (
        metadata["document_id"]
        == TEST_DOCUMENT_ID
    )

    print(
        "PASS: Stored document_id"
    )


# ============================================================
# Test 14
# ============================================================

def test_upsert():
    """
    驗證相同 Record ID
    使用 upsert 不會重複建立資料。
    """

    mappings = create_rag3_mappings()
    indexer = create_indexer()

    ids_first = (
        indexer.index_mappings(
            mappings
        )
    )

    count_first = (
        indexer.count()
    )

    ids_second = (
        indexer.index_mappings(
            mappings
        )
    )

    count_second = (
        indexer.count()
    )

    assert (
        ids_first
        == ids_second
    )

    assert (
        count_first
        == count_second
    )

    print(
        "PASS: Upsert behavior"
    )

    print(
        f"      Count: {count_second}"
    )


# ============================================================
# Test 15
# ============================================================

def test_read_record():
    """
    驗證 Read。

    確認 ChromaDB 可以讀回：

        Document
        Embedding
        Metadata
    """

    mappings = create_rag3_mappings()
    indexer = create_indexer()

    ids = (
        indexer.index_mappings(
            mappings
        )
    )

    record_id = ids[0]

    result = (
        indexer.get_record(
            record_id
        )
    )

    # --------------------------------------------------
    # Documents
    # --------------------------------------------------

    assert (
        result["documents"]
        is not None
    )

    assert (
        len(result["documents"])
        > 0
    )

    # --------------------------------------------------
    # Embeddings
    #
    # ChromaDB may return NumPy array.
    # Do not use:
    #
    #     assert result["embeddings"]
    # --------------------------------------------------

    assert (
        result["embeddings"]
        is not None
    )

    assert (
        len(result["embeddings"])
        > 0
    )

    # --------------------------------------------------
    # Metadata
    # --------------------------------------------------

    assert (
        result["metadatas"]
        is not None
    )

    assert (
        len(result["metadatas"])
        > 0
    )

    print(
        "PASS: Read ChromaDB record"
    )

    print(
        f"      Record ID: {record_id}"
    )

# ============================================================
# Test 16
# ============================================================

def test_count():
    """
    驗證 Count。
    """

    mappings = create_rag3_mappings()
    indexer = create_indexer()

    before = (
        indexer.count()
    )

    indexer.index_mappings(
        mappings
    )

    after = (
        indexer.count()
    )

    assert (
        after
        >= before
    )

    assert (
        after
        >= len(mappings)
    )

    print(
        "PASS: ChromaDB count"
    )

    print(
        f"      Before: {before}"
    )

    print(
        f"      After: {after}"
    )


# ============================================================
# Test 17
# ============================================================

def test_real_article_indexing():
    """
    真實 Article：

        MCP
          ↓
        RAG-1
          ↓
        RAG-2
          ↓
        RAG-3
          ↓
        RAG-4.4 Indexer
          ↓
        ChromaDB
    """

    document = create_document()
    chunks = create_chunks()
    mappings = create_rag3_mappings()
    indexer = create_indexer()

    ids = (
        indexer.index_mappings(
            mappings
        )
    )

    assert (
        document.metadata[
            "document_id"
        ]
        == TEST_DOCUMENT_ID
    )

    assert (
        len(ids)
        == len(chunks)
    )

    for index, record_id in enumerate(
        ids
    ):

        parsed = (
            indexer.parse_record_id(
                record_id
            )
        )

        assert (
            parsed["document_id"]
            == TEST_DOCUMENT_ID
        )

        assert (
            parsed["chunk_index"]
            == index
        )

        result = (
            indexer.get_record(
                record_id
            )
        )

        assert (
            result["documents"][0]
            == chunks[index].page_content
        )

        assert (
            result["metadatas"][0][
                "document_id"
            ]
            == TEST_DOCUMENT_ID
        )

        assert (
            len(
                result["embeddings"][0]
            )
            == 1024
        )

    print(
        "PASS: Real Article → ChromaDB Index"
    )

    print(
        f"      Document ID: "
        f"{TEST_DOCUMENT_ID}"
    )

    print(
        f"      Chunk count: "
        f"{len(chunks)}"
    )

    print(
        f"      Indexed records: "
        f"{len(ids)}"
    )


# ============================================================
# Validation Tests
# ============================================================

def test_none_mapping():
    """
    驗證 None Mapping。
    """

    indexer = create_indexer()

    try:

        indexer.index_mapping(
            None
        )

    except ValueError:

        print(
            "PASS: None mapping validation"
        )

        return

    raise AssertionError(
        "None mapping "
        "should raise ValueError."
    )


def test_none_mappings():
    """
    驗證 None Mappings。
    """

    indexer = create_indexer()

    try:

        indexer.index_mappings(
            None
        )

    except ValueError:

        print(
            "PASS: None mappings validation"
        )

        return

    raise AssertionError(
        "None mappings "
        "should raise ValueError."
    )


def test_empty_mappings():
    """
    驗證空 Mappings。
    """

    indexer = create_indexer()

    try:

        indexer.index_mappings(
            []
        )

    except ValueError:

        print(
            "PASS: Empty mappings validation"
        )

        return

    raise AssertionError(
        "Empty mappings "
        "should raise ValueError."
    )


def test_invalid_mapping_type():
    """
    驗證 Mapping 型別錯誤。
    """

    indexer = create_indexer()

    try:

        indexer.index_mapping(
            "invalid"
        )

    except TypeError:

        print(
            "PASS: Invalid mapping type validation"
        )

        return

    raise AssertionError(
        "Invalid mapping type "
        "should raise TypeError."
    )


def test_none_record_id():
    """
    驗證 None Record ID。
    """

    indexer = create_indexer()

    try:

        indexer.get_record(
            None
        )

    except ValueError:

        print(
            "PASS: None Record ID validation"
        )

        return

    raise AssertionError(
        "None Record ID "
        "should raise ValueError."
    )


def test_empty_record_id():
    """
    驗證空 Record ID。
    """

    indexer = create_indexer()

    try:

        indexer.get_record(
            "   "
        )

    except ValueError:

        print(
            "PASS: Empty Record ID validation"
        )

        return

    raise AssertionError(
        "Empty Record ID "
        "should raise ValueError."
    )


def test_invalid_record_id():
    """
    驗證錯誤 Record ID。
    """

    indexer = create_indexer()

    try:

        indexer.parse_record_id(
            "invalid_record_id"
        )

    except ValueError:

        print(
            "PASS: Invalid Record ID validation"
        )

        return

    raise AssertionError(
        "Invalid Record ID "
        "should raise ValueError."
    )


def test_invalid_document_id():
    """
    驗證 Document 缺少 document_id。
    """

    indexer = create_indexer()

    document = Document(
        page_content="test",
        metadata={}
    )

    try:

        indexer.create_record_id(
            document,
            0
        )

    except ValueError:

        print(
            "PASS: Missing document_id validation"
        )

        return

    raise AssertionError(
        "Missing document_id "
        "should raise ValueError."
    )


def test_invalid_chunk_index():
    """
    驗證負數 Chunk Index。
    """

    indexer = create_indexer()

    document = Document(
        page_content="test",
        metadata={
            "document_id": "test"
        }
    )

    try:

        indexer.create_record_id(
            document,
            -1
        )

    except ValueError:

        print(
            "PASS: Invalid chunk index validation"
        )

        return

    raise AssertionError(
        "Negative chunk index "
        "should raise ValueError."
    )


# ============================================================
# Main
# ============================================================

def main():
    """
    執行 RAG-4.4 ChromaDB Indexer Test。
    """

    print("=" * 60)

    print(
        "RAG-4.4 ChromaDB Indexer Test"
    )

    print("=" * 60)

    print()

    print(
        "Testing:"
    )

    print(
        "Chunk + Embedding + Metadata → ChromaDB"
    )

    print(
        "Chroma ID ↔ document_id / chunk"
    )

    print(
        "Upsert"
    )

    print(
        "Read / Count"
    )

    print()

    # --------------------------------------------------
    # Initialization
    # --------------------------------------------------

    test_indexer_initialization()

    # --------------------------------------------------
    # ID / Metadata Mapping
    # --------------------------------------------------

    test_rag3_mapping_input()

    test_record_id_generation()

    test_record_id_parsing()

    test_id_mapping_consistency()

    test_metadata_mapping()

    test_metadata_schema()

    # --------------------------------------------------
    # Index
    # --------------------------------------------------

    test_single_mapping_index()

    test_multiple_mapping_index()

    # --------------------------------------------------
    # Stored Data
    # --------------------------------------------------

    test_stored_document()

    test_stored_embedding()

    test_stored_metadata()

    test_document_id_metadata()

    # --------------------------------------------------
    # Upsert
    # --------------------------------------------------

    test_upsert()

    # --------------------------------------------------
    # Read / Count
    # --------------------------------------------------

    test_read_record()

    test_count()

    # --------------------------------------------------
    # Real Article
    # --------------------------------------------------

    test_real_article_indexing()

    # --------------------------------------------------
    # Validation
    # --------------------------------------------------

    print()

    print(
        "Testing indexer validation..."
    )

    print()

    test_none_mapping()

    test_none_mappings()

    test_empty_mappings()

    test_invalid_mapping_type()

    test_none_record_id()

    test_empty_record_id()

    test_invalid_record_id()

    test_invalid_document_id()

    test_invalid_chunk_index()

    print()

    print("=" * 60)

    print(
        "ALL RAG-4.4 CHROMADB INDEXER TESTS PASSED"
    )

    print("=" * 60)


if __name__ == "__main__":
    main()