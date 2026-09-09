"""
tests/V7_3/test_rag_embedding_mapping.py

AutoSearch V7

RAG-3.4

Embedding Mapping Test

功能：

    測試 RAG-3.4
    Chunk ↔ Embedding Mapping。

完整資料流程：

    MCP
      ↓
    RAG-1 Document Preparation
      ↓
    Prepared Document
      ↓
    RAG-2 Document Chunking
      ↓
    Chunk Documents
      ↓
    RAG-3.2 EmbeddingModel
      ↓
    Qwen/Qwen3-Embedding-0.6B
      ↓
    RAG-3.3 Chunk → Embedding
      ↓
    RAG-3.4 Embedding Mapping
      ↓
    Chunk + Embedding

Mapping 結構：

    {
        "document": LangChain Document,
        "embedding": list[float]
    }

正式 RAG Metadata Schema：

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

本測試原則：

    1. 共用同一個 Prepared Document
    2. 共用同一份 Chunks
    3. 共用同一個 Embedder
    4. Qwen Model 只初始化一次
    5. 避免每個 test 重複載入模型

本測試不負責：

    1. ChromaDB
    2. Retriever
    3. Context Builder
    4. LLM
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
)


# ============================================================
# Test Article Identifier
# ============================================================

TEST_DOCUMENT_ID = (
    "d9ce4740c3f0b6f1d260c094c0549f68727187b0a2b57c94f6308b4df9fd9d13"
)


# ============================================================
# Expected Metadata Schema
# ============================================================

EXPECTED_METADATA_FIELDS = (
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
)


# ============================================================
# Shared Test Objects
# ============================================================

_PREPARED_DOCUMENT = None
_CHUNKS = None
_EMBEDDER = None


# ============================================================
# Create Prepared Document
# ============================================================

def create_prepared_document():
    """
    透過 RAG-1 DocumentPreparation
    取得真實 Prepared Document。

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

        assert isinstance(
            _PREPARED_DOCUMENT.metadata,
            dict
        )

    return _PREPARED_DOCUMENT


# ============================================================
# Create Real Chunks
# ============================================================

