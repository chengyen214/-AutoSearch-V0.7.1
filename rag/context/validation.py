"""
rag/context/validation.py

AutoSearch V7

RAG-6.5

Context Validation

功能：

    驗證 RAG-6 Context 是否符合標準格式，
    確保後續 RAG-7 LLM Generation 可以安全使用。

資料流程：

    RAG-6.2 Context Formatting
            ↓
    RAG-6.3 Metadata Handling
            ↓
    RAG-6.4 Context Ordering
            ↓
    RAG-6.5 Context Validation
            ↓
    RAG-7 LLM Generation

本檔案負責：

    1. Context 結構驗證
    2. Context Entry 驗證
    3. Context Count 驗證
    4. Source Index 驗證
    5. Context 長度驗證

本檔案不負責：

    1. Retrieval
    2. ChromaDB
    3. Embedding
    4. Similarity Calculation
    5. Context Formatting
    6. Metadata Processing
    7. LLM
    8. Prompt
"""


from rag.context.config import (
    MAX_CONTEXT_CHARACTERS,
)


# ============================================================
# Context Entry Fields
# ============================================================

REQUIRED_ENTRY_FIELDS = (
    "source_index",
    "document_id",
    "chunk_index",
    "title",
    "url",
    "content",
)


# ============================================================
# Context Validator
# ============================================================

class ContextValidator:
    """
    RAG-6.5 Context Validator

    驗證 Context 是否符合 RAG-6 標準格式。
    """

    def __init__(
        self,
        max_context_characters=None,
    ):
        self.max_context_characters = (
            max_context_characters
            if max_context_characters is not None
            else MAX_CONTEXT_CHARACTERS
        )

        if not isinstance(
            self.max_context_characters,
            int,
        ):
            raise TypeError(
                "max_context_characters must be an integer."
            )

        if self.max_context_characters <= 0:
            raise ValueError(
                "max_context_characters must be greater than 0."
            )

    # ========================================================
    # Public API
    # ========================================================

    def validate(
        self,
        context,
    ):
        """
        驗證完整 Context。

        成功：

            回傳 True

        失敗：

            Raise ValueError / TypeError
        """

        self._validate_context_type(
            context
        )

        entries = context["entries"]
        context_text = context["context_text"]
        count = context["count"]

        self._validate_entries(
            entries
        )

        self._validate_count(
            count,
            entries,
        )

        self._validate_context_text(
            context_text
        )

        return True

    # ========================================================
    # Context Validation
    # ========================================================

    def _validate_context_type(
        self,
        context,
    ):
        if not isinstance(
            context,
            dict,
        ):
            raise TypeError(
                "context must be a dictionary."
            )

        required_fields = (
            "entries",
            "context_text",
            "count",
        )

        for field in required_fields:
            if field not in context:
                raise ValueError(
                    f"Context is missing required field: {field}"
                )

    # ========================================================
    # Entry Validation
    # ========================================================

    def _validate_entries(
        self,
        entries,
    ):
        if not isinstance(
            entries,
            list,
        ):
            raise TypeError(
                "context['entries'] must be a list."
            )

        for position, entry in enumerate(
            entries,
            start=1,
        ):
            if not isinstance(
                entry,
                dict,
            ):
                raise TypeError(
                    "Each context entry must be a dictionary."
                )

            for field in REQUIRED_ENTRY_FIELDS:
                if field not in entry:
                    raise ValueError(
                        "Context entry is missing "
                        f"required field: {field}"
                    )

            if entry["source_index"] != position:
                raise ValueError(
                    "Context source_index must be "
                    "sequential starting from 1."
                )

            if not isinstance(
                entry["content"],
                str,
            ):
                raise TypeError(
                    "Context entry content must be a string."
                )

    # ========================================================
    # Count Validation
    # ========================================================

    def _validate_count(
        self,
        count,
        entries,
    ):
        if not isinstance(
            count,
            int,
        ):
            raise TypeError(
                "context['count'] must be an integer."
            )

        if count < 0:
            raise ValueError(
                "context['count'] cannot be negative."
            )

        if count != len(entries):
            raise ValueError(
                "context['count'] must equal "
                "the number of context entries."
            )

    # ========================================================
    # Context Text Validation
    # ========================================================

    def _validate_context_text(
        self,
        context_text,
    ):
        if not isinstance(
            context_text,
            str,
        ):
            raise TypeError(
                "context['context_text'] must be a string."
            )

        if len(context_text) > (
            self.max_context_characters
        ):
            raise ValueError(
                "context_text exceeds "
                "MAX_CONTEXT_CHARACTERS."
            )


__all__ = [
    "ContextValidator",
]