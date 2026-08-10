"""
tests/test_ai_config.py

AutoSearch V4

AI Configuration Test
"""

from config.ai_config import (
    LLM_PROVIDER,
    LLM_MODEL,
)


def test_ai_config():
    assert LLM_PROVIDER is not None
    assert LLM_MODEL is not None

    print("Provider:", LLM_PROVIDER)
    print("Model:", LLM_MODEL)