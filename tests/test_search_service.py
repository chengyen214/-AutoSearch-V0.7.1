"""
tests/test_search_service.py

AutoSearch V4

P3.8

Search Service Tests

測試：

1. Keyword Search
2. Entity Search
3. Empty Query
4. Search Ranking
5. Final Search Score
6. Hybrid Search
7. Hybrid Search Deduplication
8. Search Pagination
9. Hybrid Pagination
10. Get All
11. Query Normalize
12. Invalid Pagination
"""


from models.knowledge_search_score import (
    KnowledgeSearchScore
)

from services.search_service import (
    SearchService
)


# ==================================================
# Fake Search Index
# ==================================================

class FakeSearchIndex:

    def __init__(
        self,
        index_id,
        knowledge_id,
        search_text="",
        keywords=None,
        entities=None,
        topic=""
    ):

        self.id = index_id

        self.knowledge_id = knowledge_id

        self.search_text = search_text

        self.keywords = (
            keywords
            if keywords is not None
            else []
        )

        self.entities = (
            entities
            if entities is not None
            else []
        )

        self.topic = topic


# ==================================================
# Fake Repository
# ==================================================

class FakeSearchIndexRepository:
    """
    Fake Search Index Repository。

    不連接 MySQL。
    """

    def __init__(self):

        self.indexes = [

            FakeSearchIndex(
                1,
                101,
                search_text="AI semiconductor",
                keywords=[
                    "AI",
                    "semiconductor"
                ],
                entities=[
                    "NVIDIA",
                    "台積電"
                ],
                topic="Semiconductor"
            ),

            FakeSearchIndex(
                2,
                102,
                search_text="AI GPU",
                keywords=[
                    "AI",
                    "GPU"
                ],
                entities=[
                    "NVIDIA"
                ],
                topic="Artificial Intelligence"
            ),

            FakeSearchIndex(
                3,
                103,
                search_text="Python programming",
                keywords=[
                    "Python"
                ],
                entities=[
                    "Python"
                ],
                topic="Programming"
            ),

            FakeSearchIndex(
                4,
                104,
                search_text="AI hardware",
                keywords=[
                    "AI",
                    "hardware"
                ],
                entities=[
                    "NVIDIA"
                ],
                topic="AI Hardware"
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

                query in item.search_text.lower()

                or

                any(
                    query in str(keyword).lower()
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

                query in str(entity).lower()

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

class FakeSearchRankingService:
    """
    Fake Ranking Service。

    用固定規則產生 KnowledgeSearchScore。
    """

    def build_search_score(
        self,
        query,
        search_index
    ):

        query = query.lower()

        keyword_score = 0

        entity_score = 0

        topic_score = 0

        importance_score = 5

        confidence_score = 5

        freshness_score = 5

        ranking_score = 5

        # ==================================
        # Keyword
        # ==================================

        if any(

            query == str(keyword).lower()

            for keyword in search_index.keywords

        ):

            keyword_score = 10

        elif query in search_index.search_text.lower():

            keyword_score = 8

        # ==================================
        # Entity
        # ==================================

        if any(

            query == str(entity).lower()

            for entity in search_index.entities

        ):

            entity_score = 10

        # ==================================
        # Topic
        # ==================================

        if query in search_index.topic.lower():

            topic_score = 10

        # ==================================
        # Ranking
        # ==================================

        ranking_score = (

            keyword_score
            + entity_score
            + topic_score

        ) / 3

        return KnowledgeSearchScore(

            keyword_score=keyword_score,

            entity_score=entity_score,

            topic_score=topic_score,

            importance_score=importance_score,

            confidence_score=confidence_score,

            freshness_score=freshness_score,

            ranking_score=ranking_score

        )


# ==================================================
# Fixture Helper
# ==================================================

def create_service():

    repository = (
        FakeSearchIndexRepository()
    )

    ranking_service = (
        FakeSearchRankingService()
    )

    return SearchService(

        repository=repository,

        ranking_service=ranking_service

    )


# ==================================================
# 1. Keyword Search
# ==================================================

def test_keyword_search():

    service = create_service()

    result = service.search_keyword(
        "AI"
    )

    assert isinstance(
        result,
        list
    )

    assert len(result) == 3


# ==================================================
# 2. Entity Search
# ==================================================

def test_entity_search():

    service = create_service()

    result = service.search_entity(
        "NVIDIA"
    )

    assert isinstance(
        result,
        list
    )

    assert len(result) == 3


# ==================================================
# 3. Empty Query
# ==================================================

def test_empty_query():

    service = create_service()

    result = service.search(
        "   "
    )

    assert result == []


# ==================================================
# 4. Search Ranking
# ==================================================

def test_search_ranking():

    service = create_service()

    result = service.search(
        "AI"
    )

    assert len(result) == 3

    scores = [

        item["score"].final_score

        for item in result

    ]

    assert scores == sorted(
        scores,
        reverse=True
    )


# ==================================================
# 5. Final Search Score
# ==================================================

def test_final_search_score():

    service = create_service()

    result = service.search(
        "AI"
    )

    for item in result:

        score = item["score"]

        assert isinstance(
            score,
            KnowledgeSearchScore
        )

        assert isinstance(
            score.final_score,
            float
        )


# ==================================================
# 6. Hybrid Search
# ==================================================

def test_hybrid_search():

    service = create_service()

    result = service.hybrid_search(
        "NVIDIA"
    )

    assert isinstance(
        result,
        list
    )

    assert len(result) == 3


# ==================================================
# 7. Hybrid Search Deduplication
# ==================================================

def test_hybrid_search_deduplication():

    service = create_service()

    result = service.hybrid_search(
        "AI"
    )

    ids = [

        item["search_index"].id

        for item in result

    ]

    assert len(ids) == len(
        set(ids)
    )


# ==================================================
# 8. Search Pagination
# ==================================================

def test_search_pagination():

    service = create_service()

    result = service.search_paginated(

        "AI",

        page=1,

        page_size=2

    )

    assert result["query"] == "AI"

    assert result["page"] == 1

    assert result["page_size"] == 2

    assert result["total"] == 3

    assert result["count"] == 2

    assert len(
        result["data"]
    ) == 2


# ==================================================
# 9. Hybrid Pagination
# ==================================================

def test_hybrid_pagination():

    service = create_service()

    result = (
        service.hybrid_search_paginated(

            "NVIDIA",

            page=1,

            page_size=2

        )
    )

    assert result["query"] == "NVIDIA"

    assert result["page"] == 1

    assert result["page_size"] == 2

    assert result["total"] == 3

    assert result["count"] == 2

    assert len(
        result["data"]
    ) == 2


# ==================================================
# 10. Get All
# ==================================================

def test_get_all():

    service = create_service()

    result = service.get_all()

    assert isinstance(
        result,
        list
    )

    assert len(result) == 4


# ==================================================
# 11. Query Normalize
# ==================================================

def test_query_normalize():

    service = create_service()

    result = service.search(
        "  AI  "
    )

    assert len(result) == 3


# ==================================================
# 12. Invalid Pagination
# ==================================================

def test_invalid_pagination():

    service = create_service()

    result = service.search_paginated(

        "AI",

        page=0,

        page_size=0

    )

    assert result["page"] == 1

    assert result["page_size"] == 20


# ==================================================
# 13. Invalid Pagination String
# ==================================================

def test_invalid_pagination_string():

    service = create_service()

    result = service.search_paginated(

        "AI",

        page="invalid",

        page_size="invalid"

    )

    assert result["page"] == 1

    assert result["page_size"] == 20


# ==================================================
# 14. Pagination Second Page
# ==================================================

def test_search_pagination_second_page():

    service = create_service()

    result = service.search_paginated(

        "AI",

        page=2,

        page_size=2

    )

    assert result["page"] == 2

    assert result["page_size"] == 2

    assert result["total"] == 3

    assert result["count"] == 1


# ==================================================
# 15. Pagination Out Of Range
# ==================================================

def test_search_pagination_out_of_range():

    service = create_service()

    result = service.search_paginated(

        "AI",

        page=10,

        page_size=20

    )

    assert result["total"] == 3

    assert result["count"] == 0

    assert result["data"] == []


# ==================================================
# 16. Empty Hybrid Search
# ==================================================

def test_empty_hybrid_search():

    service = create_service()

    result = service.hybrid_search(
        "   "
    )

    assert result == []


# ==================================================
# 17. Empty Paginated Search
# ==================================================

def test_empty_paginated_search():

    service = create_service()

    result = service.search_paginated(

        "   ",

        page=1,

        page_size=20

    )

    assert result["query"] == ""

    assert result["total"] == 0

    assert result["count"] == 0

    assert result["data"] == []


# ==================================================
# 18. Empty Hybrid Pagination
# ==================================================

def test_empty_hybrid_pagination():

    service = create_service()

    result = (
        service.hybrid_search_paginated(

            "   ",

            page=1,

            page_size=20

        )
    )

    assert result["query"] == ""

    assert result["total"] == 0

    assert result["count"] == 0

    assert result["data"] == []


# ==================================================
# 19. Result Structure
# ==================================================

def test_result_structure():

    service = create_service()

    result = service.search(
        "AI"
    )

    assert len(result) > 0

    for item in result:

        assert "search_index" in item

        assert "score" in item

        assert isinstance(

            item["score"],

            KnowledgeSearchScore

        )

        assert hasattr(

            item["score"],

            "final_score"

        )
