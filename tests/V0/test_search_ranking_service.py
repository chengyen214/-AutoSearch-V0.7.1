"""
tests/test_search_ranking_service.py

AutoSearch V4

P2.6 Step 7

Search Ranking Service Integration Test

Purpose:

    Test SearchRankingService coordination
    with individual ranking calculators.

Test Scope:

    1. Service initialization

    Keyword Score:

    2. Keyword Score delegation
    3. Keyword Score getter

    Entity Score:

    4. Entity Score delegation
    5. Entity Score getter

    Topic Score:

    6. Topic Score delegation
    7. Topic Score getter

    Importance Score:

    8. Importance Score delegation
    9. Importance Score getter

    Confidence Score:

    10. Confidence Score delegation
    11. Confidence Score getter

    Freshness Score:

    12. Freshness Score delegation
    13. Freshness Score getter

    Search Score:

    14. Build KnowledgeSearchScore
    15. Keyword + Entity + Topic + Importance
        + Confidence + Freshness integration

    Edge Cases:

    16. Empty query
    17. None query
    18. None search index
"""


from datetime import datetime, timedelta


from services.search_ranking_service import (
    SearchRankingService
)


class MockSearchIndex:
    """
    Minimal SearchIndex object
    used for integration testing.
    """

    def __init__(
        self,
        search_text="",
        entities=None,
        topic="",
        importance=0,
        confidence=None,
        published=None
    ):

        self.search_text = search_text

        self.entities = entities

        self.topic = topic

        self.importance = importance

        self.confidence = confidence

        self.published = published


# ==========================================
# Service Initialization
# ==========================================


def test_service_initialization():

    service = SearchRankingService()

    assert service.keyword_calculator is not None

    assert service.entity_calculator is not None

    assert service.topic_calculator is not None

    assert service.importance_calculator is not None

    assert service.confidence_calculator is not None

    assert service.freshness_calculator is not None

    print(
        "PASS: test_service_initialization"
    )


# ==========================================
# Keyword Score Integration
# ==========================================


def test_keyword_score_delegation():

    service = SearchRankingService()

    search_index = MockSearchIndex(
        "AI semiconductor technology"
    )

    score = service.calculate_keyword_score(
        "AI semiconductor",
        search_index
    )

    assert score == 10.0

    print(
        "PASS: test_keyword_score_delegation"
    )


def test_get_keyword_score():

    service = SearchRankingService()

    search_index = MockSearchIndex(
        "AI semiconductor"
    )

    score = service.get_keyword_score(
        "AI",
        search_index
    )

    assert score == 10.0

    print(
        "PASS: test_get_keyword_score"
    )


# ==========================================
# Entity Score Integration
# ==========================================


def test_entity_score_delegation():

    service = SearchRankingService()

    search_index = MockSearchIndex(
        "NVIDIA AI semiconductor",
        entities=[
            "NVIDIA",
            "AI",
            "semiconductor"
        ]
    )

    score = service.calculate_entity_score(
        "NVIDIA AI",
        search_index
    )

    assert score == 10.0

    print(
        "PASS: test_entity_score_delegation"
    )


def test_get_entity_score():

    service = SearchRankingService()

    search_index = MockSearchIndex(
        "NVIDIA AI",
        entities=[
            "NVIDIA",
            "AI"
        ]
    )

    score = service.get_entity_score(
        "NVIDIA",
        search_index
    )

    assert score == 10.0

    print(
        "PASS: test_get_entity_score"
    )


# ==========================================
# Topic Score Integration
# ==========================================


def test_topic_score_delegation():

    service = SearchRankingService()

    search_index = MockSearchIndex(
        "AI semiconductor technology",
        topic="AI semiconductor technology"
    )

    score = service.calculate_topic_score(
        "AI semiconductor",
        search_index
    )

    assert score == 10.0

    print(
        "PASS: test_topic_score_delegation"
    )


def test_get_topic_score():

    service = SearchRankingService()

    search_index = MockSearchIndex(
        "AI semiconductor",
        topic="AI semiconductor"
    )

    score = service.get_topic_score(
        "AI",
        search_index
    )

    assert score == 10.0

    print(
        "PASS: test_get_topic_score"
    )


# ==========================================
# Importance Score Integration
# ==========================================


def test_importance_score_delegation():

    service = SearchRankingService()

    search_index = MockSearchIndex(
        "AI semiconductor",
        importance=8
    )

    score = service.calculate_importance_score(
        search_index
    )

    assert score == 8.0

    print(
        "PASS: test_importance_score_delegation"
    )


def test_get_importance_score():

    service = SearchRankingService()

    search_index = MockSearchIndex(
        "AI semiconductor",
        importance=9
    )

    score = service.get_importance_score(
        search_index
    )

    assert score == 9.0

    print(
        "PASS: test_get_importance_score"
    )


# ==========================================
# Confidence Score Integration
# ==========================================


def test_confidence_score_delegation():

    service = SearchRankingService()

    search_index = MockSearchIndex(
        "AI semiconductor",
        confidence=0.8
    )

    score = service.calculate_confidence_score(
        search_index
    )

    assert score == 8.0

    print(
        "PASS: test_confidence_score_delegation"
    )


def test_get_confidence_score():

    service = SearchRankingService()

    search_index = MockSearchIndex(
        "AI semiconductor",
        confidence=0.9
    )

    score = service.get_confidence_score(
        search_index
    )

    assert score == 9.0

    print(
        "PASS: test_get_confidence_score"
    )


# ==========================================
# Freshness Score Integration
# ==========================================


def test_freshness_score_delegation():

    service = SearchRankingService()

    search_index = MockSearchIndex(
        "AI semiconductor",
        published=datetime.now()
    )

    score = service.calculate_freshness_score(
        search_index
    )

    assert score == 10.0

    print(
        "PASS: test_freshness_score_delegation"
    )


