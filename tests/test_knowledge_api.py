"""
tests/test_knowledge_api.py

AutoSearch V4

P3.6

Knowledge API Tests

測試:

1. Article Knowledge
2. Topic Search
3. Entity Search
4. Relation Search
5. Full Knowledge Search
6. Latest Knowledge

錯誤:

7. Article Not Found
8. Empty Topic
9. Empty Entity
10. Empty Relation
11. Empty Search
12. Invalid Latest Limit

OpenAPI:

13. Knowledge API Routes
14. Knowledge API HTTP Methods
"""

import pytest

from fastapi import FastAPI
from fastapi.testclient import TestClient


# ==================================================
# Import Router
# ==================================================

from api.routes.knowledge import (
    router,
)


# ==================================================
# Import Module
# ==================================================

import api.routes.knowledge as knowledge_module


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

class FakeKnowledgeRepository:
    """
    測試用 Knowledge Repository。

    不連接 MySQL。

    直接提供 Knowledge API 所需要的資料。
    """

    def __init__(self):

        self.knowledge = [

            {
                "id": 1,
                "article_id": 1,
                "topic": "Semiconductor",
                "entities": "台積電,AI,NVIDIA",
                "relations": "台積電-NVIDIA",
                "knowledge_version": "1.0",
                "created_time": None
            },

            {
                "id": 2,
                "article_id": 2,
                "topic": "Artificial Intelligence",
                "entities": "AI,NVIDIA,GPU",
                "relations": "NVIDIA-AI",
                "knowledge_version": "1.0",
                "created_time": None
            },

            {
                "id": 3,
                "article_id": 3,
                "topic": "Python Programming",
                "entities": "Python,Programming",
                "relations": "Python-Programming",
                "knowledge_version": "1.0",
                "created_time": None
            }
        ]


    # ==================================================
    # Get By Article ID
    # ==================================================

    def get_by_article_id(
        self,
        article_id
    ):

        for item in self.knowledge:

            if item["article_id"] == article_id:

                return item

        return None


    # ==================================================
    # Topic Search
    # ==================================================

    def find_by_topic(
        self,
        topic
    ):

        topic = topic.lower()

        return [

            item

            for item in self.knowledge

            if topic in item["topic"].lower()

        ]


    # ==================================================
    # Entity Search
    # ==================================================

    def find_by_entity(
        self,
        entity
    ):

        entity = entity.lower()

        return [

            item

            for item in self.knowledge

            if entity in item["entities"].lower()

        ]


    # ==================================================
    # Relation Search
    # ==================================================

    def find_by_relation(
        self,
        relation
    ):

        relation = relation.lower()

        return [

            item

            for item in self.knowledge

            if relation in item["relations"].lower()

        ]


    # ==================================================
    # Full Search
    # ==================================================

    def search(
        self,
        keyword
    ):

        keyword = keyword.lower()

        return [

            item

            for item in self.knowledge

            if (
                keyword in item["topic"].lower()
                or
                keyword in item["entities"].lower()
                or
                keyword in item["relations"].lower()
            )

        ]


    # ==================================================
    # Latest
    # ==================================================

    def find_all(
        self,
        limit=20
    ):

        return self.knowledge[:limit]


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
        FakeKnowledgeRepository()
    )

    monkeypatch.setattr(

        knowledge_module.service,

        "repository",

        fake_repository

    )

    return fake_repository


# ==================================================
# P3.6.1
# Article Knowledge
# ==================================================