def create_chunks():
    """
    透過 RAG-2 DocumentChunking
    取得真實 Chunk Documents。

    整個測試只建立一次。
    """

    global _CHUNKS

    if _CHUNKS is None:

        document = create_prepared_document()

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
    建立並共用 RAG-3.3 Embedder。

    整個測試只初始化一次。

    目的：

        避免每個 test
        重複載入 Qwen Model。
    """

    global _EMBEDDER

    if _EMBEDDER is None:

        _EMBEDDER = Embedder()

    return _EMBEDDER


# ============================================================
# Test Single Mapping
# ============================================================

def test_single_mapping():
    """
    測試單一 Document
    是否可以建立 Mapping。
    """

    chunks = create_chunks()

    embedder = create_embedder()

    document = chunks[0]

    mapping = (
        embedder.embed_document_with_mapping(
            document
        )
    )

    assert mapping is not None

    assert isinstance(
        mapping,
        dict
    )

    assert "document" in mapping

    assert "embedding" in mapping

    print(
        "PASS: Single embedding mapping"
    )


# ============================================================
# Test Single Mapping Document
# ============================================================

def test_single_mapping_document():
    """
    確認 Mapping 中的 Document
    就是原始 Chunk Document。
    """

    chunks = create_chunks()

    embedder = create_embedder()

    document = chunks[0]

    mapping = (
        embedder.embed_document_with_mapping(
            document
        )
    )

    mapped_document = mapping[
        "document"
    ]

    assert isinstance(
        mapped_document,
        Document
    )

    assert (
        mapped_document.page_content
        == document.page_content
    )

    assert (
        mapped_document.metadata
        == document.metadata
    )

    print(
        "PASS: Mapped Document preservation"
    )


# ============================================================
# Test Single Mapping Embedding
# ============================================================

def test_single_mapping_embedding():
    """
    確認單一 Mapping 中的 Embedding
    是 1024 維。
    """

    chunks = create_chunks()

    embedder = create_embedder()

    mapping = (
        embedder.embed_document_with_mapping(
            chunks[0]
        )
    )

    embedding = mapping[
        "embedding"
    ]

    assert isinstance(
        embedding,
        list
    )

    assert (
        len(embedding)
        == EMBEDDING_DIMENSION
    )

    print(
        "PASS: Single mapping embedding"
    )

    print(
        f"      Embedding dimension: "
        f"{len(embedding)}"
    )


# ============================================================
# Test Multiple Mappings
# ============================================================

def test_multiple_mappings():
    """
    測試多個 Chunk
    是否可以建立多個 Mapping。
    """

    chunks = create_chunks()

    embedder = create_embedder()

    mappings = (
        embedder.embed_documents_with_mapping(
            chunks
        )
    )

    assert mappings is not None

    assert isinstance(
        mappings,
        list
    )

    assert (
        len(mappings)
        == len(chunks)
    )

    print(
        "PASS: Multiple embedding mappings"
    )

    print(
        f"      Chunks: "
        f"{len(chunks)}"
    )

    print(
        f"      Mappings: "
        f"{len(mappings)}"
    )


# ============================================================
# Test Mapping Structure
# ============================================================

def test_mapping_structure():
    """
    確認每個 Mapping
    都具有正確結構。
    """

    chunks = create_chunks()

    embedder = create_embedder()

    mappings = (
        embedder.embed_documents_with_mapping(
            chunks
        )
    )

    for index, mapping in enumerate(
        mappings
    ):

        assert isinstance(
            mapping,
            dict
        ), (
            f"Mapping {index} is not dict."
        )

        assert set(
            mapping.keys()
        ) == {
            "document",
            "embedding",
        }, (
            f"Mapping {index} has unexpected keys."
        )

    print(
        "PASS: Mapping structure"
    )


# ============================================================
# Test One-to-One Mapping
# ============================================================

def test_one_to_one_mapping():
    """
    確認：

        N Chunks
            ↓
        N Mappings
            ↓
        N Embeddings

    數量必須一一對應。
    """

    chunks = create_chunks()

    embedder = create_embedder()

    mappings = (
        embedder.embed_documents_with_mapping(
            chunks
        )
    )

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

    print(
        "PASS: One-to-one Chunk ↔ Embedding mapping"
    )


# ============================================================
# Test Embedding Dimension
# ============================================================

def test_embedding_dimensions():
    """
    確認所有 Mapping Embedding
    都是 1024 維。
    """

    chunks = create_chunks()

    embedder = create_embedder()

    mappings = (
        embedder.embed_documents_with_mapping(
            chunks
        )
    )

    for index, mapping in enumerate(
        mappings
    ):

        embedding = mapping[
            "embedding"
        ]

        assert (
            len(embedding)
            == EMBEDDING_DIMENSION
        ), (
            f"Mapping {index} embedding "
            "dimension mismatch."
        )

    print(
        "PASS: Mapping embedding dimensions"
    )


# ============================================================
# Test Metadata Preservation
# ============================================================

def test_metadata_preservation():
    """
    確認 Mapping 中的 Document
    保留完整 RAG Metadata。
    """

    chunks = create_chunks()

    embedder = create_embedder()

    mappings = (
        embedder.embed_documents_with_mapping(
            chunks
        )
    )

    expected_fields = set(
        EXPECTED_METADATA_FIELDS
    )

    for index, mapping in enumerate(
        mappings
    ):

        document = mapping[
            "document"
        ]

        metadata_fields = set(
            document.metadata.keys()
        )

        assert (
            metadata_fields
            == expected_fields
        ), (
            f"Mapping {index} metadata "
            "schema mismatch."
        )

    print(
        "PASS: Mapping metadata preservation"
    )


# ============================================================
# Test Document Identity
# ============================================================

def test_document_identity():
    """
    確認每個 Mapping 的 Document
    與原始 Chunk 一一對應。
    """

    chunks = create_chunks()

    embedder = create_embedder()

    mappings = (
        embedder.embed_documents_with_mapping(
            chunks
        )
    )

    for index, mapping in enumerate(
        mappings
    ):

        assert (
            mapping["document"]
            is chunks[index]
        )

    print(
        "PASS: Document identity preservation"
    )


# ============================================================
# Test Document ID Mapping
# ============================================================

def test_document_id_mapping():
    """
    確認所有 Mapping
    都指向同一個測試 Article。
    """

    chunks = create_chunks()

    embedder = create_embedder()

    mappings = (
        embedder.embed_documents_with_mapping(
            chunks
        )
    )

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
        ), (
            f"Mapping {index} "
            "document_id mismatch."
        )

    print(
        "PASS: Document ID mapping"
    )


# ============================================================
# Test Article Identity Mapping
# ============================================================

def test_article_identity_mapping():
    """
    確認 Mapping 中的 Document
    保留文章 title / url。
    """

    document = create_prepared_document()

    chunks = create_chunks()

    embedder = create_embedder()

    mappings = (
        embedder.embed_documents_with_mapping(
            chunks
        )
    )

    for index, mapping in enumerate(
        mappings
    ):

        mapped_document = mapping[
            "document"
        ]

        assert (
            mapped_document.metadata["title"]
            == document.metadata["title"]
        )

        assert (
            mapped_document.metadata["url"]
            == document.metadata["url"]
        )

    print(
        "PASS: Article identity mapping"
    )


# ============================================================
# Test AI Metadata Mapping
# ============================================================

def test_ai_metadata_mapping():
    """
    確認 AI Metadata
    在 Mapping 中仍然存在。
    """

    chunks = create_chunks()

    embedder = create_embedder()

    mappings = (
        embedder.embed_documents_with_mapping(
            chunks
        )
    )

    ai_fields = (
        "ai_summary",
        "ai_category",
        "ai_keywords",
        "ai_importance",
        "ai_confidence",
    )

    for index, mapping in enumerate(
        mappings
    ):

        document = mapping[
            "document"
        ]

        for field in ai_fields:

            assert (
                field in document.metadata
            ), (
                f"Mapping {index} missing "
                f"AI metadata '{field}'."
            )

    print(
        "PASS: AI metadata mapping"
    )


# ============================================================
# Test Embedding Values
# ============================================================

def test_embedding_values():
    """
    確認 Embedding
    不是全零向量。
    """

    chunks = create_chunks()

    embedder = create_embedder()

    mappings = (
        embedder.embed_documents_with_mapping(
            chunks
        )
    )

    for index, mapping in enumerate(
        mappings
    ):

        embedding = mapping[
            "embedding"
        ]

        assert any(
            value != 0
            for value in embedding
        ), (
            f"Mapping {index} embedding "
            "contains only zero values."
        )

    print(
        "PASS: Embedding values"
    )


# ============================================================
# Test Mapping Validation
# ============================================================

def test_mapping_validation():
    """
    測試 Embedder
    是否可以驗證 Mapping。
    """

    chunks = create_chunks()

    embedder = create_embedder()

    mappings = (
        embedder.embed_documents_with_mapping(
            chunks
        )
    )

    assert (
        embedder.validate_mappings(
            mappings
        )
        is True
    )

    print(
        "PASS: Mapping validation"
    )


# ============================================================
# Test Invalid Mapping
# ============================================================

def test_invalid_mapping():
    """
    測試缺少 document / embedding
    的 Mapping。
    """

    embedder = create_embedder()

    try:

        embedder.validate_mapping(
            {
                "document": Document(
                    page_content="test",
                    metadata={}
                )
            }
        )

    except ValueError:

        print(
            "PASS: Invalid mapping validation"
        )

        return

    raise AssertionError(
        "Invalid mapping should raise ValueError."
    )


# ============================================================
# Test None Mapping
# ============================================================

def test_none_mapping():
    """
    測試 mapping=None。
    """

    embedder = create_embedder()

    try:

        embedder.validate_mapping(
            None
        )

    except ValueError:

        print(
            "PASS: None mapping validation"
        )

        return

    raise AssertionError(
        "None mapping should raise ValueError."
    )


# ============================================================
# Test Invalid Mapping Type
# ============================================================

def test_invalid_mapping_type():
    """
    測試 mapping 不是 dict。
    """

    embedder = create_embedder()

    try:

        embedder.validate_mapping(
            "invalid"
        )

    except TypeError:

        print(
            "PASS: Invalid mapping type validation"
        )

        return

    raise AssertionError(
        "Non-dict mapping should raise TypeError."
    )


# ============================================================
# Test None Mappings
# ============================================================

def test_none_mappings():
    """
    測試 mappings=None。
    """

    embedder = create_embedder()

    try:

        embedder.validate_mappings(
            None
        )

    except ValueError:

        print(
            "PASS: None mappings validation"
        )

        return

    raise AssertionError(
        "None mappings should raise ValueError."
    )


# ============================================================
# Test Empty Mappings
# ============================================================

def test_empty_mappings():
    """
    測試空 mappings list。
    """

    embedder = create_embedder()

    try:

        embedder.validate_mappings(
            []
        )

    except ValueError:

        print(
            "PASS: Empty mappings validation"
        )

        return

    raise AssertionError(
        "Empty mappings should raise ValueError."
    )


# ============================================================
# Test Real Article Mapping
# ============================================================

def test_real_article_mapping():
    """
    使用真實 Article
    完成完整 Embedding Mapping 測試。
    """

    document = create_prepared_document()

    chunks = create_chunks()

    embedder = create_embedder()

    mappings = (
        embedder.embed_documents_with_mapping(
            chunks
        )
    )

    assert (
        len(mappings)
        == len(chunks)
    )

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

    print(
        "PASS: Real Article embedding mapping"
    )

    print(
        f"      Document ID: "
        f"{document.metadata['document_id']}"
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
    執行 RAG-3.4 Embedding Mapping Test。
    """

    print("=" * 60)
    print(
        "RAG-3.4 Embedding Mapping Test"
    )
    print("=" * 60)

    print()

    print(
        "Testing real RAG-2 Chunks..."
    )

    print()

    test_single_mapping()

    test_single_mapping_document()

    test_single_mapping_embedding()

    print()

    test_multiple_mappings()

    test_mapping_structure()

    test_one_to_one_mapping()

    test_embedding_dimensions()

    test_metadata_preservation()

    test_document_identity()

    test_document_id_mapping()

    test_article_identity_mapping()

    test_ai_metadata_mapping()

    test_embedding_values()

    test_mapping_validation()

    test_real_article_mapping()

    print()

    print(
        "Testing mapping validation..."
    )

    print()

    test_invalid_mapping()

    test_none_mapping()

    test_invalid_mapping_type()

    test_none_mappings()

    test_empty_mappings()

    print()

    print("=" * 60)
    print(
        "ALL RAG-3.4 EMBEDDING MAPPING TESTS PASSED"
    )
    print("=" * 60)


if __name__ == "__main__":
    main()