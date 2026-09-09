"""
tests/V7/test_rag_environment.py

AutoSearch V7

RAG-0.4
RAG Minimal Environment Test

測試內容：
    1. LangChain 是否可以正常 import
    2. ChromaDB 是否可以正常 import / 初始化
    3. Sentence Transformers 是否可以正常 import
    4. RAG Configuration 是否可以正常載入
    5. Qwen Embedding Model 是否可以正常載入
    6. Qwen Embedding 是否可以正常產生向量

目的：
    確認目前 RAG Foundation 所需的最小環境
    可以在同一個 Python Environment 中正常運作。

注意：
    本測試不建立正式 RAG Pipeline。
    本測試不建立正式 ChromaDB Vector Store。
    本測試不修改 AutoSearch 現有資料流程。
"""


# ==================================================
# LangChain
# ==================================================

def test_langchain():
    import langchain

    assert langchain is not None

    print("PASS: LangChain import")


# ==================================================
# ChromaDB
# ==================================================

def test_chromadb():
    import chromadb

    assert chromadb is not None

    client = chromadb.Client()

    assert client is not None

    print("PASS: ChromaDB import")
    print("PASS: ChromaDB initialization")


# ==================================================
# Sentence Transformers
# ==================================================

def test_sentence_transformers():
    from sentence_transformers import SentenceTransformer

    assert SentenceTransformer is not None

    print("PASS: Sentence Transformers import")


# ==================================================
# RAG Configuration
# ==================================================

def test_rag_config():
    from config.rag_config import (
        EMBEDDING_PROVIDER,
        EMBEDDING_MODEL,
        EMBEDDING_DIMENSION,
    )

    assert EMBEDDING_PROVIDER == "sentence-transformers"

    assert EMBEDDING_MODEL == (
        "Qwen/Qwen3-Embedding-0.6B"
    )

    assert EMBEDDING_DIMENSION == 1024

    print("PASS: RAG Configuration")
    print(
        f"      Provider : {EMBEDDING_PROVIDER}"
    )
    print(
        f"      Model    : {EMBEDDING_MODEL}"
    )
    print(
        f"      Dimension: {EMBEDDING_DIMENSION}"
    )


# ==================================================
# Qwen Embedding Model
# ==================================================

def test_qwen_embedding():
    from sentence_transformers import SentenceTransformer

    from config.rag_config import (
        EMBEDDING_MODEL,
        EMBEDDING_DIMENSION,
    )

    print()
    print("Loading Qwen Embedding Model...")

    model = SentenceTransformer(
        EMBEDDING_MODEL
    )

    assert model is not None

    print("PASS: Qwen Embedding Model loading")

    text = [
        "台積電是全球重要的半導體晶圓代工公司。"
    ]

    embeddings = model.encode(text)

    assert embeddings is not None

    assert len(embeddings) == 1

    assert embeddings.shape[1] == EMBEDDING_DIMENSION

    print("PASS: Qwen Embedding generation")
    print(
        f"      Embedding Shape: {embeddings.shape}"
    )
    print(
        f"      Embedding Dimension: "
        f"{embeddings.shape[1]}"
    )


# ==================================================
# Main
# ==================================================

def main():
    print("=" * 60)
    print("RAG-0.4 Minimal Environment Test")
    print("=" * 60)

    print()

    test_langchain()

    test_chromadb()

    test_sentence_transformers()

    test_rag_config()

    test_qwen_embedding()

    print()
    print("=" * 60)
    print("ALL RAG ENVIRONMENT TESTS PASSED")
    print("=" * 60)


if __name__ == "__main__":
    main()