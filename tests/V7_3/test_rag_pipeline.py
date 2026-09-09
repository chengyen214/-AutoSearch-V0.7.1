"""
tests/V7_3/test_rag_pipeline.py

AutoSearch V7

RAG Pipeline Integration Test

測試：

    RAG-1 Document Preparation
            ↓
    RAG-2 Chunking
            ↓
    RAG-3 Embedding
            ↓
    Embedding Mapping
            ↓
    Embedding Validation

本測試負責確認：

    1. RAGPipeline 初始化
    2. RAG-1 → RAG-2 → RAG-3
    3. Document ID 流程
    4. URL 流程
    5. Prepared Document 流程
    6. Chunk 數量
    7. Embedding 數量
    8. Mapping 數量
    9. Embedding Dimension
    10. Metadata Preservation
    11. Document Identity
    12. Embedding Validation
    13. Pipeline Input Validation

本測試不負責：

    1. ChromaDB
    2. Retriever
    3. Context Builder
    4. LLM
"""


from langchain_core.documents import Document

from rag.rag_pipeline import (
    RAGPipeline
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

from rag.embedding.config import (
    EMBEDDING_DIMENSION,
    EMBEDDING_MODEL,
)


# ============================================================
# Test Article
# ============================================================

TEST_DOCUMENT_ID = (
    "d9ce4740c3f0b6f1d260c094c0549f68727187b0a2b57c94f6308b4df9fd9d13"
)

TEST_URL = (
    "https://finance.technews.tw/2026/02/26/"
    "navitas-semiconductor-announces-fourth-quarter-and-full-year-2025-financial-results/"
)


# ============================================================
# Shared Objects
# ============================================================

_DOCUMENT_PREPARATION = None
_DOCUMENT_CHUNKING = None
_EMBEDDING_PIPELINE = None
_RAG_PIPELINE = None
_PREPARED_DOCUMENT = None
_RESULT_BY_DOCUMENT_ID = None
_RESULT_BY_URL = None
_RESULT_BY_DOCUMENT = None


# ============================================================
# Create Document Preparation
# ============================================================

def create_document_preparation():
    """
    建立共用 RAG-1 DocumentPreparation。
    """

    global _DOCUMENT_PREPARATION

    if _DOCUMENT_PREPARATION is None:
        _DOCUMENT_PREPARATION = DocumentPreparation()

    return _DOCUMENT_PREPARATION


# ============================================================
# Create Document Chunking
# ============================================================

def create_document_chunking():
    """
    建立共用 RAG-2 DocumentChunking。
    """

    global _DOCUMENT_CHUNKING

    if _DOCUMENT_CHUNKING is None:
        _DOCUMENT_CHUNKING = DocumentChunking()

    return _DOCUMENT_CHUNKING


# ============================================================
# Create Embedding Pipeline
# ============================================================

def create_embedding_pipeline():
    """
    建立共用 RAG-3 EmbeddingPipeline。
    """

    global _EMBEDDING_PIPELINE

    if _EMBEDDING_PIPELINE is None:
        _EMBEDDING_PIPELINE = EmbeddingPipeline()

    return _EMBEDDING_PIPELINE


# ============================================================
# Create RAG Pipeline
# ============================================================

def create_rag_pipeline():
    """
    建立共用 RAGPipeline。

    使用 Dependency Injection，
    確保測試所使用的元件可被明確確認。
    """

    global _RAG_PIPELINE

    if _RAG_PIPELINE is None:

        _RAG_PIPELINE = RAGPipeline(
            document_preparation=(
                create_document_preparation()
            ),
            document_chunking=(
                create_document_chunking()
            ),
            embedding_pipeline=(
                create_embedding_pipeline()
            ),
        )

    return _RAG_PIPELINE


# ============================================================
# Create Prepared Document
# ============================================================

def create_prepared_document():
    """
    建立共用 Prepared Document。

    主要用於測試 process_document()。
    """

    global _PREPARED_DOCUMENT

    if _PREPARED_DOCUMENT is None:

        preparation = (
            create_document_preparation()
        )

        _PREPARED_DOCUMENT = (
            preparation.prepare_by_document_id(
                TEST_DOCUMENT_ID
            )
        )

    assert (
        _PREPARED_DOCUMENT
        is not None
    )

    assert isinstance(
        _PREPARED_DOCUMENT,
        Document
    )

    return _PREPARED_DOCUMENT


# ============================================================
# Process By Document ID
# ============================================================

def create_result_by_document_id():
    """
    建立 Document ID 流程結果。
    """

    global _RESULT_BY_DOCUMENT_ID

    if _RESULT_BY_DOCUMENT_ID is None:

        pipeline = create_rag_pipeline()

        _RESULT_BY_DOCUMENT_ID = (
            pipeline.process_by_document_id(
                TEST_DOCUMENT_ID
            )
        )

    return _RESULT_BY_DOCUMENT_ID


# ============================================================
# Process By URL
# ============================================================

def create_result_by_url():
    """
    建立 URL 流程結果。
    """

    global _RESULT_BY_URL

    if _RESULT_BY_URL is None:

        pipeline = create_rag_pipeline()

        _RESULT_BY_URL = (
            pipeline.process_by_url(
                TEST_URL
            )
        )

    return _RESULT_BY_URL


# ============================================================
# Process Existing Document
# ============================================================

def create_result_by_document():
    """
    建立既有 Prepared Document 流程結果。
    """

    global _RESULT_BY_DOCUMENT

    if _RESULT_BY_DOCUMENT is None:

        pipeline = create_rag_pipeline()

        document = (
            create_prepared_document()
        )

        _RESULT_BY_DOCUMENT = (
            pipeline.process_document(
                document
            )
        )

    return _RESULT_BY_DOCUMENT


# ============================================================
# Test 1
# ============================================================

def test_pipeline_initialization():
    """
    驗證 RAGPipeline 初始化。
    """

    pipeline = create_rag_pipeline()

    assert isinstance(
        pipeline,
        RAGPipeline
    )

    print(
        "PASS: RAGPipeline initialization"
    )


# ============================================================
# Test 2
# ============================================================

def test_component_integration():
    """
    驗證 RAGPipeline 正確持有：

        RAG-1
        RAG-2
        RAG-3
    """

    pipeline = create_rag_pipeline()

    assert isinstance(
        pipeline.document_preparation,
        DocumentPreparation
    )

    assert isinstance(
        pipeline.document_chunking,
        DocumentChunking
    )

    assert isinstance(
        pipeline.embedding_pipeline,
        EmbeddingPipeline
    )

    print(
        "PASS: RAG-1 / RAG-2 / RAG-3 component integration"
    )


# ============================================================
# Test 3
# ============================================================

def test_process_document():
    """
    測試：

        Prepared Document
            ↓
        RAG-2
            ↓
        RAG-3
    """

    result = create_result_by_document()

    assert isinstance(
        result,
        dict
    )

    assert "document" in result
    assert "chunks" in result
    assert "embeddings" in result
    assert "mappings" in result

    print(
        "PASS: process_document"
    )


# ============================================================
# Test 4
# ============================================================

def test_process_by_document_id():
    """
    測試：

        Document ID
            ↓
        RAG-1
            ↓
        RAG-2
            ↓
        RAG-3
    """

    result = (
        create_result_by_document_id()
    )

    assert isinstance(
        result,
        dict
    )

    assert "document" in result
    assert "chunks" in result
    assert "embeddings" in result
    assert "mappings" in result

    print(
        "PASS: process_by_document_id"
    )


# ============================================================
# Test 5
# ============================================================

def test_process_by_url():
    """
    測試：

        URL
          ↓
        RAG-1
          ↓
        RAG-2
          ↓
        RAG-3
    """

    result = create_result_by_url()

    assert isinstance(
        result,
        dict
    )

    assert "document" in result
    assert "chunks" in result
    assert "embeddings" in result
    assert "mappings" in result

    print(
        "PASS: process_by_url"
    )


# ============================================================
# Test 6
# ============================================================

def test_result_types():
    """
    驗證 RAGPipeline 回傳資料型別。
    """

    result = (
        create_result_by_document_id()
    )

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

    print(
        "PASS: RAGPipeline result types"
    )


# ============================================================
# Test 7
# ============================================================

def test_count_consistency():
    """
    驗證：

        Chunks
          =
        Embeddings
          =
        Mappings
    """

    result = (
        create_result_by_document_id()
    )

    chunks = result[
        "chunks"
    ]

    embeddings = result[
        "embeddings"
    ]

    mappings = result[
        "mappings"
    ]

    assert len(chunks) > 0

    assert (
        len(chunks)
        == len(embeddings)
        == len(mappings)
    )

    print(
        "PASS: Chunk / Embedding / Mapping count consistency"
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


# ============================================================
# Test 8
# ============================================================

def test_embedding_dimension():
    """
    驗證所有 Embedding 都是 1024 維。
    """

    result = (
        create_result_by_document_id()
    )

    embeddings = result[
        "embeddings"
    ]

    for index, embedding in enumerate(
        embeddings
    ):

        assert (
            len(embedding)
            == EMBEDDING_DIMENSION
        ), (
            f"Embedding {index} "
            "dimension mismatch."
        )

    print(
        "PASS: RAGPipeline embedding dimensions"
    )

    print(
        f"      Dimension: "
        f"{EMBEDDING_DIMENSION}"
    )


# ============================================================
# Test 9
# ============================================================

def test_mapping_integrity():
    """
    驗證：

        Chunk
          ↕
        Embedding

    Mapping 一一對應。
    """

    result = (
        create_result_by_document_id()
    )

    chunks = result[
        "chunks"
    ]

    embeddings = result[
        "embeddings"
    ]

    mappings = result[
        "mappings"
    ]

    for index, mapping in enumerate(
        mappings
    ):

        assert (
            mapping["document"]
            is chunks[index]
        )

        assert (
            mapping["embedding"]
            == embeddings[index]
        )

    print(
        "PASS: RAGPipeline mapping integrity"
    )


# ============================================================
# Test 10
# ============================================================

def test_metadata_preservation():
    """
    驗證 Metadata 從 RAG-1
    一路保留到 RAG-3。
    """

    result = (
        create_result_by_document_id()
    )

    document = result[
        "document"
    ]

    chunks = result[
        "chunks"
    ]

    mappings = result[
        "mappings"
    ]

    for index, chunk in enumerate(
        chunks
    ):

        assert (
            chunk.metadata
            == document.metadata
        )

        assert (
            mappings[index]["document"].metadata
            == document.metadata
        )

    print(
        "PASS: RAGPipeline metadata preservation"
    )


# ============================================================
# Test 11
# ============================================================

def test_document_identity():
    """
    驗證 Pipeline 不會更換原始 Chunk。
    """

    result = (
        create_result_by_document_id()
    )

    chunks = result[
        "chunks"
    ]

    mappings = result[
        "mappings"
    ]

    for index, mapping in enumerate(
        mappings
    ):

        assert (
            mapping["document"]
            is chunks[index]
        )

    print(
        "PASS: RAGPipeline document identity"
    )


# ============================================================
# Test 12
# ============================================================

def test_document_id_preservation():
    """
    驗證 document_id 保留。
    """

    result = (
        create_result_by_document_id()
    )

    document = result[
        "document"
    ]

    chunks = result[
        "chunks"
    ]

    mappings = result[
        "mappings"
    ]

    assert (
        document.metadata[
            "document_id"
        ]
        == TEST_DOCUMENT_ID
    )

    for chunk in chunks:

        assert (
            chunk.metadata[
                "document_id"
            ]
            == TEST_DOCUMENT_ID
        )

    for mapping in mappings:

        assert (
            mapping["document"]
            .metadata["document_id"]
            == TEST_DOCUMENT_ID
        )

    print(
        "PASS: RAGPipeline document_id preservation"
    )


# ============================================================
# Test 13
# ============================================================

def test_embedding_validation():
    """
    驗證最終 Embedding
    通過 RAG-3.5 Validation。
    """

    result = (
        create_result_by_document_id()
    )

    embeddings = result[
        "embeddings"
    ]

    mappings = result[
        "mappings"
    ]

    pipeline = create_rag_pipeline()

    assert (
        pipeline.embedding_pipeline
        .embedder
        .validate_embeddings(
            embeddings
        )
        is True
    )

    assert (
        pipeline.embedding_pipeline
        .embedder
        .validate_mappings(
            mappings
        )
        is True
    )

    print(
        "PASS: RAGPipeline embedding validation"
    )


# ============================================================
# Test 14
# ============================================================

def test_url_document_identity():
    """
    驗證 URL 流程取得的 Article
    與 Document ID 流程具有一致識別資料。
    """

    document_id_result = (
        create_result_by_document_id()
    )

    url_result = (
        create_result_by_url()
    )

    document_id_document = (
        document_id_result[
            "document"
        ]
    )

    url_document = (
        url_result[
            "document"
        ]
    )

    assert (
        document_id_document.metadata[
            "document_id"
        ]
        == url_document.metadata[
            "document_id"
        ]
    )

    assert (
        document_id_document.metadata[
            "url"
        ]
        == url_document.metadata[
            "url"
        ]
    )

    print(
        "PASS: Document ID / URL identity consistency"
    )


# ============================================================
# Test 15
# ============================================================

def test_full_rag_pipeline_flow():
    """
    RAG Pipeline 完整整合驗證。

        Document ID
            ↓
        RAG-1
            ↓
        Document
            ↓
        RAG-2
            ↓
        Chunks
            ↓
        RAG-3
            ↓
        Embeddings
            ↓
        Mapping
            ↓
        Validation
    """

    result = (
        create_result_by_document_id()
    )

    document = result[
        "document"
    ]

    chunks = result[
        "chunks"
    ]

    embeddings = result[
        "embeddings"
    ]

    mappings = result[
        "mappings"
    ]

    # --------------------------------------------------
    # RAG-1
    # --------------------------------------------------

    assert isinstance(
        document,
        Document
    )

    assert (
        document.metadata[
            "document_id"
        ]
        == TEST_DOCUMENT_ID
    )

    # --------------------------------------------------
    # RAG-2
    # --------------------------------------------------

    assert len(
        chunks
    ) > 0

    for chunk in chunks:

        assert isinstance(
            chunk,
            Document
        )

        assert (
            chunk.page_content
        )

    # --------------------------------------------------
    # RAG-3
    # --------------------------------------------------

    assert (
        len(embeddings)
        == len(chunks)
    )

    assert (
        len(mappings)
        == len(chunks)
    )

    # --------------------------------------------------
    # Mapping
    # --------------------------------------------------

    for index, mapping in enumerate(
        mappings
    ):

        assert (
            mapping["document"]
            is chunks[index]
        )

        assert (
            mapping["embedding"]
            == embeddings[index]
        )

        assert (
            len(
                mapping["embedding"]
            )
            == EMBEDDING_DIMENSION
        )

    # --------------------------------------------------
    # Validation
    # --------------------------------------------------

    pipeline = create_rag_pipeline()

    assert (
        pipeline.embedding_pipeline
        .embedder
        .validate_embeddings(
            embeddings
        )
        is True
    )

    assert (
        pipeline.embedding_pipeline
        .embedder
        .validate_mappings(
            mappings
        )
        is True
    )

    print(
        "PASS: Full RAG-1 → RAG-2 → RAG-3 pipeline"
    )

    print(
        f"      Model: {EMBEDDING_MODEL}"
    )

    print(
        f"      Document ID: "
        f"{TEST_DOCUMENT_ID}"
    )

    print(
        f"      Source length: "
        f"{len(document.page_content)}"
    )

    print(
        f"      Chunk count: "
        f"{len(chunks)}"
    )

    print(
        f"      Embedding count: "
        f"{len(embeddings)}"
    )

    print(
        f"      Mapping count: "
        f"{len(mappings)}"
    )

    print(
        f"      Dimension: "
        f"{EMBEDDING_DIMENSION}"
    )


# ============================================================
# Validation Tests
# ============================================================

def test_none_document():
    """
    驗證 process_document(None)。
    """

    pipeline = create_rag_pipeline()

    try:

        pipeline.process_document(
            None
        )

    except ValueError:

        print(
            "PASS: None document validation"
        )

        return

    raise AssertionError(
        "None document should raise ValueError."
    )


def test_none_document_id():
    """
    驗證 process_by_document_id(None)。
    """

    pipeline = create_rag_pipeline()

    try:

        pipeline.process_by_document_id(
            None
        )

    except ValueError:

        print(
            "PASS: None document_id validation"
        )

        return

    raise AssertionError(
        "None document_id should raise ValueError."
    )


def test_empty_document_id():
    """
    驗證空 Document ID。
    """

    pipeline = create_rag_pipeline()

    try:

        pipeline.process_by_document_id(
            "   "
        )

    except ValueError:

        print(
            "PASS: Empty document_id validation"
        )

        return

    raise AssertionError(
        "Empty document_id should raise ValueError."
    )


def test_none_url():
    """
    驗證 process_by_url(None)。
    """

    pipeline = create_rag_pipeline()

    try:

        pipeline.process_by_url(
            None
        )

    except ValueError:

        print(
            "PASS: None URL validation"
        )

        return

    raise AssertionError(
        "None URL should raise ValueError."
    )


def test_empty_url():
    """
    驗證空 URL。
    """

    pipeline = create_rag_pipeline()

    try:

        pipeline.process_by_url(
            "   "
        )

    except ValueError:

        print(
            "PASS: Empty URL validation"
        )

        return

    raise AssertionError(
        "Empty URL should raise ValueError."
    )


# ============================================================
# Main
# ============================================================

def main():
    """
    執行 RAGPipeline Integration Test。
    """

    print("=" * 60)

    print(
        "RAGPipeline Integration Test"
    )

    print("=" * 60)

    print()

    print(
        f"Embedding Model: {EMBEDDING_MODEL}"
    )

    print(
        f"Embedding Dimension: "
        f"{EMBEDDING_DIMENSION}"
    )

    print()

    print(
        "Testing RAG-1 → RAG-2 → RAG-3..."
    )

    print()

    test_pipeline_initialization()

    test_component_integration()

    test_process_document()

    test_process_by_document_id()

    test_process_by_url()

    test_result_types()

    test_count_consistency()

    test_embedding_dimension()

    test_mapping_integrity()

    test_metadata_preservation()

    test_document_identity()

    test_document_id_preservation()

    test_embedding_validation()

    test_url_document_identity()

    test_full_rag_pipeline_flow()

    print()

    print(
        "Testing RAGPipeline input validation..."
    )

    print()

    test_none_document()

    test_none_document_id()

    test_empty_document_id()

    test_none_url()

    test_empty_url()

    print()

    print("=" * 60)

    print(
        "ALL RAG PIPELINE INTEGRATION TESTS PASSED"
    )

    print("=" * 60)


if __name__ == "__main__":
    main()