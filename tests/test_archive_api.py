"""
tests/test_archive_api.py

AutoSearch V4

P2.3.9 API/UI Integration

測試:

    1. Archive Router
    2. Article List
    3. Article
    4. Versions
    5. Latest Version
    6. Date
    7. Month
    8. Year
    9. Source
    10. Search
    11. Count
    12. Article Count
    13. Count By Source
    14. Count By Date
    15. Statistics
    16. Pagination
    17. Knowledge History
    18. Latest Knowledge
    19. Knowledge Evolution
    20. Health
    21. Error Handling
"""

import pytest

from fastapi import FastAPI
from fastapi.testclient import TestClient

from api.routes import archive


# ============================================================
# Fake Archive Service
# ============================================================

class FakeArchiveService:
    """
    測試用 ArchiveWebService。
    """

    def get_articles(self, limit=100):

        return [
            {
                "id": 1,
                "title": "TSMC 2nm",
                "source": "TechNews"
            },
            {
                "id": 2,
                "title": "AI Semiconductor",
                "source": "CNA"
            }
        ][:limit]

    def get_article(self, article_id):

        if article_id == 1:

            return {
                "id": 1,
                "title": "TSMC 2nm",
                "source": "TechNews"
            }

        return None

    def get_versions(self, article_id):

        return [
            {
                "version_id": 10,
                "article_id": article_id,
                "version_number": 1
            },
            {
                "version_id": 11,
                "article_id": article_id,
                "version_number": 2
            }
        ]

    def get_latest_version(self, article_id):

        if article_id != 1:

            return None

        return {
            "version_id": 11,
            "article_id": article_id,
            "version_number": 2
        }

    def get_by_date(self, archive_date):

        return [
            {
                "id": 1,
                "date": archive_date
            }
        ]

    def get_by_month(self, year, month):

        return [
            {
                "id": 1,
                "year": year,
                "month": month
            }
        ]

    def get_by_year(self, year):

        return [
            {
                "id": 1,
                "year": year
            }
        ]

    def get_by_source(self, source):

        return [
            {
                "id": 1,
                "source": source
            }
        ]

    def search(self, query):

        if not query:

            return []

        return [
            {
                "id": 1,
                "title": "TSMC 2nm",
                "query": query
            }
        ]

    def count(self):

        return 10

    def count_articles(self):

        return 5

    def count_by_source(self, source):

        if source == "Unknown":

            return 0

        return 3

    def count_by_date(self, archive_date):

        return 2

    def get_statistics(self):

        return {
            "total": 10,
            "articles": 5,
            "sources": 2
        }

    def get_articles_with_pagination(
        self,
        page=1,
        page_size=20
    ):

        return {
            "page": page,
            "page_size": page_size,
            "total": 5,
            "items": [
                {
                    "id": 1,
                    "title": "TSMC 2nm"
                }
            ]
        }

    def get_knowledge_history(self, article_id):

        if article_id != 1:

            return []

        return [
            {
                "article_id": article_id,
                "version_number": 1,
                "summary": "Initial knowledge"
            },
            {
                "article_id": article_id,
                "version_number": 2,
                "summary": "Updated knowledge"
            }
        ]

    def get_latest_knowledge(self, article_id):

        if article_id != 1:

            return None

        return {
            "article_id": article_id,
            "version_number": 2,
            "summary": "Updated knowledge"
        }

    def get_knowledge_evolution(self, article_id):

        if article_id != 1:

            return []

        return [
            {
                "version_number": 1,
                "summary": "Initial knowledge"
            },
            {
                "version_number": 2,
                "summary": "Updated knowledge"
            }
        ]


# ============================================================
# Fixtures
# ============================================================

@pytest.fixture
def fake_service():

    return FakeArchiveService()


@pytest.fixture
def client(fake_service):

    app = FastAPI()

    archive._service = fake_service

    app.include_router(
        archive.router
    )

    return TestClient(app)


# ============================================================
# Router
# ============================================================

def test_archive_router(client):

    response = client.get(
        "/archive/health"
    )

    assert response.status_code == 200


# ============================================================
# Articles
# ============================================================

