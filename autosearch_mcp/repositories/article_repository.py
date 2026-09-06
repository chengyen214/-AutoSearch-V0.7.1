"""
autosearch_mcp/repositories/article_repository.py

AutoSearch V6.5

MCP-4

MCP Article Repository

用途：

    專門提供 AutoSearch MCP
    Article Search / Article Retrieval
    Advanced Search
    所需要的 Article Database Query。

Flow：

    MCP SearchTool
          ↓
    MCP SearchService
          ↓
    MCP ArticleRepository
          ↓
        articles

目前支援：

    Article Search
    Date Filter
    Source Filter
    Category Filter
    Sort
    Pagination

    Get Article By ID
    Get Article By Document ID
    Get Article By URL

本 Repository 與：

    database/article_repository.py

    分離。

原本的 ArticleRepository：

    負責 Article Persistence
    AI Analysis Persistence
    Article Management
    Database Lifecycle

MCP ArticleRepository：

    只負責 MCP 所需要的
    Article Query。

本階段原則：

    1. MCP 使用專用 Repository。
    2. 查詢資料來源為 articles。
    3. 支援 Article Search。
    4. 日期 Filter 使用 crawl_time。
    5. Source Filter 保留介面，但目前暫不使用。
    6. 支援 Category Filter。
    7. 支援 Sort。
    8. 支援 Pagination。
    9. 支援 Document ID Retrieval。
    10. 支援 URL Retrieval。
    11. 不使用 search_index。
    12. 不使用 SearchRankingService。
    13. 不直接由 MCP Tool 操作 SQL。
    14. 不修改既有 database/article_repository.py。
    15. 不重新實作 Article Persistence。
"""


from database.connection import (
    get_connection
)

from utils.logger import (
    logger
)


