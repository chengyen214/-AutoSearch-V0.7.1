"""
llm_client.py

AutoSearch V7

LLM Provider 管理

支援：

    - mock
    - groq
    - gemini

未來：

    - ollama

RAG-7.1

LLM Configuration
"""


import time

from typing import Union

from groq import Groq
from google import genai

from config.ai_config import (

    LLM_PROVIDER,

    LLM_MODEL,

    LLM_TEMPERATURE,

    LLM_MAX_TOKENS,

    LLM_TIMEOUT,

    GROQ_API_KEY,

    GEMINI_API_KEY,

    GEMINI_MODEL

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

        logger.info(
            f"LLM Model: {LLM_MODEL}"
        )

        logger.info(
            f"LLM Temperature: {LLM_TEMPERATURE}"
        )

        logger.info(
            f"LLM Max Tokens: {LLM_MAX_TOKENS}"
        )

        logger.info(
            f"LLM Timeout: {LLM_TIMEOUT}"
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

        # =========================
        # Gemini Client
        # =========================

        elif self.provider == "gemini":

            if not GEMINI_API_KEY:

                raise ValueError(
                    "GEMINI_API_KEY is missing."
                )

            self.client = genai.Client(
                api_key=GEMINI_API_KEY
            )

            logger.info(
                "Gemini Client initialized."
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

        elif self.provider == "gemini":

            return self._gemini(
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

        MAX_RETRY = 2

        logger.info(
            "===== GROQ REQUEST ====="
        )

        logger.info(
            f"Provider : {self.provider}"
        )

        logger.info(
            f"Model    : {LLM_MODEL}"
        )

        logger.info(
            f"Temperature : {LLM_TEMPERATURE}"
        )

        logger.info(
            f"Max Tokens  : {LLM_MAX_TOKENS}"
        )

        logger.info(
            f"Timeout     : {LLM_TIMEOUT}"
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

                    temperature=LLM_TEMPERATURE,

                    max_tokens=LLM_MAX_TOKENS,

                    timeout=LLM_TIMEOUT

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
    # Gemini Provider
    # ===================================================

    def _gemini(
        self,
        prompt: str
    ) -> str:
        """
        Gemini API 呼叫
        """

        MAX_RETRY = 2

        model = GEMINI_MODEL

        logger.info(
            "===== GEMINI REQUEST ====="
        )

        logger.info(
            f"Provider : {self.provider}"
        )

        logger.info(
            f"Model    : {model}"
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

                response = self.client.models.generate_content(

                    model=model,

                    contents=prompt

                )

                elapsed = time.perf_counter() - start

                logger.info(
                    "===== GEMINI RESPONSE OK ====="
                )

                logger.info(
                    f"Elapsed : {elapsed:.2f} sec"
                )

                return response.text

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
                        "Gemini API failed after maximum retries."
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