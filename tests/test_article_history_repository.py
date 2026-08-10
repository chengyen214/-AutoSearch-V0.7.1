"""
tests/test_article_history_repository.py

AutoSearch V4

P2.3.3 Article History

測試：

1. get_history
2. get_latest
3. get_first
4. get_version
5. get_nonexistent_version
6. get_version_by_id
7. count_versions
8. has_history
9. get_timeline
10. get_previous_version
11. get_previous_version_first
12. get_next_version
13. get_next_version_latest
14. get_summary
15. get_history_with_article

使用：

pytest
"""

import uuid

import pytest

from database.connection import get_connection
from database.article_history_repository import (
    ArticleHistoryRepository
)


# ==================================
# Repository
# ==================================

@pytest.fixture
def repository():

    return ArticleHistoryRepository()


# ==================================
# Test Article + Archive History
# ==================================

@pytest.fixture
def test_article():

    conn = get_connection()

    cursor = conn.cursor()

    document_id = (
        "test-history-"
        + uuid.uuid4().hex
    )

    raw_hashes = [
        "test-raw-" + uuid.uuid4().hex,
        "test-raw-" + uuid.uuid4().hex,
        "test-raw-" + uuid.uuid4().hex
    ]

    article_id = None

    try:

        # ==================================
        # Create Article
        # ==================================

        cursor.execute(
            """
            INSERT INTO articles
            (
                document_id,
                keyword,
                title,
                url,
                source,
                status,
                ai_status
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )
            """,
            (
                document_id,
                "TEST_HISTORY",
                "P2.3.3 Article History Test",
                "https://example.com/test-history",
                "TEST",
                "Success",
                "completed"
            )
        )

        article_id = cursor.lastrowid

        # ==================================
        # Create Raw Documents
        # ==================================

        raw_documents = [

            (
                article_id,
                "https://example.com/test-history/v1",
                "/test/history/v1.html",
                raw_hashes[0],
                100,
                "text/html"
            ),

            (
                article_id,
                "https://example.com/test-history/v2",
                "/test/history/v2.html",
                raw_hashes[1],
                200,
                "text/html"
            ),

            (
                article_id,
                "https://example.com/test-history/v3",
                "/test/history/v3.html",
                raw_hashes[2],
                300,
                "text/html"
            )

        ]

        cursor.executemany(
            """
            INSERT INTO raw_documents
            (
                article_id,
                original_url,
                storage_path,
                file_hash,
                file_size,
                mime_type
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )
            """,
            raw_documents
        )

        conn.commit()

        # ==================================
        # Get Raw Document IDs
        # ==================================

        cursor.execute(
            """
            SELECT id
            FROM raw_documents
            WHERE article_id=%s
            ORDER BY id ASC
            """,
            (
                article_id,
            )
        )

        raw_document_ids = [
            row[0]
            for row in cursor.fetchall()
        ]

        assert len(raw_document_ids) == 3

        # ==================================
        # Create Archive Versions
        # ==================================

        versions = [

            (
                article_id,
                raw_document_ids[0],
                1,
                raw_hashes[0],
                "/test/history/v1.html",
                100,
                "text/html"
            ),

            (
                article_id,
                raw_document_ids[1],
                2,
                raw_hashes[1],
                "/test/history/v2.html",
                200,
                "text/html"
            ),

            (
                article_id,
                raw_document_ids[2],
                3,
                raw_hashes[2],
                "/test/history/v3.html",
                300,
                "text/html"
            )

        ]

        cursor.executemany(
            """
            INSERT INTO archive_versions
            (
                article_id,
                raw_document_id,
                version_number,
                file_hash,
                storage_path,
                file_size,
                mime_type
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )
            """,
            versions
        )

        conn.commit()

        # ==================================
        # Return Article ID
        # ==================================

        yield article_id

    finally:

        # ==================================
        # Cleanup
        # ==================================

        if article_id is not None:

            cursor.execute(
                """
                DELETE FROM archive_versions
                WHERE article_id=%s
                """,
                (
                    article_id,
                )
            )

            cursor.execute(
                """
                DELETE FROM raw_documents
                WHERE article_id=%s
                """,
                (
                    article_id,
                )
            )

            cursor.execute(
                """
                DELETE FROM articles
                WHERE id=%s
                """,
                (
                    article_id,
                )
            )

            conn.commit()

        cursor.close()
        conn.close()


