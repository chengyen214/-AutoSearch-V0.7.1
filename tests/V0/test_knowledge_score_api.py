"""
tests/test_knowledge_score_api.py

AutoSearch V4

P3.7

Knowledge Score / Ranking API Tests

測試：

1. Top Ranking
2. Score Filter
3. Ranking Limit
4. Score Filter Value
5. Empty Ranking Result
6. OpenAPI Routes
7. HTTP Methods
8. Invalid Ranking Limit
9. Invalid Score
10. Boundary Values
"""

import pytest

from fastapi import FastAPI
from fastapi.testclient import TestClient


# ==================================================
# Import Router
# ==================================================

from api.routes.knowledge_ranking import (
    router,
)


# ==================================================
# Import Module
# ==================================================

import api.routes.knowledge_ranking as ranking_module


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

class FakeKnowledgeScoreRepository:
    """
    測試用 Knowledge Score Repository。

    不連接 MySQL。

    提供 P3.7 Ranking API 所需要的測試資料。
    """

    def __init__(self):

        self.scores = [

            {
                "id": 1,
                "knowledge_id": 1,
                "importance": 10,
                "confidence": 0.95,
                "quality_score": 9.0,
                "freshness_score": 10.0,
                "ranking_score": 9.5
            },

            {
                "id": 2,
                "knowledge_id": 2,
                "importance": 8,
                "confidence": 0.90,
                "quality_score": 8.0,
                "freshness_score": 8.0,
                "ranking_score": 8.2
            },

            {
                "id": 3,
                "knowledge_id": 3,
                "importance": 5,
                "confidence": 0.80,
                "quality_score": 6.0,
                "freshness_score": 6.0,
                "ranking_score": 6.1
            },

            {
                "id": 4,
                "knowledge_id": 4,
                "importance": 3,
                "confidence": 0.60,
                "quality_score": 4.0,
                "freshness_score": 4.0,
                "ranking_score": 4.2
            }
        ]


    # ==================================================
    # Top Ranking
    # ==================================================

    def top_ranking(
        self,
        limit=10
    ):

        return sorted(

            self.scores,

            key=lambda item:
                item["ranking_score"],

            reverse=True

        )[:limit]


    # ==================================================
    # Score Filter
    # ==================================================

    def find_by_score(
        self,
        score
    ):

        return [

            item

            for item in self.scores

            if item["ranking_score"] >= score

        ]


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
        FakeKnowledgeScoreRepository()
    )

    monkeypatch.setattr(

        ranking_module.service,

        "repository",

        fake_repository

    )

    return fake_repository


# ==================================================
# P3.7.1
# Top Ranking
# ==================================================

