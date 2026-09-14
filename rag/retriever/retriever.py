"""
rag/retriever/retriever.py

AutoSearch V7

RAG-5
Retriever Integration

功能：

    提供 RAG-5 的統整使用入口。

完整資料流程：

    User Query
        ↓
    RAG-5.2 Query Embedding
        ↓
    RAG-5.3 ChromaDB Candidate Retrieval
        ↓
    Candidate Results
        ↓
    RAG-5.4 Final Top-K
        ↓
    Final Top-K Results
        ↓
    RAG-5.5 Retrieval Result
        ↓
    List[RetrievalResult]

本階段負責：

    1. 建立 RAG-5 Retriever 元件
    2. 串接 QueryEmbedding
    3. 串接 ChromaDBRetrieval
    4. 串接 TopKRetrieval
    5. 串接 RetrievalResultBuilder
    6. 提供單一 search() 使用入口

本階段不負責：

    - Embedding Model Implementation
    - ChromaDB Query Implementation
    - Candidate Retrieval Logic
    - Top-K Selection Logic
    - RetrievalResult Model Logic
    - Reranking
    - Similarity Threshold
    - Context Builder
    - LLM
"""


# ============================================================
# Imports
# ============================================================

from rag.chroma.client import (
    ChromaDBClient,
)

from rag.chroma.collection import (
    ChromaCollection,
)

from rag.retriever.config import (
    CANDIDATE_K,
    TOP_K,
)

from rag.retriever.query_embedding import (
    QueryEmbedding,
)

from rag.retriever.chroma_retrieval import (
    ChromaDBRetrieval,
)

from rag.retriever.top_k import (
    TopKRetrieval,
)

from rag.retriever.retrieval_result import (
    RetrievalResultBuilder,
)


# ============================================================
# RAG Retriever
# ============================================================

class RAGRetriever:
    """
    RAG-5 統整使用入口。

    將 RAG-5.2～RAG-5.5 串接成單一 Retrieval API。
    """

    # ========================================================
    # Initialize
    # ========================================================

    def __init__(
        self,
        chroma_client=None,
        chroma_collection=None,
        query_embedding=None,
        chroma_retrieval=None,
        top_k_retrieval=None,
        retrieval_result_builder=None,
        candidate_k=None,
        top_k=None,
    ):
        """
        初始化 RAG-5 Retriever。

        Parameters
        ----------
        chroma_client:
            可注入 ChromaDBClient。

        chroma_collection:
            可注入 ChromaCollection。

        query_embedding:
            可注入 QueryEmbedding。

        chroma_retrieval:
            可注入 ChromaDBRetrieval。

        top_k_retrieval:
            可注入 TopKRetrieval。

        retrieval_result_builder:
            可注入 RetrievalResultBuilder。

        candidate_k:
            Candidate Retrieval 數量。

        top_k:
            最終 Retrieval 結果數量。
        """

        # ----------------------------------------------------
        # Configuration
        # ----------------------------------------------------

        if candidate_k is None:
            candidate_k = CANDIDATE_K

        if top_k is None:
            top_k = TOP_K

        # ----------------------------------------------------
        # ChromaDB Client
        # ----------------------------------------------------

        if chroma_client is None:
            chroma_client = (
                ChromaDBClient()
            )

        self.chroma_client = (
            chroma_client
        )

        # ----------------------------------------------------
        # ChromaDB Collection
        # ----------------------------------------------------

        if chroma_collection is None:
            chroma_collection = (
                ChromaCollection(
                    chroma_client=(
                        self.chroma_client
                    )
                )
            )

        self.chroma_collection = (
            chroma_collection
        )

        # ----------------------------------------------------
        # RAG-5.2 Query Embedding
        # ----------------------------------------------------

        if query_embedding is None:
            query_embedding = (
                QueryEmbedding()
            )

        self.query_embedding = (
            query_embedding
        )

        # ----------------------------------------------------
        # RAG-5.3 Candidate Retrieval
        # ----------------------------------------------------

        if chroma_retrieval is None:
            chroma_retrieval = (
                ChromaDBRetrieval(
                    chroma_collection=(
                        self.chroma_collection
                    ),
                    query_embedding=(
                        self.query_embedding
                    ),
                    candidate_k=candidate_k,
                )
            )

        self.chroma_retrieval = (
            chroma_retrieval
        )

        # ----------------------------------------------------
        # RAG-5.4 Final Top-K
        # ----------------------------------------------------

        if top_k_retrieval is None:
            top_k_retrieval = (
                TopKRetrieval(
                    top_k=top_k
                )
            )

        self.top_k_retrieval = (
            top_k_retrieval
        )

        # ----------------------------------------------------
        # RAG-5.5 Retrieval Result
        # ----------------------------------------------------

        if retrieval_result_builder is None:
            retrieval_result_builder = (
                RetrievalResultBuilder()
            )

        self.retrieval_result_builder = (
            retrieval_result_builder
        )

    # ========================================================
    # Search
    # ========================================================

    def search(
        self,
        query,
    ):
        """
        執行完整 RAG-5 Retrieval。

        Flow：

            Query
                ↓
            RAG-5.2
                ↓
            RAG-5.3
                ↓
            RAG-5.4
                ↓
            RAG-5.5
                ↓
            List[RetrievalResult]

        Returns
        -------
        list[RetrievalResult]
        """

        # ----------------------------------------------------
        # Validate Query
        #
        # QueryEmbedding 本身會執行完整 query validation。
        # 這裡直接交由 RAG-5.3 使用既有 QueryEmbedding。
        # ----------------------------------------------------

        candidate_result = (
            self.chroma_retrieval.retrieve(
                query
            )
        )

        final_result = (
            self.top_k_retrieval.select(
                candidate_result
            )
        )

        retrieval_results = (
            self.retrieval_result_builder.build(
                final_result
            )
        )

        return retrieval_results

    # ========================================================
    # Configuration Getters
    # ========================================================

    def get_candidate_k(
        self
    ):
        """
        取得 Candidate-K。
        """

        return (
            self.chroma_retrieval.get_candidate_k()
        )

    def get_top_k(
        self
    ):
        """
        取得 Final Top-K。
        """

        return (
            self.top_k_retrieval.get_top_k()
        )

    # ========================================================
    # Component Getters
    # ========================================================

    def get_query_embedding(
        self
    ):
        """
        取得 QueryEmbedding。
        """

        return self.query_embedding

    def get_chroma_retrieval(
        self
    ):
        """
        取得 ChromaDBRetrieval。
        """

        return self.chroma_retrieval

    def get_top_k_retrieval(
        self
    ):
        """
        取得 TopKRetrieval。
        """

        return self.top_k_retrieval

    def get_retrieval_result_builder(
        self
    ):
        """
        取得 RetrievalResultBuilder。
        """

        return self.retrieval_result_builder


# ============================================================
# Public API
# ============================================================

__all__ = [
    "RAGRetriever",
]