"""
tests/V7_3/test_rag_embedding_pipeline.py

AutoSearch V7

RAG-3

Embedding Pipeline Test

功能：

    驗證 RAG-3 EmbeddingPipeline
    是否可以正確串接：

        RAG-2 Chunks
              ↓
        EmbeddingPipeline
              ↓
        Embedder
              ↓
        Embedding
              ↓
        Mapping
              ↓
        Validation

測試流程：

    MCP Article
        ↓
    RAG-1 Document Preparation
        ↓
    RAG-2 Chunking
        ↓
    RAG-3 EmbeddingPipeline

本測試驗證：

    1. EmbeddingPipeline initialization
    2. RAG-2 Chunk input
    3. RAG-3 Embedding generation
    4. Embedding Mapping
    5. Embedding Validation
    6. Document preservation
    7. Metadata preservation
    8. Count consistency
    9. Embedding dimension
    10. Single Document processing
    11. Multiple Chunk processing
    12. Full RAG-3 Pipeline integration

本階段不負責：

    1. ChromaDB
    2. Retriever
    3. Context Builder
    4. LLM Generation
"""


from langchain_core.documents import Document

from rag.document_preparation import (
    DocumentPreparation
)

from rag.chunking.document_chunking import (
    DocumentChunking
)

from rag.embedding.embedder import (
    Embedder
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


# ============================================================
# Shared Test Objects
# ============================================================

_PREPARED_DOCUMENT = None
_CHUNKS = None
_EMBEDDER = None
_PIPELINE = None


# ============================================================
# Create Prepared Document
# ============================================================

def create_prepared_document():
    """
    建立真實 Prepared Document。

    整個測試只建立一次。
    """

    global _PREPARED_DOCUMENT

    if _PREPARED_DOCUMENT is None:

        preparation = DocumentPreparation()

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
# Create Chunks
# ============================================================

def create_chunks():
    """
    建立真實 RAG-2 Chunks。

    整個測試只建立一次。
    """

    global _CHUNKS

    if _CHUNKS is None:

        document = (
            create_prepared_document()
        )

        chunking = DocumentChunking()

        _CHUNKS = chunking.chunk(
            document
        )

    assert (
        _CHUNKS
        is not None
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
# Create Embedder
# ============================================================

def create_embedder():
    """
    建立共用 Embedder。

    Qwen Model 只載入一次。
    """

    global _EMBEDDER

    if _EMBEDDER is None:

        _EMBEDDER = Embedder()

    return _EMBEDDER


# ============================================================
# Create Embedding Pipeline
# ============================================================

def create_pipeline():
    """
    建立共用 EmbeddingPipeline。

    使用共用 Embedder，
    避免重複初始化 Qwen Model。
    """

    global _PIPELINE

    if _PIPELINE is None:

        _PIPELINE = EmbeddingPipeline(
            embedder=create_embedder()
        )

    return _PIPELINE


# ============================================================
# Test 1
# ============================================================

def test_pipeline_initialization():
    """
    驗證 EmbeddingPipeline 初始化。
    """

    pipeline = create_pipeline()

    assert (
        pipeline
        is not None
    )

    assert isinstance(
        pipeline,
        EmbeddingPipeline
    )

    print(
        "PASS: EmbeddingPipeline initialization"
    )


# ============================================================
# Test 2
# ============================================================

def test_pipeline_embedder():
    """
    驗證 Pipeline 正確持有 Embedder。
    """

    embedder = create_embedder()
    pipeline = create_pipeline()

    assert (
        pipeline.get_embedder()
        is embedder
    )

    print(
        "PASS: EmbeddingPipeline Embedder integration"
    )


# ============================================================
# Test 3
# ============================================================

def test_pipeline_dimension():
    """
    驗證 Pipeline 的 Embedding Dimension。
    """

    pipeline = create_pipeline()

    assert (
        pipeline.get_dimension()
        == EMBEDDING_DIMENSION
    )

    print(
        "PASS: EmbeddingPipeline dimension"
    )

    print(
        f"      Dimension: "
        f"{pipeline.get_dimension()}"
    )


# ============================================================
# Test 4
# ============================================================

def test_process_documents():
    """
    測試：

        Chunks
          ↓
        EmbeddingPipeline.process()
    """

    chunks = create_chunks()
    pipeline = create_pipeline()

    result = pipeline.process(
        chunks
    )

    assert isinstance(
        result,
        dict
    )

    assert "documents" in result
    assert "embeddings" in result
    assert "mappings" in result

    print(
        "PASS: Pipeline document processing"
    )


# ============================================================
# Test 5
# ============================================================

def test_process_document_count():
    """
    驗證：

        Documents
        Embeddings
        Mappings

    數量一致。
    """

    chunks = create_chunks()
    pipeline = create_pipeline()

    result = pipeline.process(
        chunks
    )

    documents = result[
        "documents"
    ]

    embeddings = result[
        "embeddings"
    ]

    mappings = result[
        "mappings"
    ]

    assert (
        len(documents)
        == len(chunks)
    )

    assert (
        len(embeddings)
        == len(chunks)
    )

    assert (
        len(mappings)
        == len(chunks)
    )

    assert (
        len(documents)
        == len(embeddings)
        == len(mappings)
    )

    print(
        "PASS: Pipeline count consistency"
    )

    print(
        f"      Chunks: "
        f"{len(chunks)}"
    )

    print(
        f"      Embeddings: "
        f"{len(embeddings)}"
    )

    print(
        f"      Mappings: "
        f"{len(mappings)}"
    )


# ============================================================
# Test 6
# ============================================================

def test_pipeline_embedding_dimension():
    """
    驗證 Pipeline 產生的 Embedding
    全部為 1024 維。
    """

    chunks = create_chunks()
    pipeline = create_pipeline()

    result = pipeline.process(
        chunks
    )

    embeddings = result[
        "embeddings"
    ]

    for index, embedding in enumerate(
        embeddings
    ):

        assert isinstance(
            embedding,
            list
        )

        assert (
            len(embedding)
            == EMBEDDING_DIMENSION
        ), (
            f"Embedding {index} "
            "dimension mismatch."
        )

    print(
        "PASS: Pipeline embedding dimensions"
    )


# ============================================================
# Test 7
# ============================================================

def test_pipeline_mapping():
    """
    驗證 Chunk ↔ Embedding Mapping。
    """

    chunks = create_chunks()
    pipeline = create_pipeline()

    result = pipeline.process(
        chunks
    )

    mappings = result[
        "mappings"
    ]

    for index, mapping in enumerate(
        mappings
    ):

        assert isinstance(
            mapping,
            dict
        )

        assert (
            set(mapping.keys())
            == {
                "document",
                "embedding",
            }
        )

        assert (
            mapping["document"]
            is chunks[index]
        )

        assert (
            len(
                mapping["embedding"]
            )
            == EMBEDDING_DIMENSION
        )

    print(
        "PASS: Pipeline embedding mapping"
    )


# ============================================================
# Test 8
# ============================================================

def test_pipeline_validation():
    """
    驗證 Pipeline 產生的 Embedding
    與 Mapping 都能通過 Validation。
    """

    chunks = create_chunks()
    pipeline = create_pipeline()

    result = pipeline.process(
        chunks
    )

    embeddings = result[
        "embeddings"
    ]

    mappings = result[
        "mappings"
    ]

    assert (
        pipeline.embedder.validate_embeddings(
            embeddings
        )
        is True
    )

    assert (
        pipeline.embedder.validate_mappings(
            mappings
        )
        is True
    )

    print(
        "PASS: Pipeline embedding validation"
    )


# ============================================================
# Test 9
# ============================================================

def test_pipeline_document_preservation():
    """
    驗證 Pipeline 不會替換原始 Chunk Document。
    """

    chunks = create_chunks()
    pipeline = create_pipeline()

    result = pipeline.process(
        chunks
    )

    documents = result[
        "documents"
    ]

    mappings = result[
        "mappings"
    ]

    for index in range(
        len(chunks)
    ):

        assert (
            documents[index]
            is chunks[index]
        )

        assert (
            mappings[index]["document"]
            is chunks[index]
        )

    print(
        "PASS: Pipeline document preservation"
    )


# ============================================================
# Test 10
# ============================================================

def test_pipeline_metadata_preservation():
    """
    驗證 Pipeline 保留完整 Metadata。
    """

    chunks = create_chunks()
    pipeline = create_pipeline()

    result = pipeline.process(
        chunks
    )

    mappings = result[
        "mappings"
    ]

    for index, mapping in enumerate(
        mappings
    ):

        source = chunks[index]
        mapped = mapping[
            "document"
        ]

        assert (
            mapped.metadata
            == source.metadata
        )

    print(
        "PASS: Pipeline metadata preservation"
    )


# ============================================================
# Test 11
# ============================================================

def test_pipeline_document_id_preservation():
    """
    驗證 document_id
    從 RAG-1 → RAG-2 → RAG-3 Pipeline
    全程保留。
    """

    chunks = create_chunks()
    pipeline = create_pipeline()

    result = pipeline.process(
        chunks
    )

    mappings = result[
        "mappings"
    ]

    for mapping in mappings:

        document = mapping[
            "document"
        ]

        assert (
            document.metadata[
                "document_id"
            ]
            == TEST_DOCUMENT_ID
        )

    print(
        "PASS: Pipeline document_id preservation"
    )


# ============================================================
# Test 12
# ============================================================

def test_process_single_document():
    """
    測試：

        Single Document
            ↓
        process_document()
    """

    chunks = create_chunks()
    pipeline = create_pipeline()

    document = chunks[0]

    result = pipeline.process_document(
        document
    )

    assert isinstance(
        result,
        dict
    )

    assert "document" in result
    assert "embedding" in result
    assert "mapping" in result

    assert (
        result["document"]
        is document
    )

    assert (
        result["mapping"]["document"]
        is document
    )

    assert (
        len(result["embedding"])
        == EMBEDDING_DIMENSION
    )

    assert (
        len(
            result["mapping"]["embedding"]
        )
        == EMBEDDING_DIMENSION
    )

    print(
        "PASS: Single Document pipeline processing"
    )


# ============================================================
# Test 13
# ============================================================

def test_process_chunks():
    """
    測試 process_chunks()。
    """

    chunks = create_chunks()
    pipeline = create_pipeline()

    result = pipeline.process_chunks(
        chunks
    )

    assert isinstance(
        result,
        dict
    )

    assert (
        len(result["documents"])
        == len(chunks)
    )

    assert (
        len(result["embeddings"])
        == len(chunks)
    )

    assert (
        len(result["mappings"])
        == len(chunks)
    )

    print(
        "PASS: Chunk processing pipeline"
    )


# ============================================================
# Test 14
# ============================================================

def test_pipeline_embedding_values():
    """
    驗證 Embedding 不為全零。
    """

    chunks = create_chunks()
    pipeline = create_pipeline()

    result = pipeline.process(
        chunks
    )

    embeddings = result[
        "embeddings"
    ]

    for index, embedding in enumerate(
        embeddings
    ):

        assert any(
            value != 0
            for value in embedding
        ), (
            f"Embedding {index} "
            "contains only zeros."
        )

    print(
        "PASS: Pipeline embedding values"
    )


# ============================================================
# Test 15
# ============================================================

def test_full_rag3_embedding_pipeline():
    """
    RAG-3 完整整合測試。

        RAG-1 Article
              ↓
        RAG-1 Document
              ↓
        RAG-2 Chunks
              ↓
        RAG-3 EmbeddingPipeline
              ↓
        Embedding
              ↓
        Mapping
              ↓
        Validation
    """

    document = (
        create_prepared_document()
    )

    chunks = create_chunks()

    pipeline = create_pipeline()

    result = pipeline.process(
        chunks
    )

    documents = result[
        "documents"
    ]

    embeddings = result[
        "embeddings"
    ]

    mappings = result[
        "mappings"
    ]

    # --------------------------------------------------------
    # RAG-1
    # --------------------------------------------------------

    assert isinstance(
        document,
        Document
    )

    # --------------------------------------------------------
    # RAG-2
    # --------------------------------------------------------

    assert len(
        chunks
    ) > 0

    # --------------------------------------------------------
    # RAG-3.3
    # --------------------------------------------------------

    assert (
        len(embeddings)
        == len(chunks)
    )

    # --------------------------------------------------------
    # RAG-3.4
    # --------------------------------------------------------

    assert (
        len(mappings)
        == len(chunks)
    )

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

    # --------------------------------------------------------
    # RAG-3.5
    # --------------------------------------------------------

    assert (
        pipeline.embedder.validate_embeddings(
            embeddings
        )
        is True
    )

    assert (
        pipeline.embedder.validate_mappings(
            mappings
        )
        is True
    )

    # --------------------------------------------------------
    # Document Integrity
    # --------------------------------------------------------

    for index, chunk in enumerate(
        chunks
    ):

        assert (
            documents[index]
            is chunk
        )

        assert (
            mappings[index]["document"]
            is chunk
        )

        assert (
            documents[index].metadata
            == chunk.metadata
        )

        assert (
            mappings[index]["document"].metadata
            == chunk.metadata
        )

        assert (
            len(
                embeddings[index]
            )
            == EMBEDDING_DIMENSION
        )

        assert any(
            value != 0
            for value in embeddings[index]
        )

    print(
        "PASS: Full RAG-3 EmbeddingPipeline integration"
    )

    print(
        f"      Model: "
        f"{EMBEDDING_MODEL}"
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
        f"      Embedding dimension: "
        f"{EMBEDDING_DIMENSION}"
    )


# ============================================================
# Validation Tests
# ============================================================

def test_none_documents():
    """
    驗證 process(None)。
    """

    pipeline = create_pipeline()

    try:

        pipeline.process(
            None
        )

    except ValueError:

        print(
            "PASS: None documents validation"
        )

        return

    raise AssertionError(
        "None documents should raise ValueError."
    )


def test_invalid_documents_type():
    """
    驗證 process() 收到非 list。
    """

    pipeline = create_pipeline()

    try:

        pipeline.process(
            "invalid"
        )

    except TypeError:

        print(
            "PASS: Invalid documents type validation"
        )

        return

    raise AssertionError(
        "Invalid documents type "
        "should raise TypeError."
    )


def test_empty_documents():
    """
    驗證 process() 收到空 list。
    """

    pipeline = create_pipeline()

    try:

        pipeline.process(
            []
        )

    except ValueError:

        print(
            "PASS: Empty documents validation"
        )

        return

    raise AssertionError(
        "Empty documents "
        "should raise ValueError."
    )


def test_none_document():
    """
    驗證 process_document(None)。
    """

    pipeline = create_pipeline()

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
        "None document "
        "should raise ValueError."
    )


def test_invalid_document_type():
    """
    驗證 process_document() 收到非 Document。
    """

    pipeline = create_pipeline()

    try:

        pipeline.process_document(
            "invalid"
        )

    except TypeError:

        print(
            "PASS: Invalid document type validation"
        )

        return

    raise AssertionError(
        "Invalid document type "
        "should raise TypeError."
    )


# ============================================================
# Main
# ============================================================

def main():
    """
    執行 RAG-3 EmbeddingPipeline Test。
    """

    print("=" * 60)

    print(
        "RAG-3 EmbeddingPipeline Test"
    )

    print("=" * 60)

    print()

    print(
        f"Model: {EMBEDDING_MODEL}"
    )

    print(
        f"Dimension: {EMBEDDING_DIMENSION}"
    )

    print()

    print(
        "Testing RAG-3 Embedding Pipeline..."
    )

    print()

    test_pipeline_initialization()

    test_pipeline_embedder()

    test_pipeline_dimension()

    test_process_documents()

    test_process_document_count()

    test_pipeline_embedding_dimension()

    test_pipeline_mapping()

    test_pipeline_validation()

    test_pipeline_document_preservation()

    test_pipeline_metadata_preservation()

    test_pipeline_document_id_preservation()

    test_process_single_document()

    test_process_chunks()

    test_pipeline_embedding_values()

    test_full_rag3_embedding_pipeline()

    print()

    print(
        "Testing pipeline input validation..."
    )

    print()

    test_none_documents()

    test_invalid_documents_type()

    test_empty_documents()

    test_none_document()

    test_invalid_document_type()

    print()

    print("=" * 60)

    print(
        "ALL RAG-3 EMBEDDING PIPELINE TESTS PASSED"
    )

    print("=" * 60)


if __name__ == "__main__":
    main()