def test_top_ranking():

    response = client.get(

        "/knowledge/ranking/top"

    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    assert data["count"] == 4

    assert len(
        data["data"]
    ) == 4

    assert (
        data["data"][0]["ranking_score"]
        == 9.5
    )


# ==================================================
# P3.7.2
# Top Ranking Order
# ==================================================

def test_top_ranking_order():

    response = client.get(

        "/knowledge/ranking/top"

    )

    assert response.status_code == 200

    data = response.json()

    scores = [

        item["ranking_score"]

        for item in data["data"]

    ]

    assert scores == sorted(

        scores,

        reverse=True

    )


# ==================================================
# P3.7.3
# Top Ranking Limit
# ==================================================

def test_top_ranking_limit():

    response = client.get(

        "/knowledge/ranking/top?limit=2"

    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    assert data["count"] == 2

    assert len(
        data["data"]
    ) == 2

    assert (
        data["data"][0]["ranking_score"]
        == 9.5
    )

    assert (
        data["data"][1]["ranking_score"]
        == 8.2
    )


# ==================================================
# P3.7.4
# Top Ranking Limit 1
# ==================================================

def test_top_ranking_limit_one():

    response = client.get(

        "/knowledge/ranking/top?limit=1"

    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    assert data["count"] == 1

    assert len(
        data["data"]
    ) == 1


# ==================================================
# P3.7.5
# Score Filter
# ==================================================

def test_score_filter():

    response = client.get(

        "/knowledge/ranking/score/8"

    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    assert data["score"] == 8

    assert data["count"] == 2

    assert len(
        data["data"]
    ) == 2


# ==================================================
# P3.7.6
# Score Filter Result
# ==================================================

def test_score_filter_result():

    response = client.get(

        "/knowledge/ranking/score/8"

    )

    assert response.status_code == 200

    data = response.json()

    for item in data["data"]:

        assert (
            item["ranking_score"] >= 8
        )


# ==================================================
# P3.7.7
# Score Filter High Score
# ==================================================

def test_score_filter_high_score():

    response = client.get(

        "/knowledge/ranking/score/9"

    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    assert data["score"] == 9

    assert data["count"] == 1

    assert (
        data["data"][0]["ranking_score"]
        == 9.5
    )


# ==================================================
# P3.7.8
# Score Filter Low Score
# ==================================================

def test_score_filter_low_score():

    response = client.get(

        "/knowledge/ranking/score/4"

    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    assert data["count"] == 4


# ==================================================
# P3.7.9
# Score Filter No Result
# ==================================================

def test_score_filter_no_result():

    response = client.get(

        "/knowledge/ranking/score/100"

    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    assert data["score"] == 100

    assert data["count"] == 0

    assert data["data"] == []


# ==================================================
# P3.7.10
# Score Filter Decimal
# ==================================================

def test_score_filter_decimal():

    response = client.get(

        "/knowledge/ranking/score/8.5"

    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    assert data["score"] == 8.5

    assert data["count"] == 1


# ==================================================
# P3.7.11
# Score Filter Zero
# ==================================================

def test_score_filter_zero():

    response = client.get(

        "/knowledge/ranking/score/0"

    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    assert data["count"] == 4


# ==================================================
# P3.7.12
# Invalid Ranking Limit - Zero
# ==================================================

def test_invalid_ranking_limit_zero():

    response = client.get(

        "/knowledge/ranking/top?limit=0"

    )

    assert response.status_code == 422


# ==================================================
# P3.7.13
# Invalid Ranking Limit - Negative
# ==================================================

def test_invalid_ranking_limit_negative():

    response = client.get(

        "/knowledge/ranking/top?limit=-1"

    )

    assert response.status_code == 422


# ==================================================
# P3.7.14
# Invalid Ranking Limit - Over Maximum
# ==================================================

def test_invalid_ranking_limit_over_max():

    response = client.get(

        "/knowledge/ranking/top?limit=101"

    )

    assert response.status_code == 422


# ==================================================
# P3.7.15
# Invalid Ranking Limit - String
# ==================================================

def test_invalid_ranking_limit_string():

    response = client.get(

        "/knowledge/ranking/top?limit=abc"

    )

    assert response.status_code == 422


# ==================================================
# P3.7.16
# Invalid Score
# ==================================================

def test_invalid_score():

    response = client.get(

        "/knowledge/ranking/score/abc"

    )

    assert response.status_code == 422


# ==================================================
# P3.7.17
# OpenAPI Routes
# ==================================================

def test_knowledge_ranking_openapi_paths():

    response = client.get(
        "/openapi.json"
    )

    assert response.status_code == 200

    paths = response.json()["paths"]

    assert (
        "/knowledge/ranking/top"
        in paths
    )

    assert (
        "/knowledge/ranking/score/{score}"
        in paths
    )


# ==================================================
# P3.7.18
# HTTP Methods
# ==================================================

def test_knowledge_ranking_http_methods():

    response = client.get(
        "/openapi.json"
    )

    assert response.status_code == 200

    paths = response.json()["paths"]

    assert "get" in paths[
        "/knowledge/ranking/top"
    ]

    assert "get" in paths[
        "/knowledge/ranking/score/{score}"
    ]


# ==================================================
# P3.7.19
# Default Limit
# ==================================================

def test_top_ranking_default_limit():

    response = client.get(

        "/knowledge/ranking/top"

    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    assert data["count"] <= 10

    assert isinstance(
        data["data"],
        list
    )
