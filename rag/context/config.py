"""
rag/context/config.py

AutoSearch V7

RAG-6.1

Context Builder Configuration

功能：

    管理 RAG-6 Context Builder 的設定。

設定項目：

    1. Context 最大 Chunk 數
    2. Context 最大內容長度
    3. Context Format
    4. Context Ordering Rule

資料流程：

    RAG-5 Retriever
            ↓
    RetrievalResult
            ↓
    RAG-6 Context Configuration
            ↓
    RAG-6.2 Context Formatting

本檔案負責：

    1. 定義 Context Builder 設定
    2. 驗證 Context Builder 設定

本檔案不負責：

    1. Retrieval
    2. ChromaDB
    3. Embedding
    4. Context Formatting
    5. Metadata Processing
    6. LLM
    7. Prompt
"""


from rag.retriever.config import TOP_K


# ============================================================
# Context Chunk Configuration
# ============================================================

# Context 預設使用 RAG-5 最終 Top-K 結果。
#
# 不重新定義一個不同的 Top-K。
#
# RAG-5 TOP_K
#     ↓
# RAG-6 MAX_CONTEXT_CHUNKS

MAX_CONTEXT_CHUNKS = TOP_K


# ============================================================
# Context Length Configuration
# ============================================================

# Context 最大字元數。
#
# 本階段使用 character length 作為 deterministic
# context validation 的基準。
#
# 後續若需要 Token-based Context Management，
# 再於後續階段擴充。

MAX_CONTEXT_CHARACTERS = 20000


# ============================================================
# Context Format Configuration
# ============================================================

# 每個 Context Source 之間的分隔方式。

SOURCE_SEPARATOR = "\n\n"


# ============================================================
# Context Ordering Configuration
# ============================================================

# Context 維持 RAG-5 RetrievalResult 原始順序。
#
# RAG-5 已完成 relevance ordering。
# RAG-6 不重新計算 similarity。

PRESERVE_RETRIEVAL_ORDER = True


# ============================================================
# Validation
# ============================================================

def _validate_positive_integer(
    value,
    name,
):
    if not isinstance(
        value,
        int,
    ):
        raise TypeError(
            f"{name} must be an integer."
        )

    if value <= 0:
        raise ValueError(
            f"{name} must be greater than 0."
        )


_validate_positive_integer(
    MAX_CONTEXT_CHUNKS,
    "MAX_CONTEXT_CHUNKS",
)

_validate_positive_integer(
    MAX_CONTEXT_CHARACTERS,
    "MAX_CONTEXT_CHARACTERS",
)


if not isinstance(
    SOURCE_SEPARATOR,
    str,
):
    raise TypeError(
        "SOURCE_SEPARATOR must be a string."
    )


if not isinstance(
    PRESERVE_RETRIEVAL_ORDER,
    bool,
):
    raise TypeError(
        "PRESERVE_RETRIEVAL_ORDER must be a boolean."
    )


if MAX_CONTEXT_CHUNKS > TOP_K:
    raise ValueError(
        "MAX_CONTEXT_CHUNKS cannot be greater "
        "than RAG-5 TOP_K."
    )


# ============================================================
# Public API
# ============================================================

__all__ = [
    "MAX_CONTEXT_CHUNKS",
    "MAX_CONTEXT_CHARACTERS",
    "SOURCE_SEPARATOR",
    "PRESERVE_RETRIEVAL_ORDER",
]