"""
config/ai_config.py

AutoSearch V4

P2.4.2

AI Configuration

功能:

1. AI Provider 設定
2. AI Model 設定
3. Groq API 設定
4. Async AI Task Batch Threshold

P2.4.2:

當資料庫 WAITING AI Task
累積達到指定數量時，

由 AI Scheduler
觸發 Async AI Processing。

預設:

    50 Tasks
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
# Groq API Key
# ==================================================

GROQ_API_KEY = os.getenv(
    "GROQ_API_KEY",
    ""
)


