"""
tests/test_search_api.py

AutoSearch V4

P3.8

Search API Tests

測試:

1. Full Search
2. Keyword Search
3. Entity Search
4. Hybrid Search
5. Search Pagination
6. Hybrid Search Pagination
7. Search Index All

錯誤:

8. Empty Search
9. Empty Keyword
10. Empty Entity
11. Empty Hybrid Search
12. Invalid Page
13. Invalid Page Size

OpenAPI:

14. Search API Routes
15. Search API HTTP Methods
"""


import pytest

from fastapi import (
    FastAPI
)

from fastapi.testclient import (
    TestClient
)


from api.routes.search import (
    router
)


import api.routes.search as search_module


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
        id,
        knowledge_id,
        search_text,
        keywords,
        entities,
        topic
    ):

        self.id = id

        self.knowledge_id = knowledge_id

        self.search_text = search_text

        self.keywords = keywords

        self.entities = entities

        self.topic = topic

        self.embedding_reference = None

        self.index_version = "1.0"

        self.created_time = None


    def to_dict(self):

        return {

            "id":
                self.id,

            "knowledge_id":
                self.knowledge_id,

            "search_text":
                self.search_text,

            "keywords":
                self.keywords,

            "entities":
                self.entities,

            "topic":
                self.topic,

            "embedding_reference":
                self.embedding_reference,

            "index_version":
                self.index_version,

            "created_time":
                self.created_time

        }


# ==================================================
# Fake Ranking Score
# ==================================================

class FakeSearchScore:

    def __init__(
        self,
        final_score
    ):

        self.final_score = final_score


    def to_dict(self):

        return {

            "keyword_score": 5,

            "entity_score": 5,

            "topic_score": 5,

            "importance_score": 5,

            "confidence_score": 5,

            "freshness_score": 5,

            "ranking_score": 5,

            "final_score":
                self.final_score

        }


# ==================================================
# Fake Ranking Service
# ==================================================

class FakeRankingService:

    def build_search_score(
        self,
        query,
        search_index
    ):

        if search_index.id == 1:

            return FakeSearchScore(
                9.5
            )

        if search_index.id == 2:

            return FakeSearchScore(
                8.0
            )

        return FakeSearchScore(
            6.0
        )


# ==================================================
# Fake Repository
# ==================================================

