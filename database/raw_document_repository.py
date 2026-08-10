"""
database/raw_document_repository.py

AutoSearch V4

P1.1 Step 4.2.3

RawDocument Repository

功能:

1. 儲存 Raw HTML Archive 資訊
2. 查詢文章 Raw Archive
3. 檢查 Raw Document 是否存在
4. 依 File Hash 查詢既有 Archive
5. 更新 Archive Metadata
6. 刪除 Article 的 Raw Archive

Database:

raw_documents

V4 Knowledge Archive Foundation
"""

from database.connection import get_connection

from models.raw_document import RawDocument


class RawDocumentRepository:

    """
    Raw Document Repository

    封裝 raw_documents table 操作。
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

        如果 file_hash 已存在，
        不重複建立 RawDocument。

        回傳：

            RawDocument
        """

        # ----------------------------------
        # 先檢查 File Hash
        # ----------------------------------

        existing = self.get_by_file_hash(
            raw_document.file_hash
        )

        if existing is not None:

            return existing

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
                    raw_document.original_url,
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

        return self.save(
            raw_document
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
        查詢 Raw Archive。

        注意：

        一個 Article 可能有多個
        RawDocument。

        因此這裡取得最新一筆。
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
    # Query By File Hash
    # ==================================

    def get_by_file_hash(
        self,
        file_hash
    ):
        """
        根據 File Hash
        查詢既有 RawDocument。

        用途：

        相同 HTML 內容會產生相同
        SHA256 Hash。

        如果 Hash 已存在，
        代表內容沒有變化。
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
    # Find All
    # ==================================

    def find_all(
        self
    ):

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

            result = cursor.fetchall()

        finally:

            cursor.close()
            conn.close()

        return result

    # ==================================
    # Exists By Article
    # ==================================

    def exists(
        self,
        article_id
    ):

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
        """

        return (
            self.get_by_file_hash(
                file_hash
            )
            is not None
        )

    # ==================================
    # Update Path
    # ==================================

    def update_path(
        self,
        article_id,
        storage_path
    ):

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

        finally:

            cursor.close()
            conn.close()

    # ==================================
    # Delete
    # ==================================

    def delete_by_article_id(
        self,
        article_id
    ):

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
        →
        RawDocument Model
        """

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