def test_get_articles(client):

    response = client.get(
        "/archive/articles"
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(
        data,
        list
    )

    assert len(data) == 2


def test_get_articles_with_limit(client):

    response = client.get(
        "/archive/articles?limit=1"
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1


# ============================================================
# Article
# ============================================================

def test_get_article(client):

    response = client.get(
        "/archive/articles/1"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == 1


def test_get_nonexistent_article(client):

    response = client.get(
        "/archive/articles/999"
    )

    assert response.status_code == 404


# ============================================================
# Versions
# ============================================================

def test_get_versions(client):

    response = client.get(
        "/archive/articles/1/versions"
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2


def test_get_latest_version(client):

    response = client.get(
        "/archive/articles/1/versions/latest"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["version_number"] == 2


def test_get_latest_version_not_found(client):

    response = client.get(
        "/archive/articles/999/versions/latest"
    )

    assert response.status_code == 404


# ============================================================
# Date
# ============================================================

def test_get_by_date(client):

    response = client.get(
        "/archive/date/2026-08-08"
    )

    assert response.status_code == 200

    data = response.json()

    assert data[0]["date"] == "2026-08-08"


# ============================================================
# Month
# ============================================================

def test_get_by_month(client):

    response = client.get(
        "/archive/month/2026/8"
    )

    assert response.status_code == 200

    data = response.json()

    assert data[0]["year"] == 2026

    assert data[0]["month"] == 8


def test_invalid_month(client):

    response = client.get(
        "/archive/month/2026/13"
    )

    assert response.status_code == 400


# ============================================================
# Year
# ============================================================

def test_get_by_year(client):

    response = client.get(
        "/archive/year/2026"
    )

    assert response.status_code == 200

    data = response.json()

    assert data[0]["year"] == 2026


# ============================================================
# Source
# ============================================================

def test_get_by_source(client):

    response = client.get(
        "/archive/source/TechNews"
    )

    assert response.status_code == 200

    data = response.json()

    assert data[0]["source"] == "TechNews"


# ============================================================
# Search
# ============================================================

def test_search_archive(client):

    response = client.get(
        "/archive/search?q=TSMC"
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1

    assert data[0]["query"] == "TSMC"


def test_search_empty_query(client):

    response = client.get(
        "/archive/search?q="
    )

    assert response.status_code == 422


# ============================================================
# Count
# ============================================================

def test_count_archive(client):

    response = client.get(
        "/archive/count"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["count"] == 10


def test_count_articles(client):

    response = client.get(
        "/archive/count/articles"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["count"] == 5


def test_count_by_source(client):

    response = client.get(
        "/archive/count/source/TechNews"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["source"] == "TechNews"

    assert data["count"] == 3


def test_count_by_date(client):

    response = client.get(
        "/archive/count/date/2026-08-08"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["date"] == "2026-08-08"

    assert data["count"] == 2


# ============================================================
# Statistics
# ============================================================

def test_get_statistics(client):

    response = client.get(
        "/archive/statistics"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 10

    assert data["articles"] == 5

    assert data["sources"] == 2


# ============================================================
# Pagination
# ============================================================

def test_get_articles_with_pagination(client):

    response = client.get(
        "/archive/articles/page?page=2&page_size=10"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["page"] == 2

    assert data["page_size"] == 10

    assert data["total"] == 5


# ============================================================
# Knowledge History
# ============================================================

def test_get_knowledge_history(client):

    response = client.get(
        "/archive/knowledge/1/history"
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2

    assert data[0]["version_number"] == 1

    assert data[1]["version_number"] == 2


def test_get_latest_knowledge(client):

    response = client.get(
        "/archive/knowledge/1/latest"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["version_number"] == 2


def test_get_latest_knowledge_not_found(client):

    response = client.get(
        "/archive/knowledge/999/latest"
    )

    assert response.status_code == 404


def test_get_knowledge_evolution(client):

    response = client.get(
        "/archive/knowledge/1/evolution"
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2

    assert data[0]["version_number"] == 1

    assert data[1]["version_number"] == 2


def test_empty_knowledge_history(client):

    response = client.get(
        "/archive/knowledge/999/history"
    )

    assert response.status_code == 200

    data = response.json()

    assert data == []


# ============================================================
# Health
# ============================================================

def test_archive_health(client):

    response = client.get(
        "/archive/health"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"

    assert data["service"] == "archive"

    assert data["version"] == "V4-P2.3.9"