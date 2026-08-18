"""
utils/test_groq.py

AutoSearch V4

用途：
    測試 Groq API 是否可以正常使用。

測試項目：
    1. 讀取 .env
    2. 讀取 LLM_PROVIDER
    3. 讀取 LLM_MODEL
    4. 讀取 GROQ_API_KEY
    5. 呼叫 Groq Chat Completion
    6. 顯示模型回應

執行：

    python -m utils.test_groq
"""

import os

from dotenv import load_dotenv
from groq import Groq


# ==================================================
# Load Environment
# ==================================================

load_dotenv()


# ==================================================
# Configuration
# ==================================================

LLM_PROVIDER = os.getenv(
    "LLM_PROVIDER",
    ""
)

LLM_MODEL = os.getenv(
    "LLM_MODEL",
    ""
)

GROQ_API_KEY = os.getenv(
    "GROQ_API_KEY",
    ""
)


# ==================================================
# Test
# ==================================================

def main():

    print("=" * 70)
    print("AutoSearch V4 - Groq API Test")
    print("=" * 70)

    print()
    print(f"Provider : {LLM_PROVIDER}")
    print(f"Model    : {LLM_MODEL}")
    print(
        f"API Key  : "
        f"{'Loaded' if GROQ_API_KEY else 'MISSING'}"
    )
    print()

    # ------------------------------------------------
    # Configuration Check
    # ------------------------------------------------

    if LLM_PROVIDER != "groq":

        print(
            "ERROR: LLM_PROVIDER is not set to 'groq'."
        )

        return

    if not LLM_MODEL:

        print(
            "ERROR: LLM_MODEL is empty."
        )

        return

    if not GROQ_API_KEY:

        print(
            "ERROR: GROQ_API_KEY is missing."
        )

        return

    # ------------------------------------------------
    # Create Client
    # ------------------------------------------------

    try:

        client = Groq(
            api_key=GROQ_API_KEY
        )

        print("Groq Client: OK")

    except Exception as e:

        print("ERROR: Failed to create Groq client.")
        print(str(e))

        return

    print()

    # ------------------------------------------------
    # API Request
    # ------------------------------------------------

    print("Sending test request...")
    print()

    try:

        response = client.chat.completions.create(

            model=LLM_MODEL,

            messages=[

                {
                    "role": "system",
                    "content": (
                        "你是一個 AI API 測試助手。"
                        "請簡短回答。"
                    )
                },

                {
                    "role": "user",
                    "content": (
                        "請回答："
                        "AutoSearch V4 Groq API 測試成功。"
                    )
                }

            ],

            temperature=0.2

        )

        # ------------------------------------------------
        # Response
        # ------------------------------------------------

        content = (
            response
            .choices[0]
            .message
            .content
        )

        print("=" * 70)
        print("GROQ API TEST SUCCESS")
        print("=" * 70)

        print()
        print(f"Model : {LLM_MODEL}")
        print()
        print("Response:")
        print(content)
        print()

        # ------------------------------------------------
        # Usage
        # ------------------------------------------------

        if hasattr(response, "usage") and response.usage:

            print("Usage:")

            print(
                f"Prompt tokens     : "
                f"{response.usage.prompt_tokens}"
            )

            print(
                f"Completion tokens : "
                f"{response.usage.completion_tokens}"
            )

            print(
                f"Total tokens      : "
                f"{response.usage.total_tokens}"
            )

        print()
        print("=" * 70)

    except Exception as e:

        print("=" * 70)
        print("GROQ API TEST FAILED")
        print("=" * 70)

        print()
        print(f"Model : {LLM_MODEL}")
        print()
        print("Error:")
        print(str(e))
        print()
        print("=" * 70)


# ==================================================
# Entry Point
# ==================================================

if __name__ == "__main__":

    main()