"""
database/historical_search_repository.py

AutoSearch V4

P2.3.5

Historical Search Repository

功能:

1. 搜尋歷史版本
2. 依 Article 搜尋歷史內容
3. 依 Keyword 搜尋歷史內容
4. 依 Source 搜尋歷史內容
5. 依 Version 搜尋
6. 依日期範圍搜尋
7. 取得 Article 歷史版本
8. 取得指定歷史版本
9. 計算歷史搜尋結果數量

Database:

    articles
    raw_documents
    archive_versions

設計:

Historical Search
        ↓
HistoricalSearchRepository
        ↓
archive_versions
        ↓
raw_documents
        ↓
articles
"""

from database.connection import get_connection


class HistoricalSearchRepository:
    """
    Historical Search Repository

    封裝 Historical Search 所需的
    Database 查詢。

    P2.3.5 負責：

        Historical Content Search
        Historical Version Search
        Historical Timeline Query
    """

    # ==================================
    # Search
    # ==================================

    def search(
        self,
        keyword=None,
        article_id=None,
        source=None,
        start_date=None,
        end_date=None,
        version_number=None,
        limit=50,
        offset=0
    ):
        """
        搜尋歷史版本。

        Parameters
        ----------
        keyword :
            搜尋 Article title / content

        article_id :
            指定 Article

        source :
            指定來源

        start_date :
            歷史版本開始日期

        end_date :
            歷史版本結束日期

        version_number :
            指定 Version

        limit :
            最大結果數量

        offset :
            分頁 offset

        Returns
        -------
        list
        """

        conn = get_connection()

        cursor = conn.cursor(
            dictionary=True
        )

        try:

            sql = """
                SELECT
                    av.id AS version_id,
                    av.article_id,
                    av.raw_document_id,
                    av.version_number,
                    av.file_hash,
                    av.storage_path,
                    av.file_size,
                    av.mime_type,
                    av.created_time,

                    a.title,
                    a.url,
                    a.source,
                    a.keyword,

                    rd.original_url

                FROM archive_versions av

                INNER JOIN articles a
                    ON av.article_id = a.id

                LEFT JOIN raw_documents rd
                    ON av.raw_document_id = rd.id

                WHERE 1=1
            """

            params = []

            # ==================================
            # Keyword
            # ==================================

            if keyword:

                sql += """
                    AND (
                        a.title LIKE %s
                        OR a.keyword LIKE %s
                    )
                """

                search_keyword = (
                    f"%{keyword}%"
                )

                params.extend(
                    [
                        search_keyword,
                        search_keyword
                    ]
                )

            # ==================================
            # Article
            # ==================================

            if article_id is not None:

                sql += """
                    AND av.article_id = %s
                """

                params.append(
                    article_id
                )

            # ==================================
            # Source
            # ==================================

            if source:

                sql += """
                    AND a.source = %s
                """

                params.append(
                    source
                )

            # ==================================
            # Version
            # ==================================

            if version_number is not None:

                sql += """
                    AND av.version_number = %s
                """

                params.append(
                    version_number
                )

            # ==================================
            # Start Date
            # ==================================

            if start_date is not None:

                sql += """
                    AND av.created_time >= %s
                """

                params.append(
                    start_date
                )

            # ==================================
            # End Date
            # ==================================

            if end_date is not None:

                sql += """
                    AND av.created_time <= %s
                """

                params.append(
                    end_date
                )

            # ==================================
            # Order
            # ==================================

            sql += """
                ORDER BY
                    av.created_time DESC,
                    av.article_id ASC,
                    av.version_number DESC
            """

            # ==================================
            # Pagination
            # ==================================

            sql += """
                LIMIT %s
                OFFSET %s
            """

            params.extend(
                [
                    limit,
                    offset
                ]
            )

            cursor.execute(
                sql,
                tuple(params)
            )

            return cursor.fetchall()

        finally:

            cursor.close()
            conn.close()

    # ==================================
    # Search By Article
    # ==================================

    def get_by_article_id(
        self,
        article_id
    ):
        """
        取得 Article 所有歷史版本。

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
                SELECT
                    av.*,
                    a.title,
                    a.url,
                    a.source,
                    a.keyword
                FROM archive_versions av
                INNER JOIN articles a
                    ON av.article_id = a.id
                WHERE av.article_id = %s
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
    # Get Version
    # ==================================

    def get_version(
        self,
        article_id,
        version_number
    ):
        """
        取得指定 Article 的歷史版本。
        """

        conn = get_connection()

        cursor = conn.cursor(
            dictionary=True
        )

        try:

            cursor.execute(
                """
                SELECT
                    av.*,
                    a.title,
                    a.url,
                    a.source,
                    a.keyword,
                    rd.original_url
                FROM archive_versions av
                INNER JOIN articles a
                    ON av.article_id = a.id
                LEFT JOIN raw_documents rd
                    ON av.raw_document_id = rd.id
                WHERE av.article_id = %s
                AND av.version_number = %s
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
    # Get Latest Historical Version
    # ==================================

    def get_latest_version(
        self,
        article_id
    ):
        """
        取得 Article 最新歷史版本。
        """

        conn = get_connection()

        cursor = conn.cursor(
            dictionary=True
        )

        try:

            cursor.execute(
                """
                SELECT
                    av.*,
                    a.title,
                    a.url,
                    a.source,
                    a.keyword
                FROM archive_versions av
                INNER JOIN articles a
                    ON av.article_id = a.id
                WHERE av.article_id = %s
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
    # Search By Source
    # ==================================

    def search_by_source(
        self,
        source,
        limit=50,
        offset=0
    ):
        """
        搜尋指定來源的歷史版本。
        """

        return self.search(
            source=source,
            limit=limit,
            offset=offset
        )

    # ==================================
    # Search By Date
    # ==================================

    def search_by_date(
        self,
        start_date,
        end_date,
        limit=50,
        offset=0
    ):
        """
        依歷史日期搜尋。
        """

        return self.search(
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            offset=offset
        )

    # ==================================
    # Count
    # ==================================

    def count(
        self,
        keyword=None,
        article_id=None,
        source=None,
        start_date=None,
        end_date=None,
        version_number=None
    ):
        """
        計算 Historical Search 結果數量。
        """

        conn = get_connection()

        cursor = conn.cursor()

        try:

            sql = """
                SELECT COUNT(*)

                FROM archive_versions av

                INNER JOIN articles a
                    ON av.article_id = a.id

                WHERE 1=1
            """

            params = []

            # ==================================
            # Keyword
            # ==================================

            if keyword:

                sql += """
                    AND (
                        a.title LIKE %s
                        OR a.keyword LIKE %s
                    )
                """

                search_keyword = (
                    f"%{keyword}%"
                )

                params.extend(
                    [
                        search_keyword,
                        search_keyword
                    ]
                )

            # ==================================
            # Article
            # ==================================

            if article_id is not None:

                sql += """
                    AND av.article_id = %s
                """

                params.append(
                    article_id
                )

            # ==================================
            # Source
            # ==================================

            if source:

                sql += """
                    AND a.source = %s
                """

                params.append(
                    source
                )

            # ==================================
            # Version
            # ==================================

            if version_number is not None:

                sql += """
                    AND av.version_number = %s
                """

                params.append(
                    version_number
                )

            # ==================================
            # Date
            # ==================================

            if start_date is not None:

                sql += """
                    AND av.created_time >= %s
                """

                params.append(
                    start_date
                )

            if end_date is not None:

                sql += """
                    AND av.created_time <= %s
                """

                params.append(
                    end_date
                )

            cursor.execute(
                sql,
                tuple(params)
            )

            result = cursor.fetchone()

            return result[0]

        finally:

            cursor.close()
            conn.close()

    # ==================================
    # Exists
    # ==================================

    def exists(
        self,
        article_id,
        version_number
    ):
        """
        檢查指定歷史版本是否存在。
        """

        conn = get_connection()

        cursor = conn.cursor()

        try:

            cursor.execute(
                """
                SELECT id
                FROM archive_versions
                WHERE article_id = %s
                AND version_number = %s
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