"""
tests/test_knowledge_score_service.py

AutoSearch V4

P3.7

Knowledge Score Service Tests

測試:

1. Create
2. Get By Knowledge ID
3. Top Ranking
4. Score Filter
5. Update
6. Exists

不連接 MySQL。

使用 Fake Repository 測試 Service Layer。
"""


import pytest


from models.knowledge_score import (
    KnowledgeScore
)


from services.knowledge_score_service import (
    KnowledgeScoreService
)


# ==================================================
# Fake Repository
# ==================================================

class FakeKnowledgeScoreRepository:
    """
    測試用 Knowledge Score Repository。

    不連接 MySQL。
    """

    def __init__(self):

        self.scores = [

            {
                "id": 1,
                "knowledge_id": 1,
                "importance": 9,
                "confidence": 0.95,
                "quality_score": 9.0,
                "freshness_score": 8.5,
                "ranking_score": 9.2
            },

            {
                "id": 2,
                "knowledge_id": 2,
                "importance": 8,
                "confidence": 0.90,
                "quality_score": 8.5,
                "freshness_score": 8.0,
                "ranking_score": 8.7
            },

            {
                "id": 3,
                "knowledge_id": 3,
                "importance": 6,
                "confidence": 0.75,
                "quality_score": 6.5,
                "freshness_score": 7.0,
                "ranking_score": 6.8
            }
        ]


    # ==================================================
    # Insert
    # ==================================================

    def insert(
        self,
        score
    ):

        score.id = (
            len(self.scores) + 1
        )

        self.scores.append(

            {

                "id": score.id,

                "knowledge_id":
                    score.knowledge_id,

                "importance":
                    score.importance,

                "confidence":
                    score.confidence,

                "quality_score":
                    score.quality_score,

                "freshness_score":
                    score.freshness_score,

                "ranking_score":
                    score.ranking_score
            }

        )

        return score


    # ==================================================
    # Get By Knowledge ID
    # ==================================================

    def get_by_knowledge_id(
        self,
        knowledge_id
    ):

        for score in self.scores:

            if (
                score["knowledge_id"]
                == knowledge_id
            ):

                return score

        return None


    # ==================================================
    # Top Ranking
    # ==================================================

    def top_ranking(
        self,
        limit=10
    ):

        return sorted(

            self.scores,

            key=lambda x:
                x["ranking_score"],

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

            if item["ranking_score"]
            >= score

        ]


    # ==================================================
    # Update
    # ==================================================

    def update(
        self,
        knowledge_id,
        score
    ):

        for item in self.scores:

            if (
                item["knowledge_id"]
                == knowledge_id
            ):

                item.update(

                    {

                        "importance":
                            score.importance,

                        "confidence":
                            score.confidence,

                        "quality_score":
                            score.quality_score,

                        "freshness_score":
                            score.freshness_score,

                        "ranking_score":
                            score.ranking_score

                    }

                )

                return True

        return False


    # ==================================================
    # Exists
    # ==================================================

    def exists(
        self,
        knowledge_id
    ):

        return any(

            item["knowledge_id"]
            == knowledge_id

            for item in self.scores

        )


# ==================================================
# Fixture
# ==================================================

@pytest.fixture
def service(
    monkeypatch
):

    fake_repository = (
        FakeKnowledgeScoreRepository()
    )

    service = (
        KnowledgeScoreService()
    )

    monkeypatch.setattr(

        service,

        "repository",

        fake_repository

    )

    return service


# ==================================================
# P3.7.1
# Create
# ==================================================

def test_create(
    service
):

    score = KnowledgeScore(

        knowledge_id=10,

        importance=8,

        confidence=0.9,

        quality_score=8.5,

        freshness_score=8.0,

        ranking_score=8.3

    )


    result = service.create(

        score

    )


    assert result is score

    assert result.id is not None

    assert result.knowledge_id == 10

    assert result.ranking_score == 8.3


# ==================================================
# Create None
# ==================================================

def test_create_none(
    service
):

    result = service.create(

        None

    )


    assert result is None


# ==================================================
# P3.7.2
# Get By Knowledge ID
# ==================================================

def test_get_by_knowledge_id(
    service
):

    result = (
        service.get_by_knowledge_id(
            1
        )
    )


    assert result is not None

    assert result["knowledge_id"] == 1

    assert result["ranking_score"] == 9.2


# ==================================================
# Get Not Found
# ==================================================

def test_get_by_knowledge_id_not_found(
    service
):

    result = (
        service.get_by_knowledge_id(
            99999
        )
    )


    assert result is None


# ==================================================
# P3.7.3
# Top Ranking
# ==================================================

def test_top_ranking(
    service
):

    result = service.top_ranking(

        2

    )


    assert len(result) == 2

    assert (
        result[0]["ranking_score"]
        >=
        result[1]["ranking_score"]
    )

    assert result[0]["knowledge_id"] == 1

    assert result[1]["knowledge_id"] == 2


# ==================================================
# P3.7.4
# Score Filter
# ==================================================

def test_find_by_score(
    service
):

    result = service.find_by_score(

        8.0

    )


    assert len(result) == 2

    for item in result:

        assert (
            item["ranking_score"]
            >= 8.0
        )


# ==================================================
# Score Filter Empty
# ==================================================

def test_find_by_score_empty(
    service
):

    result = service.find_by_score(

        10.0

    )


    assert result == []


# ==================================================
# P3.7.5
# Update
# ==================================================

def test_update(
    service
):

    score = KnowledgeScore(

        knowledge_id=1,

        importance=10,

        confidence=0.99,

        quality_score=9.8,

        freshness_score=9.5,

        ranking_score=9.9

    )


    result = service.update(

        1,

        score

    )


    assert result is True


    updated = (
        service.get_by_knowledge_id(
            1
        )
    )


    assert (
        updated["importance"]
        == 10
    )

    assert (
        updated["ranking_score"]
        == 9.9
    )


# ==================================================
# Update Not Found
# ==================================================

def test_update_not_found(
    service
):

    score = KnowledgeScore(

        knowledge_id=99999,

        ranking_score=5.0

    )


    result = service.update(

        99999,

        score

    )


    assert result is False


# ==================================================
# Update None
# ==================================================

def test_update_none(
    service
):

    result = service.update(

        1,

        None

    )


    assert result is False


# ==================================================
# P3.7.6
# Exists
# ==================================================

def test_exists(
    service
):

    assert service.exists(

        1

    ) is True


    assert service.exists(

        99999

    ) is False
