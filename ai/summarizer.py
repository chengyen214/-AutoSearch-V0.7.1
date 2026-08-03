"""
summarizer.py

AutoSearch V3

文章摘要模組

功能：
    1. 接收文章內容
    2. 回傳文章摘要

目前：
    Mock Version

未來：
    OpenAI
    Gemini
    Ollama
    LangChain
"""


class Summarizer:
    """
    文章摘要器
    """

    def summarize(self, text: str) -> str:
        """
        產生文章摘要

        Parameters
        ----------
        text : str
            原始文章內容

        Returns
        -------
        str
            摘要結果
        """

        if not text:
            return ""

        # Mock：先取前 100 個字
        summary = text.strip()

        if len(summary) > 100:
            summary = summary[:100] + "..."

        return summary