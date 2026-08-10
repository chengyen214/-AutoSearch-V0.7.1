"""
tests/test_archive_web_service.py

AutoSearch V4

P2.3.9 Archive Web UI

測試：

1. 建立 ArchiveWebService
2. Repository Injection
3. 取得文章列表
4. 取得單一文章
5. 取得文章 Versions
6. 取得最新 Version
7. 依日期查詢
8. 依月份查詢
9. 依年份查詢
10. 依來源查詢
11. 搜尋 Archive
12. Article Count
13. Version Count
14. Statistics
15. Pagination
16. 不存在 Article
17. 不存在 Source
18. 不存在 Search
19. Knowledge History
20. Knowledge Evolution
21. Repr
"""

import pytest

from services.archive_web_service import (
    ArchiveWebService
)


# ==================================================
# Fake Repository
# ==================================================

class FakeArchiveRepository:
    """
    Fake Archive Browser Repository。

    不連接真實 Database。
    """

    def get_articles(self, limit=None):
        articles = [
            {
                "id": 1,
                "title": "TSMC 2nm",
                "url": "https://example.com/tsmc",
                "source": "TechNews",
            },
            {
                "id": 2,
                "title": "HBM3E Demand",
                "url": "https://example.com/hbm",
                "source": "CNA",
            },
        ]

        if limit is not None:
            return articles[:limit]

        return articles

    def get_article(self, article_id):

        if article_id == 1:

            return {
                "id": 1,
                "title": "TSMC 2nm",
                "url": "https://example.com/tsmc",
                "source": "TechNews",
            }

        return None

    def get_versions(self, article_id):

        if article_id != 1:
            return []

        return [
            {
                "version_id": 10,
                "article_id": 1,
                "version_number": 1,
                "file_hash": "hash-v1",
            },
            {
                "version_id": 11,
                "article_id": 1,
                "version_number": 2,
                "file_hash": "hash-v2",
            },
        ]

    def get_latest_version(self, article_id):

        versions = self.get_versions(
            article_id
        )

        if not versions:
            return None

        return versions[-1]

    def get_by_date(self, archive_date):

        if archive_date == "2026-08-08":

            return [
                {
                    "id": 1,
                    "title": "TSMC 2nm",
                }
            ]

        return []

    def get_by_month(self, year, month):

        if year == 2026 and month == 8:

            return [
                {
                    "id": 1,
                    "title": "TSMC 2nm",
                }
            ]

        return []

    def get_by_year(self, year):

        if year == 2026:

            return [
                {
                    "id": 1,
                    "title": "TSMC 2nm",
                },
                {
                    "id": 2,
                    "title": "HBM3E Demand",
                },
            ]

        return []

    def get_by_source(self, source):

        if source == "TechNews":

            return [
                {
                    "id": 1,
                    "title": "TSMC 2nm",
                    "source": "TechNews",
                }
            ]

        return []

    def search(self, keyword):

        if keyword == "TSMC":

            return [
                {
                    "id": 1,
                    "title": "TSMC 2nm",
                }
            ]

        return []

    def count(self):

        return 2

    def count_articles(self):

        return 2

    def count_by_source(self, source=None):

        if source is None:
            return 2

        if source == "TechNews":
            return 1

        return 0

    def count_by_date(self, archive_date=None):

        if archive_date is None:
            return 2

        if archive_date == "2026-08-08":
            return 1

        return 0

    def get_statistics(self):

        return {
            "total": 2,
            "articles": 2,
            "versions": 3,
        }

    def get_articles_with_pagination(
        self,
        page=1,
        page_size=10
    ):

        return {
            "items": [
                {
                    "id": 1,
                    "title": "TSMC 2nm",
                }
            ],
            "page": page,
            "page_size": page_size,
            "total": 2,
        }


# ==================================================
# Fake Knowledge History
# ==================================================

class FakeKnowledgeHistory:

    def get_history(self, article_id):

        if article_id != 1:
            return []

        return [
            {
                "article_id": 1,
                "version_number": 1,
                "summary": "Initial knowledge",
                "category": "Semiconductor",
                "keywords": ["2nm"],
                "importance": 8,
                "confidence": 0.8,
            },
            {
                "article_id": 1,
                "version_number": 2,
                "summary": "Updated knowledge",
                "category": "Semiconductor",
                "keywords": [
                    "2nm",
                    "AI",
                ],
                "importance": 9,
                "confidence": 0.9,
            },
        ]

    def get_latest(self, article_id):

        history = self.get_history(
            article_id
        )

        if not history:
            return None

        return history[-1]

    def get_evolution(self, article_id):

        return self.get_history(
            article_id
        )


# ==================================================
# Fixtures
# ==================================================

@pytest.fixture
def repository():

    return FakeArchiveRepository()


@pytest.fixture
def service(repository):

    return ArchiveWebService(
        repository=repository
    )


# ==================================================
# Create
# ==================================================

def test_create_archive_web_service(
    service
):

    assert service is not None


# ==================================================
# Repository Injection
# ==================================================

def test_repository_injection(
    service,
    repository
):

    assert (
        service.repository
        is repository
    )


# ==================================================
# Get Articles
# ==================================================

