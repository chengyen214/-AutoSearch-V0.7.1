"""
tests/V7_5/test_embeddinggemma_download.py

AutoSearch V7

EmbeddingGemma Model Download / Load Test

目的：

    確認：

        taide/embeddinggemma-GTAIDE-300m-2605

    可以在目前 Python 環境：

        1. 成功下載
        2. 成功載入
        3. 取得 Embedding Dimension
        4. 執行文字 Embedding
        5. 回傳有效向量

本測試：

    - 不修改現有 RAG-3
    - 不修改現有 EmbeddingModel
    - 不修改 ChromaDB
    - 不修改 RAG-5

預期：

    Model:
        taide/embeddinggemma-GTAIDE-300m-2605

    Dimension:
        768
"""


# ============================================================
# Imports
# ============================================================

import math

from sentence_transformers import (
    SentenceTransformer,
)


# ============================================================
# Test Constants
# ============================================================

MODEL_NAME = (
    "taide/embeddinggemma-GTAIDE-300m-2605"
)

EXPECTED_DIMENSION = 768

TEST_TEXT = (
    "台灣半導體產業未來發展趨勢"
)


# ============================================================
# Main Test
# ============================================================

def main():

    print(
        "=" * 60
    )

    print(
        "EmbeddingGemma Model Download / Load Test"
    )

    print(
        "=" * 60
    )

    print()

    print(
        f"Model: {MODEL_NAME}"
    )

    print(
        f"Expected Dimension: {EXPECTED_DIMENSION}"
    )

    print()

    # ========================================================
    # Model Download / Load
    # ========================================================

    print(
        "Loading / downloading model..."
    )

    model = SentenceTransformer(
        MODEL_NAME
    )

    assert (
        model is not None
    )

    print(
        "PASS: Model download / load"
    )

    # ========================================================
    # Model Dimension
    # ========================================================

    dimension = (
        model.get_sentence_embedding_dimension()
    )

    assert (
        dimension == EXPECTED_DIMENSION
    )

    print(
        "PASS: Embedding dimension"
    )

    print(
        f"      Dimension: {dimension}"
    )

    # ========================================================
    # Test Encoding
    # ========================================================

    embedding = (
        model.encode(
            TEST_TEXT
        )
    )

    assert (
        embedding is not None
    )

    print(
        "PASS: Test embedding generation"
    )

    # ========================================================
    # Embedding Dimension
    # ========================================================

    assert (
        len(embedding)
        == EXPECTED_DIMENSION
    )

    print(
        "PASS: Test embedding dimension validation"
    )

    # ========================================================
    # Embedding Values
    # ========================================================

    for value in embedding:

        assert math.isfinite(
            float(value)
        )

    print(
        "PASS: Embedding values validation"
    )

    # ========================================================
    # Embedding Type
    # ========================================================

    assert (
        hasattr(
            embedding,
            "tolist"
        )
        or isinstance(
            embedding,
            list
        )
    )

    print(
        "PASS: Embedding result type"
    )

    # ========================================================
    # Multiple Text Encoding
    # ========================================================

    texts = [
        "台灣半導體產業",
        "先進製程與先進封裝",
        "人工智慧與高效運算",
    ]

    embeddings = (
        model.encode(
            texts
        )
    )

    assert (
        embeddings is not None
    )

    print(
        "PASS: Multiple text embedding generation"
    )

    assert (
        len(embeddings)
        == len(texts)
    )

    print(
        "PASS: Multiple embedding count"
    )

    for vector in embeddings:

        assert (
            len(vector)
            == EXPECTED_DIMENSION
        )

        for value in vector:

            assert math.isfinite(
                float(value)
            )

    print(
        "PASS: Multiple embedding dimension / value validation"
    )

    # ========================================================
    # Final
    # ========================================================

    print()

    print(
        "=" * 60
    )

    print(
        "EMBEDDINGGEMMA MODEL DOWNLOAD / "
        "LOAD TEST PASSED"
    )

    print(
        "=" * 60
    )


# ============================================================
# Entry Point
# ============================================================

if __name__ == "__main__":
    main()