def test_get_article_knowledge():

    response = client.get(
        "/knowledge/article/1"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    assert data["data"]["article_id"] == 1

    assert data["data"]["topic"] == (
        "Semiconductor"
    )

    assert data["data"]["entities"] == (
        "台積電,AI,NVIDIA"
    )


# ==================================================
# P3.6.2
# Topic Search
# ==================================================

def test_topic_search():

    response = client.get(
        "/knowledge/topic/Semiconductor"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    assert data["count"] == 1

    assert len(
        data["data"]
    ) == 1

    assert data["data"][0]["topic"] == (
        "Semiconductor"
    )


# ==================================================
# Topic Case Insensitive
# ==================================================

def test_topic_search_case_insensitive():

    response = client.get(
        "/knowledge/topic/semiconductor"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    assert data["count"] == 1


# ==================================================
# P3.6.3
# Entity Search
# ==================================================

def test_entity_search():

    response = client.get(
        "/knowledge/entity/AI"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    assert data["count"] == 2

    assert len(
        data["data"]
    ) == 2


# ==================================================
# Entity Case Insensitive
# ==================================================

def test_entity_search_case_insensitive():

    response = client.get(
        "/knowledge/entity/ai"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    assert data["count"] == 2


# ==================================================
# P3.6.4
# Relation Search
# ==================================================

def test_relation_search():

    response = client.get(
        "/knowledge/relation/台積電"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    assert data["count"] == 1

    assert len(
        data["data"]
    ) == 1

    assert data["data"][0]["article_id"] == 1


# ==================================================
# Relation Search Case Insensitive
# ==================================================

def test_relation_search_case_insensitive():

    response = client.get(
        "/knowledge/relation/nvidia"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    assert data["count"] == 2


# ==================================================
# P3.6.5
# Full Knowledge Search
# ==================================================

def test_full_search():

    response = client.get(
        "/knowledge/search?q=CoWoS"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    assert data["keyword"] == "CoWoS"

    assert data["count"] == 0

    assert data["data"] == []


# ==================================================
# Full Search Existing Keyword
# ==================================================

def test_full_search_existing_keyword():

    response = client.get(
        "/knowledge/search?q=AI"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    assert data["keyword"] == "AI"

    assert data["count"] == 2

    assert len(
        data["data"]
    ) == 2


# ==================================================
# P3.6.6
# Latest Knowledge
# ==================================================

def test_latest():

    response = client.get(
        "/knowledge/latest"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    assert data["count"] == 3

    assert len(
        data["data"]
    ) == 3


# ==================================================
# Latest Limit
# ==================================================

def test_latest_limit():

    response = client.get(
        "/knowledge/latest?limit=2"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    assert data["count"] == 2

    assert len(
        data["data"]
    ) == 2


# ==================================================
# Article Not Found
# ==================================================

def test_get_article_knowledge_not_found():

    response = client.get(
        "/knowledge/article/99999"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    assert data["data"] is None


# ==================================================
# Empty Topic
#
# P3.6 Validation
#
# Empty Topic -> 400
#
# ==================================================

def test_empty_topic():

    response = client.get(
        "/knowledge/topic/%20"
    )

    assert response.status_code == 400

    data = response.json()

    assert data["detail"]["success"] is False

    assert data["detail"]["message"] == (
        "Topic cannot be empty"
    )


# ==================================================
# Empty Entity
#
# P3.6 Validation
#
# Empty Entity -> 400
#
# ==================================================

def test_empty_entity():

    response = client.get(
        "/knowledge/entity/%20"
    )

    assert response.status_code == 400

    data = response.json()

    assert data["detail"]["success"] is False

    assert data["detail"]["message"] == (
        "Entity cannot be empty"
    )


# ==================================================
# Empty Relation
#
# P3.6 Validation
#
# Empty Relation -> 400
#
# ==================================================

def test_empty_relation():

    response = client.get(
        "/knowledge/relation/%20"
    )

    assert response.status_code == 400

    data = response.json()

    assert data["detail"]["success"] is False

    assert data["detail"]["message"] == (
        "Relation cannot be empty"
    )


# ==================================================
# Empty Full Search
#
# P3.6 Validation
#
# Empty Keyword -> 400
#
# ==================================================

def test_empty_full_search():

    response = client.get(
        "/knowledge/search?q=%20"
    )

    assert response.status_code == 400

    data = response.json()

    assert data["detail"]["success"] is False

    assert data["detail"]["message"] == (
        "Keyword cannot be empty"
    )


# ==================================================
# Invalid Latest Limit
#
# P3.6 Validation
#
# limit:
#
#     minimum = 1
#     maximum = 100
#
# FastAPI Query validation
# returns HTTP 422.
#
# ==================================================

@pytest.mark.parametrize(
    "limit",
    [
        0,
        -1,
        101
    ]
)
def test_latest_invalid_limit(
    limit
):

    response = client.get(

        f"/knowledge/latest?limit={limit}"

    )

    assert response.status_code == 422


# ==================================================
# OpenAPI Routes
# ==================================================

def test_knowledge_openapi_paths():

    response = client.get(
        "/openapi.json"
    )

    assert response.status_code == 200

    paths = response.json()["paths"]

    assert (
        "/knowledge/article/{article_id}"
        in paths
    )

    assert (
        "/knowledge/topic/{keyword}"
        in paths
    )

    assert (
        "/knowledge/entity/{keyword}"
        in paths
    )

    assert (
        "/knowledge/relation/{keyword}"
        in paths
    )

    assert (
        "/knowledge/search"
        in paths
    )

    assert (
        "/knowledge/latest"
        in paths
    )


# ==================================================
# HTTP Methods
# ==================================================

def test_knowledge_http_methods():

    response = client.get(
        "/openapi.json"
    )

    assert response.status_code == 200

    paths = response.json()["paths"]

    assert "get" in paths[
        "/knowledge/article/{article_id}"
    ]

    assert "get" in paths[
        "/knowledge/topic/{keyword}"
    ]

    assert "get" in paths[
        "/knowledge/entity/{keyword}"
    ]

    assert "get" in paths[
        "/knowledge/relation/{keyword}"
    ]

    assert "get" in paths[
        "/knowledge/search"
    ]

    assert "get" in paths[
        "/knowledge/latest"
    ]
