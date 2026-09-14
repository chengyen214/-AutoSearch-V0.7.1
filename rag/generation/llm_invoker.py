"""
rag/generation/llm_invoker.py

AutoSearch V7

RAG-7.4

LLM Invocation

功能：

1. 接收 RAG-7.3 Final Prompt
2. 呼叫既有 LLMClient
3. 取得 LLM Response
4. 驗證 Response 不為空
"""

from ai.llm_client import LLMClient


class LLMInvoker:
    """
    RAG-7.4 LLM Invocation Layer

    負責將 RAG-7.3 產生的 Final Prompt
    交給既有 LLMClient 執行。

    本層不負責：
    - Prompt Construction
    - Context Retrieval
    - LLM Provider 初始化
    - API Key 管理
    """

    def __init__(self, llm_client=None):
        if llm_client is None:
            llm_client = LLMClient()

        self.llm_client = llm_client

    def invoke(self, prompt):
        """
        呼叫 LLM。

        Parameters
        ----------
        prompt : str
            RAG-7.3 PromptBuilder 產生的 Final Prompt。

        Returns
        -------
        str
            LLM Response。
        """

        self._validate_prompt(prompt)

        response = self.llm_client.analyze(prompt)

        self._validate_response(response)

        return response

    @staticmethod
    def _validate_prompt(prompt):
        """
        驗證 Final Prompt。
        """

        if not isinstance(prompt, str):
            raise TypeError("prompt must be a string")

        if not prompt.strip():
            raise ValueError("prompt cannot be empty")

    @staticmethod
    def _validate_response(response):
        """
        驗證 LLM Response。
        """

        if response is None:
            raise ValueError("LLM response cannot be None")

        if not isinstance(response, str):
            raise TypeError("LLM response must be a string")

        if not response.strip():
            raise ValueError("LLM response cannot be empty")


__all__ = [
    "LLMInvoker",
]