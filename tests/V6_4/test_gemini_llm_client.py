"""
test_gemini_llm_client.py

AutoSearch V5

V6.4 Gemini LLMClient 測試

測試內容：

1. Gemini API Key 是否成功載入
2. Gemini Model 是否成功載入
3. LLMClient 是否能初始化 Gemini
4. Gemini API 是否能正常呼叫
5. 是否取得 Gemini response.text

注意：

本測試不修改：

- AIAnalyzer
- AI Worker
- Groq Provider
- 現有 AI Analysis Pipeline
"""

from config.ai_config import (
    GEMINI_API_KEY,
    GEMINI_MODEL
)

from ai.llm_client import LLMClient


def test_gemini_api_key():
    """
    測試 Gemini API Key 是否成功載入
    """

    print("\n===== TEST 1: GEMINI API KEY =====")

    assert GEMINI_API_KEY, (
        "GEMINI_API_KEY is missing."
    )

    print("GEMINI_API_KEY loaded: OK")


def test_gemini_model():
    """
    測試 Gemini Model 是否成功載入
    """

    print("\n===== TEST 2: GEMINI MODEL =====")

    assert GEMINI_MODEL, (
        "GEMINI_MODEL is missing."
    )

    print(
        f"GEMINI_MODEL loaded: {GEMINI_MODEL}"
    )


def test_gemini_client_initialization():
    """
    測試 Gemini LLMClient 是否成功初始化
    """

    print("\n===== TEST 3: GEMINI CLIENT INITIALIZATION =====")

    client = LLMClient(
        provider="gemini"
    )

    assert client.provider == "gemini"
    assert client.client is not None

    print("Gemini Client initialized: OK")


def test_gemini_api_request():
    """
    測試 Gemini API 是否可以正常呼叫
    """

    print("\n===== TEST 4: GEMINI API REQUEST =====")

    client = LLMClient(
        provider="gemini"
    )

    prompt = (
        "請用一句簡短的中文介紹半導體。"
    )

    response = client.analyze(
        prompt
    )

    assert response is not None
    assert isinstance(
        response,
        str
    )
    assert response.strip(), (
        "Gemini returned an empty response."
    )

    print("\nGemini Response:")
    print(response)

    print("\nGemini API request: OK")


if __name__ == "__main__":

    print("=" * 60)
    print("AutoSearch V6.4 Gemini LLMClient Test")
    print("=" * 60)

    test_gemini_api_key()

    test_gemini_model()

    test_gemini_client_initialization()

    test_gemini_api_request()

    print("\n" + "=" * 60)
    print("ALL GEMINI TESTS PASSED")
    print("=" * 60)