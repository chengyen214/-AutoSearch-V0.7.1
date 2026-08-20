"""
tests/P2/test_ai_analysis_persistence.py

AutoSearch V4

P2.4.1

Test:

    Article 已先以 pending 狀態保存
            ↓
    模擬 AI Analysis 完成
            ↓
    ArticleRepository.update_ai_analysis()
            ↓
    articles AI fields 正確回寫

驗證：

    ai_summary
    ai_category
    ai_keywords
    ai_importance
    ai_model
    ai_version
    ai_analyze_time
    ai_confidence
    ai_status

注意：

    本測試不呼叫真正 Groq / LLM。
    使用 Mock AIAnalysis 驗證 Database Persistence。
"""

import uuid

import pytest

from database.article_repository import (
    ArticleRepository
)

from models.article import (
    Article
)

from models.ai_analysis import (
    AIAnalysis
)


# ============================================================
# Test Article Factory
# ============================================================

def create_test_article():
    """
    建立一筆測試 Article。

    不進行 AI Analysis。
    """

    article = Article(

        keyword="P2 AI Persistence Test",

        title="P2 AI Analysis Persistence Test",

        url=(
            "https://example.com/"
            + str(uuid.uuid4())
        ),

        source="P2_TEST",

        published=None,

        content=(
            "This is a test article content "
            "for AutoSearch V4 P2 AI persistence."
        ),

        crawl_time=None,

        status="Success"
    )

    # --------------------------------------------------------
    # Article Model 如果沒有自動產生 document_id，
    # 這裡補上一個唯一值。
    # --------------------------------------------------------

    article.document_id = (
        "P2-AI-"
        + uuid.uuid4().hex
    )

    return article


# ============================================================
# Test AI Analysis Persistence
# ============================================================

def test_ai_analysis_persistence():

    repo = ArticleRepository()

    article = None

    try:

        # ====================================================
        # Step 1
        #
        # Article 先保存
        #
        # 此時尚未 AI Analysis
        # ====================================================

        article = create_test_article()

        result = repo.save(
            article
        )

        assert result is True

        assert article.id is not None

        # ====================================================
        # Step 2
        #
        # 確認 Article 初始狀態
        # ====================================================

        row = repo.find_by_id(
            article.id
        )

        assert row is not None

        assert row["ai_status"] == "pending"

        assert row["ai_summary"] is None

        assert row["ai_category"] is None

        assert row["ai_keywords"] is None

        assert row["ai_importance"] is None

        assert row["ai_model"] is None

        assert row["ai_version"] is None

        assert row["ai_analyze_time"] is None

        assert row["ai_confidence"] is None

        # ====================================================
        # Step 3
        #
        # 模擬 AI Analysis
        #
        # 不呼叫 Groq。
        # ====================================================

        analysis = AIAnalysis(

            article_id=article.id,

            summary=(
                "This is a test AI summary."
            ),

            category="Technology",

            keywords=[
                "AI",
                "LLM",
                "AutoSearch"
            ],

            entities=[
                "OpenAI",
                "Groq"
            ],

            relations=[
                "AI -> LLM",
                "AutoSearch -> Knowledge Archive"
            ],

            importance=8,

            ai_model=(
                "test-model"
            ),

            ai_version="4.0-test",

            confidence=0.95,

            status="completed"
        )

        # ====================================================
        # Step 4
        #
        # 將 AI Analysis 放入 Article
        # ====================================================

        article.ai_analysis = analysis

        # ====================================================
        # Step 5
        #
        # AI Analysis -> SQL
        # ====================================================

        result = repo.update_ai_analysis(
            article
        )

        assert result is True

        # ====================================================
        # Step 6
        #
        # 從 SQL 重新讀取
        #
        # 不使用記憶中的 Article Object。
        # ====================================================

        row = repo.find_by_id(
            article.id
        )

        assert row is not None

        # ====================================================
        # Step 7
        #
        # 驗證 AI Summary
        # ====================================================

        assert (
            row["ai_summary"]
            == "This is a test AI summary."
        )

        # ====================================================
        # Step 8
        #
        # 驗證 Category
        # ====================================================

        assert (
            row["ai_category"]
            == "Technology"
        )

        # ====================================================
        # Step 9
        #
        # 驗證 Keywords
        #
        # Repository 會轉成 JSON。
        # ====================================================

        import json

        keywords = json.loads(
            row["ai_keywords"]
        )

        assert keywords == [
            "AI",
            "LLM",
            "AutoSearch"
        ]

        # ====================================================
        # Step 10
        #
        # 驗證 Importance
        # ====================================================

        assert (
            row["ai_importance"]
            == 8
        )

        # ====================================================
        # Step 11
        #
        # 驗證 AI Model
        # ====================================================

        assert (
            row["ai_model"]
            == "test-model"
        )

        # ====================================================
        # Step 12
        #
        # 驗證 AI Version
        # ====================================================

        assert (
            row["ai_version"]
            == "4.0-test"
        )

        # ====================================================
        # Step 13
        #
        # 驗證 Analyze Time
        #
        # AIAnalysis constructor 會自動產生 datetime.now()
        # ====================================================

        assert (
            row["ai_analyze_time"]
            is not None
        )

        # ====================================================
        # Step 14
        #
        # 驗證 Confidence
        # ====================================================

        assert (
            float(row["ai_confidence"])
            == pytest.approx(
                0.95
            )
        )

        # ====================================================
        # Step 15
        #
        # 驗證 AI Status
        # ====================================================

        assert (
            row["ai_status"]
            == "completed"
        )

    finally:

        # ====================================================
        # Cleanup
        #
        # 測試完成後刪除測試 Article。
        #
        # 注意：
        # update_ai_analysis() 不會建立 ai_tasks，
        # knowledge_archive 等資料，
        # 因此可以直接刪除。
        # ====================================================

        if article is not None:

            try:

                repo.delete(
                    article.id
                )

            except Exception:

                pass

        repo.close()
