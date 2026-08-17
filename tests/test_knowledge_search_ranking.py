"""
tests/test_knowledge_search_ranking.py

AutoSearch V4

P1.7 Step 3

Knowledge Search Ranking Optimization Test

測試：

    KnowledgeIntelligentSearchService

驗證：

    1. 建立 Knowledge Archive
    2. 建立 Knowledge Score
    3. 執行 Intelligent Search
    4. Search Score
    5. Final Score
    6. Ranking Result
"""


from models.knowledge import Knowledge
from models.knowledge_score import KnowledgeScore

from database.knowledge_repository import (
    KnowledgeRepository
)

from database.knowledge_score_repository import (
    KnowledgeScoreRepository
)

from services.knowledge_intelligent_search_service import (
    KnowledgeIntelligentSearchService
)


def test_search_ranking():

    # ==================================
    # Repository
    # ==================================

    knowledge_repository = KnowledgeRepository()

    score_repository = KnowledgeScoreRepository()

    # ==================================
    # Create Knowledge
    # ==================================

    knowledge = Knowledge(

        article_id=8,

        topic="CoWoS Advanced Packaging",

        entities="TSMC,CoWoS,NVIDIA,HBM",

        relations="TSMC develops CoWoS advanced packaging",

        knowledge_version="1.0"

    )

    knowledge = knowledge_repository.insert(
        knowledge
    )

    print()

    print("================")
    print("Knowledge")
    print("================")

    print(
        knowledge
    )

    assert knowledge.id is not None

    # ==================================
    # Create Knowledge Score
    # ==================================

    score = KnowledgeScore(

        knowledge_id=knowledge.id,

        importance=9,

        confidence=0.9,

        quality_score=8.5,

        freshness_score=9,

        ranking_score=8.8

    )

    score = score_repository.insert(
        score
    )

    print()

    print("================")
    print("Knowledge Score")
    print("================")

    print(
        score.to_dict()
    )

    assert score.id is not None

    # ==================================
    # Intelligent Search
    # ==================================

    service = KnowledgeIntelligentSearchService()

    result = service.search(
        "CoWoS"
    )

    # ==================================
    # Output
    # ==================================

    print()

    print("================")
    print("Knowledge Search Ranking")
    print("================")

    for item in result:

        print()

        print(
            "Knowledge:"
        )

        print(
            item["knowledge"]
        )

        print()

        print(
            "Score:"
        )

        print(
            item["score"]
        )

        print()

        print(
            "Search Score:"
        )

        print(
            item["search_score"]
        )

    # ==================================
    # Assertion
    # ==================================

    assert len(result) > 0

    assert (
        "knowledge"
        in result[0]
    )

    assert (
        "score"
        in result[0]
    )

    assert (
        "search_score"
        in result[0]
    )

    assert (
        "final_score"
        in result[0]["search_score"]
    )

    assert (
        result[0]["search_score"]["final_score"]
        > 0
    )

    # ==================================
    # Verify Keyword Score
    # ==================================

    search_score = result[0]["search_score"]

    assert (
        search_score["keyword_score"]
        > 0
    )

    # ==================================
    # Verify Entity Score
    # ==================================

    assert (
        search_score["entity_score"]
        > 0
    )

    # ==================================
    # Verify Topic Score
    # ==================================

    assert (
        search_score["topic_score"]
        > 0
    )

    # ==================================
    # Verify Ranking Score
    # ==================================

    assert (
        search_score["ranking_score"]
        > 0
    )


if __name__ == "__main__":

    test_search_ranking()
