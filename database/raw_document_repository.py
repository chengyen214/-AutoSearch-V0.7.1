"""
database/raw_document_repository.py

AutoSearch V4

P1.1 Step 4.2.3

RawDocument Repository

功能:

1. 儲存 Raw HTML Archive 資訊
2. 依 ID 查詢 Raw Document
3. 查詢文章 Raw Archive
4. 檢查 Raw Document 是否存在
5. 依 File Hash 查詢既有 Archive
6. 依 URL + File Hash 查詢既有 Archive
7. 更新 Archive Metadata
8. 刪除 Article 的 Raw Archive
9. Database Row → RawDocument Model

Database:

    raw_documents

V4 Knowledge Archive Foundation

Duplicate Policy:

    RawDocument
        ↓
    URL
    +
    File Hash

    相同 URL + 相同 HTML
        ↓
    重用既有 RawDocument

    不同 URL + 相同 HTML
        ↓
    建立新的 RawDocument

注意:

    article_id 不參與 RawDocument
    Duplicate Detection。

Archive Version 的重複判斷：

    URL
    +
    File Hash

    ↓

    相同 URL + 相同 HTML
        → 不建立新的 Version

    相同 HTML + 不同 URL
        → 建立新的 Archive Version
        → 建立新的 RawDocument 關聯
"""

from database.connection import get_connection

from models.raw_document import RawDocument


