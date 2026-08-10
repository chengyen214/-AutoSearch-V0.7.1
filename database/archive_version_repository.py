"""
database/archive_version_repository.py

AutoSearch V4

P2.3.2

Archive Version Repository

功能:

1. 儲存 Archive Version
2. 插入 Archive Version
3. 查詢指定 Version
4. 查詢 Article 所有 Version
5. 查詢最新 Version
6. 計算下一個 Version Number
7. 檢查 Version 是否存在
8. 計算 Article Version 數量
9. 刪除指定 Version
10. 刪除 Article 的所有 Version
11. Database Row → ArchiveVersion Model

Database:

    archive_versions
"""

from database.connection import get_connection
from models.archive_version import ArchiveVersion


class ArchiveVersionRepository:
    """
    Archive Version Repository

    封裝 archive_versions table 操作。

    P2.3.2 負責：

        Article Version Storage
        Version Retrieval
        Version Management
    """

    # ==================================
    # Create
    # ==================================

    def save(
        self,
        archive_version
    ):
        """
        儲存 Archive Version。
        """

        conn = get_connection()
        cursor = conn.cursor()

        try:

            sql = """
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
            """

            cursor.execute(
                sql,
                (
                    archive_version.article_id,
                    archive_version.raw_document_id,
                    archive_version.version_number,
                    archive_version.file_hash,
                    archive_version.storage_path,
                    archive_version.file_size,
                    archive_version.mime_type
                )
            )

            conn.commit()

            archive_version.id = cursor.lastrowid

            return archive_version

        except Exception:

            conn.rollback()

            raise

        finally:

            cursor.close()
            conn.close()

    # ==================================
    # Alias
    # ==================================

    def insert(
        self,
        archive_version
    ):
        """
        save() Alias。
        """

        return self.save(
            archive_version
        )

    # ==================================
    # Get By ID
    # ==================================

    def get_by_id(
        self,
        version_id
    ):
        """
        依 Version ID 取得 Archive Version。
        """

        conn = get_connection()

        cursor = conn.cursor(
            dictionary=True
        )

        try:

            cursor.execute(
                """
                SELECT *
                FROM archive_versions
                WHERE id=%s
                """,
                (
                    version_id,
                )
            )

            result = cursor.fetchone()

            if result is None:
                return None

            return self._to_model(result)

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
        """
        取得 Article 指定版本。

        例如：

            Article 10
            Version 3

        用於：

            Version Viewer
            Version Comparison
            Version Diff
        """

        conn = get_connection()

        cursor = conn.cursor(
            dictionary=True
        )

        try:

            cursor.execute(
                """
                SELECT *
                FROM archive_versions
                WHERE article_id=%s
                AND version_number=%s
                LIMIT 1
                """,
                (
                    article_id,
                    version_number
                )
            )

            result = cursor.fetchone()

            if result is None:
                return None

            return self._to_model(result)

        finally:

            cursor.close()
            conn.close()

    # ==================================
    # Get By Article ID
    # ==================================

    def get_by_article_id(
        self,
        article_id
    ):
        """
        取得 Article 所有 Archive Versions。

        排序：

            Version 1
            Version 2
            Version 3
            ...
        """

        conn = get_connection()

        cursor = conn.cursor(
            dictionary=True
        )

        try:

            cursor.execute(
                """
                SELECT *
                FROM archive_versions
                WHERE article_id=%s
                ORDER BY version_number ASC
                """,
                (
                    article_id,
                )
            )

            results = cursor.fetchall()

            return [
                self._to_model(row)
                for row in results
            ]

        finally:

            cursor.close()
            conn.close()

    # ==================================
    # Get Latest Version
    # ==================================

    def get_latest_version(
        self,
        article_id
    ):
        """
        取得 Article 最新 Version。
        """

        conn = get_connection()

        cursor = conn.cursor(
            dictionary=True
        )

        try:

            cursor.execute(
                """
                SELECT *
                FROM archive_versions
                WHERE article_id=%s
                ORDER BY version_number DESC
                LIMIT 1
                """,
                (
                    article_id,
                )
            )

            result = cursor.fetchone()

            if result is None:
                return None

            return self._to_model(result)

        finally:

            cursor.close()
            conn.close()

    # ==================================
    # Get Latest Version Number
    # ==================================

    def get_latest_version_number(
        self,
        article_id
    ):
        """
        取得 Article 最新 Version Number。

        若不存在 Version：

            回傳 0
        """

        conn = get_connection()

        cursor = conn.cursor()

        try:

            cursor.execute(
                """
                SELECT MAX(version_number)
                FROM archive_versions
                WHERE article_id=%s
                """,
                (
                    article_id,
                )
            )

            result = cursor.fetchone()

            if result is None:
                return 0

            if result[0] is None:
                return 0

            return result[0]

        finally:

            cursor.close()
            conn.close()

    # ==================================
    # Get Next Version Number
    # ==================================

    def get_next_version_number(
        self,
        article_id
    ):
        """
        計算下一個 Version Number。

        例如：

            沒有 Version → 1
            Version 1 → 2
            Version 2 → 3
        """

        latest = self.get_latest_version_number(
            article_id
        )

        return latest + 1

    # ==================================
    # Exists
    # ==================================

    def exists(
        self,
        article_id,
        version_number
    ):
        """
        檢查指定 Version 是否存在。
        """

        conn = get_connection()

        cursor = conn.cursor()

        try:

            cursor.execute(
                """
                SELECT id
                FROM archive_versions
                WHERE article_id=%s
                AND version_number=%s
                LIMIT 1
                """,
                (
                    article_id,
                    version_number
                )
            )

            result = cursor.fetchone()

            return result is not None

        finally:

            cursor.close()
            conn.close()

    # ==================================
    # Count By Article
    # ==================================

    def count_by_article_id(
        self,
        article_id
    ):
        """
        計算 Article 的 Archive Version 數量。
        """

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

            return result[0]

        finally:

            cursor.close()
            conn.close()

    # ==================================
    # Delete By ID
    # ==================================

    def delete_by_id(
        self,
        version_id
    ):
        """
        刪除指定 Archive Version。
        """

        conn = get_connection()

        cursor = conn.cursor()

        try:

            cursor.execute(
                """
                DELETE FROM archive_versions
                WHERE id=%s
                """,
                (
                    version_id,
                )
            )

            conn.commit()

            return cursor.rowcount > 0

        except Exception:

            conn.rollback()

            raise

        finally:

            cursor.close()
            conn.close()

    # ==================================
    # Delete By Article
    # ==================================

    def delete_by_article_id(
        self,
        article_id
    ):
        """
        刪除 Article 的所有 Archive Versions。
        """

        conn = get_connection()

        cursor = conn.cursor()

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

            return cursor.rowcount

        except Exception:

            conn.rollback()

            raise

        finally:

            cursor.close()
            conn.close()

    # ==================================
    # Convert DB Row → Model
    # ==================================

    def _to_model(
        self,
        row
    ):
        """
        Database Row → ArchiveVersion Model。
        """

        archive_version = ArchiveVersion(

            article_id=row["article_id"],

            raw_document_id=row[
                "raw_document_id"
            ],

            version_number=row[
                "version_number"
            ],

            file_hash=row[
                "file_hash"
            ],

            storage_path=row[
                "storage_path"
            ],

            file_size=row[
                "file_size"
            ],

            mime_type=row[
                "mime_type"
            ],

            created_time=row[
                "created_time"
            ]
        )

        archive_version.id = row["id"]

        return archive_version