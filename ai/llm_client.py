"""
llm_client.py

AutoSearch V3

LLM Provider 管理

支援：

    - mock
    - groq

未來：

    - ollama
"""


import time

from typing import Union

from groq import Groq

from config.ai_config import (

    LLM_PROVIDER,

    LLM_MODEL,

    GROQ_API_KEY

)

from utils.logger import logger


class LLMClient:
    """
    LLM 統一入口
    """

    def __init__(
        self,
        provider=None
    ):
        """
        初始化 LLM Provider
        """

        if provider is None:

            provider = LLM_PROVIDER

        self.provider = provider

        logger.info(
            f"LLM Provider: {self.provider}"
        )

        # =========================
        # Groq Client
        # =========================

        if self.provider == "groq":

            if not GROQ_API_KEY:

                raise ValueError(
                    "GROQ_API_KEY is missing."
                )

            self.client = Groq(
                api_key=GROQ_API_KEY
            )

            logger.info(
                "Groq Client initialized."
            )

    # ===================================================
    # Analyze
    # ===================================================

    def analyze(
        self,
        prompt: str
    ) -> Union[str, dict]:
        """
        執行 LLM 分析
        """

        if self.provider == "mock":

            return self._mock()

        elif self.provider == "groq":

            return self._groq(
                prompt
            )

        elif self.provider == "ollama":

            return self._ollama(
                prompt
            )

        else:

            raise ValueError(
                f"Unsupported provider: {self.provider}"
            )

    # ===================================================
    # Mock Provider
    # ===================================================

    def _mock(
        self
    ) -> dict:
        """
        測試用假 AI
        """

        logger.info(
            "Using Mock Provider."
        )

        return {

            "summary":
                "Mock Summary",

            "category":
                "Unknown",

            "keywords":
                [],

            "importance":
                0

        }

    # ===================================================
    # Groq Provider
    # ===================================================

    def _groq(
        self,
        prompt: str
    ) -> str:
        """
        Groq API 呼叫
        """

        MAX_RETRY = 3

        logger.info(
            "===== GROQ REQUEST ====="
        )

        logger.info(
            f"Provider : {self.provider}"
        )

        logger.info(
            f"Model    : {LLM_MODEL}"
        )

        for attempt in range(
            1,
            MAX_RETRY + 1
        ):

            start = time.perf_counter()

            try:

                logger.info(
                    f"Sending request... ({attempt}/{MAX_RETRY})"
                )

                response = self.client.chat.completions.create(

                    model=LLM_MODEL,

                    messages=[

                        {

                            "role":
                            "system",

                            "content":
                            (
                                "你是一位專業的半導體產業分析師，"
                                "負責分析 IC、半導體、AI Chip、"
                                "先進製程、先進封裝與記憶體技術。"
                            )

                        },

                        {

                            "role":
                            "user",

                            "content":
                            prompt

                        }

                    ],

                    temperature=0.2

                )

                elapsed = time.perf_counter() - start

                logger.info(
                    "===== GROQ RESPONSE OK ====="
                )

                logger.info(
                    f"Elapsed : {elapsed:.2f} sec"
                )

                return (

                    response

                    .choices[0]

                    .message

                    .content

                )

            except Exception as e:

                elapsed = time.perf_counter() - start

                logger.warning(

                    f"Attempt {attempt} failed "

                    f"({elapsed:.2f} sec)"

                )

                logger.warning(
                    str(e)
                )

                if attempt == MAX_RETRY:

                    logger.exception(
                        "Groq API failed after maximum retries."
                    )

                    raise

    # ===================================================
    # Ollama Provider
    # ===================================================

    def _ollama(
        self,
        prompt: str
    ) -> str:
        """
        Ollama 本地模型

        Future
        """

        raise NotImplementedError(

            "Ollama provider is not implemented yet."

        )