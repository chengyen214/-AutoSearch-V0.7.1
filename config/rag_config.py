"""
config/rag_config.py

AutoSearch V7

RAG-0.3
Embedding Configuration

功能：
    1. 載入 RAG Embedding Provider
    2. 載入 RAG Embedding Model
    3. 載入 RAG Embedding Dimension

資料來源：
    .env

目前設定：
    EMBEDDING_PROVIDER=sentence-transformers
    EMBEDDING_MODEL=Qwen/Qwen3-Embedding-0.6B
    EMBEDDING_DIMENSION=1024
"""

import os

from dotenv import load_dotenv


# ==================================================
# Load Environment
# ==================================================

load_dotenv()


# ==================================================
# Embedding Configuration
# ==================================================

EMBEDDING_PROVIDER = os.getenv(
    "EMBEDDING_PROVIDER",
    "sentence-transformers"
).strip()


EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "Qwen/Qwen3-Embedding-0.6B"
).strip()


EMBEDDING_DIMENSION = int(
    os.getenv(
        "EMBEDDING_DIMENSION",
        "1024"
    )
)


# ==================================================
# Validation
# ==================================================

if not EMBEDDING_PROVIDER:
    raise ValueError(
        "EMBEDDING_PROVIDER is not configured."
    )


if not EMBEDDING_MODEL:
    raise ValueError(
        "EMBEDDING_MODEL is not configured."
    )


if EMBEDDING_DIMENSION <= 0:
    raise ValueError(
        "EMBEDDING_DIMENSION must be greater than 0."
    )


# ==================================================
# Public API
# ==================================================

__all__ = [
    "EMBEDDING_PROVIDER",
    "EMBEDDING_MODEL",
    "EMBEDDING_DIMENSION",
]