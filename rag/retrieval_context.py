"""
rag/retrieval_context.py

AutoSearch V7

RAG-5 → RAG-6 Integration

功能：

    提供 RAG-5 Retrieval 與 RAG-6 Context
    之間的統一整合入口。

資料流程：

    User Query
        ↓
    RAG-5 Retriever
        ↓
    List[RetrievalResult]
        ↓
    RAG-6 ContextBuilder
        ↓
    Context

本檔案負責：

    1. 建立 RAG-5 RAGRetriever
    2. 建立 RAG-6 ContextBuilder
    3. 串接 RAG-5 → RAG-6
    4. 提供單一 retrieval_to_context() 使用入口

本檔案不負責：

    1. Query Embedding
    2. ChromaDB Retrieval
    3. Top-K Selection
    4. RetrievalResult 建立
    5. Context Formatting
    6. Metadata Handling
    7. Context Ordering
    8. Context Validation
    9. LLM
    10. Prompt
"""


# ============================================================
# Imports
# ============================================================

from rag.retriever.retriever import (
    RAGRetriever,
)

from rag.context.context_builder import (
    ContextBuilder,
)


# ============================================================
# Retrieval Context
# ============================================================

class RetrievalContext:
    """
    RAG-5 → RAG-6 整合入口。

    負責將：

        User Query
            ↓
        RAG-5 RetrievalResult
            ↓
        RAG-6 Context

    串接成單一 API。
    """

    # ========================================================
    # Initialize
    # ========================================================

    def __init__(
        self,
        retriever=None,
        context_builder=None,
    ):
        """
        初始化 RAG-5 → RAG-6 整合入口。

        Parameters
        ----------
        retriever:
            可注入 RAGRetriever。

        context_builder:
            可注入 ContextBuilder。
        """

        if retriever is None:
            retriever = RAGRetriever()

        self.retriever = retriever

        if context_builder is None:
            context_builder = ContextBuilder()

        self.context_builder = context_builder

    # ========================================================
    # Query → Context
    # ========================================================

    def build(
        self,
        query,
    ):
        """
        執行完整 RAG-5 → RAG-6 流程。

        Flow：

            Query
                ↓
            RAG-5 Retriever
                ↓
            List[RetrievalResult]
                ↓
            RAG-6 ContextBuilder
                ↓
            Context

        Returns
        -------
        dict
            RAG-6 Context。
        """

        retrieval_results = (
            self.retriever.search(
                query
            )
        )

        context = (
            self.context_builder.build(
                retrieval_results
            )
        )

        return context

    # ========================================================
    # Component Getters
    # ========================================================

    def get_retriever(
        self,
    ):
        """
        取得 RAG-5 Retriever。
        """

        return self.retriever

    def get_context_builder(
        self,
    ):
        """
        取得 RAG-6 ContextBuilder。
        """

        return self.context_builder


# ============================================================
# Public API
# ============================================================

__all__ = [
    "RetrievalContext",
]