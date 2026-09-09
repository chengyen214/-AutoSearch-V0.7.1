"""
tests/test_historical_search.py

AutoSearch V4

P2.3.5

Historical Search Tests

測試：

1. Service 建立
2. Keyword Search
3. Article Search
4. Article History
5. Version Search
6. Latest Version
7. Source Search
8. Date Search
9. Version Exists
10. Count
11. Empty Search
12. Invalid Article ID
13. Invalid Version
14. Pagination
15. Get All History
16. Repr
"""

from services.historical_search_service import (
    HistoricalSearchService
)


# ==========================================
# Mock Repository
# ==========================================

class MockHistoricalSearchRepository:
    """
    Mock Historical Search Repository。

    不連接 MySQL。
    """

    def __init__(self):

        self.results = [

            {
                "version_id": 1,
                "article_id": 100,
                "version_number": 1,
                "title": "TSMC 2nm",
                "url": "https://example.com/tsmc",
                "source": "TechNews",
                "keyword": "2nm",
                "file_hash": "hash_v1",
                "storage_path": (
                    "archive/html/2026/08/08/hash_v1.html"
                )
            },

            {
                "version_id": 2,
                "article_id": 100,
                "version_number": 2,
                "title": "TSMC 2nm Updated",
                "url": "https://example.com/tsmc",
                "source": "TechNews",
                "keyword": "2nm",
                "file_hash": "hash_v2",
                "storage_path": (
                    "archive/html/2026/08/08/hash_v2.html"
                )
            },

            {
                "version_id": 3,
                "article_id": 200,
                "version_number": 1,
                "title": "CoWoS Expansion",
                "url": "https://example.com/cowos",
                "source": "CNA",
                "keyword": "CoWoS",
                "file_hash": "hash_v1",
                "storage_path": (
                    "archive/html/2026/08/08/hash_v1.html"
                )
            }
        ]

    # ======================================
    # Search
    # ======================================

    def search(
        self,
        keyword=None,
        article_id=None,
        source=None,
        start_date=None,
        end_date=None,
        version_number=None,
        limit=50,
        offset=0
    ):

        results = self.results

        if keyword:

            results = [

                item
                for item in results

                if (
                    keyword.lower()
                    in item["title"].lower()
                    or
                    keyword.lower()
                    in item["keyword"].lower()
                )

            ]

        if article_id is not None:

            results = [

                item
                for item in results

                if item["article_id"]
                == article_id

            ]

        if source:

            results = [

                item
                for item in results

                if item["source"]
                == source

            ]

        if version_number is not None:

            results = [

                item
                for item in results

                if item["version_number"]
                == version_number

            ]

        return results[
            offset:
            offset + limit
        ]

    # ======================================
    # Get By Article
    # ======================================

    def get_by_article_id(
        self,
        article_id
    ):

        return [

            item
            for item in self.results

            if item["article_id"]
            == article_id

        ]

    # ======================================
    # Get Version
    # ======================================

    def get_version(
        self,
        article_id,
        version_number
    ):

        for item in self.results:

            if (
                item["article_id"]
                == article_id
                and
                item["version_number"]
                == version_number
            ):

                return item

        return None

    # ======================================
    # Latest Version
    # ======================================

    def get_latest_version(
        self,
        article_id
    ):

        versions = (
            self.get_by_article_id(
                article_id
            )
        )

        if not versions:

            return None

        return max(
            versions,
            key=lambda item:
            item["version_number"]
        )

    # ======================================
    # Source
    # ======================================

    def search_by_source(
        self,
        source,
        limit=50,
        offset=0
    ):

        results = [

            item
            for item in self.results

            if item["source"]
            == source

        ]

        return results[
            offset:
            offset + limit
        ]

    # ======================================
    # Date
    # ======================================

    def search_by_date(
        self,
        start_date,
        end_date,
        limit=50,
        offset=0
    ):

        # Mock 不需要實際日期過濾。
        return self.results[
            offset:
            offset + limit
        ]

    # ======================================
    # Count
    # ======================================

    def count(
        self,
        keyword=None,
        article_id=None,
        source=None,
        start_date=None,
        end_date=None,
        version_number=None
    ):

        return len(

            self.search(

                keyword=keyword,

                article_id=article_id,

                source=source,

                start_date=start_date,

                end_date=end_date,

                version_number=version_number,

                limit=999999,

                offset=0

            )

        )

    # ======================================
    # Exists
    # ======================================

    def exists(
        self,
        article_id,
        version_number
    ):

        return (
            self.get_version(
                article_id,
                version_number
            )
            is not None
        )


