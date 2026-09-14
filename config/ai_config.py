"""
config/ai_config.py

AutoSearch V7

RAG-7.1

LLM Configuration

功能:

1. AI / LLM Provider 設定
2. LLM Model 設定
3. LLM Temperature 設定
4. LLM Max Tokens 設定
5. LLM Timeout 設定
6. Groq API 設定
7. Gemini API 設定

注意:

本設定檔沿用 AutoSearch 既有 LLM Configuration，
RAG-7 不建立第二套 LLM 設定系統。
"""


import os

from dotenv import load_dotenv


# ==================================================
# Environment
# ==================================================

load_dotenv()


# ==================================================
# LLM Provider
# ==================================================

LLM_PROVIDER = os.getenv(
    "LLM_PROVIDER",
    "mock"
)


# ==================================================
# LLM Model
# ==================================================

LLM_MODEL = os.getenv(
    "LLM_MODEL",
    ""
)


# ==================================================
# LLM Temperature
# ==================================================

LLM_TEMPERATURE = float(
    os.getenv(
        "LLM_TEMPERATURE",
        "0.2"
    )
)


# ==================================================
# LLM Max Tokens
# ==================================================

LLM_MAX_TOKENS = int(
    os.getenv(
        "LLM_MAX_TOKENS",
        "4096"
    )
)


# ==================================================
# LLM Timeout
# ==================================================

LLM_TIMEOUT = int(
    os.getenv(
        "LLM_TIMEOUT",
        "60"
    )
)


# ==================================================
# Gemini Model
# ==================================================

GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    ""
)


# ==================================================
# Groq API Key
# ==================================================

GROQ_API_KEY = os.getenv(
    "GROQ_API_KEY",
    ""
)


# ==================================================
# Gemini API Key
# ==================================================

GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY",
    ""
)