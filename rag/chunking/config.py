"""
rag/chunking/config.py

AutoSearch V7

RAG-2.1

Chunking Configuration

功能：

    定義 RAG Chunking 的正式設定。

目前設定：

    Splitter:
        RecursiveCharacterTextSplitter

    Chunk Size:
        1000

    Chunk Overlap:
        200

設定原則：

    1. RAG-2 只負責 Chunking。
    2. 本階段只建立 Configuration。
    3. 不執行 Chunking。
    4. 不執行 Embedding。
    5. 不使用 ChromaDB。
    6. 不使用 Retriever。
    7. 不使用 LLM。
"""


import os

from dotenv import load_dotenv


# ============================================================
# Load Environment
# ============================================================

load_dotenv()


# ============================================================
# Chunking Configuration
# ============================================================

CHUNK_SPLITTER = os.getenv(
    "CHUNK_SPLITTER",
    "recursive"
).strip()

CHUNK_SIZE = int(
    os.getenv(
        "CHUNK_SIZE",
        "1000"
    )
)

CHUNK_OVERLAP = int(
    os.getenv(
        "CHUNK_OVERLAP",
        "200"
    )
)


# ============================================================
# Validation
# ============================================================

if not CHUNK_SPLITTER:
    raise ValueError(
        "CHUNK_SPLITTER is not configured."
    )

if CHUNK_SIZE <= 0:
    raise ValueError(
        "CHUNK_SIZE must be greater than 0."
    )

if CHUNK_OVERLAP < 0:
    raise ValueError(
        "CHUNK_OVERLAP cannot be negative."
    )

if CHUNK_OVERLAP >= CHUNK_SIZE:
    raise ValueError(
        "CHUNK_OVERLAP must be smaller than CHUNK_SIZE."
    )


# ============================================================
# Export
# ============================================================

__all__ = [
    "CHUNK_SPLITTER",
    "CHUNK_SIZE",
    "CHUNK_OVERLAP",
]