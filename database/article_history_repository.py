"""
database/article_history_repository.py

AutoSearch V4

P2.3.3 Article History

功能:

1. 查詢 Article 完整歷史
2. 查詢指定 Version
3. 查詢最新 Version
4. 查詢第一個 Version
5. 查詢 Version 數量
6. 查詢 Version Timeline
7. 檢查 Article 是否存在 History
8. 查詢前一個 Version
9. 查詢下一個 Version
10. 查詢 Article History Summary

Database:

articles
archive_versions
raw_documents
"""

from database.connection import get_connection


class ArticleHistoryRepository:

    """
    Article History Repository

    負責：

        Article
            ↓
        Archive Versions
            ↓
        Historical Timeline

    本 Repository 不負責：

        - 建立 Version
        - 修改 Version
        - Version Diff
        - AI Analysis
        - Search Ranking

    Version CRUD 由：

        ArchiveVersionRepository

    負責。
    """

    # ==================================
    # Get Article History
    # ==================================

    def get_history(
        self,
        article_id
    ):

        conn = get_connection()

        cursor = conn.cursor(
            dictionary=True
        )

        try:

            cursor.execute(
                """
                SELECT
                    av.id,
                    av.article_id,
                    av.raw_document_id,
                    av.version_number,
                    av.file_hash,
                    av.storage_path,
                    av.file_size,
                    av.mime_type,
                    av.created_time
                FROM archive_versions av
                WHERE av.article_id=%s
                ORDER BY
                    av.version_number ASC
                """,
                (
                    article_id,
                )
            )

            return cursor.fetchall()

        finally:

            cursor.close()
            conn.close()

    # ==================================
    # Get Latest Version
    # ==================================

    def get_latest(
        self,
        article_id
    ):

        conn = get_connection()

        cursor = conn.cursor(
            dictionary=True
        )

        try:

            cursor.execute(
                """
                SELECT
                    av.id,
                    av.article_id,
                    av.raw_document_id,
                    av.version_number,
                    av.file_hash,
                    av.storage_path,
                    av.file_size,
                    av.mime_type,
                    av.created_time
                FROM archive_versions av
                WHERE av.article_id=%s
                ORDER BY
                    av.version_number DESC
                LIMIT 1
                """,
                (
                    article_id,
                )
            )

            return cursor.fetchone()

        finally:

            cursor.close()
            conn.close()

    # ==================================
    # Get First Version
    # ==================================

    def get_first(
        self,
        article_id
    ):

        conn = get_connection()

        cursor = conn.cursor(
            dictionary=True
        )

        try:

            cursor.execute(
                """
                SELECT
                    av.id,
                    av.article_id,
                    av.raw_document_id,
                    av.version_number,
                    av.file_hash,
                    av.storage_path,
                    av.file_size,
                    av.mime_type,
                    av.created_time
                FROM archive_versions av
                WHERE av.article_id=%s
                ORDER BY
                    av.version_number ASC
                LIMIT 1
                """,
                (
                    article_id,
                )
            )

            return cursor.fetchone()

        finally:

            cursor.close()
            conn.close()

    # ==================================
    # Get Specific Version
    # ==================================

    def get_version(
        self,
        article_id,
        version_number
    ):

        conn = get_connection()

        cursor = conn.cursor(
            dictionary=True
        )

        try:

            cursor.execute(
                """
                SELECT
                    av.id,
                    av.article_id,
                    av.raw_document_id,
                    av.version_number,
                    av.file_hash,
                    av.storage_path,
                    av.file_size,
                    av.mime_type,
                    av.created_time
                FROM archive_versions av
                WHERE
                    av.article_id=%s
                AND
                    av.version_number=%s
                LIMIT 1
                """,
                (
                    article_id,
                    version_number
                )
            )

            return cursor.fetchone()

        finally:

            cursor.close()
            conn.close()

    # ==================================
    # Get Version By ID
    # ==================================

    def get_version_by_id(
        self,
        version_id
    ):

        conn = get_connection()

        cursor = conn.cursor(
            dictionary=True
        )

        try:

            cursor.execute(
                """
                SELECT
                    av.id,
                    av.article_id,
                    av.raw_document_id,
                    av.version_number,
                    av.file_hash,
                    av.storage_path,
                    av.file_size,
                    av.mime_type,
                    av.created_time
                FROM archive_versions av
                WHERE av.id=%s
                LIMIT 1
                """,
                (
                    version_id,
                )
            )

            return cursor.fetchone()

        finally:

            cursor.close()
            conn.close()

    # ==================================
    # Count Versions
    # ==================================

    def count_versions(
        self,
        article_id
    ):

        conn = get_connection()

        cursor = conn.cursor()

        try:

            cursor.execute(
                """
                SELECT COUNT(*)
                FROM archive_versions
                WHERE article_id=%s
                """,
                (
                    article_id,
                )
            )

            result = cursor.fetchone()

            return result[0] if result else 0

        finally:

            cursor.close()
            conn.close()

    # ==================================
    # Has History
    # ==================================

    def has_history(
        self,
        article_id
    ):

        return (
            self.count_versions(
                article_id
            ) > 0
        )

    # ==================================
    # Get Timeline
    # ==================================

    def get_timeline(
        self,
        article_id
    ):

        conn = get_connection()

        cursor = conn.cursor(
            dictionary=True
        )

        try:

            cursor.execute(
                """
                SELECT
                    av.id AS version_id,
                    av.article_id,
                    av.version_number,
                    av.raw_document_id,
                    av.file_hash,
                    av.file_size,
                    av.mime_type,
                    av.created_time
                FROM archive_versions av
                WHERE av.article_id=%s
                ORDER BY
                    av.created_time ASC,
                    av.version_number ASC
                """,
                (
                    article_id,
                )
            )

            return cursor.fetchall()

        finally:

            cursor.close()
            conn.close()

    # ==================================
    # Get Previous Version
    # ==================================

    def get_previous_version(
        self,
        article_id,
        version_number
    ):

        conn = get_connection()

        cursor = conn.cursor(
            dictionary=True
        )

        try:

            cursor.execute(
                """
                SELECT
                    av.id,
                    av.article_id,
                    av.raw_document_id,
                    av.version_number,
                    av.file_hash,
                    av.storage_path,
                    av.file_size,
                    av.mime_type,
                    av.created_time
                FROM archive_versions av
                WHERE
                    av.article_id=%s
                AND
                    av.version_number < %s
                ORDER BY
                    av.version_number DESC
                LIMIT 1
                """,
                (
                    article_id,
                    version_number
                )
            )

            return cursor.fetchone()

        finally:

            cursor.close()
            conn.close()

    # ==================================
    # Get Next Version
    # ==================================

    def get_next_version(
        self,
        article_id,
        version_number
    ):

        conn = get_connection()

        cursor = conn.cursor(
            dictionary=True
        )

        try:

            cursor.execute(
                """
                SELECT
                    av.id,
                    av.article_id,
                    av.raw_document_id,
                    av.version_number,
                    av.file_hash,
                    av.storage_path,
                    av.file_size,
                    av.mime_type,
                    av.created_time
                FROM archive_versions av
                WHERE
                    av.article_id=%s
                AND
                    av.version_number > %s
                ORDER BY
                    av.version_number ASC
                LIMIT 1
                """,
                (
                    article_id,
                    version_number
                )
            )

            return cursor.fetchone()

        finally:

            cursor.close()
            conn.close()

    # ==================================
    # Get History Summary
    # ==================================

    def get_summary(
        self,
        article_id
    ):

        conn = get_connection()

        cursor = conn.cursor(
            dictionary=True
        )

        try:

            cursor.execute(
                """
                SELECT

                    COUNT(*) AS version_count,

                    MIN(version_number)
                        AS first_version,

                    MAX(version_number)
                        AS latest_version,

                    MIN(created_time)
                        AS first_created_time,

                    MAX(created_time)
                        AS latest_created_time

                FROM archive_versions

                WHERE article_id=%s
                """,
                (
                    article_id,
                )
            )

            return cursor.fetchone()

        finally:

            cursor.close()
            conn.close()

    # ==================================
    # Get History With Article
    # ==================================

    def get_history_with_article(
        self,
        article_id
    ):

        conn = get_connection()

        cursor = conn.cursor(
            dictionary=True
        )

        try:

            cursor.execute(
                """
                SELECT

                    a.id AS article_id,
                    a.document_id,
                    a.title,
                    a.url,
                    a.source,

                    av.id AS version_id,
                    av.raw_document_id,
                    av.version_number,
                    av.file_hash,
                    av.storage_path,
                    av.file_size,
                    av.mime_type,
                    av.created_time

                FROM articles a

                LEFT JOIN archive_versions av
                    ON a.id = av.article_id

                WHERE a.id=%s

                ORDER BY
                    av.version_number ASC
                """,
                (
                    article_id,
                )
            )

            return cursor.fetchall()

        finally:

            cursor.close()
            conn.close()