"""
tests/test_article_repository_ai.py

AutoSearch V4

Article Repository AI Analysis Tests

測試:

1. find_by_importance()
2. find_by_category()
3. find_by_ai_keyword()
4. get_top_ai_articles()
5. find_by_id()
6. get_ai_status()
7. update_ai_status()
8. update_ai_analysis()
"""

import json
from datetime import datetime


from database.article_repository import (
    ArticleRepository
)


from models.article import (
    Article
)


from models.ai_analysis import (
    AIAnalysis
)


# ==================================================
# Test Configuration
# ==================================================

TEST_ARTICLE_ID = None


# ==================================================
# Fixture
# ==================================================

def create_repository():

    return ArticleRepository()


# ==================================================
# Tests
# ==================================================

def test_find_by_importance():

    repository = create_repository()

    try:

        articles = repository.find_by_importance(
            0
        )

        assert isinstance(
            articles,
            list
        )

        for article in articles:

            assert (
                article["ai_importance"] is None
                or article["ai_importance"] >= 0
            )

    finally:

        repository.close()


# ==================================================
# Find By Category
# ==================================================

def test_find_by_category():

    repository = create_repository()

    try:

        articles = repository.find_by_category(
            "AI"
        )

        assert isinstance(
            articles,
            list
        )

        for article in articles:

            assert "ai_category" in article

    finally:

        repository.close()


# ==================================================
# Find By AI Keyword
# ==================================================

def test_find_by_ai_keyword():

    repository = create_repository()

    try:

        articles = repository.find_by_ai_keyword(
            "AI"
        )

        assert isinstance(
            articles,
            list
        )

        for article in articles:

            assert "ai_keywords" in article

    finally:

        repository.close()


# ==================================================
# Get Top AI Articles
# ==================================================

def test_get_top_ai_articles():

    repository = create_repository()

    try:

        articles = repository.get_top_ai_articles(
            limit=10
        )

        assert isinstance(
            articles,
            list
        )

        assert len(
            articles
        ) <= 10

        # ------------------------------------------
        # Verify Ordering
        # ------------------------------------------

        importance_values = [

            article.get(
                "ai_importance"
            ) or 0

            for article in articles

        ]

        assert importance_values == sorted(
            importance_values,
            reverse=True
        )

    finally:

        repository.close()


# ==================================================
# Find By ID
# ==================================================

def test_find_by_id():

    repository = create_repository()

    try:

        articles = repository.find_all(
            limit=1
        )

        if not articles:

            return

        article_id = articles[0]["id"]

        article = repository.find_by_id(
            article_id
        )

        assert article is not None

        assert article["id"] == article_id

    finally:

        repository.close()


# ==================================================
# Get AI Status
# ==================================================

def test_get_ai_status():

    repository = create_repository()

    try:

        articles = repository.find_all(
            limit=1
        )

        if not articles:

            return

        article_id = articles[0]["id"]

        result = repository.get_ai_status(
            article_id
        )

        assert result is not None

        assert result["id"] == article_id

        assert "ai_status" in result

    finally:

        repository.close()


# ==================================================
# Update AI Status
# ==================================================

def test_update_ai_status():

    repository = create_repository()

    try:

        articles = repository.find_all(
            limit=1
        )

        if not articles:

            return

        article_id = articles[0]["id"]

        original = repository.get_ai_status(
            article_id
        )

        assert original is not None

        original_status = original.get(
            "ai_status"
        )

        # ------------------------------------------
        # Update
        # ------------------------------------------

        result = repository.update_ai_status(
            article_id,
            "pending"
        )

        assert result is True

        # ------------------------------------------
        # Verify
        # ------------------------------------------

        current = repository.get_ai_status(
            article_id
        )

        assert current is not None

        assert (
            current["ai_status"]
            == "pending"
        )

        # ------------------------------------------
        # Restore
        # ------------------------------------------

        repository.update_ai_status(
            article_id,
            original_status
        )

    finally:

        repository.close()


# ==================================================
# Update AI Analysis
# ==================================================

