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
9. 查詢 URL + File Hash 是否已存在
10. 刪除指定 Version
11. 刪除 Article 的所有 Version
12. Database Row → ArchiveVersion Model

Database:

    archive_versions

Relationship:

    archive_versions
            │
            │ raw_document_id
            ↓
    raw_documents
            │
            └── original_url

Duplicate Detection:

    original_url
        +
    file_hash

注意：

    article_id 不參與 Archive Duplicate Detection。

    article_id 只負責：

        1. Version 所屬 Article
        2. Version Number 管理
        3. Article Version History

V4 Knowledge Archive Foundation
"""

from database.connection import get_connection

from models.archive_version import (
    ArchiveVersion
)


class ArchiveVersionRepository:
    """
    Archive Version Repository

    封裝 archive_versions table 操作。

    P2.3.2 負責：

        Article Version Storage
        Version Retrieval
        Version Management
        Archive Change Detection

    Duplicate Detection:

        original_url
        +
        file_hash

    article_id 不參與 Duplicate Detection。
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

        回傳：

            ArchiveVersion
        """

        if archive_version is None:

            raise ValueError(
                "archive_version cannot be None"
            )

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

            archive_version.id = (
                cursor.lastrowid
            )

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

        if version_id is None:

            return None

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
                LIMIT 1
                """,
                (
                    version_id,
                )
            )

            result = cursor.fetchone()

        finally:

            cursor.close()
            conn.close()

        if result is None:

            return None

        return self._to_model(
            result
        )

    # ==================================
    # Get Specific Version
    # ==================================

    def get_version(
        self,
        article_id,
        version_number
    ):
        """
        取得 Article 指定 Version。

        article_id 在這裡是：

            Version History 定位條件

        不是 Duplicate Detection 條件。
        """

        if article_id is None:

            return None

        if version_number is None:

            return None

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

        finally:

            cursor.close()
            conn.close()

        if result is None:

            return None

        return self._to_model(
            result
        )

    # ==================================
    # Get By URL + File Hash
    # ==================================

    def get_by_url_and_file_hash(
        self,
        url,
        file_hash
    ):
        """
        查詢是否已存在相同 Archive。

        Duplicate Detection:

            original_url
            +
            file_hash

        article_id 不參與判斷。

        例如：

            Article A
            URL = https://example.com/a
            Hash = ABC

        與：

            Article B
            URL = https://example.com/a
            Hash = ABC

        仍視為相同 Archive Content。

        Database Relationship:

            archive_versions.raw_document_id
                    ↓
            raw_documents.id
                    ↓
            raw_documents.original_url
        """

        if not url:

            return None

        if not file_hash:

            return None

        url = str(
            url
        ).strip()

        if not url:

            return None

        conn = get_connection()

        cursor = conn.cursor(
            dictionary=True
        )

        try:

            cursor.execute(
                """
                SELECT
                    av.*
                FROM archive_versions av
                INNER JOIN raw_documents rd
                    ON av.raw_document_id = rd.id
                WHERE rd.original_url=%s
                AND av.file_hash=%s
                ORDER BY av.id ASC
                LIMIT 1
                """,
                (
                    url,
                    file_hash
                )
            )

            result = cursor.fetchone()

        finally:

            cursor.close()
            conn.close()

        if result is None:

            return None

        return self._to_model(
            result
        )

    # ==================================
    # Alias
    # ==================================

    def get_by_article_url_hash(
        self,
        article_id,
        url,
        file_hash
    ):
        """
        Compatibility API。

        注意：

        article_id 保留在 method signature，
        是為了相容目前 ArchiveService 呼叫方式。

        但：

            article_id

        不參與 Duplicate Detection。

        真正判斷：

            URL
            +
            File Hash
        """

        return self.get_by_url_and_file_hash(
            url=url,
            file_hash=file_hash
        )

    # ==================================
    # Get By Article ID
    # ==================================

    def get_by_article_id(
        self,
        article_id
    ):
        """
        取得 Article 所有 Archive Versions。

        這裡使用 article_id
        是因為這是 Version History Query。

        不是 Duplicate Detection。
        """

        if article_id is None:

            return []

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

        finally:

            cursor.close()
            conn.close()

        return [
            self._to_model(row)
            for row in results
        ]

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

        if article_id is None:

            return None

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

        finally:

            cursor.close()
            conn.close()

        if result is None:

            return None

        return self._to_model(
            result
        )

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

        if article_id is None:

            return 0

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

        finally:

            cursor.close()
            conn.close()

        if result is None:

            return 0

        if result[0] is None:

            return 0

        return result[0]

    # ==================================
    # Get Next Version Number
    # ==================================

    def get_next_version_number(
        self,
        article_id
    ):
        """
        計算下一個 Version Number。

        Version Number 是：

            Article Scope

        因此這裡 article_id
        是必要條件。

        例如：

            Article 10
                Version 1
                Version 2

            Article 20
                Version 1
        """

        latest = (
            self.get_latest_version_number(
                article_id
            )
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

        用於 Version Management。

        不是 Duplicate Detection。
        """

        if article_id is None:

            return False

        if version_number is None:

            return False

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

        finally:

            cursor.close()
            conn.close()

        return result is not None

    # ==================================
    # Exists By URL + Hash
    # ==================================

    def exists_by_url_and_file_hash(
        self,
        url,
        file_hash
    ):
        """
        判斷 Archive 是否已存在。

        Duplicate Detection:

            URL
            +
            File Hash

        article_id 不參與判斷。
        """

        return (
            self.get_by_url_and_file_hash(
                url=url,
                file_hash=file_hash
            )
            is not None
        )

    # ==================================
    # Compatibility Exists API
    # ==================================

    def exists_by_article_url_hash(
        self,
        article_id,
        url,
        file_hash
    ):
        """
        Compatibility API。

        article_id 不參與 Duplicate Detection。

        實際判斷：

            URL
            +
            File Hash
        """

        return (
            self.exists_by_url_and_file_hash(
                url=url,
                file_hash=file_hash
            )
        )

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

        if article_id is None:

            return 0

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

        finally:

            cursor.close()
            conn.close()

        if result is None:

            return 0

        return result[0]

    # ==================================
    # Delete By ID
    # ==================================

    def delete_by_id(
        self,
        version_id
    ):
        """
        刪除指定 Archive Version。

        回傳：

            True
                成功刪除

            False
                找不到 Version
        """

        if version_id is None:

            return False

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

            return (
                cursor.rowcount > 0
            )

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

        回傳：

            實際刪除筆數
        """

        if article_id is None:

            return 0

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
        Database Row
        ↓
        ArchiveVersion Model
        """

        if row is None:

            return None

        archive_version = ArchiveVersion(

            article_id=row[
                "article_id"
            ],

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

        archive_version.id = (
            row["id"]
        )

        return archive_version


# ======================================
# Public API
# ======================================

__all__ = [
    "ArchiveVersionRepository",
]
