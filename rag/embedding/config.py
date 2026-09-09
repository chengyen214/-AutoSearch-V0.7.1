"""
rag/embedding/config.py

AutoSearch V7

RAG-3.1

Embedding Configuration

功能：

    提供 RAG-3 Embedding 所需的正式設定。

資料來源：

    config.rag_config

目前設定：

    Embedding Provider：
        sentence-transformers

    Embedding Model：
        Qwen/Qwen3-Embedding-0.6B

    Embedding Dimension：
        1024

設計原則：

    1. 不重新定義 .env 設定。
    2. 使用既有 config.rag_config。
    3. 避免出現多份 Embedding Configuration。
    4. 本階段只提供 Configuration。
    5. 不載入 Embedding Model。
    6. 不產生 Embedding。
    7. 不使用 ChromaDB。
    8. 不使用 Retriever。
    9. 不使用 LLM。
"""


from config.rag_config import (
    EMBEDDING_PROVIDER,
    EMBEDDING_MODEL,
    EMBEDDING_DIMENSION,
)


# ============================================================
# Supported Provider
# ============================================================

SUPPORTED_EMBEDDING_PROVIDERS = (
    "sentence-transformers",
)


# ============================================================
# Validation
# ============================================================

if (
    EMBEDDING_PROVIDER
    not in SUPPORTED_EMBEDDING_PROVIDERS
):
    raise ValueError(
        "Unsupported embedding provider: "
        f"{EMBEDDING_PROVIDER}"
    )


if not EMBEDDING_MODEL:
    raise ValueError(
        "EMBEDDING_MODEL is not configured."
    )


if EMBEDDING_DIMENSION <= 0:
    raise ValueError(
        "EMBEDDING_DIMENSION must be greater than 0."
    )


# ============================================================
# Export
# ============================================================

__all__ = [
    "EMBEDDING_PROVIDER",
    "EMBEDDING_MODEL",
    "EMBEDDING_DIMENSION",
    "SUPPORTED_EMBEDDING_PROVIDERS",
]