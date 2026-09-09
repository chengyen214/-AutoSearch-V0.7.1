"""
tests/V7/test_rag_config.py

AutoSearch V7

RAG-0.3
Embedding Configuration Test

測試內容：
    1. EMBEDDING_PROVIDER 是否正確載入
    2. EMBEDDING_MODEL 是否正確載入
    3. EMBEDDING_DIMENSION 是否正確載入
    4. Configuration 是否符合目前 RAG-0.2 的設定

注意：
    本測試不會載入 Qwen 模型。
    本測試不會使用 LangChain。
    本測試不會使用 ChromaDB。
"""

from config.rag_config import (
    EMBEDDING_PROVIDER,
    EMBEDDING_MODEL,
    EMBEDDING_DIMENSION,
)


def test_embedding_provider():
    assert EMBEDDING_PROVIDER == "sentence-transformers"


def test_embedding_model():
    assert EMBEDDING_MODEL == "Qwen/Qwen3-Embedding-0.6B"


def test_embedding_dimension():
    assert EMBEDDING_DIMENSION == 1024


def main():
    print("=" * 60)
    print("RAG-0.3 RAG Configuration Test")
    print("=" * 60)

    print()
    print(f"Embedding Provider : {EMBEDDING_PROVIDER}")
    print(f"Embedding Model    : {EMBEDDING_MODEL}")
    print(f"Embedding Dimension: {EMBEDDING_DIMENSION}")

    print()

    test_embedding_provider()
    print("PASS: EMBEDDING_PROVIDER")

    test_embedding_model()
    print("PASS: EMBEDDING_MODEL")

    test_embedding_dimension()
    print("PASS: EMBEDDING_DIMENSION")

    print()
    print("=" * 60)
    print("ALL RAG CONFIG TESTS PASSED")
    print("=" * 60)


if __name__ == "__main__":
    main()