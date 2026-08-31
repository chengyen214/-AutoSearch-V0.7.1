"""
database/archive_browser_repository.py

AutoSearch V4

P2.3.6
P2.4.2 Composite Archive Search

Archive Browser Repository

功能：

1. 查詢 Archive Article
2. 查詢 Article Archive Versions
3. 查詢指定日期 Archive
4. 查詢指定月份 Archive
5. 查詢指定年份 Archive
6. 查詢指定 Source Archive
7. 查詢最新 Archive
8. 分頁查詢 Archive
9. 計算 Archive 數量
10. 查詢 Archive Statistics
11. Database Row -> Archive Browser Record
12. Composite Archive Search

Database：

    articles
    raw_documents
    archive_versions
    knowledge_archive
    knowledge_scores
    search_index
    ai_tasks

重要：

目前 AutoSearch V4 的 AI Analysis
直接儲存在 articles table。

不存在：

    ai_analysis

因此：

    Repository 不可 JOIN ai_analysis。

AI 欄位：

    articles.ai_summary
    articles.ai_category
    articles.ai_keywords
    articles.ai_importance
    articles.ai_model
    articles.ai_version
    articles.ai_analyze_time
    articles.ai_confidence
    articles.ai_status

Archive Version Schema：

    archive_versions.id
    archive_versions.article_id
    archive_versions.raw_document_id
    archive_versions.version_number
    archive_versions.file_hash
    archive_versions.storage_path
    archive_versions.file_size
    archive_versions.mime_type
    archive_versions.created_time

用途：

    提供 Archive Browser Service
    所需的 Database Query。

架構：

    Web UI / API
          ↓
    ArchiveWebService
          ↓
    ArchiveBrowserRepository
          ↓
    MySQL Database

Repository 負責 Database Query。
Service 不直接操作 Database。
"""

from database.connection import get_connection


