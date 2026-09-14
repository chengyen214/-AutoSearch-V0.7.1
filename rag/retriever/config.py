"""
rag/retriever/config.py

AutoSearch V7

RAG-5 Retriever Configuration
"""


# ============================================================
# ChromaDB Candidate Retrieval
# ============================================================

CANDIDATE_K = 20


# ============================================================
# Final Top-K Retrieval
# ============================================================

TOP_K = 5


# ============================================================
# Similarity Threshold
# ============================================================
#
# None:
#     本階段不啟用 Similarity Threshold。
#
# 後續 RAG-5.x 再處理。
#

SIMILARITY_THRESHOLD = None


# ============================================================
# Distance Metric
# ============================================================

DISTANCE_METRIC = "cosine"


# ============================================================
# Embedding Dimension
# ============================================================

EMBEDDING_DIMENSION = 768


# ============================================================
# Validation
# ============================================================

def _validate_positive_integer(
    value,
    name,
):
    """
    驗證正整數設定。
    """

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
    CANDIDATE_K,
    "CANDIDATE_K",
)

_validate_positive_integer(
    TOP_K,
    "TOP_K",
)

_validate_positive_integer(
    EMBEDDING_DIMENSION,
    "EMBEDDING_DIMENSION",
)


if CANDIDATE_K < TOP_K:
    raise ValueError(
        "CANDIDATE_K must be greater than "
        "or equal to TOP_K."
    )


__all__ = [
    "CANDIDATE_K",
    "TOP_K",
    "SIMILARITY_THRESHOLD",
    "DISTANCE_METRIC",
    "EMBEDDING_DIMENSION",
]