def test_get_articles(
    service
):

    result = service.get_articles()

    assert isinstance(
        result,
        list
    )

    assert len(result) == 2

    assert result[0]["id"] == 1


# ==================================================
# Get Articles With Limit
# ==================================================

def test_get_articles_with_limit(
    service
):

    result = service.get_articles(
        limit=1
    )

    assert len(result) == 1


# ==================================================
# Get Article
# ==================================================

def test_get_article(
    service
):

    result = service.get_article(
        1
    )

    assert result is not None

    assert result["id"] == 1


# ==================================================
# Get Nonexistent Article
# ==================================================

def test_get_nonexistent_article(
    service
):

    result = service.get_article(
        999
    )

    assert result is None


# ==================================================
# Get Versions
# ==================================================

def test_get_versions(
    service
):

    result = service.get_versions(
        1
    )

    assert len(result) == 2

    assert (
        result[0]["version_number"]
        == 1
    )

    assert (
        result[1]["version_number"]
        == 2
    )


# ==================================================
# Get Latest Version
# ==================================================

def test_get_latest_version(
    service
):

    result = service.get_latest_version(
        1
    )

    assert result is not None

    assert (
        result["version_number"]
        == 2
    )


# ==================================================
# Get By Date
# ==================================================

def test_get_by_date(
    service
):

    result = service.get_by_date(
        "2026-08-08"
    )

    assert len(result) == 1

    assert result[0]["id"] == 1


# ==================================================
# Get By Month
# ==================================================

def test_get_by_month(
    service
):

    result = service.get_by_month(
        2026,
        8
    )

    assert len(result) == 1


# ==================================================
# Get By Year
# ==================================================

def test_get_by_year(
    service
):

    result = service.get_by_year(
        2026
    )

    assert len(result) == 2


# ==================================================
# Get By Source
# ==================================================

def test_get_by_source(
    service
):

    result = service.get_by_source(
        "TechNews"
    )

    assert len(result) == 1

    assert (
        result[0]["source"]
        == "TechNews"
    )


# ==================================================
# Search
# ==================================================

def test_search(
    service
):

    result = service.search(
        "TSMC"
    )

    assert len(result) == 1

    assert result[0]["id"] == 1


# ==================================================
# Empty Search
# ==================================================

def test_empty_search(
    service
):

    result = service.search(
        "UNKNOWN"
    )

    assert result == []


# ==================================================
# Count
# ==================================================

def test_count(
    service
):

    result = service.count()

    assert result == 2


# ==================================================
# Count Articles
# ==================================================

def test_count_articles(
    service
):

    result = service.count_articles()

    assert result == 2


# ==================================================
# Count By Source
# ==================================================

def test_count_by_source(
    service
):

    result = service.count_by_source(
        "TechNews"
    )

    assert result == 1


# ==================================================
# Count By Date
# ==================================================

def test_count_by_date(
    service
):

    result = service.count_by_date(
        "2026-08-08"
    )

    assert result == 1


# ==================================================
# Statistics
# ==================================================

def test_get_statistics(
    service
):

    result = service.get_statistics()

    assert isinstance(
        result,
        dict
    )

    assert result["total"] == 2

    assert result["articles"] == 2

    assert result["versions"] == 3


# ==================================================
# Pagination
# ==================================================

def test_get_articles_with_pagination(
    service
):

    result = (
        service.get_articles_with_pagination(
            page=1,
            page_size=10
        )
    )

    assert isinstance(
        result,
        dict
    )

    assert result["page"] == 1

    assert result["page_size"] == 10

    assert result["total"] == 2

    assert len(
        result["items"]
    ) == 1


# ==================================================
# Knowledge History
# ==================================================

def test_get_knowledge_history(
    service
):

    knowledge = FakeKnowledgeHistory()

    service.knowledge_history = knowledge

    result = (
        service.get_knowledge_history(
            1
        )
    )

    assert len(result) == 2

    assert (
        result[0]["version_number"]
        == 1
    )

    assert (
        result[1]["version_number"]
        == 2
    )


# ==================================================
# Latest Knowledge
# ==================================================

def test_get_latest_knowledge(
    service
):

    knowledge = FakeKnowledgeHistory()

    service.knowledge_history = knowledge

    result = (
        service.get_latest_knowledge(
            1
        )
    )

    assert result is not None

    assert (
        result["importance"]
        == 9
    )


# ==================================================
# Knowledge Evolution
# ==================================================

def test_get_knowledge_evolution(
    service
):

    knowledge = FakeKnowledgeHistory()

    service.knowledge_history = knowledge

    result = (
        service.get_knowledge_evolution(
            1
        )
    )

    assert len(result) == 2

    assert (
        result[0]["summary"]
        == "Initial knowledge"
    )

    assert (
        result[1]["summary"]
        == "Updated knowledge"
    )


# ==================================================
# Empty Knowledge History
# ==================================================

def test_empty_knowledge_history(
    service
):

    knowledge = FakeKnowledgeHistory()

    service.knowledge_history = knowledge

    result = (
        service.get_knowledge_history(
            999
        )
    )

    assert result == []


# ==================================================
# Repr
# ==================================================

def test_repr(
    service
):

    result = repr(
        service
    )

    assert (
        "ArchiveWebService"
        in result
    )