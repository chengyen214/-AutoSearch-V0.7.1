"""
rag/context/ordering.py

AutoSearch V7

RAG-6.4

Context Ordering

功能：

    管理 RAG-6 Context 的最終排列順序。

設計原則：

    RAG-5 Retriever 已經完成相關性排序。

    RAG-6.4 不重新計算：
        1. distance
        2. similarity
        3. embedding
        4. retrieval score

    預設直接保留 RAG-5 RetrievalResult 的順序。

資料流程：

    RAG-5 Retriever
            ↓
    RetrievalResult
            ↓
    Context Ordering
            ↓
    RAG-6.5 Context Validation
"""


from rag.retriever.retrieval_result import (
    RetrievalResult
)

from rag.context.config import (
    PRESERVE_RETRIEVAL_ORDER,
)


class ContextOrdering:
    """
    RAG-6.4 Context Ordering

    負責決定 Context 中 RetrievalResult
    的最終排列順序。
    """

    def __init__(
        self,
        preserve_retrieval_order=None,
    ):
        self.preserve_retrieval_order = (
            preserve_retrieval_order
            if preserve_retrieval_order is not None
            else PRESERVE_RETRIEVAL_ORDER
        )

        if not isinstance(
            self.preserve_retrieval_order,
            bool,
        ):
            raise TypeError(
                "preserve_retrieval_order must be a boolean."
            )

    def order(
        self,
        retrieval_results,
    ):
        """
        排列 RetrievalResult。

        預設：

            保留 RAG-5 RetrievalResult 原始順序。

        回傳：

            新的 list，不修改原始 list。
        """

        if retrieval_results is None:
            raise ValueError(
                "retrieval_results cannot be None."
            )

        if not isinstance(
            retrieval_results,
            (list, tuple),
        ):
            raise TypeError(
                "retrieval_results must be a list or tuple."
            )

        for result in retrieval_results:
            if not isinstance(
                result,
                RetrievalResult,
            ):
                raise TypeError(
                    "Each retrieval result must be "
                    "a RetrievalResult."
                )

        ordered_results = list(
            retrieval_results
        )

        if self.preserve_retrieval_order:
            return ordered_results

        return ordered_results


__all__ = [
    "ContextOrdering",
]