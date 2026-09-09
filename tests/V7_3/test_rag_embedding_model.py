"""
tests/V7_3/test_rag_embedding_model.py

AutoSearch V7

RAG-3.2

Embedding Model Test

功能：

    測試 RAG-3.2 EmbeddingModel
    是否可以正常載入 Qwen Embedding Model。

目前模型：

    Provider:
        sentence-transformers

    Model:
        Qwen/Qwen3-Embedding-0.6B

    Dimension:
        1024

測試內容：

    1. EmbeddingModel initialization
    2. Provider validation
    3. Model name validation
    4. Model loading
    5. Model object validation
    6. Configured dimension validation
    7. Actual model dimension validation
    8. Minimal embedding generation
    9. Embedding dimension validation
    10. Invalid model name validation

注意：

    Minimal embedding generation
    只用來確認模型可以正常運作。

    正式 Chunk → Embedding
    屬於 RAG-3.3，
    不在本測試完成。

本測試不負責：

    1. Article Source
    2. Document Preparation
    3. Chunking
    4. ChromaDB
    5. Retriever
    6. Context Builder
    7. LLM
"""


from sentence_transformers import SentenceTransformer

from rag.embedding.config import (
    EMBEDDING_PROVIDER,
    EMBEDDING_MODEL,
    EMBEDDING_DIMENSION,
)

from rag.embedding.model import (
    EmbeddingModel,
)


# ============================================================
# Expected Configuration
# ============================================================

EXPECTED_PROVIDER = (
    "sentence-transformers"
)

EXPECTED_MODEL = (
    "Qwen/Qwen3-Embedding-0.6B"
)

EXPECTED_DIMENSION = 1024


# ============================================================
# Test Initialization
# ============================================================

def test_initialization():
    """
    測試 EmbeddingModel
    是否可以正常初始化。
    """

    embedding_model = EmbeddingModel()

    assert embedding_model is not None

    print(
        "PASS: EmbeddingModel initialization"
    )


# ============================================================
# Test Provider
# ============================================================

def test_provider():
    """
    確認 Embedding Provider。
    """

    assert (
        EMBEDDING_PROVIDER
        == EXPECTED_PROVIDER
    )

    print(
        "PASS: Embedding provider"
    )

    print(
        f"      Provider: "
        f"{EMBEDDING_PROVIDER}"
    )


# ============================================================
# Test Model Name
# ============================================================

def test_model_name():
    """
    確認 Embedding Model 名稱。
    """

    embedding_model = EmbeddingModel()

    assert (
        embedding_model.model_name
        == EXPECTED_MODEL
    )

    print(
        "PASS: Embedding model name"
    )

    print(
        f"      Model: "
        f"{embedding_model.model_name}"
    )


# ============================================================
# Test Model Loading
# ============================================================

def test_model_loading():
    """
    確認 SentenceTransformer
    Model 已成功載入。
    """

    embedding_model = EmbeddingModel()

    model = embedding_model.get_model()

    assert model is not None

    assert isinstance(
        model,
        SentenceTransformer
    )

    print(
        "PASS: Qwen Embedding Model loading"
    )


# ============================================================
# Test Configured Dimension
# ============================================================

def test_configured_dimension():
    """
    確認 Configuration 中的
    Embedding Dimension。
    """

    embedding_model = EmbeddingModel()

    assert (
        embedding_model.get_dimension()
        == EXPECTED_DIMENSION
    )

    assert (
        EMBEDDING_DIMENSION
        == EXPECTED_DIMENSION
    )

    print(
        "PASS: Configured embedding dimension"
    )

    print(
        f"      Dimension: "
        f"{embedding_model.get_dimension()}"
    )


# ============================================================
# Test Actual Model Dimension
# ============================================================

def test_actual_model_dimension():
    """
    確認 Qwen 模型實際輸出維度
    與 Configuration 一致。
    """

    embedding_model = EmbeddingModel()

    model = embedding_model.get_model()

    actual_dimension = model.get_sentence_embedding_dimension()

    assert (
        actual_dimension
        == EMBEDDING_DIMENSION
    ), (
        "Actual model dimension does not "
        "match configured dimension."
    )

    print(
        "PASS: Actual model embedding dimension"
    )

    print(
        f"      Configured: "
        f"{EMBEDDING_DIMENSION}"
    )

    print(
        f"      Actual: "
        f"{actual_dimension}"
    )