class FakeSearchIndexRepository:

    def __init__(self):

        self.indexes = [

            FakeSearchIndex(

                id=1,

                knowledge_id=1,

                search_text=(
                    "AI Semiconductor "
                    "NVIDIA TSMC"
                ),

                keywords=[
                    "AI",
                    "Semiconductor",
                    "NVIDIA"
                ],

                entities=[
                    "AI",
                    "NVIDIA",
                    "台積電"
                ],

                topic="Semiconductor"

            ),

            FakeSearchIndex(

                id=2,

                knowledge_id=2,

                search_text=(
                    "Artificial Intelligence "
                    "GPU NVIDIA"
                ),

                keywords=[
                    "AI",
                    "GPU",
                    "NVIDIA"
                ],

                entities=[
                    "AI",
                    "NVIDIA",
                    "GPU"
                ],

                topic=(
                    "Artificial Intelligence"
                )

            ),

            FakeSearchIndex(

                id=3,

                knowledge_id=3,

                search_text=(
                    "Python Programming"
                ),

                keywords=[
                    "Python",
                    "Programming"
                ],

                entities=[
                    "Python"
                ],

                topic=(
                    "Python Programming"
                )

            )

        ]


    # ==================================
    # Keyword Search
    # ==================================

    def search_keyword(
        self,
        keyword
    ):

        keyword = keyword.lower()

        return [

            item

            for item in self.indexes

            if (

                keyword in
                item.search_text.lower()

                or

                any(

                    keyword in
                    value.lower()

                    for value in
                    item.keywords

                )

            )

        ]


    # ==================================
    # Entity Search
    # ==================================

    def search_entity(
        self,
        entity
    ):

        entity = entity.lower()

        return [

            item

            for item in self.indexes

            if any(

                entity in
                value.lower()

                for value in
                item.entities

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
# Fixture
# ==================================================

@pytest.fixture(
    autouse=True
)
def mock_search_service(
    monkeypatch
):

    repository = (
        FakeSearchIndexRepository()
    )

    ranking_service = (
        FakeRankingService()
    )

    service = (
        search_module.SearchService(

            repository=repository,

            ranking_service=ranking_service

        )
    )

    monkeypatch.setattr(

        search_module,

        "service",

        service

    )

    return service


# ==================================================
# P3.8.1
# Full Search
# ==================================================

def test_full_search():

    response = client.get(
        "/search?q=AI"
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
# Full Search Ranking
# ==================================================

def test_full_search_ranking():

    response = client.get(
        "/search?q=AI"
    )

    assert response.status_code == 200

    data = response.json()

    assert (
        data["data"][0]["score"]["final_score"]
        >=
        data["data"][1]["score"]["final_score"]
    )


# ==================================================
# P3.8.2
# Keyword Search
# ==================================================

def test_keyword_search():

    response = client.get(
        "/search/keyword/AI"
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
# Keyword Case Insensitive
# ==================================================

def test_keyword_search_case_insensitive():

    response = client.get(
        "/search/keyword/ai"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    assert data["count"] == 2


# ==================================================
# P3.8.3
# Entity Search
# ==================================================

def test_entity_search():

    response = client.get(
        "/search/entity/NVIDIA"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    assert data["entity"] == "NVIDIA"

    assert data["count"] == 2


# ==================================================
# Entity Case Insensitive
# ==================================================

def test_entity_search_case_insensitive():

    response = client.get(
        "/search/entity/nvidia"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    assert data["count"] == 2


# ==================================================
# P3.8.4
# Hybrid Search
# ==================================================

def test_hybrid_search():

    response = client.get(
        "/search/hybrid?q=AI"
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
# Hybrid Deduplication
# ==================================================

def test_hybrid_search_deduplication():

    response = client.get(
        "/search/hybrid?q=NVIDIA"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    ids = [

        item["search_index"]["id"]

        for item in data["data"]

    ]

    assert len(ids) == len(
        set(ids)
    )


# ==================================================
# P3.8.5
# Search Pagination
# ==================================================

def test_search_pagination():

    response = client.get(

        "/search/paginated"
        "?q=AI"
        "&page=1"
        "&page_size=1"

    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    assert data["keyword"] == "AI"

    assert data["page"] == 1

    assert data["page_size"] == 1

    assert data["total"] == 2

    assert data["count"] == 1

    assert len(
        data["data"]
    ) == 1


# ==================================================
# Search Pagination Page 2
# ==================================================

def test_search_pagination_page_two():

    response = client.get(

        "/search/paginated"
        "?q=AI"
        "&page=2"
        "&page_size=1"

    )

    assert response.status_code == 200

    data = response.json()

    assert data["page"] == 2

    assert data["total"] == 2

    assert data["count"] == 1


# ==================================================
# P3.8.6
# Hybrid Pagination
# ==================================================

def test_hybrid_search_pagination():

    response = client.get(

        "/search/hybrid/paginated"
        "?q=AI"
        "&page=1"
        "&page_size=1"

    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    assert data["keyword"] == "AI"

    assert data["page"] == 1

    assert data["page_size"] == 1

    assert data["total"] == 2

    assert data["count"] == 1


# ==================================================
# P3.8.7
# Get All
# ==================================================

def test_get_all_search_index():

    response = client.get(
        "/search/all"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    assert data["count"] == 3

    assert len(
        data["data"]
    ) == 3


# ==================================================
# Empty Search
# ==================================================

def test_empty_search():

    response = client.get(
        "/search?q=%20"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    assert data["count"] == 0

    assert data["data"] == []


# ==================================================
# Empty Keyword
# ==================================================

def test_empty_keyword():

    response = client.get(
        "/search/keyword/%20"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    assert data["count"] == 0

    assert data["data"] == []


# ==================================================
# Empty Entity
# ==================================================

def test_empty_entity():

    response = client.get(
        "/search/entity/%20"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    assert data["count"] == 0

    assert data["data"] == []


# ==================================================
# Empty Hybrid Search
# ==================================================

def test_empty_hybrid_search():

    response = client.get(
        "/search/hybrid?q=%20"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    assert data["count"] == 0

    assert data["data"] == []


# ==================================================
# Invalid Page
# ==================================================

@pytest.mark.parametrize(
    "page",
    [
        0,
        -1
    ]
)
def test_invalid_page(
    page
):

    response = client.get(

        "/search/paginated"
        f"?q=AI&page={page}"

    )

    assert response.status_code == 422


# ==================================================
# Invalid Page Size
# ==================================================

@pytest.mark.parametrize(
    "page_size",
    [
        0,
        -1,
        101
    ]
)
def test_invalid_page_size(
    page_size
):

    response = client.get(

        "/search/paginated"
        f"?q=AI&page_size={page_size}"

    )

    assert response.status_code == 422


# ==================================================
# OpenAPI Routes
# ==================================================

def test_search_openapi_paths():

    response = client.get(
        "/openapi.json"
    )

    assert response.status_code == 200

    paths = response.json()["paths"]

    assert "/search" in paths

    assert (
        "/search/keyword/{keyword}"
        in paths
    )

    assert (
        "/search/entity/{entity}"
        in paths
    )

    assert (
        "/search/hybrid"
        in paths
    )

    assert (
        "/search/paginated"
        in paths
    )

    assert (
        "/search/hybrid/paginated"
        in paths
    )

    assert (
        "/search/all"
        in paths
    )


# ==================================================
# HTTP Methods
# ==================================================

def test_search_http_methods():

    response = client.get(
        "/openapi.json"
    )

    assert response.status_code == 200

    paths = response.json()["paths"]

    assert "get" in paths[
        "/search"
    ]

    assert "get" in paths[
        "/search/keyword/{keyword}"
    ]

    assert "get" in paths[
        "/search/entity/{entity}"
    ]

    assert "get" in paths[
        "/search/hybrid"
    ]

    assert "get" in paths[
        "/search/paginated"
    ]

    assert "get" in paths[
        "/search/hybrid/paginated"
    ]

    assert "get" in paths[
        "/search/all"
    ]