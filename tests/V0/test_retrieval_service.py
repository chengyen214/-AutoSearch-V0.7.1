"""
tests/test_retrieval_service.py

AutoSearch V4

P2.6 Step 10

Retrieval Service Ranking Integration Test

Purpose:

    Test RetrievalService.search_ranked().

Test Strategy:

    Do NOT connect to MySQL.

    Use Mock Repository objects for:

        - ArticleRepository
        - KnowledgeRepository
        - SearchIndexRepository
        - KnowledgeScoreRepository

    Use the real:

        - SearchRankingService

Test Scope:

    1. Empty keyword
    2. Invalid limit
    3. Candidate retrieval
    4. SearchIndex retrieval
    5. KnowledgeScore retrieval
    6. Ranking calculation
    7. Final score sorting
    8. Result limit
    9. Missing SearchIndex
    10. Missing KnowledgeScore
    11. Missing Article
"""


from datetime import datetime


from services.retrieval_service import (
    RetrievalService
)


from services.search_ranking_service import (
    SearchRankingService
)


# ==========================================
# Mock Article Repository
# ==========================================


class MockArticleRepository:
    """
    Mock ArticleRepository.

    P2.6 Step 10 ranking tests
    do not require ArticleRepository
    database access.
    """

    def find_all(self):

        return []


    def find_by_importance(
        self,
        level
    ):

        return []


    def find_by_category(
        self,
        category
    ):

        return []


    def find_by_ai_keyword(
        self,
        keyword
    ):

        return []


# ==========================================
# Mock Knowledge Repository
# ==========================================


class MockKnowledgeRepository:
    """
    Mock KnowledgeRepository.

    Provides candidate Knowledge
    and Article data.
    """

    def __init__(self):

        self.knowledge_rows = [

            {
                "id": 1,
                "article_id": 101,
                "topic": "AI semiconductor"
            },

            {
                "id": 2,
                "article_id": 102,
                "topic": "AI technology"
            },

            {
                "id": 3,
                "article_id": 103,
                "topic": "AI NVIDIA"
            }

        ]


        self.article_rows = {

            1: {

                "id": 101,

                "document_id": "DOC-001",

                "keyword": "AI",

                "title": "Article A",

                "url": "https://example.com/a",

                "source": "Source A",

                "published": datetime(
                    2026,
                    8,
                    13
                ),

                "crawl_time": datetime(
                    2026,
                    8,
                    13
                ),

                "status": "Success"

            },

            2: {

                "id": 102,

                "document_id": "DOC-002",

                "keyword": "AI",

                "title": "Article B",

                "url": "https://example.com/b",

                "source": "Source B",

                "published": datetime(
                    2026,
                    8,
                    10
                ),

                "crawl_time": datetime(
                    2026,
                    8,
                    10
                ),

                "status": "Success"

            },

            3: {

                "id": 103,

                "document_id": "DOC-003",

                "keyword": "AI",

                "title": "Article C",

                "url": "https://example.com/c",

                "source": "Source C",

                "published": datetime(
                    2026,
                    8,
                    12
                ),

                "crawl_time": datetime(
                    2026,
                    8,
                    12
                ),

                "status": "Success"

            }

        }


    # ==================================
    # Candidate Search
    # ==================================

    def search(
        self,
        keyword
    ):

        return self.knowledge_rows


    # ==================================
    # Knowledge + Article
    # ==================================

    def get_with_article(
        self,
        knowledge_id
    ):

        return self.article_rows.get(
            knowledge_id
        )


# ==========================================
# Mock Search Index
# ==========================================


class MockSearchIndex:
    """
    Mock SearchIndex.

    Contains all fields required by
    SearchRankingService.
    """

    def __init__(
        self,
        knowledge_id,
        search_text,
        entities,
        topic,
        importance,
        confidence,
        ranking_score,
        published
    ):

        self.id = knowledge_id

        self.knowledge_id = knowledge_id

        self.search_text = search_text

        self.keywords = []

        self.entities = entities

        self.topic = topic

        self.embedding_reference = None

        self.index_version = "1.0"

        self.created_time = datetime.now()

        self.importance = importance

        self.confidence = confidence

        self.ranking_score = ranking_score

        self.published = published


# ==========================================
# Mock Search Index Repository
# ==========================================


