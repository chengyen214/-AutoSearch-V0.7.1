"""
tests/V7_3/test_rag_embedding.py

AutoSearch V7

RAG-3.6

Embedding Integration Test

功能：

    驗證完整 RAG-3 Embedding 流程。

資料流程：

    MCP
      ↓
    RAG-1 Document Preparation
      ↓
    RAG-2 Document Chunking
      ↓
    RAG-3.2 EmbeddingModel
      ↓
    Qwen/Qwen3-Embedding-0.6B
      ↓
    RAG-3.3 Chunk → Embedding
      ↓
    RAG-3.4 Embedding Mapping
      ↓
    RAG-3.5 Embedding Validation
      ↓
    RAG-3.6 Integration Test

本測試驗證：

    1. RAG-1 Document Preparation
    2. RAG-2 Chunking
    3. Qwen Embedding
    4. Chunk ↔ Embedding Mapping
    5. Embedding Dimension
    6. Embedding Value
    7. Metadata Preservation
    8. Document Identity
    9. Embedding Validation
    10. End-to-End Embedding Flow

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
# Shared Objects
# ============================================================

_PREPARED_DOCUMENT = None
_CHUNKS = None
_EMBEDDER = None
_MAPPINGS = None


# ============================================================
# Prepared Document
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

    assert (
        _PREPARED_DOCUMENT.page_content
    )

    return _PREPARED_DOCUMENT


# ============================================================
# Chunks
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
# Embedder
# ============================================================

def create_embedder():
    """
    建立並共用 Embedder。

    Qwen Model 只初始化一次。
    """

    global _EMBEDDER

    if _EMBEDDER is None:

        _EMBEDDER = Embedder()

    return _EMBEDDER


# ============================================================
# Mappings
# ============================================================

def create_mappings():
    """
    建立真實 Chunk ↔ Embedding Mapping。

    整個測試只建立一次。
    """

    global _MAPPINGS

    if _MAPPINGS is None:

        chunks = create_chunks()
        embedder = create_embedder()

        _MAPPINGS = (
            embedder.embed_documents_with_mapping(
                chunks
            )
        )

    assert (
        _MAPPINGS
        is not None
    )

    assert isinstance(
        _MAPPINGS,
        list
    )

    assert len(
        _MAPPINGS
    ) > 0

    return _MAPPINGS


# ============================================================
# Test 1
# ============================================================

def test_embedding_model_configuration():
    """
    確認 Embedding Model 設定。
    """

    assert (
        EMBEDDING_MODEL
        == "Qwen/Qwen3-Embedding-0.6B"
    )

    assert (
        EMBEDDING_DIMENSION
        == 1024
    )

    print(
        "PASS: Embedding model configuration"
    )

    print(
        f"      Model: {EMBEDDING_MODEL}"
    )

    print(
        f"      Dimension: "
        f"{EMBEDDING_DIMENSION}"
    )


# ============================================================
# Test 2
# ============================================================

def test_rag1_document_preparation():
    """
    確認 RAG-1 Document Preparation。
    """

    document = (
        create_prepared_document()
    )

    assert isinstance(
        document,
        Document
    )

    assert (
        document.page_content
    )

    assert (
        document.metadata
    )

    print(
        "PASS: RAG-1 Document Preparation"
    )


# ============================================================
# Test 3
# ============================================================

def test_rag2_chunking():
    """
    確認 RAG-2 Chunking。
    """

    document = (
        create_prepared_document()
    )

    chunks = create_chunks()

    assert (
        len(chunks)
        > 0
    )

    for chunk in chunks:

        assert isinstance(
            chunk,
            Document
        )

        assert (
            chunk.page_content
        )

        assert (
            chunk.metadata
            == document.metadata
        )

    print(
        "PASS: RAG-2 Chunking"
    )

    print(
        f"      Source length: "
        f"{len(document.page_content)}"
    )

    print(
        f"      Chunk count: "
        f"{len(chunks)}"
    )


# ============================================================
# Test 4
# ============================================================

def test_embedding_generation():
    """
    確認 RAG-3.3 Embedding。
    """

    chunks = create_chunks()
    embedder = create_embedder()

    embeddings = (
        embedder.embed_documents(
            chunks
        )
    )

    assert (
        len(embeddings)
        == len(chunks)
    )

    for embedding in embeddings:

        assert isinstance(
            embedding,
            list
        )

        assert (
            len(embedding)
            == EMBEDDING_DIMENSION
        )

    print(
        "PASS: RAG-3.3 Embedding generation"
    )

    print(
        f"      Embeddings: "
        f"{len(embeddings)}"
    )

    print(
        f"      Dimension: "
        f"{EMBEDDING_DIMENSION}"
    )


# ============================================================
# Test 5
# ============================================================

def test_embedding_mapping():
    """
    確認 RAG-3.4 Mapping。
    """

    chunks = create_chunks()
    mappings = create_mappings()

    assert (
        len(mappings)
        == len(chunks)
    )

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

    print(
        "PASS: RAG-3.4 Embedding mapping"
    )


# ============================================================
# Test 6
# ============================================================

def test_embedding_validation():
    """
    確認 RAG-3.5 Validation。
    """

    embedder = create_embedder()
    mappings = create_mappings()

    embeddings = [
        mapping["embedding"]
        for mapping in mappings
    ]

    assert (
        embedder.validate_embeddings(
            embeddings
        )
        is True
    )

    print(
        "PASS: RAG-3.5 Embedding validation"
    )


# ============================================================
# Test 7
# ============================================================

def test_embedding_values():
    """
    確認 Embedding 不為全零，
    且每個值為有限 numeric。
    """

    mappings = create_mappings()

    for index, mapping in enumerate(
        mappings
    ):

        embedding = mapping[
            "embedding"
        ]

        assert len(
            embedding
        ) == EMBEDDING_DIMENSION

        assert any(
            value != 0
            for value in embedding
        )

        for value in embedding:

            assert isinstance(
                value,
                (int, float)
            )

    print(
        "PASS: Embedding values"
    )


# ============================================================
# Test 8
# ============================================================

def test_document_metadata_preservation():
    """
    確認 Embedding Mapping
    沒有破壞 Document Metadata。
    """

    chunks = create_chunks()
    mappings = create_mappings()

    for index, mapping in enumerate(
        mappings
    ):

        source_document = chunks[
            index
        ]

        mapped_document = mapping[
            "document"
        ]

        assert (
            mapped_document.metadata
            == source_document.metadata
        )

    print(
        "PASS: Document metadata preservation"
    )


# ============================================================
# Test 9
# ============================================================

def test_document_identity():
    """
    確認 Mapping 中的 Document
    就是原始 Chunk。
    """

    chunks = create_chunks()
    mappings = create_mappings()

    for index, mapping in enumerate(
        mappings
    ):

        assert (
            mapping["document"]
            is chunks[index]
        )

    print(
        "PASS: Document identity"
    )


# ============================================================
# Test 10
# ============================================================

def test_document_id_preservation():
    """
    確認 document_id
    從 MCP Article 一路保留到 Embedding Mapping。
    """

    mappings = create_mappings()

    for index, mapping in enumerate(
        mappings
    ):

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
        "PASS: Document ID preservation"
    )


# ============================================================
# Test 11
# ============================================================

def test_embedding_mapping_validation():
    """
    確認 RAG-3.4 Mapping
    可以通過 RAG-3.5 Validation。
    """

    embedder = create_embedder()
    mappings = create_mappings()

    assert (
        embedder.validate_mappings(
            mappings
        )
        is True
    )

    print(
        "PASS: Mapping + Validation integration"
    )


# ============================================================
# Test 12
# ============================================================

def test_embedding_count_consistency():
    """
    確認：

        Chunks
          =
        Mappings
          =
        Embeddings
    """

    chunks = create_chunks()
    mappings = create_mappings()

    embeddings = [
        mapping["embedding"]
        for mapping in mappings
    ]

    assert (
        len(chunks)
        == len(mappings)
        == len(embeddings)
    )

    print(
        "PASS: Chunk ↔ Mapping ↔ Embedding count consistency"
    )


# ============================================================
# Test 13
# ============================================================

def test_full_rag3_embedding_flow():
    """
    RAG-3 完整 Embedding End-to-End Test。

        MCP Article
            ↓
        RAG-1 Document
            ↓
        RAG-2 Chunk
            ↓
        Qwen Embedding
            ↓
        Mapping
            ↓
        Validation
    """

    document = (
        create_prepared_document()
    )

    chunks = create_chunks()

    embedder = create_embedder()

    mappings = (
        create_mappings()
    )

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

    embeddings = [
        mapping["embedding"]
        for mapping in mappings
    ]

    assert (
        len(embeddings)
        == len(chunks)
    )

    # --------------------------------------------------------
    # RAG-3.4
    # --------------------------------------------------------

    for index, mapping in enumerate(
        mappings
    ):

        assert (
            mapping["document"]
            is chunks[index]
        )

    # --------------------------------------------------------
    # RAG-3.5
    # --------------------------------------------------------

    assert (
        embedder.validate_mappings(
            mappings
        )
        is True
    )

    # --------------------------------------------------------
    # Final Validation
    # --------------------------------------------------------

    for index, mapping in enumerate(
        mappings
    ):

        mapped_document = mapping[
            "document"
        ]

        embedding = mapping[
            "embedding"
        ]

        assert (
            mapped_document.metadata[
                "document_id"
            ]
            == TEST_DOCUMENT_ID
        )

        assert (
            mapped_document.page_content
            == chunks[index].page_content
        )

        assert (
            mapped_document.metadata
            == chunks[index].metadata
        )

        assert (
            len(embedding)
            == EMBEDDING_DIMENSION
        )

        assert any(
            value != 0
            for value in embedding
        )

    print(
        "PASS: Full RAG-3 embedding flow"
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
        f"      Mapping count: "
        f"{len(mappings)}"
    )

    print(
        f"      Embedding dimension: "
        f"{EMBEDDING_DIMENSION}"
    )


# ============================================================
# Main
# ============================================================

def main():
    """
    執行 RAG-3.6 Embedding Integration Test。
    """

    print("=" * 60)

    print(
        "RAG-3.6 Embedding Integration Test"
    )

    print("=" * 60)

    print()

    print(
        "Testing complete RAG-3 Embedding flow..."
    )

    print()

    test_embedding_model_configuration()

    test_rag1_document_preparation()

    test_rag2_chunking()

    test_embedding_generation()

    test_embedding_mapping()

    test_embedding_validation()

    test_embedding_values()

    test_document_metadata_preservation()

    test_document_identity()

    test_document_id_preservation()

    test_embedding_mapping_validation()

    test_embedding_count_consistency()

    test_full_rag3_embedding_flow()

    print()

    print("=" * 60)

    print(
        "ALL RAG-3.6 EMBEDDING INTEGRATION TESTS PASSED"
    )

    print("=" * 60)


if __name__ == "__main__":
    main()