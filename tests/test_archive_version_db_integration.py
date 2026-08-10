"""
tests/test_archive_version_db_integration.py

AutoSearch V4

P2.2.2 Step 7

Archive Version Database Integration Test

功能：

1. 建立測試 Article
2. 建立 Archive Version 1
3. 建立 Archive Version 2
4. 建立 Archive Version 3
5. 驗證 Version Number
6. 驗證 Version History
7. 驗證 Latest Version
8. 驗證 File Hash
9. 驗證 Archive File
10. 測試完成後清理資料
"""

import os

import pytest

from database.connection import get_connection

from services.archive_service import (
    ArchiveService
)


# ==================================================
# Database Check
# ==================================================


def check_database():

    try:

        conn = get_connection()

        if conn is None:

            return False

        cursor = conn.cursor()

        cursor.execute(
            "SELECT 1"
        )

        cursor.fetchone()

        cursor.close()
        conn.close()

        return True

    except Exception:

        return False


# ==================================================
# Test
# ==================================================


@pytest.mark.integration
def test_archive_version_database():

    # ==============================================
    # Database Availability
    # ==============================================

    if not check_database():

        pytest.skip(
            "MySQL database unavailable"
        )

    conn = get_connection()

    cursor = conn.cursor()

    article_id = None

    created_paths = []

    try:

        # ==========================================
        # Create Test Article
        # ==========================================

        cursor.execute(
            """
            INSERT INTO articles
            (
                document_id,
                keyword,
                title,
                url,
                source,
                status
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
            (
                "TEST_ARCHIVE_VERSION_STEP7",
                "TEST",
                "Archive Version Integration Test",
                "https://example.com/test",
                "TEST",
                "Success"
            )
        )

        conn.commit()

        article_id = cursor.lastrowid

        assert article_id is not None

        # ==========================================
        # Service
        # ==========================================

        service = ArchiveService()

        # ==========================================
        # HTML Version 1
        # ==========================================

        html_v1 = """
        <html>
            <body>
                Semiconductor Version 1
            </body>
        </html>
        """

        # ==========================================
        # Save Version 1
        # ==========================================

        version_1 = service.save_html(

            article_id=article_id,

            url=(
                "https://example.com/"
                "semiconductor"
            ),

            html=html_v1

        )

        assert version_1 is not None

        assert (
            version_1.article_id
            == article_id
        )

        assert (
            version_1.version_number
            == 1
        )

        assert (
            version_1.raw_document_id
            is not None
        )

        assert (
            version_1.file_hash
            is not None
        )

        assert (
            version_1.storage_path
            is not None
        )

        assert (
            version_1.file_size
            > 0
        )

        assert (
            version_1.mime_type
            == "text/html"
        )

        assert os.path.exists(
            version_1.storage_path
        )

        created_paths.append(
            version_1.storage_path
        )

        # ==========================================
        # HTML Version 2
        # ==========================================

        html_v2 = """
        <html>
            <body>
                Semiconductor Version 2
                Updated Information
            </body>
        </html>
        """

        # ==========================================
        # Save Version 2
        # ==========================================

        version_2 = service.save_html(

            article_id=article_id,

            url=(
                "https://example.com/"
                "semiconductor"
            ),

            html=html_v2

        )

        assert version_2 is not None

        assert (
            version_2.article_id
            == article_id
        )

        assert (
            version_2.version_number
            == 2
        )

        assert (
            version_2.raw_document_id
            is not None
        )

        assert (
            version_2.file_hash
            is not None
        )

        assert (
            version_2.storage_path
            is not None
        )

        assert (
            version_2.file_size
            > 0
        )

        assert (
            version_2.mime_type
            == "text/html"
        )

        assert os.path.exists(
            version_2.storage_path
        )

        created_paths.append(
            version_2.storage_path
        )

        # ==========================================
        # HTML Version 3
        # ==========================================

        html_v3 = """
        <html>
            <body>
                Semiconductor Version 3
                More Updated Information
            </body>
        </html>
        """

        # ==========================================
        # Save Version 3
        # ==========================================

        version_3 = service.save_html(

            article_id=article_id,

            url=(
                "https://example.com/"
                "semiconductor"
            ),

            html=html_v3

        )

        assert version_3 is not None

        assert (
            version_3.article_id
            == article_id
        )

        assert (
            version_3.version_number
            == 3
        )

        assert (
            version_3.raw_document_id
            is not None
        )

        assert (
            version_3.file_hash
            is not None
        )

        assert (
            version_3.storage_path
            is not None
        )

        assert (
            version_3.file_size
            > 0
        )

        assert (
            version_3.mime_type
            == "text/html"
        )

        assert os.path.exists(
            version_3.storage_path
        )

        created_paths.append(
            version_3.storage_path
        )

        # ==========================================
        # Verify Different Hashes
        # ==========================================

        assert (
            version_1.file_hash
            != version_2.file_hash
        )

        assert (
            version_2.file_hash
            != version_3.file_hash
        )

        assert (
            version_1.file_hash
            != version_3.file_hash
        )

        # ==========================================
        # Get Version History
        # ==========================================

        versions = (
            service.get_versions(
                article_id
            )
        )

        assert versions is not None

        assert len(versions) == 3

        # ==========================================
        # Verify Version Numbers
        # ==========================================

        version_numbers = [

            version.version_number

            for version in versions

        ]

        assert version_numbers == [
            1,
            2,
            3
        ]

        # ==========================================
        # Verify Article ID
        # ==========================================

        for version in versions:

            assert (
                version.article_id
                == article_id
            )

        # ==========================================
        # Get Latest Version
        # ==========================================

        latest = (
            service.get_latest_version(
                article_id
            )
        )

        assert latest is not None

        assert (
            latest.article_id
            == article_id
        )

        assert (
            latest.version_number
            == 3
        )

        assert (
            latest.file_hash
            == version_3.file_hash
        )

        assert (
            latest.storage_path
            == version_3.storage_path
        )

        # ==========================================
        # Verify Database Records
        # ==========================================

        cursor.execute(
            """
            SELECT
                COUNT(*)
            FROM archive_versions
            WHERE article_id=%s
            """,
            (
                article_id,
            )
        )

        result = cursor.fetchone()

        assert result is not None

        assert result[0] == 3

        # ==========================================
        # Verify Raw Documents
        # ==========================================

        cursor.execute(
            """
            SELECT
                COUNT(*)
            FROM raw_documents
            WHERE article_id=%s
            """,
            (
                article_id,
            )
        )

        result = cursor.fetchone()

        assert result is not None

        assert result[0] == 3

    finally:

        # ==========================================
        # Cleanup Database
        # ==========================================

        if article_id is not None:

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

        # ==========================================
        # Cleanup Archive Files
        # ==========================================

        for path in created_paths:

            try:

                if os.path.exists(path):

                    os.remove(path)

            except Exception:

                pass

        # ==========================================
        # Close Database
        # ==========================================

        cursor.close()

        conn.close()