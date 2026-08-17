"""
tests/test_p3_3_archive_management_api.py

AutoSearch V4

P3.3

Archive Management API Tests

測試：

    1. Management Status
    2. Statistics
    3. Article Management
    4. Article Versions
    5. Knowledge Management
    6. Knowledge History
    7. Knowledge Evolution
    8. Composite Archive Search
    9. Search Index Management
    10. Management Health

注意：

    本測試使用 Mock Service。

    不直接操作 MySQL。
"""


from fastapi.testclient import TestClient

from api.main import app


# ============================================================
# Import Router Module
# ============================================================

from api.routes import archive_management


# ============================================================
# Mock Archive Management Service
# ============================================================

class MockArchiveManagementService:
    """
    P3.3 API Test Mock Service。

    模擬 Archive Management Service。

    不連接 Database。
    """

    def __init__(self):

        self.statistics_calls = 0

        self.article_calls = 0

        self.version_calls = 0

        self.knowledge_calls = 0

        self.search_calls = 0

    # ==================================================
    # Statistics
    # ==================================================

    def get_statistics(self):

        self.statistics_calls += 1

        return {

            "articles": 10,

            "archive_versions": 20

        }

    # ==================================================
    # Articles
    # ==================================================

    def get_articles(self):

        return [

            {

                "id": 1,

                "title":
                    "Test Article",

                "source":
                    "CNA"

            },

            {

                "id": 2,

                "title":
                    "Second Article",

                "source":
                    "Reuters"

            }

        ]

    # ==================================================

    def get_article(
        self,
        article_id
    ):

        self.article_calls += 1

        if article_id == 1:

            return {

                "id": 1,

                "title":
                    "Test Article",

                "source":
                    "CNA"

            }

        return None

    # ==================================================
    # Versions
    # ==================================================

    def get_versions(
        self,
        article_id
    ):

        self.version_calls += 1

        if article_id != 1:

            return []

        return [

            {

                "id": 1,

                "article_id": 1,

                "version_number": 1

            },

            {

                "id": 2,

                "article_id": 1,

                "version_number": 2

            }

        ]

    # ==================================================
    # Knowledge History
    # ==================================================

    def get_knowledge_history(
        self,
        article_id
    ):

        self.knowledge_calls += 1

        return [

            {

                "version": 1,

                "topic":
                    "Semiconductor"

            },

            {

                "version": 2,

                "topic":
                    "AI"

            }

        ]

    # ==================================================
    # Latest Knowledge
    # ==================================================

    def get_latest_knowledge(
        self,
        article_id
    ):

        return {

            "version": 2,

            "topic":
                "AI"

        }

    # ==================================================
    # Knowledge Evolution
    # ==================================================

    def get_knowledge_evolution(
        self,
        article_id
    ):

        return [

            {

                "version": 1,

                "topic":
                    "Semiconductor"

            },

            {

                "version": 2,

                "topic":
                    "AI"

            }

        ]

    # ==================================================
    # Composite Search
    # ==================================================

    def composite_search(
        self,
        keyword=None,
        source=None,
        date_from=None,
        date_to=None,
        year=None,
        month=None,
        category=None,
        importance_min=None,
        importance_max=None,
        page=1,
        page_size=20
    ):

        self.search_calls += 1

        return {

            "results": [

                {

                    "id": 1,

                    "title":
                        "TSMC Test Article"

                }

            ],

            "total": 1,

            "page": page,

            "page_size": page_size,

            "filters": {

                key: value

                for key, value in {

                    "keyword":
                        keyword,

                    "source":
                        source,

                    "date_from":
                        date_from,

                    "date_to":
                        date_to,

                    "year":
                        year,

                    "month":
                        month,

                    "category":
                        category,

                    "importance_min":
                        importance_min,

                    "importance_max":
                        importance_max

                }.items()

                if value is not None

            }

        }


# ============================================================
# Fixtures
# ============================================================

mock_service = MockArchiveManagementService()

archive_management._service = mock_service


client = TestClient(
    app
)


# ============================================================
# Management Status
# ============================================================

