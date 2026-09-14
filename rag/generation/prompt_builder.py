"""
rag/generation/prompt_builder.py

AutoSearch V7

RAG-7.2

Prompt Builder

功能：

1. 接收 User Query
2. 接收 RAG-6 Context
3. 組合 System Prompt
4. 組合 Retrieved Context
5. 組合 Answer Instructions
6. 產生 Final Prompt
"""

from rag.generation.prompt_config import (
    SYSTEM_PROMPT,
    USER_QUERY_LABEL,
    RETRIEVED_CONTEXT_LABEL,
    ANSWER_INSTRUCTIONS_LABEL,
    ANSWER_INSTRUCTIONS,
)


class PromptBuilder:
    """
    RAG-7.2 Prompt Builder

    將 User Query 與 RAG-6 Context
    組合成可直接交給 LLMClient 的 Final Prompt。
    """

    def __init__(
        self,
        system_prompt=None,
        answer_instructions=None,
    ):
        self.system_prompt = (
            SYSTEM_PROMPT
            if system_prompt is None
            else system_prompt
        )

        self.answer_instructions = (
            ANSWER_INSTRUCTIONS
            if answer_instructions is None
            else answer_instructions
        )

    def build(self, query, context):
        """
        建立 Final Prompt。

        Parameters
        ----------
        query : str
            使用者問題。

        context : dict
            RAG-6 ContextBuilder.build() 回傳結果。

        Returns
        -------
        str
            Final Prompt。
        """

        self._validate_query(query)
        context_text = self._extract_context(context)

        return self._build_prompt(
            query=query,
            context_text=context_text,
        )

    def _build_prompt(self, query, context_text):
        """
        組合最終 Prompt。
        """

        return (
            f"{self.system_prompt.strip()}\n\n"
            f"{USER_QUERY_LABEL}\n"
            f"{query.strip()}\n\n"
            f"{RETRIEVED_CONTEXT_LABEL}\n"
            f"{context_text}\n\n"
            f"{ANSWER_INSTRUCTIONS_LABEL}\n"
            f"{self.answer_instructions.strip()}"
        )

    @staticmethod
    def _validate_query(query):
        """
        驗證 User Query。
        """

        if not isinstance(query, str):
            raise TypeError("query must be a string")

        if not query.strip():
            raise ValueError("query cannot be empty")

    @staticmethod
    def _extract_context(context):
        """
        從 RAG-6 Context 取得 context_text。
        """

        if not isinstance(context, dict):
            raise TypeError("context must be a dictionary")

        context_text = context.get("context_text")

        if context_text is None:
            raise ValueError(
                "context must contain 'context_text'"
            )

        if not isinstance(context_text, str):
            raise TypeError(
                "context['context_text'] must be a string"
            )

        if not context_text.strip():
            raise ValueError(
                "context['context_text'] cannot be empty"
            )

        return context_text.strip()


__all__ = [
    "PromptBuilder",
]