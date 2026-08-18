"""
utils/check_groq_pipeline.py

AutoSearch V4

Groq Pipeline Integration Test

用途：

    驗證 AutoSearch V4 正式 AI Analysis Pipeline
    是否真的可以使用 Groq LLM。

測試流程：

    Test Article
        ↓
    AIAnalysisService
        ↓
    PromptBuilder
        ↓
    LLMClient
        ↓
    Groq
        ↓
    openai/gpt-oss-120b
        ↓
    JSONParser
        ↓
    AIAnalysis

輸出：

    output/groq_pipeline_test.json

執行：

    python -m utils.check_groq_pipeline

注意：

    此測試不建立 AI Task。
    此測試不修改 articles。
    此測試不寫入 knowledge_archive。
    此測試只驗證正式 AI Analysis Service
    是否真的能完成 Groq Analysis。
"""

import json
import os
import time
from datetime import datetime

from config.ai_config import (
    LLM_PROVIDER,
    LLM_MODEL,
    GROQ_API_KEY,
)

from services.ai_analysis_service import (
    AIAnalysisService
)

from utils.logger import logger


# ==================================================
# Output
# ==================================================

OUTPUT_DIR = "output"

OUTPUT_FILE = os.path.join(
    OUTPUT_DIR,
    "groq_pipeline_test.json"
)


# ==================================================
# Test Article
# ==================================================

class TestArticle:
    """
    測試用 Article Model。

    不使用資料庫，
    避免測試污染正式資料。
    """

    id = 0

    title = (
        "TSMC 2nm advanced process and AI chip "
        "manufacturing"
    )

    source = "Groq Pipeline Test"

    published = (
        "2026-08-18 00:00:00"
    )

    content = (
        "台積電正在推進 2nm 先進製程，"
        "並持續擴大 AI 晶片相關製造能力。"
        "NVIDIA 等 AI 晶片公司對先進製程與先進封裝需求持續增加，"
        "CoWoS 與 HBM 等技術也成為 AI 伺服器的重要組成。"
    )


# ==================================================
# JSON Safe
# ==================================================

def _json_safe(value):
    """
    將 Python Object 轉成 JSON 可序列化資料。
    """

    if value is None:

        return None

    if isinstance(
        value,
        (
            str,
            int,
            float,
            bool
        )
    ):

        return value

    if isinstance(
        value,
        datetime
    ):

        return value.isoformat()

    if isinstance(
        value,
        list
    ):

        return [
            _json_safe(item)
            for item in value
        ]

    if isinstance(
        value,
        dict
    ):

        return {
            str(key): _json_safe(item)
            for key, item in value.items()
        }

    return str(value)


# ==================================================
# Build AI Analysis Result
# ==================================================

def _analysis_to_dict(
    analysis
):
    """
    將 AIAnalysis Model
    轉成 JSON Dict。
    """

    if analysis is None:

        return None

    return {

        "article_id":
            _json_safe(
                getattr(
                    analysis,
                    "article_id",
                    None
                )
            ),

        "summary":
            _json_safe(
                getattr(
                    analysis,
                    "summary",
                    ""
                )
            ),

        "category":
            _json_safe(
                getattr(
                    analysis,
                    "category",
                    ""
                )
            ),

        "keywords":
            _json_safe(
                getattr(
                    analysis,
                    "keywords",
                    []
                )
            ),

        "entities":
            _json_safe(
                getattr(
                    analysis,
                    "entities",
                    []
                )
            ),

        "relations":
            _json_safe(
                getattr(
                    analysis,
                    "relations",
                    []
                )
            ),

        "importance":
            _json_safe(
                getattr(
                    analysis,
                    "importance",
                    0
                )
            ),

        "ai_model":
            _json_safe(
                getattr(
                    analysis,
                    "ai_model",
                    ""
                )
            ),

        "ai_version":
            _json_safe(
                getattr(
                    analysis,
                    "ai_version",
                    ""
                )
            ),

        "confidence":
            _json_safe(
                getattr(
                    analysis,
                    "confidence",
                    0
                )
            ),

        "status":
            _json_safe(
                getattr(
                    analysis,
                    "status",
                    ""
                )
            )

    }


# ==================================================
# Main Test
# ==================================================

