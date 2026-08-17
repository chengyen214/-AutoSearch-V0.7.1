"""
tests/test_ai_analysis_api.py

AutoSearch V4

P3.5

AI Analysis API Tests

測試:

1. AI Analysis Detail
2. AI Analysis Status
3. AI Analysis by Importance
4. AI Analysis by Category
5. AI Analysis by Keyword
6. AI Top Articles

錯誤:

7. Article Not Found
8. Invalid Importance
9. Empty Category
10. Empty Keyword
11. Invalid Top Limit
"""

import json

import pytest

from fastapi import FastAPI
from fastapi.testclient import TestClient


# ==================================================
# Import Router
# ==================================================

from api.routes.ai_analysis import (
    router,
)


# ==================================================
# Import Module
# ==================================================

import api.routes.ai_analysis as ai_analysis_module


# ==================================================
# Test App
# ==================================================

app = FastAPI()

app.include_router(
    router
)


client = TestClient(
    app
)


# ==================================================
# Fake Repository
# ==================================================

class FakeArticleRepository:
    """
    測試用 Repository。

    不連接 MySQL。

    直接提供 API 所需要的資料。
    """

    def __init__(self):

        self.articles = [

            {
                "id": 1,
                "document_id": "doc-001",
                "keyword": "AI",
                "title": "AI Article",
                "url": "https://example.com/ai",
                "source": "Example",
                "published": None,
                "content": "AI article content",

                "ai_summary":
                    "AI summary",

                "ai_category":
                    "AI",

                "ai_keywords":
                    json.dumps(
                        [
                            "AI",
                            "LLM",
                            "Machine Learning"
                        ],
                        ensure_ascii=False
                    ),

                "ai_importance":
                    9,

                "ai_model":
                    "test-model",

                "ai_version":
                    "1.0",

                "ai_analyze_time":
                    None,

                "ai_confidence":
                    0.95,

                "ai_status":
                    "completed"
            },

            {
                "id": 2,
                "document_id": "doc-002",
                "keyword": "NVIDIA",
                "title": "NVIDIA Article",
                "url": "https://example.com/nvidia",
                "source": "Example",
                "published": None,
                "content": "NVIDIA article content",

                "ai_summary":
                    "NVIDIA summary",

                "ai_category":
                    "Technology",

                "ai_keywords":
                    json.dumps(
                        [
                            "NVIDIA",
                            "GPU",
                            "AI"
                        ],
                        ensure_ascii=False
                    ),

                "ai_importance":
                    8,

                "ai_model":
                    "test-model",

                "ai_version":
                    "1.0",

                "ai_analyze_time":
                    None,

                "ai_confidence":
                    0.90,

                "ai_status":
                    "completed"
            },

            {
                "id": 3,
                "document_id": "doc-003",
                "keyword": "Python",
                "title": "Python Article",
                "url": "https://example.com/python",
                "source": "Example",
                "published": None,
                "content": "Python article content",

                "ai_summary":
                    "Python summary",

                "ai_category":
                    "Programming",

                "ai_keywords":
                    json.dumps(
                        [
                            "Python",
                            "Programming"
                        ],
                        ensure_ascii=False
                    ),

                "ai_importance":
                    6,

                "ai_model":
                    "test-model",

                "ai_version":
                    "1.0",

                "ai_analyze_time":
                    None,

                "ai_confidence":
                    0.85,

                "ai_status":
                    "completed"
            }
        ]


    # ==================================================
    # Find By ID
    # ==================================================

    def find_by_id(
        self,
        article_id
    ):

        for article in self.articles:

            if article["id"] == article_id:

                return article

        return None


    # ==================================================
    # Find By Importance
    # ==================================================

    def find_by_importance(
        self,
        level
    ):

        return [

            article

            for article in self.articles

            if article["ai_importance"] >= level

        ]


    # ==================================================
    # Find By Category
    # ==================================================

    def find_by_category(
        self,
        category
    ):

        return [

            article

            for article in self.articles

            if article["ai_category"].lower()
            == category.lower()

        ]


    # ==================================================
    # Find By AI Keyword
    # ==================================================

    def find_by_ai_keyword(
        self,
        keyword
    ):

        keyword = keyword.lower()

        result = []

        for article in self.articles:

            keywords = json.loads(
                article["ai_keywords"]
            )

            if any(
                keyword in item.lower()
                for item in keywords
            ):

                result.append(
                    article
                )

        return result


    # ==================================================
    # Get Top AI Articles
    # ==================================================

    def get_top_ai_articles(
        self,
        limit=10
    ):

        articles = sorted(

            self.articles,

            key=lambda article:
                article["ai_importance"],

            reverse=True

        )

        return articles[:limit]


# ==================================================
# Replace Repository
# ==================================================

@pytest.fixture(
    autouse=True
)
def mock_repository(
    monkeypatch
):

    fake_repository = (
        FakeArticleRepository()
    )

    monkeypatch.setattr(

        ai_analysis_module,

        "repository",

        fake_repository

    )

    return fake_repository


# ==================================================
# P3.5.1
# AI Analysis Detail
# ==================================================