def test_get_freshness_score():

    service = SearchRankingService()

    search_index = MockSearchIndex(
        "AI semiconductor",
        published=datetime.now()
    )

    score = service.get_freshness_score(
        search_index
    )

    assert score == 10.0

    print(
        "PASS: test_get_freshness_score"
    )


# ==========================================
# Build Search Score
# ==========================================


def test_build_search_score():

    service = SearchRankingService()

    search_index = MockSearchIndex(

        "AI semiconductor technology",

        entities=[
            "AI",
            "semiconductor"
        ],

        topic="AI semiconductor technology",

        importance=8,

        confidence=0.8,

        published=datetime.now()

    )

    result = service.build_search_score(

        "AI semiconductor",

        search_index

    )

    assert result.keyword_score == 10.0

    assert result.entity_score == 10.0

    assert result.topic_score == 10.0

    assert result.importance_score == 8.0

    assert result.confidence_score == 8.0

    assert result.freshness_score == 10.0

    assert result.ranking_score == 0

    print(
        "PASS: test_build_search_score"
    )


# ==========================================
# Full Integration
# ==========================================


def test_keyword_entity_topic_importance_confidence_freshness_integration():

    service = SearchRankingService()

    search_index = MockSearchIndex(

        "AI semiconductor technology NVIDIA",

        entities=[
            "NVIDIA",
            "AI",
            "semiconductor"
        ],

        topic="AI semiconductor technology",

        importance=8,

        confidence=0.8,

        published=datetime.now()

    )

    result = service.build_search_score(

        "AI semiconductor NVIDIA",

        search_index

    )

    assert result.keyword_score == 10.0

    assert result.entity_score == 10.0

    assert result.topic_score == 6.67

    assert result.importance_score == 8.0

    assert result.confidence_score == 8.0

    assert result.freshness_score == 10.0

    assert result.ranking_score == 0

    print(
        "PASS: "
        "test_keyword_entity_topic_importance_confidence_freshness_integration"
    )


# ==========================================
# Edge Cases
# ==========================================


def test_empty_query():

    service = SearchRankingService()

    search_index = MockSearchIndex(

        "AI semiconductor",

        entities=[
            "AI",
            "semiconductor"
        ],

        topic="AI semiconductor",

        importance=8,

        confidence=0.8,

        published=datetime.now()

    )

    result = service.build_search_score(

        "",

        search_index

    )

    assert result.keyword_score == 0.0

    assert result.entity_score == 0.0

    assert result.topic_score == 0.0

    assert result.importance_score == 8.0

    assert result.confidence_score == 8.0

    assert result.freshness_score == 10.0

    print(
        "PASS: test_empty_query"
    )


def test_none_query():

    service = SearchRankingService()

    search_index = MockSearchIndex(

        "AI semiconductor",

        entities=[
            "AI",
            "semiconductor"
        ],

        topic="AI semiconductor",

        importance=8,

        confidence=0.8,

        published=datetime.now()

    )

    result = service.build_search_score(

        None,

        search_index

    )

    assert result.keyword_score == 0.0

    assert result.entity_score == 0.0

    assert result.topic_score == 0.0

    assert result.importance_score == 8.0

    assert result.confidence_score == 8.0

    assert result.freshness_score == 10.0

    print(
        "PASS: test_none_query"
    )


def test_none_search_index():

    service = SearchRankingService()

    result = service.build_search_score(

        "AI",

        None

    )

    assert result.keyword_score == 0.0

    assert result.entity_score == 0.0

    assert result.topic_score == 0.0

    assert result.importance_score == 0.0

    assert result.confidence_score == 0.0

    assert result.freshness_score == 0.0

    print(
        "PASS: test_none_search_index"
    )


# ==========================================
# Test Runner
# ==========================================


def main():

    print()

    print(
        "=========="
    )

    print(
        "AutoSearch V4"
    )

    print(
        "P2.6 Step 7"
    )

    print(
        "Search Ranking Service Integration Test"
    )

    print(
        "=========="
    )

    print()


    tests = [

        # ------------------------------
        # Service
        # ------------------------------

        test_service_initialization,

        # ------------------------------
        # Keyword
        # ------------------------------

        test_keyword_score_delegation,
        test_get_keyword_score,

        # ------------------------------
        # Entity
        # ------------------------------

        test_entity_score_delegation,
        test_get_entity_score,

        # ------------------------------
        # Topic
        # ------------------------------

        test_topic_score_delegation,
        test_get_topic_score,

        # ------------------------------
        # Importance
        # ------------------------------

        test_importance_score_delegation,
        test_get_importance_score,

        # ------------------------------
        # Confidence
        # ------------------------------

        test_confidence_score_delegation,
        test_get_confidence_score,

        # ------------------------------
        # Freshness
        # ------------------------------

        test_freshness_score_delegation,
        test_get_freshness_score,

        # ------------------------------
        # Search Score
        # ------------------------------

        test_build_search_score,

        test_keyword_entity_topic_importance_confidence_freshness_integration,

        # ------------------------------
        # Edge Cases
        # ------------------------------

        test_empty_query,
        test_none_query,
        test_none_search_index

    ]


    passed = 0

    failed = 0


    for test in tests:

        try:

            test()

            passed += 1

        except Exception as e:

            failed += 1

            print(
                f"FAIL: {test.__name__}"
            )

            print(
                f"      {e}"
            )


    print()

    print(
        "========== Test Result =========="
    )

    print(
        f"Passed: {passed}"
    )

    print(
        f"Failed: {failed}"
    )

    print(
        "================================="
    )


    if failed > 0:

        raise SystemExit(1)


if __name__ == "__main__":

    main()