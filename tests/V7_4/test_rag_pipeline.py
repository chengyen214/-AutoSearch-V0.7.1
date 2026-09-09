"""
tests/V7_4/test_rag_pipeline.py

AutoSearch V7

RAGPipeline Integration Test

測試：

    RAG-1 Document Preparation
            ↓
    RAG-2 Chunking
            ↓
    RAG-3 Embedding
            ↓
    Embedding Mapping
            ↓
    RAG-4 ChromaDB Index

驗證：

    1. RAGPipeline initialization
    2. RAG-1 / RAG-2 / RAG-3 component integration
    3. RAG-4 ChromaDB component integration
    4. process_document
    5. process_by_document_id
    6. process_by_url
    7. Chunk / Embedding / Mapping consistency
    8. Embedding dimension
    9. Mapping integrity
    10. ChromaDB record IDs
    11. ChromaDB indexed count
    12. ChromaDB stored records
    13. ChromaDB metadata
    14. ChromaDB embedding dimension
    15. Document ID consistency
    16. Input validation
"""


# ============================================================
# Imports
# ============================================================

from langchain_core.documents import (
    Document
)

from rag.rag_pipeline import (
    RAGPipeline
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
# Test Constants
# ============================================================

TEST_DOCUMENT_ID = (
    "rag_pipeline_v7_4_test_document"
)

TEST_URL = (
    "https://example.com/rag-pipeline-v7-4-test"
)

TEST_CONTENT = (
    "AutoSearch V7 RAG Pipeline integration test. "
    "This document is used to verify RAG-1, RAG-2, "
    "RAG-3 and RAG-4 integration."
)


# ============================================================
# Fake RAG Components
# ============================================================

class FakeDocumentPreparation:
    """
    Fake RAG-1 component。

    用於測試 RAGPipeline 本身，
    不依賴 MCP / Database。
    """

    def prepare_by_document_id(
        self,
        document_id
    ):
        return Document(
            page_content=TEST_CONTENT,
            metadata={
                "document_id": document_id,
                "title": "RAGPipeline V7.4 Test",
                "url": TEST_URL,
                "keyword": "RAG Pipeline",
                "source": "test",
                "crawl_time": "",
                "ai_summary": "",
                "ai_category": "",
                "ai_keywords": "",
                "ai_importance": 0,
                "ai_confidence": 0,
            }
        )

    def prepare_by_url(
        self,
        url
    ):
        return Document(
            page_content=TEST_CONTENT,
            metadata={
                "document_id": TEST_DOCUMENT_ID,
                "title": "RAGPipeline V7.4 Test",
                "url": url,
                "keyword": "RAG Pipeline",
                "source": "test",
                "crawl_time": "",
                "ai_summary": "",
                "ai_category": "",
                "ai_keywords": "",
                "ai_importance": 0,
                "ai_confidence": 0,
            }
        )


# ============================================================
# Fake RAG-3 Embedding
# ============================================================

class FakeEmbeddingPipeline:
    """
    Fake RAG-3 component。

    不載入 Qwen Model，
    只建立固定維度的測試 Embedding。

    維度：

        1024
    """

    DIMENSION = 1024

    def process_chunks(
        self,
        chunks
    ):
        embeddings = [
            [0.1] * self.DIMENSION
            for _ in chunks
        ]

        mappings = []

        for document, embedding in zip(
            chunks,
            embeddings
        ):
            mappings.append(
                {
                    "document": document,
                    "embedding": embedding
                }
            )

        return {
            "embeddings": embeddings,
            "mappings": mappings
        }


# ============================================================
# Helper
# ============================================================

def create_pipeline():
    """
    建立測試用 RAGPipeline。

    ChromaDB 使用獨立 Test Collection。
    """

    chroma_client = (
        ChromaDBClient()
    )

    chroma_collection = (
        ChromaCollection(
            chroma_client=chroma_client,
            collection_name=(
                "rag_pipeline_v7_4_test"
            ),
            distance_metric="cosine"
        )
    )

    chroma_indexer = (
        ChromaIndexer(
            chroma_collection=(
                chroma_collection
            )
        )
    )

    pipeline = (
        RAGPipeline(
            document_preparation=(
                FakeDocumentPreparation()
            ),
            embedding_pipeline=(
                FakeEmbeddingPipeline()
            ),
            chroma_indexer=(
                chroma_indexer
            )
        )
    )

    return (
        pipeline,
        chroma_collection,
        chroma_indexer
    )


# ============================================================
# Main Test
# ============================================================

def main():

    print(
        "=" * 60
    )

    print(
        "RAGPipeline RAG-4 Integration Test"
    )

    print(
        "=" * 60
    )

    print()

    # --------------------------------------------------------
    # Create Pipeline
    # --------------------------------------------------------

    (
        pipeline,
        chroma_collection,
        chroma_indexer
    ) = create_pipeline()

    # ========================================================
    # Initialization
    # ========================================================

    assert pipeline is not None

    print(
        "PASS: RAGPipeline initialization"
    )

    assert (
        pipeline.document_preparation
        is not None
    )

    assert (
        pipeline.document_chunking
        is not None
    )

    assert (
        pipeline.embedding_pipeline
        is not None
    )

    assert (
        pipeline.chroma_indexer
        is not None
    )

    print(
        "PASS: RAG-1 / RAG-2 / RAG-3 / RAG-4 "
        "component integration"
    )

    # ========================================================
    # Process Prepared Document
    # ========================================================

    document = Document(
        page_content=TEST_CONTENT,
        metadata={
            "document_id": TEST_DOCUMENT_ID,
            "title": "RAGPipeline V7.4 Test",
            "url": TEST_URL,
            "keyword": "RAG Pipeline",
            "source": "test",
            "crawl_time": "",
            "ai_summary": "",
            "ai_category": "",
            "ai_keywords": "",
            "ai_importance": 0,
            "ai_confidence": 0,
        }
    )

    result = (
        pipeline.process_document(
            document
        )
    )

    assert isinstance(
        result,
        dict
    )

    print(
        "PASS: process_document"
    )

    # ========================================================
    # Result Keys
    # ========================================================

    expected_keys = {
        "document",
        "chunks",
        "embeddings",
        "mappings",
        "record_ids",
        "indexed_count",
    }

    assert (
        expected_keys
        .issubset(
            result.keys()
        )
    )

    print(
        "PASS: RAGPipeline result keys"
    )

    # ========================================================
    # Result Types
    # ========================================================

    assert isinstance(
        result["document"],
        Document
    )

    assert isinstance(
        result["chunks"],
        list
    )

    assert isinstance(
        result["embeddings"],
        list
    )

    assert isinstance(
        result["mappings"],
        list
    )

    assert isinstance(
        result["record_ids"],
        list
    )

    assert isinstance(
        result["indexed_count"],
        int
    )

    print(
        "PASS: RAGPipeline result types"
    )

    # ========================================================
    # Count Consistency
    # ========================================================

    chunks = result[
        "chunks"
    ]

    embeddings = result[
        "embeddings"
    ]

    mappings = result[
        "mappings"
    ]

    record_ids = result[
        "record_ids"
    ]

    assert (
        len(chunks)
        == len(embeddings)
        == len(mappings)
        == len(record_ids)
    )

    assert (
        result["indexed_count"]
        == len(record_ids)
    )

    print(
        "PASS: Chunk / Embedding / Mapping / "
        "Record count consistency"
    )

    print(
        f"      Chunks: {len(chunks)}"
    )

    print(
        f"      Embeddings: {len(embeddings)}"
    )

    print(
        f"      Mappings: {len(mappings)}"
    )

    print(
        f"      Chroma Records: {len(record_ids)}"
    )

    # ========================================================
    # Embedding Dimension
    # ========================================================

    for embedding in embeddings:

        assert len(
            embedding
        ) == FakeEmbeddingPipeline.DIMENSION

    print(
        "PASS: RAGPipeline embedding dimensions"
    )

    print(
        f"      Dimension: "
        f"{FakeEmbeddingPipeline.DIMENSION}"
    )

    # ========================================================
    # Mapping Integrity
    # ========================================================

    for index, mapping in enumerate(
        mappings
    ):

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
            == FakeEmbeddingPipeline.DIMENSION
        )

        assert (
            mapping["document"]
            is chunks[index]
        )

    print(
        "PASS: RAGPipeline mapping integrity"
    )

    # ========================================================
    # Document Identity
    # ========================================================

    assert (
        result["document"]
        is document
    )

    document_id = (
        result["document"]
        .metadata
        .get(
            "document_id"
        )
    )

    assert (
        document_id
        == TEST_DOCUMENT_ID
    )

    print(
        "PASS: RAGPipeline document identity"
    )

    print(
        "PASS: RAGPipeline document_id preservation"
    )

    # ========================================================
    # RAG-4 Record IDs
    # ========================================================

    assert len(
        record_ids
    ) > 0

    for index, record_id in enumerate(
        record_ids
    ):

        assert isinstance(
            record_id,
            str
        )

        expected_record_id = (
            f"{TEST_DOCUMENT_ID}"
            f"::chunk_{index}"
        )

        assert (
            record_id
            == expected_record_id
        )

    print(
        "PASS: RAG-4 ChromaDB record IDs"
    )

    # ========================================================
    # ChromaDB Count
    # ========================================================

    chroma_count = (
        chroma_indexer.count()
    )

    assert (
        chroma_count
        == len(record_ids)
    )

    assert (
        chroma_count
        == result["indexed_count"]
    )

    print(
        "PASS: RAG-4 ChromaDB indexed count"
    )

    print(
        f"      ChromaDB Count: "
        f"{chroma_count}"
    )

    # ========================================================
    # ChromaDB Stored Records
    # ========================================================

    collection = (
        chroma_collection
        .get_collection()
    )

    stored = (
        collection.get(
            ids=record_ids,
            include=[
                "documents",
                "metadatas",
                "embeddings"
            ]
        )
    )

    assert (
        stored is not None
    )

    assert (
        len(
            stored["ids"]
        )
        == len(record_ids)
    )

    print(
        "PASS: RAG-4 ChromaDB stored records"
    )

    # ========================================================
    # ChromaDB Metadata
    # ========================================================

    for metadata in stored[
        "metadatas"
    ]:

        assert isinstance(
            metadata,
            dict
        )

        assert (
            metadata.get(
                "document_id"
            )
            == TEST_DOCUMENT_ID
        )

        assert (
            "title"
            in metadata
        )

        assert (
            "url"
            in metadata
        )

        assert (
            "keyword"
            in metadata
        )

        assert (
            "source"
            in metadata
        )

    print(
        "PASS: RAG-4 ChromaDB metadata"
    )

    # ========================================================
    # ChromaDB Embedding
    # ========================================================

    stored_embeddings = (
        stored[
            "embeddings"
        ]
    )

    assert (
        stored_embeddings
        is not None
    )

    assert (
        len(
            stored_embeddings
        )
        == len(record_ids)
    )

    for embedding in stored_embeddings:

        assert (
            len(
                embedding
            )
            == FakeEmbeddingPipeline.DIMENSION
        )

    print(
        "PASS: RAG-4 ChromaDB embedding dimension"
    )

    # ========================================================
    # Process By Document ID
    #
    # 使用新的 collection record。
    # ========================================================

    (
        pipeline_by_id,
        _,
        _,
    ) = create_pipeline()

    result_by_id = (
        pipeline_by_id
        .process_by_document_id(
            TEST_DOCUMENT_ID
        )
    )

    assert isinstance(
        result_by_id,
        dict
    )

    assert (
        result_by_id[
            "document"
        ]
        .metadata[
            "document_id"
        ]
        == TEST_DOCUMENT_ID
    )

    assert (
        result_by_id[
            "indexed_count"
        ]
        == len(
            result_by_id[
                "record_ids"
            ]
        )
    )

    print(
        "PASS: process_by_document_id"
    )

    # ========================================================
    # Process By URL
    #
    # ========================================================

    (
        pipeline_by_url,
        _,
        _,
    ) = create_pipeline()

    result_by_url = (
        pipeline_by_url
        .process_by_url(
            TEST_URL
        )
    )

    assert isinstance(
        result_by_url,
        dict
    )

    assert (
        result_by_url[
            "document"
        ]
        .metadata[
            "url"
        ]
        == TEST_URL
    )

    assert (
        result_by_url[
            "document"
        ]
        .metadata[
            "document_id"
        ]
        == TEST_DOCUMENT_ID
    )

    assert (
        result_by_url[
            "indexed_count"
        ]
        == len(
            result_by_url[
                "record_ids"
            ]
        )
    )

    print(
        "PASS: process_by_url"
    )

    # ========================================================
    # Input Validation
    # ========================================================

    try:

        pipeline.process_document(
            None
        )

        raise AssertionError(
            "Expected ValueError"
        )

    except ValueError:

        print(
            "PASS: None document validation"
        )

    try:

        pipeline.process_by_document_id(
            None
        )

        raise AssertionError(
            "Expected ValueError"
        )

    except ValueError:

        print(
            "PASS: None document_id validation"
        )

    try:

        pipeline.process_by_document_id(
            ""
        )

        raise AssertionError(
            "Expected ValueError"
        )

    except ValueError:

        print(
            "PASS: Empty document_id validation"
        )

    try:

        pipeline.process_by_url(
            None
        )

        raise AssertionError(
            "Expected ValueError"
        )

    except ValueError:

        print(
            "PASS: None URL validation"
        )

    try:

        pipeline.process_by_url(
            ""
        )

        raise AssertionError(
            "Expected ValueError"
        )

    except ValueError:

        print(
            "PASS: Empty URL validation"
        )

    # ========================================================
    # Final
    # ========================================================

    print()

    print(
        "=" * 60
    )

    print(
        "ALL RAG PIPELINE RAG-4 "
        "INTEGRATION TESTS PASSED"
    )

    print(
        "=" * 60
    )


if __name__ == "__main__":
    main()