def main():
    """
    執行 Groq Pipeline Test。
    """

    start_time = time.perf_counter()

    result = {

        "test_time":
            datetime.now().isoformat(),

        "test_name":
            "AutoSearch V4 Groq Pipeline Integration Test",

        "groq_connected":
            False,

        "provider":
            LLM_PROVIDER,

        "model":
            LLM_MODEL,

        "api_key_loaded":
            bool(GROQ_API_KEY),

        "llm_request_success":
            False,

        "json_parser_success":
            False,

        "ai_analysis_success":
            False,

        "pipeline_success":
            False,

        "response":
            None,

        "ai_analysis":
            None,

        "elapsed_seconds":
            None,

        "error":
            None

    }

    print("=" * 70)
    print("AutoSearch V4 - Groq Pipeline Integration Test")
    print("=" * 70)

    print()
    print(f"Provider : {LLM_PROVIDER}")
    print(f"Model    : {LLM_MODEL}")
    print(
        "API Key  : "
        f"{'Loaded' if GROQ_API_KEY else 'MISSING'}"
    )
    print()

    try:

        # ==================================================
        # Configuration Check
        # ==================================================

        if LLM_PROVIDER != "groq":

            raise RuntimeError(
                "LLM_PROVIDER is not 'groq'."
            )

        if not LLM_MODEL:

            raise RuntimeError(
                "LLM_MODEL is empty."
            )

        if not GROQ_API_KEY:

            raise RuntimeError(
                "GROQ_API_KEY is missing."
            )

        # ==================================================
        # AI Analysis Service
        # ==================================================

        print(
            "Initializing AIAnalysisService..."
        )

        service = AIAnalysisService()

        print(
            "AIAnalysisService initialized."
        )

        print()

        # ==================================================
        # Test Article
        # ==================================================

        article = TestArticle()

        print(
            "Executing official AI Analysis pipeline..."
        )

        print(
            "Article:"
        )

        print(
            f"  Title: {article.title}"
        )

        print(
            f"  Source: {article.source}"
        )

        print(
            f"  Content Length: "
            f"{len(article.content)}"
        )

        print()

        # ==================================================
        # Execute
        # ==================================================

        analysis = service.analyze(
            article
        )

        # ==================================================
        # Result
        # ==================================================

        if analysis is None:

            raise RuntimeError(
                "AIAnalysisService returned None."
            )

        result[
            "ai_analysis_success"
        ] = True

        result[
            "json_parser_success"
        ] = True

        result[
            "llm_request_success"
        ] = True

        result[
            "groq_connected"
        ] = True

        result[
            "pipeline_success"
        ] = True

        result[
            "ai_analysis"
        ] = _analysis_to_dict(
            analysis
        )

        # --------------------------------------------------
        # Mark successful response
        # --------------------------------------------------

        result[
            "response"
        ] = {

            "status":
                "SUCCESS",

            "provider":
                LLM_PROVIDER,

            "model":
                LLM_MODEL,

            "message":
                "Official AIAnalysisService successfully "
                "completed Groq analysis."

        }

        print("=" * 70)
        print("GROQ PIPELINE TEST SUCCESS")
        print("=" * 70)

        print()

        print(
            f"Provider : {LLM_PROVIDER}"
        )

        print(
            f"Model    : {LLM_MODEL}"
        )

        print()

        print(
            "AI Analysis:"
        )

        print(
            json.dumps(
                result["ai_analysis"],
                ensure_ascii=False,
                indent=4,
                default=str
            )
        )

        print()

    except Exception as e:

        result[
            "error"
        ] = {

            "type":
                type(e).__name__,

            "message":
                str(e)

        }

        logger.exception(
            "Groq pipeline test failed."
        )

        print("=" * 70)
        print("GROQ PIPELINE TEST FAILED")
        print("=" * 70)

        print()

        print(
            f"Error Type : "
            f"{type(e).__name__}"
        )

        print(
            f"Error      : "
            f"{e}"
        )

        print()

    finally:

        # ==================================================
        # Timing
        # ==================================================

        elapsed = (
            time.perf_counter()
            - start_time
        )

        result[
            "elapsed_seconds"
        ] = round(
            elapsed,
            3
        )

        # ==================================================
        # Output Directory
        # ==================================================

        os.makedirs(
            OUTPUT_DIR,
            exist_ok=True
        )

        # ==================================================
        # Write Result
        # ==================================================

        try:

            with open(
                OUTPUT_FILE,
                "w",
                encoding="utf-8"
            ) as file:

                json.dump(
                    result,
                    file,
                    ensure_ascii=False,
                    indent=4,
                    default=str
                )

            print(
                f"Result written to: "
                f"{OUTPUT_FILE}"
            )

        except Exception as e:

            print(
                "Failed to write test result:"
            )

            print(
                str(e)
            )

        print()

        print(
            f"Pipeline Success : "
            f"{result['pipeline_success']}"
        )

        print(
            f"Elapsed          : "
            f"{result['elapsed_seconds']} sec"
        )

        print(
            "=" * 70
        )


# ==================================================
# Entry Point
# ==================================================

if __name__ == "__main__":

    main()