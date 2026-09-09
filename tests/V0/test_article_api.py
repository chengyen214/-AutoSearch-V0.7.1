"""
tests/test_article_api.py

AutoSearch V4

P3.2

Article Management API Test

測試:

    GET /articles/
    GET /articles/{id}
    GET /articles/search/keyword/{keyword}
    GET /articles/search/source/{source}

    GET /articles/ai/importance/{level}
    GET /articles/ai/category/{category}
    GET /articles/ai/keyword/{keyword}
    GET /articles/ai/top

    GET /articles/health/check

測試方式:

    FastAPI TestClient
    Mock ArticleService

目的:

    驗證 API Router
    驗證 HTTP Status Code
    驗證 API Response
    不依賴 MySQL 真實資料
"""


from fastapi import FastAPI
from fastapi.testclient import TestClient

from unittest.mock import MagicMock

import pytest


# ============================================================
# Import Router
# ============================================================

from api.routes.articles import router


# ============================================================
# Test Application
# ============================================================

app = FastAPI()

app.include_router(router)


# ============================================================
# Test Client
# ============================================================

client = TestClient(app)


# ============================================================
# Mock Article Service
# ============================================================

@pytest.fixture
def mock_service(monkeypatch):
    """
    Mock ArticleService。

    避免測試直接連接 MySQL。
    """

    service = MagicMock()

    # --------------------------------------------------------
    # GET ALL
    # --------------------------------------------------------

    service.get_all.return_value = [
        {
            "id": 1,
            "title": "Test Article 1"
        },
        {
            "id": 2,
            "title": "Test Article 2"
        }
    ]

    # --------------------------------------------------------
    # GET BY ID
    # --------------------------------------------------------

    service.get_by_id.return_value = {
        "id": 1,
        "title": "Test Article"
    }

    # --------------------------------------------------------
    # KEYWORD
    # --------------------------------------------------------

    service.get_by_keyword.return_value = [
        {
            "id": 1,
            "keyword": "TSMC",
            "title": "TSMC Article"
        }
    ]

    # --------------------------------------------------------
    # SOURCE
    # --------------------------------------------------------

    service.get_by_source.return_value = [
        {
            "id": 1,
            "source": "CNA",
            "title": "CNA Article"
        }
    ]

    # --------------------------------------------------------
    # AI IMPORTANCE
    # --------------------------------------------------------

    service.get_by_importance.return_value = [
        {
            "id": 1,
            "ai_importance": 9
        }
    ]

    # --------------------------------------------------------
    # AI CATEGORY
    # --------------------------------------------------------

    service.get_by_category.return_value = [
        {
            "id": 1,
            "ai_category": "Semiconductor"
        }
    ]

    # --------------------------------------------------------
    # AI KEYWORD
    # --------------------------------------------------------

    service.get_by_ai_keyword.return_value = [
        {
            "id": 1,
            "ai_keywords": [
                "CoWoS"
            ]
        }
    ]

    # --------------------------------------------------------
    # AI TOP
    # --------------------------------------------------------

    service.get_ai_top.return_value = [
        {
            "id": 1,
            "ai_importance": 10
        },
        {
            "id": 2,
            "ai_importance": 9
        }
    ]

    # --------------------------------------------------------
    # Patch Router Service
    # --------------------------------------------------------

    monkeypatch.setattr(
        "api.routes.articles.service",
        service
    )

    return service


# ============================================================
# GET /articles/
# ============================================================

def test_get_articles(mock_service):
    """
    測試取得 Article List。
    """

    response = client.get(
        "/articles/?limit=10"
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(
        data,
        list
    )

    assert len(data) == 2

    mock_service.get_all.assert_called_once_with(
        10
    )


# ============================================================
# GET /articles/{article_id}
# ============================================================

def test_get_article_by_id(mock_service):
    """
    測試依 Article ID 查詢。
    """

    response = client.get(
        "/articles/1"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == 1

    mock_service.get_by_id.assert_called_once_with(
        1
    )


# ============================================================
# GET /articles/{article_id} NOT FOUND
# ============================================================

def test_get_article_by_id_not_found(
    mock_service
):
    """
    測試 Article 不存在。
    """

    mock_service.get_by_id.return_value = None

    response = client.get(
        "/articles/999999"
    )

    assert response.status_code == 404

    data = response.json()

    assert data["detail"] == (
        "Article not found"
    )


# ============================================================
# GET /articles/search/keyword/{keyword}
# ============================================================

def test_search_keyword(
    mock_service
):
    """
    測試 Article Keyword Search。
    """

    response = client.get(
        "/articles/search/keyword/TSMC"
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1

    assert data[0]["keyword"] == "TSMC"

    mock_service.get_by_keyword.assert_called_once_with(
        "TSMC"
    )


# ============================================================
# GET /articles/search/source/{source}
# ============================================================

def test_search_source(
    mock_service
):
    """
    測試 Article Source Search。
    """

    response = client.get(
        "/articles/search/source/CNA"
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1

    assert data[0]["source"] == "CNA"

    mock_service.get_by_source.assert_called_once_with(
        "CNA"
    )


# ============================================================
# GET /articles/ai/importance/{level}
# ============================================================

def test_ai_importance(
    mock_service
):
    """
    測試 AI Importance Search。
    """

    response = client.get(
        "/articles/ai/importance/8"
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1

    assert data[0]["ai_importance"] == 9

    mock_service.get_by_importance.assert_called_once_with(
        8
    )


# ============================================================
# GET /articles/ai/category/{category}
# ============================================================

def test_ai_category(
    mock_service
):
    """
    測試 AI Category Search。
    """

    response = client.get(
        "/articles/ai/category/Semiconductor"
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1

    assert (
        data[0]["ai_category"]
        == "Semiconductor"
    )

    mock_service.get_by_category.assert_called_once_with(
        "Semiconductor"
    )


# ============================================================
# GET /articles/ai/keyword/{keyword}
# ============================================================

def test_ai_keyword(
    mock_service
):
    """
    測試 AI Keyword Search。
    """

    response = client.get(
        "/articles/ai/keyword/CoWoS"
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1

    assert (
        "CoWoS"
        in data[0]["ai_keywords"]
    )

    mock_service.get_by_ai_keyword.assert_called_once_with(
        "CoWoS"
    )


# ============================================================
# GET /articles/ai/top
# ============================================================

def test_ai_top(
    mock_service
):
    """
    測試 AI Importance Ranking。
    """

    response = client.get(
        "/articles/ai/top?limit=5"
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2

    assert data[0]["ai_importance"] == 10

    mock_service.get_ai_top.assert_called_once_with(
        5
    )


# ============================================================
# GET /articles/health/check
# ============================================================

def test_health_check():
    """
    測試 Article API Health Check。
    """

    response = client.get(
        "/articles/health/check"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"

    assert data["service"] == (
        "AutoSearch V4 Article API"
    )