def test_management_status():

    response = client.get(
        "/management/archive/status"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"

    assert data["service"] == (
        "archive-management"
    )

    assert data["version"] == (
        "V4-P2.4.1"
    )


# ============================================================
# Statistics
# ============================================================

def test_management_statistics():

    response = client.get(
        "/management/archive/statistics"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["articles"] == 10

    assert data["archive_versions"] == 20

    assert (
        mock_service.statistics_calls
        >= 1
    )


# ============================================================
# Article List
# ============================================================

def test_management_articles():

    response = client.get(
        "/management/archive/articles"
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(
        data,
        list
    )

    assert len(data) == 2

    assert data[0]["id"] == 1


# ============================================================
# Article By ID
# ============================================================

def test_management_article():

    response = client.get(
        "/management/archive/articles/1"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == 1

    assert data["title"] == (
        "Test Article"
    )


# ============================================================

def test_management_article_not_found():

    response = client.get(
        "/management/archive/articles/999"
    )

    assert response.status_code == 404

    data = response.json()

    assert data["detail"] == (
        "Archive article not found"
    )


# ============================================================
# Article Versions
# ============================================================

def test_management_article_versions():

    response = client.get(
        "/management/archive/articles/1/versions"
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(
        data,
        list
    )

    assert len(data) == 2

    assert (
        data[0]["version_number"]
        == 1
    )

    assert (
        data[1]["version_number"]
        == 2
    )


# ============================================================
# Knowledge Management
# ============================================================

def test_management_knowledge():

    response = client.get(
        "/management/archive/knowledge/1"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["article_id"] == 1

    assert "history" in data

    assert "latest" in data

    assert "evolution" in data

    assert len(
        data["history"]
    ) == 2

    assert (
        data["latest"]["version"]
        == 2
    )


# ============================================================
# Knowledge History
# ============================================================

def test_management_knowledge_history():

    response = client.get(
        "/management/archive/knowledge/1/history"
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(
        data,
        list
    )

    assert len(data) == 2


# ============================================================
# Knowledge Evolution
# ============================================================

def test_management_knowledge_evolution():

    response = client.get(
        "/management/archive/knowledge/1/evolution"
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(
        data,
        list
    )

    assert len(data) == 2

    assert (
        data[0]["version"]
        == 1
    )

    assert (
        data[1]["version"]
        == 2
    )


# ============================================================
# Composite Search
# ============================================================

def test_composite_archive_search():

    response = client.get(
        "/management/archive/search"
    )

    assert response.status_code == 200

    data = response.json()

    assert "results" in data

    assert "total" in data

    assert "page" in data

    assert "page_size" in data

    assert data["page"] == 1

    assert data["page_size"] == 20


# ============================================================
# Composite Search Keyword
# ============================================================

def test_composite_archive_search_keyword():

    response = client.get(
        "/management/archive/search",
        params={

            "keyword":
                "TSMC"

        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["filters"]["keyword"] == (
        "TSMC"
    )


# ============================================================
# Composite Search Multiple Filters
# ============================================================

def test_composite_archive_search_filters():

    response = client.get(
        "/management/archive/search",
        params={

            "keyword":
                "TSMC",

            "source":
                "CNA",

            "year":
                2026,

            "month":
                8,

            "category":
                "Semiconductor",

            "importance_min":
                8,

            "importance_max":
                10,

            "page":
                2,

            "page_size":
                5

        }
    )

    assert response.status_code == 200

    data = response.json()

    filters = data["filters"]

    assert filters["keyword"] == (
        "TSMC"
    )

    assert filters["source"] == (
        "CNA"
    )

    assert filters["year"] == 2026

    assert filters["month"] == 8

    assert filters["category"] == (
        "Semiconductor"
    )

    assert filters["importance_min"] == 8

    assert filters["importance_max"] == 10

    assert data["page"] == 2

    assert data["page_size"] == 5


# ============================================================
# Search Index
# ============================================================

def test_index_management():

    response = client.get(
        "/management/archive/index"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == (
        "available"
    )

    assert data["service"] == (
        "archive-search-index"
    )

    assert "status" in (
        data["operations"]
    )

    assert "refresh" in (
        data["operations"]
    )

    assert "rebuild" in (
        data["operations"]
    )


# ============================================================
# Management Health
# ============================================================

def test_management_health():

    response = client.get(
        "/management/archive/health"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"

    assert data["service"] == (
        "archive-management"
    )

    assert data["version"] == (
        "V4-P2.4.1"
    )


# ============================================================
# HTTP Method Validation
# ============================================================

def test_management_status_wrong_method():

    response = client.post(
        "/management/archive/status"
    )

    assert response.status_code == 405


def test_management_statistics_wrong_method():

    response = client.post(
        "/management/archive/statistics"
    )

    assert response.status_code == 405


def test_management_articles_wrong_method():

    response = client.post(
        "/management/archive/articles"
    )

    assert response.status_code == 405


# ============================================================
# Article ID Validation
# ============================================================

def test_management_article_invalid_id():

    response = client.get(
        "/management/archive/articles/abc"
    )

    assert response.status_code == 422


# ============================================================
# Search Query Validation
# ============================================================

def test_composite_search_invalid_year():

    response = client.get(
        "/management/archive/search",
        params={
            "year": "invalid"
        }
    )

    assert response.status_code == 422


def test_composite_search_invalid_month():

    response = client.get(
        "/management/archive/search",
        params={
            "month": "invalid"
        }
    )

    assert response.status_code == 422


def test_composite_search_invalid_page():

    response = client.get(
        "/management/archive/search",
        params={
            "page": "invalid"
        }
    )

    assert response.status_code == 422


def test_composite_search_invalid_page_size():

    response = client.get(
        "/management/archive/search",
        params={
            "page_size": "invalid"
        }
    )

    assert response.status_code == 422


# ============================================================
# API Root Availability
# ============================================================

def test_management_router_available():

    response = client.get(
        "/management/archive/status"
    )

    assert response.status_code == 200


# ============================================================
# Test Complete
# ============================================================

def test_p3_3_api_test_suite_available():

    assert client is not None

    assert mock_service is not None