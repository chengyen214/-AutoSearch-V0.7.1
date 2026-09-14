"""
rag/context/metadata.py

AutoSearch V7

RAG-6.3

Metadata Handling

功能：

    將 RAG-5 RetrievalResult 中的 metadata
    標準化成 RAG-6 Context Builder 使用的格式。

資料流程：

    RAG-5 RetrievalResult
            ↓
    RetrievalResult.metadata
            ↓
    MetadataHandler
            ↓
    Standardized Metadata
            ↓
    RAG-6.2 Context Formatting
            ↓
    RAG-6.4 Context Ordering

本檔案負責：

    1. Metadata 欄位定義
    2. Metadata 分類
    3. Metadata 標準化
    4. Missing Metadata 處理

本檔案不負責：

    1. Retrieval
    2. ChromaDB
    3. Embedding
    4. Similarity Calculation
    5. Context Formatting
    6. Context Ordering
    7. LLM
    8. Prompt
"""


# ============================================================
# Metadata Fields
# ============================================================

SOURCE_METADATA_FIELDS = (
    "title",
    "url",
    "source",
    "crawl_time",
)


AI_METADATA_FIELDS = (
    "ai_summary",
    "ai_category",
    "ai_keywords",
    "ai_importance",
    "ai_confidence",
)


# ============================================================
# Metadata Handler
# ============================================================

class MetadataHandler:
    """
    RAG-6.3 Metadata Handler。

    將 RetrievalResult.metadata
    轉換成標準化 Metadata。

    不修改原始 metadata。
    """

    def __init__(
        self,
        source_fields=None,
        ai_fields=None,
    ):
        self.source_fields = (
            tuple(source_fields)
            if source_fields is not None
            else SOURCE_METADATA_FIELDS
        )

        self.ai_fields = (
            tuple(ai_fields)
            if ai_fields is not None
            else AI_METADATA_FIELDS
        )

    # ========================================================
    # Public API
    # ========================================================

    def handle(
        self,
        metadata=None,
    ):
        """
        標準化 Metadata。

        Parameters
        ----------
        metadata:
            RetrievalResult.metadata

        Returns
        -------
        dict
            Standardized Metadata
        """

        if metadata is None:
            metadata = {}

        if not isinstance(
            metadata,
            dict,
        ):
            raise TypeError(
                "metadata must be a dictionary."
            )

        source_metadata = (
            self._extract_fields(
                metadata,
                self.source_fields,
            )
        )

        ai_metadata = (
            self._extract_fields(
                metadata,
                self.ai_fields,
            )
        )

        return {
            "source": source_metadata,
            "ai": ai_metadata,
        }

    # ========================================================
    # Field Extraction
    # ========================================================

    def _extract_fields(
        self,
        metadata,
        fields,
    ):
        """
        擷取指定 Metadata 欄位。

        欄位不存在時使用 None。
        """

        result = {}

        for field in fields:
            result[field] = metadata.get(
                field
            )

        return result

    # ========================================================
    # Source Metadata
    # ========================================================

    def get_source_metadata(
        self,
        metadata=None,
    ):
        """
        取得 Source Metadata。
        """

        handled = self.handle(
            metadata
        )

        return handled["source"]

    # ========================================================
    # AI Metadata
    # ========================================================

    def get_ai_metadata(
        self,
        metadata=None,
    ):
        """
        取得 AI Metadata。
        """

        handled = self.handle(
            metadata
        )

        return handled["ai"]


# ============================================================
# Public API
# ============================================================

__all__ = [
    "SOURCE_METADATA_FIELDS",
    "AI_METADATA_FIELDS",
    "MetadataHandler",
]