# ==========================================
# Fixture
# ==========================================

def create_service():

    repository = (
        MockHistoricalSearchRepository()
    )

    return HistoricalSearchService(
        repository=repository
    )


# ==========================================
# Tests
# ==========================================

def test_create_historical_search_service():

    service = create_service()

    assert service is not None

    assert service.repository is not None


# ==========================================
# Keyword Search
# ==========================================

def test_search_by_keyword():

    service = create_service()

    result = service.search_by_keyword(
        "2nm"
    )

    assert result["count"] == 2

    assert len(
        result["results"]
    ) == 2


# ==========================================
# Article Search
# ==========================================

def test_search_by_article():

    service = create_service()

    result = service.search_by_article(
        100
    )

    assert result["count"] == 2

    assert len(
        result["results"]
    ) == 2


# ==========================================
# Article History
# ==========================================

def test_get_history():

    service = create_service()

    result = service.get_history(
        100
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


# ==========================================
# Get Version
# ==========================================

def test_get_version():

    service = create_service()

    result = service.get_version(
        100,
        2
    )

    assert result is not None

    assert (
        result["version_number"]
        == 2
    )


# ==========================================
# Nonexistent Version
# ==========================================

def test_get_nonexistent_version():

    service = create_service()

    result = service.get_version(
        100,
        99
    )

    assert result is None


# ==========================================
# Latest Version
# ==========================================

def test_get_latest_version():

    service = create_service()

    result = service.get_latest_version(
        100
    )

    assert result is not None

    assert (
        result["version_number"]
        == 2
    )


# ==========================================
# Source Search
# ==========================================

def test_search_by_source():

    service = create_service()

    result = service.search_by_source(
        "TechNews"
    )

    assert result["count"] == 2

    assert len(
        result["results"]
    ) == 2


# ==========================================
# Date Search
# ==========================================

def test_search_by_date():

    service = create_service()

    result = service.search_by_date(

        "2026-08-01",

        "2026-08-08"

    )

    assert result["count"] == 3

    assert len(
        result["results"]
    ) == 3


# ==========================================
# Version Search
# ==========================================

def test_search_by_version():

    service = create_service()

    result = service.search_by_version(
        1
    )

    assert result["count"] == 2

    assert len(
        result["results"]
    ) == 2


# ==========================================
# Count
# ==========================================

def test_count():

    service = create_service()

    result = service.count(
        article_id=100
    )

    assert result == 2


# ==========================================
# Exists
# ==========================================

def test_version_exists():

    service = create_service()

    assert service.exists(
        100,
        1
    ) is True


def test_version_not_exists():

    service = create_service()

    assert service.exists(
        100,
        99
    ) is False


# ==========================================
# Invalid Article
# ==========================================

def test_invalid_article():

    service = create_service()

    result = service.search_by_article(
        None
    )

    assert result["results"] == []

    assert result["count"] == 0


# ==========================================
# Invalid Version
# ==========================================

def test_invalid_version():

    service = create_service()

    result = service.get_version(
        100,
        None
    )

    assert result is None


# ==========================================
# Empty Keyword
# ==========================================

def test_empty_keyword():

    service = create_service()

    result = service.search_by_keyword(
        ""
    )

    assert result["results"] == []

    assert result["count"] == 0


# ==========================================
# Pagination
# ==========================================

def test_pagination():

    service = create_service()

    result = service.search(

        limit=1,

        offset=0

    )

    assert result["count"] == 3

    assert len(
        result["results"]
    ) == 1


# ==========================================
# Get All History
# ==========================================

def test_get_all_history():

    service = create_service()

    result = service.get_all_history()

    assert result["count"] == 3

    assert len(
        result["results"]
    ) == 3


# ==========================================
# Search Multiple Conditions
# ==========================================

def test_search_multiple_conditions():

    service = create_service()

    result = service.search(

        keyword="2nm",

        article_id=100,

        source="TechNews",

        version_number=2

    )

    assert result["count"] == 1

    assert len(
        result["results"]
    ) == 1

    assert (
        result["results"][0]["version_number"]
        == 2
    )


# ==========================================
# Repr
# ==========================================

def test_repr():

    service = create_service()

    result = repr(service)

    assert (
        "HistoricalSearchService"
        in result
    )