class MockSearchIndexRepository:
    """
    Mock SearchIndexRepository.
    """

    def __init__(self):

        self.data = {

            1: MockSearchIndex(

                knowledge_id=1,

                search_text=(
                    "AI semiconductor NVIDIA"
                ),

                entities=[

                    "AI",

                    "semiconductor",

                    "NVIDIA"

                ],

                topic=(
                    "AI semiconductor"
                ),

                importance=8,

                confidence=0.9,

                ranking_score=8,

                published=datetime(
                    2026,
                    8,
                    13
                )

            ),

            2: MockSearchIndex(

                knowledge_id=2,

                search_text=(
                    "AI technology"
                ),

                entities=[

                    "AI"

                ],

                topic=(
                    "AI technology"
                ),

                importance=6,

                confidence=0.7,

                ranking_score=6,

                published=datetime(
                    2026,
                    8,
                    10
                )

            ),

            3: MockSearchIndex(

                knowledge_id=3,

                search_text=(
                    "AI NVIDIA semiconductor"
                ),

                entities=[

                    "AI",

                    "NVIDIA"

                ],

                topic=(
                    "AI NVIDIA"
                ),

                importance=9,

                confidence=0.95,

                ranking_score=9,

                published=datetime(
                    2026,
                    8,
                    12
                )

            )

        }


    def get_by_knowledge_id(
        self,
        knowledge_id
    ):

        return self.data.get(
            knowledge_id
        )


# ==========================================
# Mock Knowledge Score Repository
# ==========================================


class MockKnowledgeScoreRepository:
    """
    Mock KnowledgeScoreRepository.
    """

    def __init__(self):

        self.data = {

            1: {

                "knowledge_id": 1,

                "importance": 8,

                "confidence": 0.9,

                "quality_score": 8,

                "freshness_score": 10,

                "ranking_score": 8

            },

            2: {

                "knowledge_id": 2,

                "importance": 6,

                "confidence": 0.7,

                "quality_score": 7,

                "freshness_score": 8,

                "ranking_score": 6

            },

            3: {

                "knowledge_id": 3,

                "importance": 9,

                "confidence": 0.95,

                "quality_score": 9,

                "freshness_score": 9,

                "ranking_score": 9

            }

        }


    def get_by_knowledge_id(
        self,
        knowledge_id
    ):

        return self.data.get(
            knowledge_id
        )


# ==========================================
# Test Service Factory
# ==========================================


def create_service():

    """
    建立完全隔離 Database 的
    RetrievalService。

    不呼叫 RetrievalService.__init__。

    避免：

        ArticleRepository()
            ↓
        MySQL Connection
    """

    service = object.__new__(
        RetrievalService
    )


    # ==================================
    # Inject Mock Repositories
    # ==================================

    service.article_repo = (
        MockArticleRepository()
    )


    service.knowledge_repo = (
        MockKnowledgeRepository()
    )


    service.search_index_repo = (
        MockSearchIndexRepository()
    )


    service.knowledge_score_repo = (
        MockKnowledgeScoreRepository()
    )


    # ==================================
    # Real Ranking Service
    # ==================================

    service.ranking_service = (
        SearchRankingService()
    )


    return service


# ==========================================
# Test Empty Keyword
# ==========================================


def test_empty_keyword():

    service = create_service()

    results = service.search_ranked(

        "",

        limit=10

    )

    assert results == []

    print(
        "PASS: test_empty_keyword"
    )


# ==========================================
# Test Invalid Limit
# ==========================================


def test_invalid_limit():

    service = create_service()

    results = service.search_ranked(

        "AI",

        limit=0

    )

    assert results == []

    print(
        "PASS: test_invalid_limit"
    )


def test_negative_limit():

    service = create_service()

    results = service.search_ranked(

        "AI",

        limit=-1

    )

    assert results == []

    print(
        "PASS: test_negative_limit"
    )


# ==========================================
# Candidate Retrieval
# ==========================================


def test_candidate_retrieval():

    service = create_service()

    results = service.search_ranked(

        "AI",

        limit=10

    )

    assert len(results) == 3

    print(
        "PASS: test_candidate_retrieval"
    )


# ==========================================
# Search Index Retrieval
# ==========================================


def test_search_index_retrieval():

    service = create_service()

    results = service.search_ranked(

        "AI",

        limit=10

    )

    assert all(

        result["search_index"] is not None

        for result in results

    )

    print(
        "PASS: test_search_index_retrieval"
    )


# ==========================================
# Knowledge Score Retrieval
# ==========================================


def test_knowledge_score_retrieval():

    service = create_service()

    results = service.search_ranked(

        "AI",

        limit=10

    )

    assert all(

        result["knowledge_score"] is not None

        for result in results

    )

    print(
        "PASS: test_knowledge_score_retrieval"
    )


# ==========================================
# Ranking Calculation
# ==========================================


def test_ranking_calculation():

    service = create_service()

    results = service.search_ranked(

        "AI",

        limit=10

    )

    assert all(

        result["search_score"] is not None

        for result in results

    )

    assert all(

        result["final_score"] is not None

        for result in results

    )

    print(
        "PASS: test_ranking_calculation"
    )


