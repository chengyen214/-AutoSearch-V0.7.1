"""
rag/chroma/config.py

AutoSearch V7

RAG-4.1

ChromaDB Configuration

功能：

    管理 RAG-4 ChromaDB 設定。

設定項目：

    1. Persist Directory
    2. Collection Name
    3. Distance Metric
    4. Embedding Dimension

Embedding Dimension：

    直接沿用 RAG-3 Embedding Configuration。

    不重新定義 Embedding Dimension。

本檔案不負責：

    1. ChromaDB Client
    2. Collection
    3. Index
    4. MySQL
    5. Embedding
    6. Retriever
"""


from config.rag_config import (
    EMBEDDING_DIMENSION
)


# ============================================================
# ChromaDB Configuration
# ============================================================

import os

from dotenv import load_dotenv


load_dotenv()


# ============================================================
# Persist Directory
# ============================================================

CHROMA_PERSIST_DIRECTORY = os.getenv(
    "CHROMA_PERSIST_DIRECTORY",
    "chroma_db"
).strip()


# ============================================================
# Collection Name
# ============================================================

CHROMA_COLLECTION_NAME = os.getenv(
    "CHROMA_COLLECTION_NAME",
    "autosearch_knowledge"
).strip()


# ============================================================
# Distance Metric
# ============================================================

CHROMA_DISTANCE_METRIC = os.getenv(
    "CHROMA_DISTANCE_METRIC",
    "cosine"
).strip().lower()


# ============================================================
# Supported Distance Metrics
# ============================================================

SUPPORTED_DISTANCE_METRICS = (
    "cosine",
    "l2",
    "ip",
)


# ============================================================
# Validation
# ============================================================

if not CHROMA_PERSIST_DIRECTORY:
    raise ValueError(
        "CHROMA_PERSIST_DIRECTORY cannot be empty."
    )


if not CHROMA_COLLECTION_NAME:
    raise ValueError(
        "CHROMA_COLLECTION_NAME cannot be empty."
    )


if CHROMA_DISTANCE_METRIC not in (
    SUPPORTED_DISTANCE_METRICS
):
    raise ValueError(
        "Unsupported ChromaDB distance metric: "
        f"{CHROMA_DISTANCE_METRIC}. "
        f"Supported metrics: "
        f"{SUPPORTED_DISTANCE_METRICS}"
    )


if EMBEDDING_DIMENSION <= 0:
    raise ValueError(
        "Embedding dimension must be greater than 0."
    )


# ============================================================
# Public API
# ============================================================

__all__ = [
    "CHROMA_PERSIST_DIRECTORY",
    "CHROMA_COLLECTION_NAME",
    "CHROMA_DISTANCE_METRIC",
    "EMBEDDING_DIMENSION",
    "SUPPORTED_DISTANCE_METRICS",
]