def test_get_ai_analysis():

    response = client.get(
        "/ai/analysis/1"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    assert data["data"]["article_id"] == 1

    assert data["data"]["summary"] == (
        "AI summary"
    )

    assert data["data"]["category"] == (
        "AI"
    )

    assert data["data"]["keywords"] == [

        "AI",
        "LLM",
        "Machine Learning"

    ]

    assert data["data"]["importance"] == 9

    assert data["data"]["model"] == (
        "test-model"
    )

    assert data["data"]["version"] == (
        "1.0"
    )

    assert data["data"]["confidence"] == 0.95

    assert data["data"]["status"] == (
        "completed"
    )


# ==================================================
# P3.5.2
# AI Analysis Status
# ==================================================

def test_get_ai_analysis_status():

    response = client.get(
        "/ai/analysis/1/status"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    assert data["article_id"] == 1

    assert data["status"] == (
        "completed"
    )

    assert "analyze_time" in data


# ==================================================
# P3.5.3
# AI Analysis Importance
# ==================================================

def test_get_ai_analysis_by_importance():

    response = client.get(
        "/ai/analysis/importance/8"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    assert data["level"] == 8

    assert data["count"] == 2

    assert len(
        data["data"]
    ) == 2

    assert data["data"][0]["importance"] >= 8


# ==================================================
# Importance Boundary
# ==================================================

def test_get_ai_analysis_by_importance_zero():

    response = client.get(
        "/ai/analysis/importance/0"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    assert data["level"] == 0

    assert data["count"] == 3


# ==================================================
# Invalid Importance
# ==================================================

@pytest.mark.parametrize(
    "level",
    [
        -1,
        11
    ]
)
def test_get_ai_analysis_invalid_importance(
    level
):

    response = client.get(

        f"/ai/analysis/importance/{level}"

    )

    assert response.status_code == 400

    data = response.json()

    assert data["detail"]["success"] is False

    assert data["detail"]["message"] == (
        "Importance level must be between 0 and 10"
    )


# ==================================================
# P3.5.4
# AI Analysis Category
# ==================================================

def test_get_ai_analysis_by_category():

    response = client.get(
        "/ai/analysis/category/AI"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    assert data["category"] == "AI"

    assert data["count"] == 1

    assert len(
        data["data"]
    ) == 1

    assert data["data"][0]["category"] == (
        "AI"
    )


# ==================================================
# Category Case Insensitive
# ==================================================

def test_get_ai_analysis_by_category_case_insensitive():

    response = client.get(
        "/ai/analysis/category/ai"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    assert data["count"] == 1

    assert data["data"][0]["category"] == (
        "AI"
    )


# ==================================================
# Empty Category
# ==================================================

def test_get_ai_analysis_empty_category():

    response = client.get(
        "/ai/analysis/category/%20"
    )

    assert response.status_code == 400

    data = response.json()

    assert data["detail"]["success"] is False

    assert data["detail"]["message"] == (
        "Category cannot be empty"
    )


# ==================================================
# P3.5.5
# AI Analysis Keyword
# ==================================================

def test_get_ai_analysis_by_keyword():

    response = client.get(
        "/ai/analysis/keyword/NVIDIA"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    assert data["keyword"] == "NVIDIA"

    assert data["count"] == 1

    assert len(
        data["data"]
    ) == 1

    assert data["data"][0]["article_id"] == 2


# ==================================================
# Keyword Case Insensitive
# ==================================================

def test_get_ai_analysis_by_keyword_case_insensitive():

    response = client.get(
        "/ai/analysis/keyword/ai"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    assert data["count"] == 2


# ==================================================
# Empty Keyword
# ==================================================

def test_get_ai_analysis_empty_keyword():

    response = client.get(
        "/ai/analysis/keyword/%20"
    )

    assert response.status_code == 400

    data = response.json()

    assert data["detail"]["success"] is False

    assert data["detail"]["message"] == (
        "Keyword cannot be empty"
    )


# ==================================================
# P3.5.6
# AI Top Articles
# ==================================================

def test_get_top_ai_analysis():

    response = client.get(
        "/ai/analysis/top"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    assert data["count"] == 3

    assert data["limit"] == 10

    assert len(
        data["data"]
    ) == 3

    # Highest importance first

    assert data["data"][0]["importance"] == 9

    assert data["data"][1]["importance"] == 8

    assert data["data"][2]["importance"] == 6


# ==================================================
# Top Articles Limit
# ==================================================

def test_get_top_ai_analysis_limit():

    response = client.get(
        "/ai/analysis/top?limit=2"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    assert data["count"] == 2

    assert data["limit"] == 2

    assert len(
        data["data"]
    ) == 2

    assert data["data"][0]["importance"] == 9

    assert data["data"][1]["importance"] == 8


# ==================================================
# Top Articles Invalid Limit
# ==================================================

@pytest.mark.parametrize(
    "limit",
    [
        0,
        -1,
        101
    ]
)
def test_get_top_ai_analysis_invalid_limit(
    limit
):

    response = client.get(

        f"/ai/analysis/top?limit={limit}"

    )

    assert response.status_code == 422


# ==================================================
# Article Not Found
# ==================================================

def test_get_ai_analysis_not_found():

    response = client.get(
        "/ai/analysis/99999"
    )

    assert response.status_code == 404

    data = response.json()

    assert data["detail"]["success"] is False

    assert data["detail"]["message"] == (
        "Article not found"
    )


# ==================================================
# Status Article Not Found
# ==================================================

def test_get_ai_analysis_status_not_found():

    response = client.get(
        "/ai/analysis/99999/status"
    )

    assert response.status_code == 404

    data = response.json()

    assert data["detail"]["success"] is False

    assert data["detail"]["message"] == (
        "Article not found"
    )