# ==========================================
# Final Score Sorting
# ==========================================


def test_final_score_sorting():

    service = create_service()

    results = service.search_ranked(

        "AI",

        limit=10

    )

    scores = [

        result["final_score"]

        for result in results

    ]


    assert scores == sorted(

        scores,

        reverse=True

    )

    print(
        "PASS: test_final_score_sorting"
    )


# ==========================================
# Result Limit
# ==========================================


def test_result_limit():

    service = create_service()

    results = service.search_ranked(

        "AI",

        limit=2

    )

    assert len(results) == 2


    scores = [

        result["final_score"]

        for result in results

    ]


    assert scores == sorted(

        scores,

        reverse=True

    )

    print(
        "PASS: test_result_limit"
    )


# ==========================================
# Result Fields
# ==========================================


def test_result_fields():

    service = create_service()

    results = service.search_ranked(

        "AI",

        limit=10

    )

    result = results[0]


    assert "knowledge_id" in result

    assert "article_id" in result

    assert "title" in result

    assert "url" in result

    assert "source" in result

    assert "published" in result

    assert "topic" in result

    assert "search_score" in result

    assert "final_score" in result

    assert "knowledge" in result

    assert "knowledge_score" in result

    assert "search_index" in result


    print(
        "PASS: test_result_fields"
    )


# ==========================================
# Missing Search Index
# ==========================================


def test_missing_search_index():

    service = create_service()

    service.search_index_repo.data.pop(
        2
    )


    results = service.search_ranked(

        "AI",

        limit=10

    )


    assert len(results) == 2


    knowledge_ids = [

        result["knowledge_id"]

        for result in results

    ]


    assert 2 not in knowledge_ids


    print(
        "PASS: test_missing_search_index"
    )


# ==========================================
# Missing Knowledge Score
# ==========================================


def test_missing_knowledge_score():

    service = create_service()

    service.knowledge_score_repo.data.pop(
        2
    )


    results = service.search_ranked(

        "AI",

        limit=10

    )


    # 沒有 KnowledgeScore 時，
    # Retrieval 仍然保留該候選。
    assert len(results) == 3


    result = next(

        item

        for item in results

        if item["knowledge_id"] == 2

    )


    assert result["knowledge_score"] is None


    # Importance / Confidence /
    # Ranking 應安全回到 0。
    assert (
        result["search_score"].importance_score
        == 0.0
    )


    assert (
        result["search_score"].confidence_score
        == 0.0
    )


    assert (
        result["search_score"].ranking_score
        == 0.0
    )


    print(
        "PASS: test_missing_knowledge_score"
    )


# ==========================================
# Missing Article
# ==========================================


def test_missing_article():

    service = create_service()


    original_method = (

        service.knowledge_repo
        .get_with_article

    )


    def get_without_article(
        knowledge_id
    ):

        if knowledge_id == 2:

            return None


        return original_method(

            knowledge_id

        )


    service.knowledge_repo.get_with_article = (

        get_without_article

    )


    results = service.search_ranked(

        "AI",

        limit=10

    )


    knowledge_ids = [

        result["knowledge_id"]

        for result in results

    ]


    assert 2 not in knowledge_ids


    print(
        "PASS: test_missing_article"
    )


# ==========================================
# Ranking Order
# ==========================================


def test_best_result_first():

    service = create_service()

    results = service.search_ranked(

        "AI",

        limit=10

    )


    assert len(results) == 3

    assert (

        results[0]["final_score"]

        >=

        results[1]["final_score"]

    )


    assert (

        results[1]["final_score"]

        >=

        results[2]["final_score"]

    )


    print(
        "PASS: test_best_result_first"
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
        "P2.6 Step 10"
    )

    print(
        "Retrieval Service Ranking Integration Test"
    )

    print(
        "=========="
    )

    print()


    tests = [

        # ------------------------------
        # Validation
        # ------------------------------

        test_empty_keyword,

        test_invalid_limit,

        test_negative_limit,

        # ------------------------------
        # Retrieval
        # ------------------------------

        test_candidate_retrieval,

        test_search_index_retrieval,

        test_knowledge_score_retrieval,

        # ------------------------------
        # Ranking
        # ------------------------------

        test_ranking_calculation,

        test_final_score_sorting,

        test_best_result_first,

        # ------------------------------
        # Result
        # ------------------------------

        test_result_limit,

        test_result_fields,

        # ------------------------------
        # Missing Data
        # ------------------------------

        test_missing_search_index,

        test_missing_knowledge_score,

        test_missing_article

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