# ============================================================
# Test Minimal Embedding Generation
# ============================================================

def test_minimal_embedding_generation():
    """
    最小 Embedding 測試。

    目的：

        確認已載入的 Qwen Model
        可以實際產生向量。

    注意：

        這不是 RAG-3.3 正式流程。
        这里只做模型可用性驗證。
    """

    embedding_model = EmbeddingModel()

    model = embedding_model.get_model()

    texts = [
        "台積電是全球重要的半導體晶圓代工公司。"
    ]

    embeddings = model.encode(
        texts
    )

    assert embeddings is not None

    assert len(
        embeddings
    ) == 1

    assert embeddings.shape[0] == 1

    assert (
        embeddings.shape[1]
        == EMBEDDING_DIMENSION
    )

    print(
        "PASS: Minimal embedding generation"
    )

    print(
        f"      Embedding shape: "
        f"{embeddings.shape}"
    )

    print(
        f"      Embedding dimension: "
        f"{embeddings.shape[1]}"
    )


# ============================================================
# Test Embedding Vector
# ============================================================

def test_embedding_vector():
    """
    確認產生的 Embedding
    具有正確向量長度。
    """

    embedding_model = EmbeddingModel()

    model = embedding_model.get_model()

    embeddings = model.encode(
        [
            "半導體產業與 AI 資料中心需求持續成長。"
        ]
    )

    vector = embeddings[0]

    assert len(
        vector
    ) == EMBEDDING_DIMENSION

    print(
        "PASS: Embedding vector dimension"
    )


# ============================================================
# Test Custom Model Name
# ============================================================

def test_custom_model_name():
    """
    確認 EmbeddingModel
    可以接受明確指定的 Model Name。

    本測試不載入第二個模型，
    只驗證參數處理邏輯。
    """

    embedding_model = EmbeddingModel(
        model_name=EXPECTED_MODEL
    )

    assert (
        embedding_model.model_name
        == EXPECTED_MODEL
    )

    print(
        "PASS: Custom model name handling"
    )


# ============================================================
# Test None Model Name
# ============================================================

def test_none_model_name():
    """
    測試 model_name=None。
    """

    try:

        EmbeddingModel(
            model_name=None
        )

    except ValueError:

        print(
            "PASS: None model name validation"
        )

        return

    raise AssertionError(
        "None model name should raise ValueError."
    )


# ============================================================
# Test Empty Model Name
# ============================================================

def test_empty_model_name():
    """
    測試空 Model Name。
    """

    try:

        EmbeddingModel(
            model_name=""
        )

    except ValueError:

        print(
            "PASS: Empty model name validation"
        )

        return

    raise AssertionError(
        "Empty model name should raise ValueError."
    )


# ============================================================
# Test Invalid Provider
# ============================================================

def test_provider_validation():
    """
    確認目前 Provider 必須為
    sentence-transformers。
    """

    assert (
        EMBEDDING_PROVIDER
        == "sentence-transformers"
    )

    print(
        "PASS: Provider validation"
    )


# ============================================================
# Test Final Model State
# ============================================================

def test_final_model_state():
    """
    確認最終 EmbeddingModel 狀態。
    """

    embedding_model = EmbeddingModel()

    assert (
        embedding_model.model_name
        == EMBEDDING_MODEL
    )

    assert (
        embedding_model.dimension
        == EMBEDDING_DIMENSION
    )

    assert (
        embedding_model.get_model()
        is not None
    )

    print(
        "PASS: Final EmbeddingModel state"
    )


# ============================================================
# Main
# ============================================================

def main():
    """
    執行 RAG-3.2 Embedding Model Test。
    """

    print("=" * 60)
    print(
        "RAG-3.2 Embedding Model Test"
    )
    print("=" * 60)

    print()

    print(
        "Testing Qwen Embedding Model..."
    )

    print()

    test_initialization()

    test_provider()

    test_model_name()

    test_model_loading()

    test_configured_dimension()

    test_actual_model_dimension()

    test_minimal_embedding_generation()

    test_embedding_vector()

    test_custom_model_name()

    test_none_model_name()

    test_empty_model_name()

    test_provider_validation()

    test_final_model_state()

    print()

    print("=" * 60)
    print(
        "ALL RAG-3.2 EMBEDDING MODEL TESTS PASSED"
    )
    print("=" * 60)


if __name__ == "__main__":
    main()