# ==================================
# Get History
# ==================================

def test_get_history(
    repository,
    test_article
):

    result = repository.get_history(
        test_article
    )

    assert result is not None
    assert len(result) == 3


# ==================================
# Get Latest
# ==================================

def test_get_latest(
    repository,
    test_article
):

    result = repository.get_latest(
        test_article
    )

    assert result is not None

    assert result["version_number"] == 3


# ==================================
# Get First
# ==================================

def test_get_first(
    repository,
    test_article
):

    result = repository.get_first(
        test_article
    )

    assert result is not None

    assert result["version_number"] == 1


# ==================================
# Get Version
# ==================================

def test_get_version(
    repository,
    test_article
):

    result = repository.get_version(
        test_article,
        2
    )

    assert result is not None

    assert result["version_number"] == 2


# ==================================
# Get Nonexistent Version
# ==================================

def test_get_nonexistent_version(
    repository,
    test_article
):

    result = repository.get_version(
        test_article,
        999
    )

    assert result is None


# ==================================
# Get Version By ID
# ==================================

def test_get_version_by_id(
    repository,
    test_article
):

    history = repository.get_history(
        test_article
    )

    assert len(history) == 3

    version_id = history[0]["id"]

    result = repository.get_version_by_id(
        version_id
    )

    assert result is not None

    assert result["id"] == version_id


# ==================================
# Count Versions
# ==================================

def test_count_versions(
    repository,
    test_article
):

    result = repository.count_versions(
        test_article
    )

    assert result == 3


# ==================================
# Has History
# ==================================

def test_has_history(
    repository,
    test_article
):

    result = repository.has_history(
        test_article
    )

    assert result is True


# ==================================
# Timeline
# ==================================

def test_get_timeline(
    repository,
    test_article
):

    result = repository.get_timeline(
        test_article
    )

    assert result is not None

    assert len(result) == 3

    assert result[0]["version_number"] == 1
    assert result[1]["version_number"] == 2
    assert result[2]["version_number"] == 3


# ==================================
# Previous Version
# ==================================

def test_get_previous_version(
    repository,
    test_article
):

    result = repository.get_previous_version(
        test_article,
        2
    )

    assert result is not None

    assert result["version_number"] == 1


# ==================================
# Previous Version - First
# ==================================

def test_get_previous_version_first(
    repository,
    test_article
):

    result = repository.get_previous_version(
        test_article,
        1
    )

    assert result is None


# ==================================
# Next Version
# ==================================

def test_get_next_version(
    repository,
    test_article
):

    result = repository.get_next_version(
        test_article,
        2
    )

    assert result is not None

    assert result["version_number"] == 3


# ==================================
# Next Version - Latest
# ==================================

def test_get_next_version_latest(
    repository,
    test_article
):

    result = repository.get_next_version(
        test_article,
        3
    )

    assert result is None


# ==================================
# Summary
# ==================================

def test_get_summary(
    repository,
    test_article
):

    result = repository.get_summary(
        test_article
    )

    assert result is not None

    assert result["version_count"] == 3

    assert result["first_version"] == 1

    assert result["latest_version"] == 3


# ==================================
# History With Article
# ==================================

def test_get_history_with_article(
    repository,
    test_article
):

    result = repository.get_history_with_article(
        test_article
    )

    assert result is not None

    assert len(result) == 3

    for row in result:

        assert row["article_id"] == test_article
        assert row["title"] == (
            "P2.3.3 Article History Test"
        )