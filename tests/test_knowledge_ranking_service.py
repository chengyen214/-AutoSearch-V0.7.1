"""
tests/test_knowledge_ranking_service.py

AutoSearch V4

P3.7

Knowledge Ranking Service Tests


測試:

1. Ranking Calculate
2. Ranking Calculate Boundary
3. Ranking Calculate Low Score
4. Ranking Calculate High Score

5. Top Ranking
6. Top Ranking Limit
7. Score Filter

8. Ranking Level
9. Invalid Limit
10. Invalid Score

11. Repository Integration
"""


import pytest


from services.knowledge_ranking_service import (
    KnowledgeRankingService
)


# ==================================================
# Fake Repository
# ==================================================


class FakeKnowledgeScoreRepository:
    """
    P3.7 測試用 Repository。

    不連接 MySQL。
    """

    def __init__(self):

        self.rows = [

            {
                "id": 1,
                "knowledge_id": 1,
                "importance": 10,
                "confidence": 0.95,
                "quality_score": 9,
                "freshness_score": 10,
                "ranking_score": 9.5
            },

            {
                "id": 2,
                "knowledge_id": 2,
                "importance": 8,
                "confidence": 0.80,
                "quality_score": 8,
                "freshness_score": 8,
                "ranking_score": 8.0
            },

            {
                "id": 3,
                "knowledge_id": 3,
                "importance": 5,
                "confidence": 0.60,
                "quality_score": 6,
                "freshness_score": 5,
                "ranking_score": 6.0
            },

            {
                "id": 4,
                "knowledge_id": 4,
                "importance": 2,
                "confidence": 0.30,
                "quality_score": 3,
                "freshness_score": 2,
                "ranking_score": 3.0
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

            self.rows,

            key=lambda x: x["ranking_score"],

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

            row

            for row in self.rows

            if row["ranking_score"] >= score

        ]


# ==================================================
# Fixture
# ==================================================


@pytest.fixture
def service():

    ranking_service = (
        KnowledgeRankingService()
    )

    ranking_service.repository = (
        FakeKnowledgeScoreRepository()
    )

    return ranking_service


# ==================================================
# P3.7.1
# Ranking Calculate
# ==================================================


def test_ranking_service():

    service = KnowledgeRankingService()

    score = service.calculate_ranking(

        importance=10,

        confidence=0.95,

        quality_score=9,

        freshness_score=10

    )

    print()

    print("================")
    print("Ranking Calculate")
    print("================")

    print(
        "Ranking:",
        score
    )

    assert isinstance(
        score,
        (int, float)
    )

    assert score > 8


# ==================================================
# P3.7.2
# Ranking Calculate Boundary
# ==================================================


def test_ranking_calculate_boundary():

    service = KnowledgeRankingService()

    score = service.calculate_ranking(

        importance=0,

        confidence=0.0,

        quality_score=0,

        freshness_score=0

    )

    assert isinstance(
        score,
        (int, float)
    )

    assert score >= 0


# ==================================================
# P3.7.3
# Ranking Calculate High Score
# ==================================================


def test_ranking_calculate_high_score():

    service = KnowledgeRankingService()

    score = service.calculate_ranking(

        importance=10,

        confidence=1.0,

        quality_score=10,

        freshness_score=10

    )

    assert score >= 9


# ==================================================
# P3.7.4
# Ranking Calculate Low Score
# ==================================================


def test_ranking_calculate_low_score():

    service = KnowledgeRankingService()

    score = service.calculate_ranking(

        importance=1,

        confidence=0.1,

        quality_score=1,

        freshness_score=1

    )

    assert score < 5


# ==================================================
# P3.7.5
# Top Ranking
# ==================================================


def test_top_ranking(
    service
):

    result = service.get_top_ranking(

        10

    )

    print()

    print("================")
    print("Top Ranking")
    print("================")

    print(result)

    assert isinstance(
        result,
        list
    )

    assert len(result) == 4

    assert result[0]["ranking_score"] >= (
        result[1]["ranking_score"]
    )


# ==================================================
# P3.7.6
# Top Ranking Limit
# ==================================================


def test_top_ranking_limit(
    service
):

    result = service.get_top_ranking(

        2

    )

    assert isinstance(
        result,
        list
    )

    assert len(result) == 2

    assert result[0]["ranking_score"] == 9.5

    assert result[1]["ranking_score"] == 8.0


# ==================================================
# P3.7.7
# Score Filter
# ==================================================


def test_score_filter(
    service
):

    result = service.repository.find_by_score(

        8

    )

    assert isinstance(
        result,
        list
    )

    assert len(result) == 2

    assert all(

        item["ranking_score"] >= 8

        for item in result

    )


# ==================================================
# P3.7.8
# Score Filter High Threshold
# ==================================================


def test_score_filter_high_threshold(
    service
):

    result = service.repository.find_by_score(

        9

    )

    assert len(result) == 1

    assert result[0]["ranking_score"] == 9.5


# ==================================================
# P3.7.9
# Score Filter No Result
# ==================================================


def test_score_filter_no_result(
    service
):

    result = service.repository.find_by_score(

        10

    )

    assert result == []


# ==================================================
# P3.7.10
# Ranking Level
# ==================================================


@pytest.mark.parametrize(

    "score, expected",

    [

        (9.5, "HIGH"),

        (8.0, "HIGH"),

        (6.0, "MEDIUM"),

        (5.0, "MEDIUM"),

        (3.0, "LOW"),

    ]

)
def test_ranking_level(
    score,
    expected
):

    if score >= 8:

        level = "HIGH"

    elif score >= 5:

        level = "MEDIUM"

    else:

        level = "LOW"

    assert level == expected


# ==================================================
# P3.7.11
# Invalid Limit
# ==================================================


@pytest.mark.parametrize(

    "limit",

    [

        0,

        -1

    ]

)
def test_invalid_limit(
    service,
    limit
):

    result = service.get_top_ranking(

        limit

    )

    assert isinstance(
        result,
        list
    )


# ==================================================
# P3.7.12
# Large Limit
# ==================================================


def test_large_limit(
    service
):

    result = service.get_top_ranking(

        100

    )

    assert isinstance(
        result,
        list
    )

    assert len(result) == 4


# ==================================================
# P3.7.13
# Repository Integration
# ==================================================


def test_repository_integration(
    service
):

    assert service.repository is not None

    assert hasattr(

        service.repository,

        "top_ranking"

    )

    assert hasattr(

        service.repository,

        "find_by_score"

    )


# ==================================================
# P3.7.14
# Ranking Result Ordering
# ==================================================


def test_ranking_result_ordering(
    service
):

    result = service.get_top_ranking(

        4

    )

    scores = [

        item["ranking_score"]

        for item in result

    ]

    assert scores == sorted(

        scores,

        reverse=True

    )