class ArchiveBrowserRepository:

    """
    Archive Browser Repository

    P2.3.6

    負責：

        Archive Browse
        Date Browse
        Source Browse
        Version Browse
        Pagination
        Archive Statistics

    P2.4.2：

        Composite Archive Search
    """

    # ============================================================
    # Internal Helpers
    # ============================================================

    @staticmethod
    def _normalize_limit(
        limit,
        default=20
    ):
        """
        統一處理 LIMIT。

        避免：

            None
            0
            負數

        造成 SQL LIMIT 問題。
        """

        if limit is None:
            return default

        try:

            limit = int(limit)

        except (
            TypeError,
            ValueError
        ):

            return default

        if limit < 1:
            return default

        return limit

    # ============================================================

    @staticmethod
    def _normalize_offset(
        offset
    ):
        """
        統一處理 OFFSET。
        """

        if offset is None:
            return 0

        try:

            offset = int(offset)

        except (
            TypeError,
            ValueError
        ):

            return 0

        if offset < 0:
            return 0

        return offset

    # ============================================================

    @staticmethod
    def _normalize_page(
        page
    ):
        """
        統一處理 page。
        """

        if page is None:
            return 1

        try:

            page = int(page)

        except (
            TypeError,
            ValueError
        ):

            return 1

        if page < 1:
            return 1

        return page

    # ============================================================

    @staticmethod
    def _normalize_page_size(
        page_size
    ):
        """
        統一處理 page_size。
        """

        if page_size is None:
            return 20

        try:

            page_size = int(
                page_size
            )

        except (
            TypeError,
            ValueError
        ):

            return 20

        if page_size < 1:
            return 20

        return page_size

    # ============================================================
    # Browse Articles
    # ============================================================

    def get_articles(
        self,
        limit=20,
        offset=0
    ):
        """
        查詢具有 Archive Version 的 Articles。

        排序：

            最新 Archive
            ↓
            最舊 Archive

        注意：

            使用 INNER JOIN archive_versions。

            因此沒有 Archive Version 的 Article
            不會出現在 Archive Browser。
        """

        limit = self._normalize_limit(
            limit
        )

        offset = self._normalize_offset(
            offset
        )

        conn = get_connection()

        cursor = conn.cursor(
            dictionary=True
        )

        try:

            cursor.execute(
                """
                SELECT

                    a.id,
                    a.document_id,
                    a.keyword,
                    a.title,
                    a.url,
                    a.source,
                    a.published,
                    a.crawl_time,
                    a.status,

                    a.ai_summary,
                    a.ai_category,
                    a.ai_keywords,
                    a.ai_importance,
                    a.ai_model,
                    a.ai_version,
                    a.ai_analyze_time,
                    a.ai_confidence,
                    a.ai_status,

                    COUNT(
                        av.id
                    ) AS version_count,

                    MAX(
                        av.version_number
                    ) AS latest_version,

                    MAX(
                        av.created_time
                    ) AS latest_archive_time

                FROM articles a

                INNER JOIN archive_versions av
                    ON a.id = av.article_id

                GROUP BY

                    a.id,
                    a.document_id,
                    a.keyword,
                    a.title,
                    a.url,
                    a.source,
                    a.published,
                    a.crawl_time,
                    a.status,

                    a.ai_summary,
                    a.ai_category,
                    a.ai_keywords,
                    a.ai_importance,
                    a.ai_model,
                    a.ai_version,
                    a.ai_analyze_time,
                    a.ai_confidence,
                    a.ai_status

                ORDER BY
                    latest_archive_time DESC

                LIMIT %s
                OFFSET %s
                """,
                (
                    limit,
                    offset
                )
            )

            return cursor.fetchall()

        finally:

            cursor.close()
            conn.close()

    # ============================================================
    # Get Article
    # ============================================================

    def get_article(
        self,
        article_id
    ):
        """
        取得指定 Article 的 Archive 資訊。

        回傳：

            Article 基本資料
            AI Analysis
            Archive Version 統計
        """

        conn = get_connection()

        cursor = conn.cursor(
            dictionary=True
        )

        try:

            cursor.execute(
                """
                SELECT

                    a.id,
                    a.document_id,
                    a.keyword,
                    a.title,
                    a.url,
                    a.source,
                    a.published,
                    a.crawl_time,
                    a.status,

                    a.ai_summary,
                    a.ai_category,
                    a.ai_keywords,
                    a.ai_importance,
                    a.ai_model,
                    a.ai_version,
                    a.ai_analyze_time,
                    a.ai_confidence,
                    a.ai_status,

                    COUNT(
                        av.id
                    ) AS version_count,

                    MAX(
                        av.version_number
                    ) AS latest_version,

                    MAX(
                        av.created_time
                    ) AS latest_archive_time

                FROM articles a

                INNER JOIN archive_versions av
                    ON a.id = av.article_id

                WHERE a.id = %s

                GROUP BY

                    a.id,
                    a.document_id,
                    a.keyword,
                    a.title,
                    a.url,
                    a.source,
                    a.published,
                    a.crawl_time,
                    a.status,

                    a.ai_summary,
                    a.ai_category,
                    a.ai_keywords,
                    a.ai_importance,
                    a.ai_model,
                    a.ai_version,
                    a.ai_analyze_time,
                    a.ai_confidence,
                    a.ai_status
                """,
                (
                    article_id,
                )
            )

            return cursor.fetchone()

        finally:

            cursor.close()
            conn.close()

    # ============================================================
    # Get Article Versions
    # ============================================================

    def get_versions(
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

    # ============================================================
    # Get Latest Archives
    # ============================================================

    def get_latest(
        self,
        limit=20
    ):
        """
        取得最新 Archive Versions。

        排序：

            最新 Archive
            ↓
            最舊 Archive
        """

        limit = self._normalize_limit(
            limit
        )

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
                    av.created_time,

                    a.document_id,
                    a.keyword,
                    a.title,
                    a.url,
                    a.source,
                    a.published,
                    a.crawl_time,
                    a.status,

                    a.ai_summary,
                    a.ai_category,
                    a.ai_keywords,
                    a.ai_importance,
                    a.ai_model,
                    a.ai_version,
                    a.ai_analyze_time,
                    a.ai_confidence,
                    a.ai_status

                FROM archive_versions av

                INNER JOIN articles a
                    ON a.id = av.article_id

                ORDER BY
                    av.created_time DESC

                LIMIT %s
                """,
                (
                    limit,
                )
            )

            return cursor.fetchall()

        finally:

            cursor.close()
            conn.close()

    # ============================================================
    # Browse By Date
    # ============================================================

    def get_by_date(
        self,
        archive_date,
        limit=20,
        offset=0
    ):
        """
        依 Archive 日期查詢。

        archive_date：

            YYYY-MM-DD
        """

        limit = self._normalize_limit(
            limit
        )

        offset = self._normalize_offset(
            offset
        )

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
                    av.created_time,

                    a.document_id,
                    a.keyword,
                    a.title,
                    a.url,
                    a.source,
                    a.published,
                    a.crawl_time,
                    a.status,

                    a.ai_summary,
                    a.ai_category,
                    a.ai_keywords,
                    a.ai_importance,
                    a.ai_model,
                    a.ai_version,
                    a.ai_analyze_time,
                    a.ai_confidence,
                    a.ai_status

                FROM archive_versions av

                INNER JOIN articles a
                    ON a.id = av.article_id

                WHERE DATE(
                    av.created_time
                ) = %s

                ORDER BY
                    av.created_time DESC

                LIMIT %s
                OFFSET %s
                """,
                (
                    archive_date,
                    limit,
                    offset
                )
            )

            return cursor.fetchall()

        finally:

            cursor.close()
            conn.close()

    # ============================================================
    # Browse By Month
    # ============================================================

    def get_by_month(
        self,
        year,
        month,
        limit=20,
        offset=0
    ):
        """
        依 Archive 年/月查詢。
        """

        limit = self._normalize_limit(
            limit
        )

        offset = self._normalize_offset(
            offset
        )

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
                    av.created_time,

                    a.document_id,
                    a.keyword,
                    a.title,
                    a.url,
                    a.source,
                    a.published,
                    a.crawl_time,
                    a.status,

                    a.ai_summary,
                    a.ai_category,
                    a.ai_keywords,
                    a.ai_importance,
                    a.ai_model,
                    a.ai_version,
                    a.ai_analyze_time,
                    a.ai_confidence,
                    a.ai_status

                FROM archive_versions av

                INNER JOIN articles a
                    ON a.id = av.article_id

                WHERE YEAR(
                    av.created_time
                ) = %s

                AND MONTH(
                    av.created_time
                ) = %s

                ORDER BY
                    av.created_time DESC

                LIMIT %s
                OFFSET %s
                """,
                (
                    year,
                    month,
                    limit,
                    offset
                )
            )

            return cursor.fetchall()

        finally:

            cursor.close()
            conn.close()

    # ============================================================
    # Browse By Year
    # ============================================================

    def get_by_year(
        self,
        year,
        limit=20,
        offset=0
    ):
        """
        依 Archive 年份查詢。
        """

        limit = self._normalize_limit(
            limit
        )

        offset = self._normalize_offset(
            offset
        )

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
                    av.created_time,

                    a.document_id,
                    a.keyword,
                    a.title,
                    a.url,
                    a.source,
                    a.published,
                    a.crawl_time,
                    a.status,

                    a.ai_summary,
                    a.ai_category,
                    a.ai_keywords,
                    a.ai_importance,
                    a.ai_model,
                    a.ai_version,
                    a.ai_analyze_time,
                    a.ai_confidence,
                    a.ai_status

                FROM archive_versions av

                INNER JOIN articles a
                    ON a.id = av.article_id

                WHERE YEAR(
                    av.created_time
                ) = %s

                ORDER BY
                    av.created_time DESC

                LIMIT %s
                OFFSET %s
                """,
                (
                    year,
                    limit,
                    offset
                )
            )

            return cursor.fetchall()

        finally:

            cursor.close()
            conn.close()

    # ============================================================
    # Browse By Source
    # ============================================================

    def get_by_source(
        self,
        source,
        limit=20,
        offset=0
    ):
        """
        依 Article Source 查詢 Archive。
        """

        limit = self._normalize_limit(
            limit
        )

        offset = self._normalize_offset(
            offset
        )

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
                    av.created_time,

                    a.document_id,
                    a.keyword,
                    a.title,
                    a.url,
                    a.source,
                    a.published,
                    a.crawl_time,
                    a.status,

                    a.ai_summary,
                    a.ai_category,
                    a.ai_keywords,
                    a.ai_importance,
                    a.ai_model,
                    a.ai_version,
                    a.ai_analyze_time,
                    a.ai_confidence,
                    a.ai_status

                FROM archive_versions av

                INNER JOIN articles a
                    ON a.id = av.article_id

                WHERE a.source = %s

                ORDER BY
                    av.created_time DESC

                LIMIT %s
                OFFSET %s
                """,
                (
                    source,
                    limit,
                    offset
                )
            )

            return cursor.fetchall()

        finally:

            cursor.close()
            conn.close()

    # ============================================================
    # Get Latest Version
    # ============================================================

    def get_latest_version(
        self,
        article_id
    ):
        """
        取得 Article 最新 Archive Version。
        """

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

    # ============================================================
    # Basic Search
    # ============================================================

    def search(
        self,
        keyword,
        limit=20,
        offset=0
    ):
        """
        搜尋 Archive Article。

        搜尋：

            title
            keyword
            source
            url
            ai_summary
            ai_keywords
            ai_category
        """

        if keyword is None:
            return []

        keyword = str(
            keyword
        ).strip()

        if not keyword:
            return []

        limit = self._normalize_limit(
            limit
        )

        offset = self._normalize_offset(
            offset
        )

        search_keyword = (
            f"%{keyword}%"
        )

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
                    av.created_time,

                    a.document_id,
                    a.keyword,
                    a.title,
                    a.url,
                    a.source,
                    a.published,
                    a.crawl_time,
                    a.status,

                    a.ai_summary,
                    a.ai_category,
                    a.ai_keywords,
                    a.ai_importance,
                    a.ai_model,
                    a.ai_version,
                    a.ai_analyze_time,
                    a.ai_confidence,
                    a.ai_status

                FROM archive_versions av

                INNER JOIN articles a
                    ON a.id = av.article_id

                WHERE

                    a.title LIKE %s

                    OR a.keyword LIKE %s

                    OR a.source LIKE %s

                    OR a.url LIKE %s

                    OR a.ai_summary LIKE %s

                    OR a.ai_keywords LIKE %s

                    OR a.ai_category LIKE %s

                ORDER BY
                    av.created_time DESC

                LIMIT %s
                OFFSET %s
                """,
                (
                    search_keyword,
                    search_keyword,
                    search_keyword,
                    search_keyword,
                    search_keyword,
                    search_keyword,
                    search_keyword,
                    limit,
                    offset
                )
            )

            return cursor.fetchall()

        finally:

            cursor.close()
            conn.close()

    # ============================================================
    # Composite Archive Search
    # ============================================================

    # ============================================================
    # Composite Archive Search
    # ============================================================

    def composite_search(
        self,
        keyword=None,
        source=None,
        url=None,
        date_from=None,
        date_to=None,
        year=None,
        month=None,
        category=None,
        importance_min=None,
        importance_max=None,
        page=1,
        page_size=20
    ):
        """
        P2.4.2

        Composite Search。

        注意：

            Composite Search 直接搜尋 articles。

            不依賴：
                archive_versions

            不 JOIN：
                archive_versions

        支援：

            keyword
            source
            url
            date_from
            date_to
            year
            month
            category
            importance_min
            importance_max

        AI 欄位：

            articles.ai_summary
            articles.ai_category
            articles.ai_keywords
            articles.ai_importance
            articles.ai_model
            articles.ai_version
            articles.ai_analyze_time
            articles.ai_confidence
            articles.ai_status

        日期：

            優先使用 articles.published

            如果 published 為 NULL，
            使用 articles.crawl_time。

        分頁：

            page
            page_size

        回傳：

        {
            "results": [...],
            "total": 10,
            "page": 1,
            "page_size": 20
        }
        """

        # ========================================================
        # Pagination
        # ========================================================

        page = self._normalize_page(
            page
        )

        page_size = self._normalize_page_size(
            page_size
        )

        offset = (
            (page - 1)
            * page_size
        )

        # ========================================================
        # Conditions
        # ========================================================

        conditions = []
        values = []

        # ========================================================
        # Keyword
        # ========================================================

        if keyword is not None:

            keyword = str(
                keyword
            ).strip()

            if keyword:

                search_keyword = (
                    f"%{keyword}%"
                )

                conditions.append(
                    """
                    (
                        a.title LIKE %s

                        OR a.keyword LIKE %s

                        OR a.source LIKE %s

                        OR a.url LIKE %s

                        OR a.ai_summary LIKE %s

                        OR a.ai_keywords LIKE %s

                        OR a.ai_category LIKE %s
                    )
                    """
                )

                values.extend(
                    [
                        search_keyword,
                        search_keyword,
                        search_keyword,
                        search_keyword,
                        search_keyword,
                        search_keyword,
                        search_keyword
                    ]
                )

        # ========================================================
        # Source
        # ========================================================

        if source is not None:

            source = str(
                source
            ).strip()

            if source:

                conditions.append(
                    """
                    a.source LIKE %s
                    """
                )

                values.append(
                    f"%{source}%"
                )

        # ========================================================
        # URL
        # ========================================================

        if url is not None:

            url = str(
                url
            ).strip()

            if url:

                conditions.append(
                    """
                    a.url LIKE %s
                    """
                )

                values.append(
                    f"%{url}%"
                )

        # ========================================================
        # Article Date Expression
        #
        # Priority:
        #
        #     published
        #         ↓
        #     crawl_time
        #
        # 不使用 archive_versions.created_time
        # ========================================================

        article_date_expression = """
            COALESCE(
                a.published,
                a.crawl_time
            )
        """

        # ========================================================
        # Date From
        # ========================================================

        if date_from is not None:

            conditions.append(
                f"""
                DATE(
                    {article_date_expression}
                ) >= %s
                """
            )

            values.append(
                date_from
            )

        # ========================================================
        # Date To
        # ========================================================

        if date_to is not None:

            conditions.append(
                f"""
                DATE(
                    {article_date_expression}
                ) <= %s
                """
            )

            values.append(
                date_to
            )

        # ========================================================
        # Year
        # ========================================================

        if year is not None:

            conditions.append(
                f"""
                YEAR(
                    {article_date_expression}
                ) = %s
                """
            )

            values.append(
                year
            )

        # ========================================================
        # Month
        # ========================================================

        if month is not None:

            conditions.append(
                f"""
                MONTH(
                    {article_date_expression}
                ) = %s
                """
            )

            values.append(
                month
            )

        # ========================================================
        # AI Category
        # ========================================================

        if category is not None:

            category = str(
                category
            ).strip()

            if category:

                conditions.append(
                    """
                    a.ai_category LIKE %s
                    """
                )

                values.append(
                    f"%{category}%"
                )

        # ========================================================
        # Importance Min
        # ========================================================

        if importance_min is not None:

            conditions.append(
                """
                a.ai_importance >= %s
                """
            )

            values.append(
                importance_min
            )

        # ========================================================
        # Importance Max
        # ========================================================

        if importance_max is not None:

            conditions.append(
                """
                a.ai_importance <= %s
                """
            )

            values.append(
                importance_max
            )

        # ========================================================
        # WHERE
        # ========================================================

        where_sql = ""

        if conditions:

            where_sql = (
                "WHERE "
                +
                " AND ".join(
                    conditions
                )
            )

        # ========================================================
        # Connection
        # ========================================================

        conn = get_connection()

        cursor = conn.cursor(
            dictionary=True
        )

        try:

            # ====================================================
            # Count
            #
            # 只計算 articles
            #
            # 不使用 archive_versions
            # ====================================================

            count_sql = f"""
                SELECT
                    COUNT(*) AS total

                FROM articles a

                {where_sql}
            """

            cursor.execute(
                count_sql,
                tuple(values)
            )

            count_result = (
                cursor.fetchone()
            )

            total = 0

            if count_result:

                total = int(
                    count_result["total"]
                )

            # ====================================================
            # Results
            #
            # 只查 articles
            #
            # 不 JOIN archive_versions
            # ====================================================

            result_sql = f"""
                SELECT

                    a.id,
                    a.document_id,
                    a.keyword,
                    a.title,
                    a.url,
                    a.source,
                    a.published,
                    a.crawl_time,
                    a.status,

                    a.ai_summary,
                    a.ai_category,
                    a.ai_keywords,
                    a.ai_importance,
                    a.ai_model,
                    a.ai_version,
                    a.ai_analyze_time,
                    a.ai_confidence,
                    a.ai_status

                FROM articles a

                {where_sql}

                ORDER BY
                    COALESCE(
                        a.published,
                        a.crawl_time
                    ) DESC

                LIMIT %s
                OFFSET %s
            """

            result_values = (
                list(values)
                +
                [
                    page_size,
                    offset
                ]
            )

            cursor.execute(
                result_sql,
                tuple(result_values)
            )

            results = (
                cursor.fetchall()
            )

            # ====================================================
            # Return
            # ====================================================

            return {
                "results": results,
                "total": total,
                "page": page,
                "page_size": page_size
            }

        finally:

            cursor.close()
            conn.close()

    # ============================================================
    # Count Archives
    # ============================================================

    def count(
        self
    ):
        """
        計算 Archive Version 總數。
        """

        conn = get_connection()

        cursor = conn.cursor()

        try:

            cursor.execute(
                """
                SELECT
                    COUNT(*)

                FROM archive_versions
                """
            )

            result = cursor.fetchone()

            if not result:
                return 0

            return result[0]

        finally:

            cursor.close()
            conn.close()

    # ============================================================
    # Count Articles
    # ============================================================

    def count_articles(
        self
    ):
        """
        計算具有 Archive 的 Article 數量。
        """

        conn = get_connection()

        cursor = conn.cursor()

        try:

            cursor.execute(
                """
                SELECT
                    COUNT(
                        DISTINCT article_id
                    )

                FROM archive_versions
                """
            )

            result = cursor.fetchone()

            if not result:
                return 0

            return result[0]

        finally:

            cursor.close()
            conn.close()

    # ============================================================
    # Count By Source
    # ============================================================

    def count_by_source(
        self,
        source=None
    ):
        """
        計算指定 Source 的 Archive 數量。

        source=None：

            計算所有 Source 的 Archive 數量。
        """

        conn = get_connection()

        cursor = conn.cursor()

        try:

            if source is None:

                cursor.execute(
                    """
                    SELECT
                        COUNT(*)

                    FROM archive_versions av

                    INNER JOIN articles a
                        ON a.id = av.article_id
                    """
                )

            else:

                cursor.execute(
                    """
                    SELECT
                        COUNT(*)

                    FROM archive_versions av

                    INNER JOIN articles a
                        ON a.id = av.article_id

                    WHERE a.source = %s
                    """,
                    (
                        source,
                    )
                )

            result = cursor.fetchone()

            if not result:
                return 0

            return result[0]

        finally:

            cursor.close()
            conn.close()

    # ============================================================
    # Count By Date
    # ============================================================

    def count_by_date(
        self,
        archive_date=None
    ):
        """
        計算指定日期 Archive 數量。

        archive_date=None：

            計算所有 Archive 數量。
        """

        conn = get_connection()

        cursor = conn.cursor()

        try:

            if archive_date is None:

                cursor.execute(
                    """
                    SELECT
                        COUNT(*)

                    FROM archive_versions
                    """
                )

            else:

                cursor.execute(
                    """
                    SELECT
                        COUNT(*)

                    FROM archive_versions

                    WHERE DATE(
                        created_time
                    ) = %s
                    """,
                    (
                        archive_date,
                    )
                )

            result = cursor.fetchone()

            if not result:
                return 0

            return result[0]

        finally:

            cursor.close()
            conn.close()

    # ============================================================
    # Statistics
    # ============================================================

    def get_statistics(
        self
    ):
        """
        取得 Archive Statistics。

        Returns
        -------

        dict

        {
            "article_count": ...,
            "version_count": ...,
            "source_count": ...,
            "total_size": ...
        }
        """

        conn = get_connection()

        cursor = conn.cursor(
            dictionary=True
        )

        try:

            cursor.execute(
                """
                SELECT

                    COUNT(
                        DISTINCT av.article_id
                    ) AS article_count,

                    COUNT(*) AS version_count,

                    COUNT(
                        DISTINCT a.source
                    ) AS source_count,

                    COALESCE(
                        SUM(
                            av.file_size
                        ),
                        0
                    ) AS total_size

                FROM archive_versions av

                INNER JOIN articles a
                    ON a.id = av.article_id
                """
            )

            result = cursor.fetchone()

            if not result:

                return {
                    "article_count": 0,
                    "version_count": 0,
                    "source_count": 0,
                    "total_size": 0
                }

            return result

        finally:

            cursor.close()
            conn.close()

    # ============================================================
    # Repr
    # ============================================================

    def __repr__(
        self
    ):

        return (
            "ArchiveBrowserRepository()"
        )