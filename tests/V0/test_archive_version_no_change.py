"""
tests/test_archive_version_no_change.py

AutoSearch V4

P2.2.2

Archive Version No Change Integration Test

功能：

1. 建立測試 Article
2. 建立 Archive Version 1
3. 使用相同 URL + 相同 HTML 再次 Archive
4. 驗證內容沒有變化
5. 驗證不建立新的 Archive Version
6. 驗證 Version Number
7. 驗證 File Hash
8. 驗證 Archive File
9. 驗證 RawDocument Content Deduplication
10. 測試完成後清理資料
"""

import os
import uuid

import pytest

from database.connection import get_connection

from services.archive_service import (
    ArchiveService
)


# ==================================================
#
# Database Check
#
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
#
# Test
#
# ==================================================

@pytest.mark.integration
def test_archive_same_url_same_html_no_new_version():

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
        # Test Data
        # ==========================================

        test_url = (
            "https://example.com/"
            "archive-no-change-test"
        )

        # ------------------------------------------
        # document_id 是 UNIQUE。
        #
        # 每次測試使用 UUID，
        # 避免重複執行測試造成：
        #
        # Duplicate entry
        # ------------------------------------------

        test_document_id = (
            "TEST_ARCHIVE_NO_CHANGE_"
            + uuid.uuid4().hex
        )

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
                test_document_id,
                "TEST",
                "Archive No Change Test",
                test_url,
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
        # HTML
        # ==========================================

        html = """
        <html>
            <body>
                Semiconductor Archive Test
            </body>
        </html>
        """

        # ==========================================
        # First Archive
        #
        # Expected:
        #
        # Version 1
        # ==========================================

        version_1 = service.save_html(

            article_id=article_id,

            url=test_url,

            html=html

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

        # ==========================================
        # Verify Archive File
        # ==========================================

        assert os.path.exists(
            version_1.storage_path
        )

        created_paths.append(
            version_1.storage_path
        )

        # ==========================================
        # Save First Version Information
        # ==========================================

        first_raw_document_id = (
            version_1.raw_document_id
        )

        first_file_hash = (
            version_1.file_hash
        )

        first_storage_path = (
            version_1.storage_path
        )

        # ==========================================
        # Second Archive
        #
        # Same URL
        # Same HTML
        #
        # Expected:
        #
        # No Version 2
        #
        # ArchiveService 應直接回傳
        # 原本的 Version 1。
        # ==========================================

        version_2 = service.save_html(

            article_id=article_id,

            url=test_url,

            html=html

        )

        assert version_2 is not None

        # ==========================================
        # Verify Same Version
        # ==========================================

        assert (
            version_2.version_number
            == 1
        )

        assert (
            version_2.article_id
            == article_id
        )

        # ==========================================
        # Verify Same RawDocument
        # ==========================================

        assert (
            version_2.raw_document_id
            == first_raw_document_id
        )

        # ==========================================
        # Verify Same File Hash
        # ==========================================

        assert (
            version_2.file_hash
            == first_file_hash
        )

        # ==========================================
        # Verify Same Storage Path
        # ==========================================

        assert (
            version_2.storage_path
            == first_storage_path
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

        # ==========================================
        # IMPORTANT
        #
        # 相同 URL + 相同 HTML
        #
        # 不應建立 Version 2。
        # ==========================================

        assert len(versions) == 1

        # ==========================================
        # Verify Version Number
        # ==========================================

        assert (
            versions[0].version_number
            == 1
        )

        # ==========================================
        # Verify File Hash
        # ==========================================

        assert (
            versions[0].file_hash
            == version_1.file_hash
        )

        # ==========================================
        # Verify RawDocument ID
        # ==========================================

        assert (
            versions[0].raw_document_id
            == version_1.raw_document_id
        )

        # ==========================================
        # Verify Storage Path
        # ==========================================

        assert (
            versions[0].storage_path
            == version_1.storage_path
        )

        # ==========================================
        # Verify Latest Version
        # ==========================================

        latest = (
            service.get_latest_version(
                article_id
            )
        )

        assert latest is not None

        assert (
            latest.version_number
            == 1
        )

        assert (
            latest.file_hash
            == version_1.file_hash
        )

        assert (
            latest.raw_document_id
            == version_1.raw_document_id
        )

        assert (
            latest.storage_path
            == version_1.storage_path
        )

        # ==========================================
        # Verify Database Archive Versions
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

        assert result[0] == 1

        # ==========================================
        # Verify Raw Document
        #
        # RawDocument 是 Content-Addressed Storage。
        #
        # file_hash UNIQUE。
        #
        # 因此不能使用：
        #
        # WHERE article_id=%s
        #
        # 應該透過 ArchiveVersion
        # 的 raw_document_id 驗證。
        # ==========================================

        cursor.execute(
            """
            SELECT
                COUNT(*)
            FROM raw_documents
            WHERE id=%s
            """,
            (
                version_1.raw_document_id,
            )
        )

        result = cursor.fetchone()

        assert result is not None

        assert result[0] == 1

        # ==========================================
        # Verify RawDocument Hash
        # ==========================================

        cursor.execute(
            """
            SELECT
                file_hash
            FROM raw_documents
            WHERE id=%s
            """,
            (
                version_1.raw_document_id,
            )
        )

        result = cursor.fetchone()

        assert result is not None

        assert (
            result[0]
            == version_1.file_hash
        )

        # ==========================================
        # Verify RawDocument Storage Path
        # ==========================================

        cursor.execute(
            """
            SELECT
                storage_path
            FROM raw_documents
            WHERE id=%s
            """,
            (
                version_1.raw_document_id,
            )
        )

        result = cursor.fetchone()

        assert result is not None

        assert (
            result[0]
            == version_1.storage_path
        )

        # ==========================================
        # Verify Content Deduplication
        #
        # 同一 HTML
        # =
        # 同一 file_hash
        #
        # raw_documents 中只能有一筆。
        # ==========================================

        cursor.execute(
            """
            SELECT
                COUNT(*)
            FROM raw_documents
            WHERE file_hash=%s
            """,
            (
                version_1.file_hash,
            )
        )

        result = cursor.fetchone()

        assert result is not None

        assert result[0] == 1

        # ==========================================
        # Verify Archive File Still Exists
        # ==========================================

        assert os.path.exists(
            version_1.storage_path
        )

        # ==========================================
        # Verify No Version 2
        #
        # Database 最終只能有：
        #
        # Version 1
        #
        # 不可以有：
        #
        # Version 2
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

        assert result[0] == 1

    finally:

        # ==========================================
        # Cleanup Archive Versions
        #
        # 先刪除 FK dependent records。
        # ==========================================

        if article_id is not None:

            try:

                cursor.execute(
                    """
                    DELETE FROM archive_versions
                    WHERE article_id=%s
                    """,
                    (
                        article_id,
                    )
                )

                conn.commit()

            except Exception:

                conn.rollback()

        # ==========================================
        # Cleanup Article
        # ==========================================

        if article_id is not None:

            try:

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

            except Exception:

                conn.rollback()

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