def test_update_ai_analysis():

    repository = create_repository()

    try:

        articles = repository.find_all(
            limit=1
        )

        if not articles:

            return

        article_id = articles[0]["id"]

        article = repository.find_model_by_id(
            article_id
        )

        assert article is not None

        # ------------------------------------------
        # Save Original AI State
        # ------------------------------------------

        original = repository.find_by_id(
            article_id
        )

        original_values = {

            "ai_summary":
                original.get(
                    "ai_summary"
                ),

            "ai_category":
                original.get(
                    "ai_category"
                ),

            "ai_keywords":
                original.get(
                    "ai_keywords"
                ),

            "ai_importance":
                original.get(
                    "ai_importance"
                ),

            "ai_model":
                original.get(
                    "ai_model"
                ),

            "ai_version":
                original.get(
                    "ai_version"
                ),

            "ai_analyze_time":
                original.get(
                    "ai_analyze_time"
                ),

            "ai_confidence":
                original.get(
                    "ai_confidence"
                ),

            "ai_status":
                original.get(
                    "ai_status"
                )

        }

        # ------------------------------------------
        # Create Test AI Analysis
        # ------------------------------------------

        analysis = AIAnalysis(

            article_id=article_id,

            summary=(
                "Repository AI Analysis Test"
            ),

            category="TEST",

            keywords=[
                "AutoSearch",
                "V4",
                "TEST"
            ],

            importance=5,

            ai_model="test-model",

            ai_version="test-1.0",

            analyze_time=datetime.now(),

            confidence=0.95

        )

        article.ai_analysis = analysis

        # ------------------------------------------
        # Update
        # ------------------------------------------

        result = repository.update_ai_analysis(
            article
        )

        assert result is True

        # ------------------------------------------
        # Verify
        # ------------------------------------------

        updated = repository.find_by_id(
            article_id
        )

        assert updated is not None

        assert (
            updated["ai_summary"]
            == "Repository AI Analysis Test"
        )

        assert (
            updated["ai_category"]
            == "TEST"
        )

        assert (
            updated["ai_importance"]
            == 5
        )

        assert (
            updated["ai_model"]
            == "test-model"
        )

        assert (
            updated["ai_version"]
            == "test-1.0"
        )

        assert (
            updated["ai_status"]
            == "completed"
        )

        # ------------------------------------------
        # Verify Keywords JSON
        # ------------------------------------------

        keywords = updated["ai_keywords"]

        if isinstance(
            keywords,
            str
        ):

            keywords = json.loads(
                keywords
            )

        assert keywords == [
            "AutoSearch",
            "V4",
            "TEST"
        ]

        # ------------------------------------------
        # Verify Confidence
        # ------------------------------------------

        assert (
            float(
                updated["ai_confidence"]
            )
            == 0.95
        )

    finally:

        # ------------------------------------------
        # Restore Original AI State
        # ------------------------------------------

        if (
            "original_values" in locals()
            and "article_id" in locals()
        ):

            cursor = repository.connection.cursor()

            try:

                cursor.execute(

                    """

                    UPDATE articles

                    SET

                        ai_summary=%s,

                        ai_category=%s,

                        ai_keywords=%s,

                        ai_importance=%s,

                        ai_model=%s,

                        ai_version=%s,

                        ai_analyze_time=%s,

                        ai_confidence=%s,

                        ai_status=%s

                    WHERE id=%s

                    """,

                    (

                        original_values[
                            "ai_summary"
                        ],

                        original_values[
                            "ai_category"
                        ],

                        original_values[
                            "ai_keywords"
                        ],

                        original_values[
                            "ai_importance"
                        ],

                        original_values[
                            "ai_model"
                        ],

                        original_values[
                            "ai_version"
                        ],

                        original_values[
                            "ai_analyze_time"
                        ],

                        original_values[
                            "ai_confidence"
                        ],

                        original_values[
                            "ai_status"
                        ],

                        article_id

                    )

                )

                repository.connection.commit()

            finally:

                cursor.close()

        repository.close()