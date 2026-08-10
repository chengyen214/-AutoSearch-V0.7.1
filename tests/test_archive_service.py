"""
tests/test_archive_service.py

AutoSearch V4

P2.2.2 Step 4

ArchiveService Integration Test

測試:

1. Hash
2. Save HTML Snapshot
3. RawDocument
4. ArchiveVersion
5. Version Number
6. Get Versions
7. Get Latest Version
"""

import os

from services.archive_service import (
    ArchiveService
)

from database.connection import (
    get_connection
)


# ==========================================
# Test Data
# ==========================================

TEST_ARTICLE_ID = 1

TEST_URL = (
    "https://example.com/test-archive"
)

TEST_HTML_V1 = """
<html>
<head>
<title>Archive Test Version 1</title>
</head>
<body>
<h1>Version 1</h1>
<p>AutoSearch V4 Archive Test</p>
</body>
</html>
"""


TEST_HTML_V2 = """
<html>
<head>
<title>Archive Test Version 2</title>
</head>
<body>
<h1>Version 2</h1>
<p>AutoSearch V4 Archive Test Updated</p>
</body>
</html>
"""


# ==========================================
# Cleanup
# ==========================================

def cleanup_test_data():

    conn = get_connection()

    cursor = conn.cursor()

    try:

        # ----------------------------------
        # Find Raw Documents
        # ----------------------------------

        cursor.execute(
            """
            SELECT id
            FROM raw_documents
            WHERE article_id = %s
            """,
            (
                TEST_ARTICLE_ID,
            )
        )

        raw_rows = cursor.fetchall()

        raw_ids = [
            row[0]
            for row in raw_rows
        ]

        # ----------------------------------
        # Delete Archive Versions
        # ----------------------------------

        cursor.execute(
            """
            DELETE FROM archive_versions
            WHERE article_id = %s
            """,
            (
                TEST_ARTICLE_ID,
            )
        )

        # ----------------------------------
        # Delete Raw Documents
        # ----------------------------------

        cursor.execute(
            """
            DELETE FROM raw_documents
            WHERE article_id = %s
            """,
            (
                TEST_ARTICLE_ID,
            )
        )

        conn.commit()

        return raw_ids

    finally:

        cursor.close()
        conn.close()


# ==========================================
# Test Hash
# ==========================================

def test_generate_hash():

    service = ArchiveService()

    hash_value = service.generate_hash(
        TEST_HTML_V1
    )

    assert hash_value is not None

    assert len(hash_value) == 64

    assert hash_value == (
        service.generate_hash(
            TEST_HTML_V1
        )
    )


# ==========================================
# Test Save HTML
# ==========================================

def test_save_html():

    cleanup_test_data()

    service = ArchiveService()

    result = service.save_html(

        article_id=TEST_ARTICLE_ID,

        url=TEST_URL,

        html=TEST_HTML_V1

    )

    assert result is not None

    assert result.id is not None

    assert result.article_id == (
        TEST_ARTICLE_ID
    )

    assert result.version_number == 1

    assert result.file_hash is not None

    assert len(result.file_hash) == 64

    assert result.storage_path is not None

    assert os.path.exists(
        result.storage_path
    )

    assert result.file_size > 0

    assert result.mime_type == (
        "text/html"
    )


# ==========================================
# Test Version History
# ==========================================

def test_version_history():

    cleanup_test_data()

    service = ArchiveService()

    # ----------------------------------
    # Version 1
    # ----------------------------------

    version1 = service.save_html(

        article_id=TEST_ARTICLE_ID,

        url=TEST_URL,

        html=TEST_HTML_V1

    )

    assert version1 is not None

    assert version1.version_number == 1

    # ----------------------------------
    # Version 2
    # ----------------------------------

    version2 = service.save_html(

        article_id=TEST_ARTICLE_ID,

        url=TEST_URL,

        html=TEST_HTML_V2

    )

    assert version2 is not None

    assert version2.version_number == 2

    # ----------------------------------
    # Hash Must Be Different
    # ----------------------------------

    assert version1.file_hash != (
        version2.file_hash
    )

    # ----------------------------------
    # Storage Path Must Be Different
    # ----------------------------------

    assert version1.storage_path != (
        version2.storage_path
    )

    # ----------------------------------
    # Files Exist
    # ----------------------------------

    assert os.path.exists(
        version1.storage_path
    )

    assert os.path.exists(
        version2.storage_path
    )


# ==========================================
# Test Get Versions
# ==========================================

def test_get_versions():

    cleanup_test_data()

    service = ArchiveService()

    service.save_html(

        article_id=TEST_ARTICLE_ID,

        url=TEST_URL,

        html=TEST_HTML_V1

    )

    service.save_html(

        article_id=TEST_ARTICLE_ID,

        url=TEST_URL,

        html=TEST_HTML_V2

    )

    versions = service.get_versions(
        TEST_ARTICLE_ID
    )

    assert versions is not None

    assert len(versions) == 2

    assert versions[0].version_number == 1

    assert versions[1].version_number == 2


# ==========================================
# Test Latest Version
# ==========================================

def test_get_latest_version():

    cleanup_test_data()

    service = ArchiveService()

    service.save_html(

        article_id=TEST_ARTICLE_ID,

        url=TEST_URL,

        html=TEST_HTML_V1

    )

    service.save_html(

        article_id=TEST_ARTICLE_ID,

        url=TEST_URL,

        html=TEST_HTML_V2

    )

    latest = service.get_latest_version(
        TEST_ARTICLE_ID
    )

    assert latest is not None

    assert latest.version_number == 2

    assert latest.file_hash == (
        service.generate_hash(
            TEST_HTML_V2
        )
    )