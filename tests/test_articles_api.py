"""
tests/test_articles_api.py

AutoSearch V4

P3.2.2

Article Management API Enhancement Test Foundation

測試:

    Article Query
    Article Search
    AI Retrieval
    Article Management
    Health Check

P3.2.2:

    Update Article
    Partial Update
    Empty Update
    Update Not Found
    Update Invalid ID
    Update Service Failure

    Delete Article
    Delete Not Found
    Delete Archive Protection
    Delete Invalid ID
    Delete Service Failure

不直接測試:

    MySQL
    ArchiveService
    AI Worker

本測試主要驗證:

    FastAPI Route
    HTTP Status
    Request / Response
    ArticleService API Contract
    Article Management API Contract
"""


from fastapi import FastAPI

from fastapi.testclient import TestClient

import pytest


from api.routes.articles import (
    router
)


# ==================================================
# Test App
# ==================================================

@pytest.fixture
def app():

    app = FastAPI()

    app.include_router(
        router
    )

    return app


# ==================================================
# Test Client
# ==================================================

@pytest.fixture
def client(
    app
):

    return TestClient(
        app
    )


# ==================================================
# GET ALL
# ==================================================

def test_get_articles(
    client,
    monkeypatch
):

    from api.routes import articles

    monkeypatch.setattr(

        articles.service,

        "get_all",

        lambda limit: [

            {
                "id": 1,
                "title": "Test Article"
            }

        ]

    )

    response = client.get(
        "/articles/?limit=10"
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1

    assert data[0]["id"] == 1


# ==================================================
# GET ALL - INVALID LIMIT
# ==================================================

def test_get_articles_invalid_limit(
    client
):

    response = client.get(
        "/articles/?limit=0"
    )

    assert response.status_code == 400


# ==================================================
# GET BY ID
# ==================================================

def test_get_article_by_id(
    client,
    monkeypatch
):

    from api.routes import articles

    monkeypatch.setattr(

        articles.service,

        "get_by_id",

        lambda article_id: {

            "id": article_id,

            "title": "Test Article"

        }

    )

    response = client.get(
        "/articles/1"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == 1


# ==================================================
# GET BY ID - NOT FOUND
# ==================================================

def test_get_article_by_id_not_found(
    client,
    monkeypatch
):

    from api.routes import articles

    monkeypatch.setattr(

        articles.service,

        "get_by_id",

        lambda article_id: None

    )

    response = client.get(
        "/articles/999"
    )

    assert response.status_code == 404


# ==================================================
# GET BY ID - INVALID ID
# ==================================================

def test_get_article_by_id_invalid(
    client
):

    response = client.get(
        "/articles/0"
    )

    assert response.status_code == 400


# ==================================================
# SEARCH KEYWORD
# ==================================================

def test_search_keyword(
    client,
    monkeypatch
):

    from api.routes import articles

    monkeypatch.setattr(

        articles.service,

        "get_by_keyword",

        lambda keyword: [

            {
                "id": 1,
                "keyword": keyword
            }

        ]

    )

    response = client.get(
        "/articles/search/keyword/TSMC"
    )

    assert response.status_code == 200

    data = response.json()

    assert data[0]["keyword"] == "TSMC"


# ==================================================
# SEARCH SOURCE
# ==================================================

def test_search_source(
    client,
    monkeypatch
):

    from api.routes import articles

    monkeypatch.setattr(

        articles.service,

        "get_by_source",

        lambda source: [

            {
                "id": 1,
                "source": source
            }

        ]

    )

    response = client.get(
        "/articles/search/source/CNA"
    )

    assert response.status_code == 200

    data = response.json()

    assert data[0]["source"] == "CNA"


# ==================================================
# AI IMPORTANCE
# ==================================================

def test_ai_importance(
    client,
    monkeypatch
):

    from api.routes import articles

    monkeypatch.setattr(

        articles.service,

        "get_by_importance",

        lambda level: [

            {
                "id": 1,
                "ai_importance": level
            }

        ]

    )

    response = client.get(
        "/articles/ai/importance/8"
    )

    assert response.status_code == 200

    data = response.json()

    assert data[0]["ai_importance"] == 8


# ==================================================
# AI IMPORTANCE - INVALID
# ==================================================

def test_ai_importance_invalid(
    client
):

    response = client.get(
        "/articles/ai/importance/-1"
    )

    assert response.status_code == 400


# ==================================================
# AI CATEGORY
# ==================================================

def test_ai_category(
    client,
    monkeypatch
):

    from api.routes import articles

    monkeypatch.setattr(

        articles.service,

        "get_by_category",

        lambda category: [

            {
                "id": 1,
                "ai_category": category
            }

        ]

    )

    response = client.get(
        "/articles/ai/category/Semiconductor"
    )

    assert response.status_code == 200

    data = response.json()

    assert (
        data[0]["ai_category"]
        == "Semiconductor"
    )


# ==================================================
# AI KEYWORD
# ==================================================

def test_ai_keyword(
    client,
    monkeypatch
):

    from api.routes import articles

    monkeypatch.setattr(

        articles.service,

        "get_by_ai_keyword",

        lambda keyword: [

            {
                "id": 1,
                "ai_keyword": keyword
            }

        ]

    )

    response = client.get(
        "/articles/ai/keyword/CoWoS"
    )

    assert response.status_code == 200

    data = response.json()

    assert (
        data[0]["ai_keyword"]
        == "CoWoS"
    )


# ==================================================
# AI TOP
# ==================================================

def test_ai_top(
    client,
    monkeypatch
):

    from api.routes import articles

    monkeypatch.setattr(

        articles.service,

        "get_ai_top",

        lambda limit: [

            {
                "id": 1,
                "ai_importance": 10
            }

        ]

    )

    response = client.get(
        "/articles/ai/top?limit=5"
    )

    assert response.status_code == 200

    data = response.json()

    assert (
        data[0]["ai_importance"]
        == 10
    )


# ==================================================
# AI TOP - INVALID LIMIT
# ==================================================

def test_ai_top_invalid_limit(
    client
):

    response = client.get(
        "/articles/ai/top?limit=0"
    )

    assert response.status_code == 400


# ==================================================
# HEALTH CHECK
# ==================================================

def test_health_check(
    client
):

    response = client.get(
        "/articles/health/check"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"

    assert (
        data["service"]
        == "AutoSearch V4 Article API"
    )

    assert (
        data["version"]
        == "P3.2.2"
    )


# ==================================================
# UPDATE ARTICLE
# ==================================================

def test_update_article(
    client,
    monkeypatch
):

    from api.routes import articles

    monkeypatch.setattr(

        articles.service,

        "get_by_id",

        lambda article_id: {

            "id": article_id,

            "title": "Old Title"

        }

    )

    monkeypatch.setattr(

        articles.service,

        "update_article",

        lambda **kwargs: {

            "id": kwargs["article_id"],

            "title": kwargs["title"],

            "source": kwargs["source"]

        }

    )

    response = client.put(

        "/articles/1",

        json={

            "title": "New Title",

            "source": "CNA"

        }

    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "success"

    assert data["article_id"] == 1

    assert (
        data["article"]["title"]
        == "New Title"
    )

    assert (
        data["article"]["source"]
        == "CNA"
    )


# ==================================================
# UPDATE ARTICLE - PARTIAL
# ==================================================

def test_update_article_partial(
    client,
    monkeypatch
):

    from api.routes import articles

    monkeypatch.setattr(

        articles.service,

        "get_by_id",

        lambda article_id: {

            "id": article_id

        }

    )

    captured = {}

    def fake_update(
        **kwargs
    ):

        captured.update(
            kwargs
        )

        return {

            "id": kwargs["article_id"]

        }

    monkeypatch.setattr(

        articles.service,

        "update_article",

        fake_update

    )

    response = client.put(

        "/articles/1",

        json={

            "title": "Only Title"

        }

    )

    assert response.status_code == 200

    assert (
        captured["article_id"]
        == 1
    )

    assert (
        captured["title"]
        == "Only Title"
    )

    assert (
        captured["source"]
        is None
    )


# ==================================================
# UPDATE ARTICLE - EMPTY BODY
# ==================================================

def test_update_article_empty_body(
    client,
    monkeypatch
):

    from api.routes import articles

    monkeypatch.setattr(

        articles.service,

        "get_by_id",

        lambda article_id: {

            "id": article_id

        }

    )

    response = client.put(

        "/articles/1",

        json={}

    )

    assert response.status_code == 400


# ==================================================
# UPDATE ARTICLE - NOT FOUND
# ==================================================

def test_update_article_not_found(
    client,
    monkeypatch
):

    from api.routes import articles

    monkeypatch.setattr(

        articles.service,

        "get_by_id",

        lambda article_id: None

    )

    response = client.put(

        "/articles/999",

        json={

            "title": "New Title"

        }

    )

    assert response.status_code == 404


# ==================================================
# UPDATE ARTICLE - INVALID ID
# ==================================================

def test_update_article_invalid_id(
    client
):

    response = client.put(

        "/articles/0",

        json={

            "title": "New Title"

        }

    )

    assert response.status_code == 400


# ==================================================
# UPDATE ARTICLE - SERVICE FAILURE
# ==================================================

def test_update_article_service_failure(
    client,
    monkeypatch
):

    from api.routes import articles

    monkeypatch.setattr(

        articles.service,

        "get_by_id",

        lambda article_id: {

            "id": article_id

        }

    )

    def failed_update(
        **kwargs
    ):

        raise RuntimeError(
            "Database error"
        )

    monkeypatch.setattr(

        articles.service,

        "update_article",

        failed_update

    )

    response = client.put(

        "/articles/1",

        json={

            "title": "New Title"

        }

    )

    assert response.status_code == 500

    data = response.json()

    assert (
        data["detail"]
        == "Article update failed"
    )


# ==================================================
# UPDATE ARTICLE - SERVICE UNAVAILABLE
# ==================================================

def test_update_article_service_unavailable(
    client,
    monkeypatch
):

    from api.routes import articles

    monkeypatch.setattr(

        articles.service,

        "get_by_id",

        lambda article_id: {

            "id": article_id

        }

    )

    def failed_update(
        **kwargs
    ):

        raise AttributeError(
            "not implemented"
        )

    monkeypatch.setattr(

        articles.service,

        "update_article",

        failed_update

    )

    response = client.put(

        "/articles/1",

        json={

            "title": "New Title"

        }

    )

    assert response.status_code == 500

    data = response.json()

    assert (
        data["detail"]
        == "Article update service unavailable"
    )

# ==================================================
# UPDATE ARTICLE - PROTECTED FIELD
#
# P3.2.3
#
# 不允許透過 Article Management API
# 修改:
#
#     id
#     document_id
#     content
#     AI fields
#     archive fields
#
# ==================================================

def test_update_article_protected_field(
    client,
    monkeypatch
):
    """
    P3.2.3

    Protected fields 必須被 API 拒絕。
    """

    from api.routes import articles

    monkeypatch.setattr(

        articles.service,

        "get_by_id",

        lambda article_id: {

            "id": article_id

        }

    )

    response = client.put(

        "/articles/1",

        json={

            "content": "Modified Content"

        }

    )

    assert response.status_code == 422


# ==================================================
# UPDATE ARTICLE - DOCUMENT ID PROTECTION
# ==================================================

def test_update_article_document_id_protected(
    client,
    monkeypatch
):
    """
    document_id 不允許透過 Management API 修改。
    """

    from api.routes import articles

    monkeypatch.setattr(

        articles.service,

        "get_by_id",

        lambda article_id: {

            "id": article_id

        }

    )

    response = client.put(

        "/articles/1",

        json={

            "document_id": "modified-document"

        }

    )

    assert response.status_code == 422


# ==================================================
# UPDATE ARTICLE - AI FIELD PROTECTION
# ==================================================

def test_update_article_ai_field_protected(
    client,
    monkeypatch
):
    """
    AI Analysis 欄位不允許修改。
    """

    from api.routes import articles

    monkeypatch.setattr(

        articles.service,

        "get_by_id",

        lambda article_id: {

            "id": article_id

        }

    )

    response = client.put(

        "/articles/1",

        json={

            "ai_summary": "Modified AI Summary"

        }

    )

    assert response.status_code == 422


# ==================================================
# UPDATE ARTICLE - EMPTY TITLE
# ==================================================

def test_update_article_empty_title(
    client,
    monkeypatch
):
    """
    title 不允許為空字串。
    """

    from api.routes import articles

    monkeypatch.setattr(

        articles.service,

        "get_by_id",

        lambda article_id: {

            "id": article_id

        }

    )

    response = client.put(

        "/articles/1",

        json={

            "title": ""

        }

    )

    assert response.status_code == 422


# ==================================================
# UPDATE ARTICLE - EMPTY SOURCE
# ==================================================

def test_update_article_empty_source(
    client,
    monkeypatch
):
    """
    source 不允許為空字串。
    """

    from api.routes import articles

    monkeypatch.setattr(

        articles.service,

        "get_by_id",

        lambda article_id: {

            "id": article_id

        }

    )

    response = client.put(

        "/articles/1",

        json={

            "source": ""

        }

    )

    assert response.status_code == 422


# ==================================================
# UPDATE ARTICLE - INVALID PUBLISHED
# ==================================================

def test_update_article_invalid_published(
    client,
    monkeypatch
):
    """
    published 必須符合日期時間格式。
    """

    from api.routes import articles

    monkeypatch.setattr(

        articles.service,

        "get_by_id",

        lambda article_id: {

            "id": article_id

        }

    )

    response = client.put(

        "/articles/1",

        json={

            "published": "invalid-date"

        }

    )

    assert response.status_code == 422


# ==================================================
# DELETE ARTICLE - SERVICE FAILURE
# ==================================================

def test_delete_article_service_failure(
    client,
    monkeypatch
):
    """
    ArticleService.delete_article()
    發生 Exception 時，API 應回傳 500。
    """

    from api.routes import articles

    # ==============================================
    # Article Exists
    # ==============================================

    monkeypatch.setattr(

        articles.service,

        "get_by_id",

        lambda article_id: {

            "id": article_id

        }

    )

    # ==============================================
    # Service Failure
    # ==============================================

    def fake_delete(
        article_id
    ):

        raise RuntimeError(
            "Database error"
        )

    monkeypatch.setattr(

        articles.service,

        "delete_article",

        fake_delete

    )

    response = client.delete(
        "/articles/1"
    )

    assert response.status_code == 500

    data = response.json()

    assert (
        data["detail"]
        == "Article delete failed"
    )



# ==================================================
# DELETE ARTICLE
# ==================================================

def test_delete_article(
    client,
    monkeypatch
):

    from api.routes import articles

    monkeypatch.setattr(

        articles.service,

        "get_by_id",

        lambda article_id: {

            "id": article_id

        }

    )

    monkeypatch.setattr(

        articles.service,

        "delete_article",

        lambda article_id: True

    )

    response = client.delete(
        "/articles/1"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "success"

    assert data["article_id"] == 1


# ==================================================
# DELETE ARTICLE - NOT FOUND
# ==================================================

def test_delete_article_not_found(
    client,
    monkeypatch
):

    from api.routes import articles

    monkeypatch.setattr(

        articles.service,

        "get_by_id",

        lambda article_id: None

    )

    response = client.delete(
        "/articles/999"
    )

    assert response.status_code == 404


# ==================================================
# DELETE ARTICLE - ARCHIVE PROTECTION
# ==================================================

def test_delete_article_archive_protection(
    client,
    monkeypatch
):

    from api.routes import articles

    monkeypatch.setattr(

        articles.service,

        "get_by_id",

        lambda article_id: {

            "id": article_id

        }

    )

    monkeypatch.setattr(

        articles.service,

        "delete_article",

        lambda article_id: False

    )

    response = client.delete(
        "/articles/1"
    )

    assert response.status_code == 409

    data = response.json()

    assert (
        "Archive"
        in data["detail"]
    )


# ==================================================
# DELETE ARTICLE - INVALID ID
# ==================================================

def test_delete_article_invalid_id(
    client
):

    response = client.delete(
        "/articles/0"
    )

    assert response.status_code == 400


# ==================================================
# DELETE ARTICLE - SERVICE FAILURE
# ==================================================

def test_delete_article_service_failure(
    client,
    monkeypatch
):

    from api.routes import articles

    monkeypatch.setattr(

        articles.service,

        "get_by_id",

        lambda article_id: {

            "id": article_id

        }

    )

    def failed_delete(
        article_id
    ):

        raise RuntimeError(
            "Database error"
        )

    monkeypatch.setattr(

        articles.service,

        "delete_article",

        failed_delete

    )

    response = client.delete(
        "/articles/1"
    )

    assert response.status_code == 500

    data = response.json()

    assert (
        data["detail"]
        == "Article delete failed"
    )


# ==================================================
# DELETE ARTICLE - SERVICE UNAVAILABLE
# ==================================================

def test_delete_article_service_unavailable(
    client,
    monkeypatch
):

    from api.routes import articles

    monkeypatch.setattr(

        articles.service,

        "get_by_id",

        lambda article_id: {

            "id": article_id

        }

    )

    def failed_delete(
        article_id
    ):

        raise AttributeError(
            "not implemented"
        )

    monkeypatch.setattr(

        articles.service,

        "delete_article",

        failed_delete

    )

    response = client.delete(
        "/articles/1"
    )

    assert response.status_code == 500

    data = response.json()

    assert (
        data["detail"]
        == "Article delete service unavailable"
    )