class ArticleRepository:
    """
    AutoSearch MCP 專用 Article Repository。

    負責：

        Article Search Query
        Article Retrieval Query
        Advanced Search Query

    支援：

        Search
        Date Filter
        Source Filter Interface
        Category Filter
        Sort
        Pagination

        Find By ID
        Find By Document ID
        Find By URL
        Count

    不負責：

        Article Save
        Article Update
        AI Analysis
        AI Worker
        Archive
        Ranking
        Search Index
    """

    # ==================================================
    # Constants
    # ==================================================

    DEFAULT_LIMIT = 20
    MAX_LIMIT = 100

    DEFAULT_SORT = "latest"

    # ==================================================
    # Sort
    # ==================================================

    ALLOWED_SORTS = {

        # Article ID
        "latest":
            "id DESC",

        "oldest":
            "id ASC",

        # ==================================================
        # MCP Date Sort
        #
        # published 欄位目前可能為 NULL，
        # 因此 MCP 日期相關排序改使用 crawl_time。
        # ==================================================

        "published":
            "crawl_time DESC",

        "published_oldest":
            "crawl_time ASC",

        # ==================================================
        # Explicit Crawl Time Sort
        # ==================================================

        "crawl_time":
            "crawl_time DESC",

        "crawl_time_oldest":
            "crawl_time ASC",

        # ==================================================
        # AI Importance
        # ==================================================

        "importance":
            "ai_importance DESC"
    }

    # ==================================================
    # Initialize
    # ==================================================

    def __init__(
        self
    ):
        """
        建立 Database Connection。
        """

        self.connection = get_connection()

        if self.connection is None:

            raise Exception(
                "Database connection failed."
            )

    # ==================================================
    # Search
    # ==================================================

    def search(
        self,
        query,
        limit=DEFAULT_LIMIT,
        source=None,
        category=None,
        published_from=None,
        published_to=None,
        sort_by=DEFAULT_SORT,
        page=1
    ):
        """
        搜尋 articles。

        支援：

            Query
            Date Filter
            Source Filter Interface
            Category Filter
            Sort
            Pagination

        搜尋欄位：

            keyword
            title
            content
            source
            ai_summary
            ai_category
            ai_keywords

        Date Filter：

            published_from
            published_to

            注意：

                MCP-4 目前不使用 articles.published
                作為日期篩選依據。

                原因：

                    articles.published
                    目前大量資料為 NULL。

                因此 MCP 日期 Filter
                統一使用：

                    crawl_time

        Source Filter：

            source

            注意：

                目前 articles.source
                資料為空。

                因此本階段保留 source
                參數介面，但不套用
                source SQL Filter。

        Category Filter：

            category

        Sort：

            latest
            oldest
            published
            published_oldest
            crawl_time
            crawl_time_oldest
            importance

        Pagination：

            page
            limit

        回傳：

            List[dict]
        """

        # ==================================================
        # Query Validation
        # ==================================================

        if query is None:

            return []

        query = str(
            query
        ).strip()

        if not query:

            return []

        # ==================================================
        # Limit Normalize
        # ==================================================

        try:

            limit = int(
                limit
            )

        except (
            TypeError,
            ValueError
        ):

            limit = self.DEFAULT_LIMIT

        if limit <= 0:

            limit = self.DEFAULT_LIMIT

        limit = min(
            limit,
            self.MAX_LIMIT
        )

        # ==================================================
        # Page Normalize
        # ==================================================

        try:

            page = int(
                page
            )

        except (
            TypeError,
            ValueError
        ):

            page = 1

        if page <= 0:

            page = 1

        offset = (
            page - 1
        ) * limit

        # ==================================================
        # Sort Normalize
        # ==================================================

        if sort_by is None:

            sort_by = self.DEFAULT_SORT

        sort_by = str(
            sort_by
        ).strip().lower()

        if sort_by not in self.ALLOWED_SORTS:

            sort_by = self.DEFAULT_SORT

        order_clause = self.ALLOWED_SORTS[
            sort_by
        ]

        # ==================================================
        # Build WHERE
        # ==================================================

        where_conditions = []

        values = []

        # ==================================================
        # Query Condition
        # ==================================================

        pattern = f"%{query}%"

        where_conditions.append(
            """
            (
                keyword LIKE %s
                OR title LIKE %s
                OR content LIKE %s
                OR source LIKE %s
                OR ai_summary LIKE %s
                OR ai_category LIKE %s
                OR ai_keywords LIKE %s
            )
            """
        )

        values.extend(
            [
                pattern,
                pattern,
                pattern,
                pattern,
                pattern,
                pattern,
                pattern
            ]
        )

        # ==================================================
        # Source Filter
        # ==================================================

        # MCP-4：
        #
        # source 參數目前只保留介面。
        #
        # articles.source 目前資料為空，
        # 因此暫時不套用 SQL Filter。
        #

        _ = source

        # ==================================================
        # Category Filter
        # ==================================================

        if category is not None:

            category = str(
                category
            ).strip()

            if category:

                where_conditions.append(
                    "ai_category=%s"
                )

                values.append(
                    category
                )

        # ==================================================
        # Date Filter From
        #
        # IMPORTANT:
        #
        # 不使用：
        #
        #     published >= %s
        #
        # 改使用：
        #
        #     crawl_time >= %s
        #
        # 因為 articles.published
        # 目前可能為 NULL。
        # ==================================================

        if published_from is not None:

            published_from = str(
                published_from
            ).strip()

            if published_from:

                where_conditions.append(
                    "crawl_time >= %s"
                )

                values.append(
                    published_from
                )

        # ==================================================
        # Date Filter To
        #
        # IMPORTANT:
        #
        # 不使用：
        #
        #     published <= %s
        #
        # 改使用：
        #
        #     crawl_time <= %s
        #
        # ==================================================

        if published_to is not None:

            published_to = str(
                published_to
            ).strip()

            if published_to:

                where_conditions.append(
                    "crawl_time <= %s"
                )

                values.append(
                    published_to
                )

        # ==================================================
        # WHERE Clause
        # ==================================================

        where_clause = "\nAND ".join(
            where_conditions
        )

        # ==================================================
        # SQL
        # ==================================================

        sql = f"""
            SELECT
                id,
                document_id,
                keyword,
                title,
                url,
                source,
                published,
                content,
                crawl_time,
                status,
                ai_summary,
                ai_category,
                ai_keywords,
                ai_importance,
                ai_model,
                ai_version,
                ai_analyze_time,
                ai_confidence,
                ai_status
            FROM articles
            WHERE
                {where_clause}
            ORDER BY {order_clause}
            LIMIT %s
            OFFSET %s
        """

        values.extend(
            [
                limit,
                offset
            ]
        )

        cursor = self.connection.cursor(
            dictionary=True
        )

        try:

            cursor.execute(
                sql,
                tuple(values)
            )

            rows = cursor.fetchall()

            return rows

        except Exception as e:

            logger.exception(
                "MCP Article advanced search failed: "
                f"{e}"
            )

            return []

        finally:

            cursor.close()

    # ==================================================
    # Find By ID
    # ==================================================

    def find_by_id(
        self,
        article_id
    ):
        """
        依 Article ID 查詢。

        Article ID 主要是 Database
        內部識別值。
        """

        if article_id is None:

            return None

        cursor = self.connection.cursor(
            dictionary=True
        )

        try:

            cursor.execute(
                """
                SELECT
                    id,
                    document_id,
                    keyword,
                    title,
                    url,
                    source,
                    published,
                    content,
                    crawl_time,
                    status,
                    ai_summary,
                    ai_category,
                    ai_keywords,
                    ai_importance,
                    ai_model,
                    ai_version,
                    ai_analyze_time,
                    ai_confidence,
                    ai_status
                FROM articles
                WHERE id=%s
                """,
                (
                    article_id,
                )
            )

            return cursor.fetchone()

        except Exception as e:

            logger.exception(
                "MCP Article find_by_id failed: "
                f"{e}"
            )

            return None

        finally:

            cursor.close()

    # ==================================================
    # Find By Document ID
    # ==================================================

    def find_by_document_id(
        self,
        document_id
    ):
        """
        依 Document ID 查詢 Article。

        Document ID 是 MCP Article
        Retrieval 的主要識別方式之一。
        """

        if document_id is None:

            return None

        document_id = str(
            document_id
        ).strip()

        if not document_id:

            return None

        cursor = self.connection.cursor(
            dictionary=True
        )

        try:

            cursor.execute(
                """
                SELECT
                    id,
                    document_id,
                    keyword,
                    title,
                    url,
                    source,
                    published,
                    content,
                    crawl_time,
                    status,
                    ai_summary,
                    ai_category,
                    ai_keywords,
                    ai_importance,
                    ai_model,
                    ai_version,
                    ai_analyze_time,
                    ai_confidence,
                    ai_status
                FROM articles
                WHERE document_id=%s
                LIMIT 1
                """,
                (
                    document_id,
                )
            )

            return cursor.fetchone()

        except Exception as e:

            logger.exception(
                "MCP Article find_by_document_id failed: "
                f"{e}"
            )

            return None

        finally:

            cursor.close()

    # ==================================================
    # Find By URL
    # ==================================================

    def find_by_url(
        self,
        url
    ):
        """
        依 Article URL 查詢 Article。
        """

        if url is None:

            return None

        url = str(
            url
        ).strip()

        if not url:

            return None

        cursor = self.connection.cursor(
            dictionary=True
        )

        try:

            cursor.execute(
                """
                SELECT
                    id,
                    document_id,
                    keyword,
                    title,
                    url,
                    source,
                    published,
                    content,
                    crawl_time,
                    status,
                    ai_summary,
                    ai_category,
                    ai_keywords,
                    ai_importance,
                    ai_model,
                    ai_version,
                    ai_analyze_time,
                    ai_confidence,
                    ai_status
                FROM articles
                WHERE url=%s
                LIMIT 1
                """,
                (
                    url,
                )
            )

            return cursor.fetchone()

        except Exception as e:

            logger.exception(
                "MCP Article find_by_url failed: "
                f"{e}"
            )

            return None

        finally:

            cursor.close()

    # ==================================================
    # Count
    # ==================================================

    def count(
        self
    ):
        """
        取得 articles 總數。
        """

        cursor = self.connection.cursor()

        try:

            cursor.execute(
                """
                SELECT COUNT(*)
                FROM articles
                """
            )

            result = cursor.fetchone()

            if result is None:

                return 0

            return result[0]

        except Exception as e:

            logger.exception(
                "MCP Article count failed: "
                f"{e}"
            )

            return 0

        finally:

            cursor.close()

    # ==================================================
    # Close
    # ==================================================

    def close(
        self
    ):
        """
        關閉 Database Connection。
        """

        try:

            if self.connection:

                self.connection.close()

                logger.info(
                    "MCP ArticleRepository "
                    "connection closed."
                )

        except Exception as e:

            logger.exception(
                "MCP ArticleRepository close failed: "
                f"{e}"
            )


__all__ = [
    "ArticleRepository"
]