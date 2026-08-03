"""
ai_config.py

AutoSearch V3

AI Provider 設定
"""


import os

from dotenv import load_dotenv


load_dotenv()



LLM_PROVIDER = os.getenv(
    "LLM_PROVIDER",
    "mock"
)



LLM_MODEL = os.getenv(
    "LLM_MODEL",
    ""
)



GROQ_API_KEY = os.getenv(
    "GROQ_API_KEY",
    ""
)