class RawDocumentRepository:

    """
    Raw Document Repository

    封裝 raw_documents table 操作。

    Repository 負責：

        Database CRUD
        Database Query
        DB Row → Model

    不負責：

        Archive File Hash 計算
        Archive Version 判斷
        Archive Business Logic
    """

    # ==================================
    # Create
    # ==================================

    def save(
        self,
        raw_document
    ):
        """
        儲存 RawDocument。

        Duplicate Policy:

            URL
            +
            File Hash

        相同 URL + 相同 File Hash：

            → 重用既有 RawDocument

        不同 URL + 相同 File Hash：

            → 建立新的 RawDocument

        注意：

            article_id 不參與
            Duplicate Detection。

        例如：

            Article A
            URL A
            HTML X

            Article B
            URL B
            HTML X

        如果：

            Hash 相同
            URL 不同

        則：

            → 必須建立不同 RawDocument。

        Archive Version 是否建立新的 Version，
        由 ArchiveService /
        ArchiveVersionRepository 判斷。
        """

        # ----------------------------------
        # Validate
        # ----------------------------------

        if raw_document is None:

            raise ValueError(
                "raw_document cannot be None"
            )

        if not raw_document.file_hash:

            raise ValueError(
                "raw_document.file_hash cannot be empty"
            )

        if not raw_document.original_url:

            raise ValueError(
                "raw_document.original_url cannot be empty"
            )

        url = str(
            raw_document.original_url
        ).strip()

        if not url:

            raise ValueError(
                "raw_document.original_url cannot be empty"
            )

        # ----------------------------------
        # Existing URL + File Hash
        #
        # IMPORTANT:
        #
        # 不可以使用：
        #
        #     get_by_file_hash()
        #
        # 作為 save() 的 Duplicate Detection。
        #
        # 原因：
        #
        #     URL A + Hash X
        #     URL B + Hash X
        #
        # 必須可以建立不同 RawDocument。
        #
        # 正確條件：
        #
        #     URL
        #     +
        #     File Hash
        # ----------------------------------

        existing = (
            self.get_by_url_and_file_hash(
                url=url,
                file_hash=raw_document.file_hash
            )
        )

        if existing is not None:

            return existing

        # ----------------------------------
        # Database Connection
        # ----------------------------------

        conn = get_connection()

        cursor = conn.cursor()

        try:

            sql = """
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
            """

            cursor.execute(
                sql,
                (
                    raw_document.article_id,
                    url,
                    raw_document.storage_path,
                    raw_document.file_hash,
                    raw_document.file_size,
                    raw_document.mime_type
                )
            )

            conn.commit()

            raw_document.id = (
                cursor.lastrowid
            )

            return raw_document

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
        raw_document
    ):
        """
        save() Alias。
        """

        return self.save(
            raw_document
        )

    # ==================================
    # Query By ID
    # ==================================

    def get_by_id(
        self,
        raw_document_id
    ):
        """
        依 RawDocument ID
        查詢指定 RawDocument。

        用途：

            ArchiveVersion
                ↓
            raw_document_id
                ↓
            RawDocument
        """

        if raw_document_id is None:

            return None

        conn = get_connection()

        cursor = conn.cursor(
            dictionary=True
        )

        try:

            cursor.execute(
                """
                SELECT *
                FROM raw_documents
                WHERE id=%s
                LIMIT 1
                """,
                (
                    raw_document_id,
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
    # Query By Article
    # ==================================

    def get_by_article_id(
        self,
        article_id
    ):
        """
        根據 Article ID
        查詢最新 RawDocument。

        注意：

            article_id 只用於
            Article 關聯查詢。

        不用於 Duplicate Detection。
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
                FROM raw_documents
                WHERE article_id=%s
                ORDER BY id DESC
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
    # Query All By Article
    # ==================================

    def get_all_by_article_id(
        self,
        article_id
    ):
        """
        根據 Article ID
        取得所有 RawDocument。

        排序：

            最新 → 最舊

        注意：

            這只是 Article 關聯查詢，
            不代表 Duplicate Detection。
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
                FROM raw_documents
                WHERE article_id=%s
                ORDER BY id DESC
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
    # Query By File Hash
    # ==================================

    def get_by_file_hash(
        self,
        file_hash
    ):
        """
        根據 File Hash
        查詢既有 RawDocument。

        注意：

            這個方法是一般內容查詢 API。

        不應該被 save()
        用來進行 Duplicate Detection。

        因為：

            URL A + Hash X

        與：

            URL B + Hash X

        可以是不同 Archive。
        """

        if not file_hash:

            return None

        conn = get_connection()

        cursor = conn.cursor(
            dictionary=True
        )

        try:

            cursor.execute(
                """
                SELECT *
                FROM raw_documents
                WHERE file_hash=%s
                ORDER BY id ASC
                LIMIT 1
                """,
                (
                    file_hash,
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
    # Query By URL + File Hash
    # ==================================

    def get_by_url_and_file_hash(
        self,
        url,
        file_hash
    ):
        """
        依：

            Original URL
            +
            File Hash

        查詢既有 RawDocument。

        Duplicate Identity：

            URL
            +
            File Hash

        相同：

            → 相同 Archive Content

        不同 URL：

            → 即使 File Hash 相同，
              也不是同一個 RawDocument。

        例如：

            URL A
            Hash AAA

            URL A
            Hash AAA

            → 相同 RawDocument

        但：

            URL A
            Hash AAA

            URL B
            Hash AAA

            → 不同 RawDocument
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
                SELECT *
                FROM raw_documents
                WHERE original_url=%s
                AND file_hash=%s
                ORDER BY id ASC
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
    # Compatibility Alias
    # ==================================

    def get_by_article_url_hash(
        self,
        article_id,
        url,
        file_hash
    ):
        """
        Compatibility API。

        舊版 API：

            get_by_article_url_hash()

        新版 Duplicate Policy：

            article_id 不參與。

        真正條件：

            URL
            +
            File Hash
        """

        return self.get_by_url_and_file_hash(
            url=url,
            file_hash=file_hash
        )

    # ==================================
    # Find All
    # ==================================

    def find_all(
        self
    ):
        """
        取得所有 RawDocument。

        排序：

            最新 → 最舊
        """

        conn = get_connection()

        cursor = conn.cursor(
            dictionary=True
        )

        try:

            cursor.execute(
                """
                SELECT *
                FROM raw_documents
                ORDER BY id DESC
                """
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
    # Exists By Article
    # ==================================

    def exists(
        self,
        article_id
    ):
        """
        判斷 Article 是否存在 RawDocument。

        注意：

            這是 Article 關聯查詢，
            不是 Duplicate Detection。
        """

        if article_id is None:

            return False

        conn = get_connection()

        cursor = conn.cursor()

        try:

            cursor.execute(
                """
                SELECT id
                FROM raw_documents
                WHERE article_id=%s
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

        return result is not None

    # ==================================
    # Exists By Hash
    # ==================================

    def exists_by_file_hash(
        self,
        file_hash
    ):
        """
        判斷 File Hash 是否已存在。

        注意：

            這是一般 File Hash 查詢。

        不代表：

            save()
            的 Duplicate Detection。

        因為：

            相同 Hash
            +
            不同 URL

        仍然可以建立不同 RawDocument。
        """

        return (
            self.get_by_file_hash(
                file_hash
            )
            is not None
        )

    # ==================================
    # Exists By URL + Hash
    # ==================================

    def exists_by_url_and_file_hash(
        self,
        url,
        file_hash
    ):
        """
        判斷：

            URL
            +
            File Hash

        是否已存在。

        這是 Archive
        Duplicate Detection
        使用的查詢。

        article_id 不參與。
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

    def exists_by_article_id_and_file_hash(
        self,
        article_id,
        file_hash
    ):
        """
        Compatibility API。

        舊版：

            Article ID + File Hash

        新版：

            article_id 不參與
            Duplicate Detection。

        為避免破壞既有 API，
        保留方法名稱。

        實際上使用：

            File Hash

        """

        return (
            self.exists_by_file_hash(
                file_hash
            )
        )

    # ==================================
    # Update Path
    # ==================================

    def update_path(
        self,
        article_id,
        storage_path
    ):
        """
        更新 Article RawDocument
        的 Storage Path。

        注意：

            這是 Article 關聯更新，
            不涉及 Duplicate Detection。
        """

        if article_id is None:

            return False

        if not storage_path:

            return False

        conn = get_connection()

        cursor = conn.cursor()

        try:

            cursor.execute(
                """
                UPDATE raw_documents
                SET storage_path=%s
                WHERE article_id=%s
                """,
                (
                    storage_path,
                    article_id
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
    # Update Metadata
    # ==================================

    def update_metadata(
        self,
        raw_document_id,
        storage_path=None,
        file_size=None,
        mime_type=None
    ):
        """
        更新 RawDocument Metadata。

        只更新有提供的欄位。

        用途：

            Archive Metadata Repair
            Archive Migration
            File Metadata Update
        """

        if raw_document_id is None:

            return False

        fields = []
        values = []

        if storage_path is not None:

            fields.append(
                "storage_path=%s"
            )

            values.append(
                storage_path
            )

        if file_size is not None:

            fields.append(
                "file_size=%s"
            )

            values.append(
                file_size
            )

        if mime_type is not None:

            fields.append(
                "mime_type=%s"
            )

            values.append(
                mime_type
            )

        if not fields:

            return False

        values.append(
            raw_document_id
        )

        conn = get_connection()

        cursor = conn.cursor()

        try:

            sql = f"""
            UPDATE raw_documents
            SET {", ".join(fields)}
            WHERE id=%s
            """

            cursor.execute(
                sql,
                tuple(values)
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
    # Delete By ID
    # ==================================

    def delete_by_id(
        self,
        raw_document_id
    ):
        """
        刪除指定 RawDocument。

        不負責刪除實體 Archive File。
        """

        if raw_document_id is None:

            return False

        conn = get_connection()

        cursor = conn.cursor()

        try:

            cursor.execute(
                """
                DELETE FROM raw_documents
                WHERE id=%s
                """,
                (
                    raw_document_id,
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
        刪除 Article 的所有 RawDocument。

        注意：

            這是資料關聯刪除，
            不是 Duplicate Detection。

        不負責刪除實體 Archive File。
        """

        if article_id is None:

            return 0

        conn = get_connection()

        cursor = conn.cursor()

        try:

            cursor.execute(
                """
                DELETE FROM raw_documents
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
    # Convert DB Row
    # ==================================

    def _to_model(
        self,
        result
    ):
        """
        Database Row
        ↓
        RawDocument Model
        """

        if result is None:

            return None

        raw_document = RawDocument(

            article_id=result[
                "article_id"
            ],

            original_url=result[
                "original_url"
            ],

            storage_path=result[
                "storage_path"
            ],

            file_hash=result[
                "file_hash"
            ],

            file_size=result[
                "file_size"
            ],

            mime_type=result[
                "mime_type"
            ],

            created_time=result[
                "created_time"
            ]
        )

        raw_document.id = (
            result["id"]
        )

        return raw_document


# ==================================
# Public API
# ==================================

__all__ = [
    "RawDocumentRepository",
]
