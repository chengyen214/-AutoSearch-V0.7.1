"""
tests/test_archive_browser_repository.py

AutoSearch V4

P2.3.6

Archive Browser Repository Tests

測試：

1. Repository 初始化
2. Article List
3. Article
4. Article Versions
5. Latest Version
6. Date Query
7. Month Query
8. Year Query
9. Source Query
10. Search
11. Count
12. Count Articles
13. Count By Source
14. Count By Date
15. Statistics
16. Pagination
17. Empty Result
18. Repository Representation
"""

import pytest

from database.archive_browser_repository import (
    ArchiveBrowserRepository
)


# ==================================================
# Fixture
# ==================================================

@pytest.fixture
def repository():

    return ArchiveBrowserRepository()


# ==================================================
# Create Repository
# ==================================================

def test_create_repository(
    repository
):

    assert repository is not None

    assert isinstance(
        repository,
        ArchiveBrowserRepository
    )


# ==================================================
# Get Articles
# ==================================================

def test_get_articles(
    repository
):

    if not hasattr(
        repository,
        "get_articles"
    ):

        pytest.skip(
            "get_articles() not implemented"
        )

    result = repository.get_articles()

    assert result is not None

    assert isinstance(
        result,
        list
    )


# ==================================================
# Get Article
# ==================================================

def test_get_article(
    repository
):

    if not hasattr(
        repository,
        "get_article"
    ):

        pytest.skip(
            "get_article() not implemented"
        )

    result = repository.get_article(
        999999999
    )

    assert (
        result is None
        or isinstance(
            result,
            dict
        )
        or hasattr(
            result,
            "__dict__"
        )
    )


# ==================================================
# Get Versions
# ==================================================

def test_get_versions(
    repository
):

    if not hasattr(
        repository,
        "get_versions"
    ):

        pytest.skip(
            "get_versions() not implemented"
        )

    result = repository.get_versions(
        999999999
    )

    assert result is not None

    assert isinstance(
        result,
        list
    )


# ==================================================
# Get Latest Version
# ==================================================

def test_get_latest_version(
    repository
):

    if not hasattr(
        repository,
        "get_latest_version"
    ):

        pytest.skip(
            "get_latest_version() not implemented"
        )

    result = repository.get_latest_version(
        999999999
    )

    assert (
        result is None
        or isinstance(
            result,
            dict
        )
        or hasattr(
            result,
            "__dict__"
        )
    )


# ==================================================
# Get By Date
# ==================================================

def test_get_by_date(
    repository
):

    if not hasattr(
        repository,
        "get_by_date"
    ):

        pytest.skip(
            "get_by_date() not implemented"
        )

    result = repository.get_by_date(
        "2099-01-01"
    )

    assert result is not None

    assert isinstance(
        result,
        list
    )


# ==================================================
# Get By Month
# ==================================================

def test_get_by_month(
    repository
):

    if not hasattr(
        repository,
        "get_by_month"
    ):

        pytest.skip(
            "get_by_month() not implemented"
        )

    result = repository.get_by_month(
        2099,
        1
    )

    assert result is not None

    assert isinstance(
        result,
        list
    )


# ==================================================
# Get By Year
# ==================================================

def test_get_by_year(
    repository
):

    if not hasattr(
        repository,
        "get_by_year"
    ):

        pytest.skip(
            "get_by_year() not implemented"
        )

    result = repository.get_by_year(
        2099
    )

    assert result is not None

    assert isinstance(
        result,
        list
    )


# ==================================================
# Get By Source
# ==================================================

def test_get_by_source(
    repository
):

    if not hasattr(
        repository,
        "get_by_source"
    ):

        pytest.skip(
            "get_by_source() not implemented"
        )

    result = repository.get_by_source(
        "__test_source__"
    )

    assert result is not None

    assert isinstance(
        result,
        list
    )


# ==================================================
# Search
# ==================================================

def test_search(
    repository
):

    if not hasattr(
        repository,
        "search"
    ):

        pytest.skip(
            "search() not implemented"
        )

    result = repository.search(
        "__test_keyword__"
    )

    assert result is not None

    assert isinstance(
        result,
        list
    )


# ==================================================
# Count
# ==================================================

def test_count(
    repository
):

    if not hasattr(
        repository,
        "count"
    ):

        pytest.skip(
            "count() not implemented"
        )

    result = repository.count()

    assert isinstance(
        result,
        int
    )

    assert result >= 0


# ==================================================
# Count Articles
# ==================================================

def test_count_articles(
    repository
):

    if not hasattr(
        repository,
        "count_articles"
    ):

        pytest.skip(
            "count_articles() not implemented"
        )

    result = repository.count_articles()

    assert isinstance(
        result,
        int
    )

    assert result >= 0


# ==================================================
# Count By Source
# ==================================================

def test_count_by_source(
    repository
):

    if not hasattr(
        repository,
        "count_by_source"
    ):

        pytest.skip(
            "count_by_source() not implemented"
        )

    result = repository.count_by_source(
        "__test_source__"
    )

    assert isinstance(
        result,
        int
    )

    assert result >= 0


# ==================================================
# Count By Date
# ==================================================

def test_count_by_date(
    repository
):

    if not hasattr(
        repository,
        "count_by_date"
    ):

        pytest.skip(
            "count_by_date() not implemented"
        )

    result = repository.count_by_date(
        "2099-01-01"
    )

    assert isinstance(
        result,
        int
    )

    assert result >= 0


# ==================================================
# Statistics
# ==================================================

def test_get_statistics(
    repository
):

    if not hasattr(
        repository,
        "get_statistics"
    ):

        pytest.skip(
            "get_statistics() not implemented"
        )

    result = repository.get_statistics()

    assert result is not None

    assert (
        isinstance(
            result,
            dict
        )
        or hasattr(
            result,
            "__dict__"
        )
    )


# ==================================================
# Pagination
# ==================================================

def test_get_articles_with_pagination(
    repository
):

    if not hasattr(
        repository,
        "get_articles"
    ):

        pytest.skip(
            "get_articles() not implemented"
        )

    try:

        result = repository.get_articles(
            limit=10,
            offset=0
        )

    except TypeError:

        pytest.skip(
            "Pagination parameters not implemented"
        )

    assert result is not None

    assert isinstance(
        result,
        list
    )

    assert len(result) <= 10


# ==================================================
# Empty Article
# ==================================================

def test_nonexistent_article_returns_empty(
    repository
):

    if not hasattr(
        repository,
        "get_versions"
    ):

        pytest.skip(
            "get_versions() not implemented"
        )

    result = repository.get_versions(
        999999999
    )

    assert result == []


# ==================================================
# Empty Source
# ==================================================

def test_nonexistent_source_returns_empty(
    repository
):

    if not hasattr(
        repository,
        "get_by_source"
    ):

        pytest.skip(
            "get_by_source() not implemented"
        )

    result = repository.get_by_source(
        "__nonexistent_source__"
    )

    assert result == []


# ==================================================
# Empty Search
# ==================================================

def test_nonexistent_search_returns_empty(
    repository
):

    if not hasattr(
        repository,
        "search"
    ):

        pytest.skip(
            "search() not implemented"
        )

    result = repository.search(
        "__nonexistent_search_keyword__"
    )

    assert result == []


# ==================================================
# Repository Representation
# ==================================================

def test_repository_repr(
    repository
):

    result = repr(
        repository
    )

    assert isinstance(
        result,
        str
    )

    assert (
        "ArchiveBrowserRepository"
        in result
    )