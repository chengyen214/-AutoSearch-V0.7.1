"""
tests/V7_6/test_llm_client_groq.py

AutoSearch V7

RAG-7.1
Groq Functional Test

測試：

1. LLM Configuration 是否正確載入
2. LLMClient 是否成功初始化
3. Groq API 是否可以正常呼叫
4. LLM Model 是否正常回應
5. RAG-7.1 Temperature / Max Tokens / Timeout 是否被載入
"""

from config.ai_config import (
    LLM_PROVIDER,
    LLM_MODEL,
    LLM_TEMPERATURE,
    LLM_MAX_TOKENS,
    LLM_TIMEOUT,
)

from ai.llm_client import LLMClient


def main():

    print("=" * 60)
    print("RAG-7.1 GROQ FUNCTIONAL TEST")
    print("=" * 60)

    print()
    print("[1] LLM Configuration")
    print(f"Provider    : {LLM_PROVIDER}")
    print(f"Model       : {LLM_MODEL}")
    print(f"Temperature : {LLM_TEMPERATURE}")
    print(f"Max Tokens  : {LLM_MAX_TOKENS}")
    print(f"Timeout     : {LLM_TIMEOUT}")

    if LLM_PROVIDER != "groq":
        raise AssertionError(
            f"Expected provider 'groq', got '{LLM_PROVIDER}'"
        )

    if not LLM_MODEL:
        raise AssertionError(
            "LLM_MODEL is empty."
        )

    if LLM_TEMPERATURE < 0:
        raise AssertionError(
            "LLM_TEMPERATURE must be >= 0."
        )

    if LLM_MAX_TOKENS <= 0:
        raise AssertionError(
            "LLM_MAX_TOKENS must be > 0."
        )

    if LLM_TIMEOUT <= 0:
        raise AssertionError(
            "LLM_TIMEOUT must be > 0."
        )

    print("[PASS] Configuration loaded")

    print()
    print("[2] Initialize LLMClient")

    client = LLMClient()

    if client.provider != "groq":
        raise AssertionError(
            f"Expected LLMClient provider 'groq', "
            f"got '{client.provider}'"
        )

    print("[PASS] LLMClient initialized")

    print()
    print("[3] Send real Groq request")

    prompt = (
        "請用繁體中文回答："
        "什麼是半導體？"
        "請用一句話簡短回答。"
    )

    response = client.analyze(prompt)

    if not isinstance(response, str):
        raise AssertionError(
            f"Expected string response, got {type(response)}"
        )

    response = response.strip()

    if not response:
        raise AssertionError(
            "Groq returned an empty response."
        )

    print("[PASS] Groq API request succeeded")

    print()
    print("[4] LLM Response")
    print("-" * 60)
    print(response)
    print("-" * 60)

    print()
    print("[5] RAG-7.1 Functional Validation")

    print("[PASS] Provider       =", LLM_PROVIDER)
    print("[PASS] Model          =", LLM_MODEL)
    print("[PASS] Temperature    =", LLM_TEMPERATURE)
    print("[PASS] Max Tokens     =", LLM_MAX_TOKENS)
    print("[PASS] Timeout        =", LLM_TIMEOUT)
    print("[PASS] Non-empty Answer")

    print()
    print("=" * 60)
    print("RAG-7.1 GROQ FUNCTIONAL TEST PASSED")
    print("=" * 60)


if __name__ == "__main__":
    main()