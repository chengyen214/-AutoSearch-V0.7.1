# test_ranking_api.py

"""
tests/test_ranking_api.py

AutoSearch V4

P3.9

Ranking API Tests

測試:

1. Ranking Search
2. Ranking Result
3. Final Score
4. Result Sorting
5. Empty Query
6. Query Validation
7. OpenAPI
8. HTTP Method
"""


from fastapi import FastAPI
from fastapi.testclient import TestClient

import pytest

import api.routes.ranking as ranking_module

from api.routes.ranking import (
    router
)


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
# Fake Search Index
# ==================================================

class FakeSearchIndex:

    def __init__(
        self,
        index_id,
        knowledge_id,
        search_text,
        keywords,
        entities,
        topic
    ):

        self.id = index_id

        self.knowledge_id = knowledge_id

        self.search_text = search_text

        self.keywords = keywords

        self.entities = entities

        self.topic = topic


# ==================================================
# Fake Search Repository
# ==================================================

class FakeSearchRepository:

    def __init__(self):

        self.indexes = [

            FakeSearchIndex(

                1,

                1,

                "Semiconductor AI NVIDIA",

                [
                    "Semiconductor",
                    "AI",
                    "NVIDIA"
                ],

                [
                    "AI",
                    "NVIDIA"
                ],

                "Semiconductor"

            ),

            FakeSearchIndex(

                2,

                2,

                "Artificial Intelligence GPU",

                [
                    "AI",
                    "GPU"
                ],

                [
                    "AI",
                    "GPU",
                    "NVIDIA"
                ],

                "Artificial Intelligence"

            ),

            FakeSearchIndex(

                3,

                3,

                "Python Programming",

                [
                    "Python",
                    "Programming"
                ],

                [
                    "Python"
                ],

                "Python Programming"

            )

        ]


    # ==================================
    # Keyword Search
    # ==================================

    def search_keyword(
        self,
        query
    ):

        query = query.lower()

        return [

            item

            for item in self.indexes

            if (

                query
                in item.search_text.lower()

                or

                any(

                    query
                    in str(keyword).lower()

                    for keyword in item.keywords

                )

            )

        ]


    # ==================================
    # Entity Search
    # ==================================

    def search_entity(
        self,
        query
    ):

        query = query.lower()

        return [

            item

            for item in self.indexes

            if any(

                query
                in str(entity).lower()

                for entity in item.entities

            )

        ]


    # ==================================
    # Get All
    # ==================================

    def get_all(
        self
    ):

        return self.indexes


# ==================================================
# Fake Ranking Service
# ==================================================

class FakeRankingService:

    def build_search_score(
        self,
        query,
        search_index
    ):

        from models.knowledge_search_score import (
            KnowledgeSearchScore
        )

        query = query.lower()

        keyword_score = 0

        entity_score = 0

        topic_score = 0

        if query in search_index.search_text.lower():

            keyword_score = 10

        if any(

            query
            in str(entity).lower()

            for entity in search_index.entities

        ):

            entity_score = 10

        if query in search_index.topic.lower():

            topic_score = 10

        return KnowledgeSearchScore(

            keyword_score=keyword_score,

            entity_score=entity_score,

            topic_score=topic_score,

            importance_score=8,

            confidence_score=9,

            freshness_score=8,

            ranking_score=9

        )


# ==================================================
# Replace Search Service Dependencies
# ==================================================

@pytest.fixture(
    autouse=True
)
def mock_service(
    monkeypatch
):

    from services.search_service import (
        SearchService
    )

    fake_repository = (
        FakeSearchRepository()
    )

    fake_ranking = (
        FakeRankingService()
    )

    fake_service = SearchService(

        repository=fake_repository,

        ranking_service=fake_ranking

    )

    monkeypatch.setattr(

        ranking_module,

        "search_service",

        fake_service,

        raising=False

    )

    return fake_service


# ==================================================
# P3.9.1
# Ranking Search
# ==================================================

def test_ranking_search():

    response = client.get(

        "/ranking/search?q=AI"

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
# P3.9.2
# Ranking Result Contains Score
# ==================================================

def test_ranking_result_contains_score():

    response = client.get(

        "/ranking/search?q=AI"

    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    result = data["data"][0]

    assert "score" in result

    assert "final_score" in result["score"]


# ==================================================
# P3.9.3
# Final Score
# ==================================================

def test_final_score():

    response = client.get(

        "/ranking/search?q=AI"

    )

    assert response.status_code == 200

    data = response.json()

    result = data["data"][0]

    assert (
        result["score"]["final_score"]
        >= 0
    )


# ==================================================
# P3.9.4
# Ranking Sorted
# ==================================================

def test_ranking_sorted():

    response = client.get(

        "/ranking/search?q=AI"

    )

    assert response.status_code == 200

    data = response.json()

    scores = [

        item["score"]["final_score"]

        for item in data["data"]

    ]

    assert scores == sorted(

        scores,

        reverse=True

    )


# ==================================================
# P3.9.5
# Empty Query
# ==================================================

def test_empty_query():

    response = client.get(

        "/ranking/search?q=%20"

    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    assert data["count"] == 0

    assert data["data"] == []


# ==================================================
# P3.9.6
# Missing Query
# ==================================================

def test_missing_query():

    response = client.get(

        "/ranking/search"

    )

    assert response.status_code == 422


# ==================================================
# P3.9.7
# Query Minimum Length
# ==================================================

def test_query_min_length():

    response = client.get(

        "/ranking/search?q="

    )

    assert response.status_code == 422


# ==================================================
# P3.9.8
# OpenAPI
# ==================================================

def test_ranking_openapi_paths():

    response = client.get(

        "/openapi.json"

    )

    assert response.status_code == 200

    paths = response.json()["paths"]

    assert (

        "/ranking/search"

        in paths

    )


# ==================================================
# P3.9.9
# HTTP Method
# ==================================================

def test_ranking_http_methods():

    response = client.get(

        "/openapi.json"

    )

    assert response.status_code == 200

    paths = response.json()["paths"]

    assert "get" in paths[

        "/ranking/search"

    ]
