"""
database/article_repository.py

AutoSearch V5

Article Repository

用途：

    負責 Article 的 Database Persistence。

Pipeline：

    Crawl
      ↓
    Parser
      ↓
    Article
      ↓
    ArticleRepository
      ↓
    SQL
      ↓
    AI Task
      ↓
    AI Worker
      ↓
    ArticleRepository.update_ai_analysis()

Repository 負責：

    - Article 儲存
    - Article 基本查詢
    - Document ID Duplicate Detection
    - Article Model Restore
    - Current Content Snapshot 更新
    - Async AI Status
    - AI Analysis Persistence
    - Failed AI 查詢
    - Article Count
    - Article Management Persistence
    - Database Connection Lifecycle

Repository 不負責：

    - Parser
    - Crawler
    - AI Analysis
    - AI Worker
    - Scheduler
    - AI Batch Trigger
    - Search Ranking
    - Knowledge Processing
    - Archive Version Creation
    - Search
    - Parser Registration
    - SQL Schema / Migration
"""


from datetime import datetime
import json


from database.connection import (
    get_connection
)


from models.article import (
    Article
)


from models.ai_analysis import (
    AIAnalysis
)


from utils.logger import (
    logger
)


class ArticleRepository:
    """
    AutoSearch V5 Article Repository。

    只負責 Article Database Persistence。

    不負責：

        AI Analysis
        Worker Scheduling
        AI Batch Trigger
        Search
        Ranking
        Knowledge
        Archive Version
        Parser
        Crawler
    """

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
    # Create
    # ==================================================

    def save(
        self,
        article
    ):
        """
        儲存 Article。

        Article 在 Parser 完成後即可直接儲存。

        AI Analysis 與 Article Storage 解耦。

        尚未 AI Analysis：

            ai_summary      = NULL
            ai_category     = NULL
            ai_keywords     = NULL
            ai_importance   = NULL
            ai_model        = NULL
            ai_version      = NULL
            ai_analyze_time = NULL
            ai_confidence   = NULL
            ai_status       = pending

        已存在 AI Analysis：

            保存 AI Analysis 結果
            ai_status = completed

        Duplicate：

            document_id 已存在
            → 不重複 INSERT

        回傳：

            True
                成功

            False
                失敗 / Duplicate
        """

        if article is None:

            logger.error(
                "Article save failed: "
                "article is None"
            )

            return False

        document_id = getattr(
            article,
            "document_id",
            None
        )

        if not document_id:

            logger.error(
                "Article save failed: "
                "document_id is empty"
            )

            return False

        if self.exists(
            document_id
        ):

            logger.info(
                "Article already exists: "
                f"document_id={document_id}"
            )

            return False

        cursor = self.connection.cursor()

        sql = """
            INSERT INTO articles
            (
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
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )
        """

        try:

            published = self._normalize_datetime(
                getattr(
                    article,
                    "published",
                    None
                )
            )

            crawl_time = getattr(
                article,
                "crawl_time",
                None
            )

            ai_summary = None
            ai_category = None
            ai_keywords = None
            ai_importance = None
            ai_model = None
            ai_version = None
            ai_analyze_time = None
            ai_confidence = None

            ai_status = "pending"

            analysis = getattr(
                article,
                "ai_analysis",
                None
            )

            if analysis is not None:

                ai_summary = getattr(
                    analysis,
                    "summary",
                    None
                )

                ai_category = getattr(
                    analysis,
                    "category",
                    None
                )

                keywords = getattr(
                    analysis,
                    "keywords",
                    None
                )

                if keywords is not None:

                    ai_keywords = json.dumps(
                        keywords,
                        ensure_ascii=False
                    )

                ai_importance = getattr(
                    analysis,
                    "importance",
                    None
                )

                if ai_importance is not None:

                    ai_importance = int(
                        ai_importance
                    )

                ai_model = getattr(
                    analysis,
                    "ai_model",
                    None
                )

                ai_version = getattr(
                    analysis,
                    "ai_version",
                    None
                )

                ai_analyze_time = getattr(
                    analysis,
                    "analyze_time",
                    None
                )

                ai_confidence = getattr(
                    analysis,
                    "confidence",
                    None
                )

                if ai_confidence is not None:

                    ai_confidence = float(
                        ai_confidence
                    )

                ai_status = "completed"

            values = (
                document_id,

                getattr(
                    article,
                    "keyword",
                    ""
                ),

                getattr(
                    article,
                    "title",
                    ""
                ),

                getattr(
                    article,
                    "url",
                    ""
                ),

                getattr(
                    article,
                    "source",
                    ""
                ),

                published,

                getattr(
                    article,
                    "content",
                    ""
                ),

                crawl_time,

                getattr(
                    article,
                    "status",
                    "Success"
                ),

                ai_summary,
                ai_category,
                ai_keywords,
                ai_importance,
                ai_model,
                ai_version,
                ai_analyze_time,
                ai_confidence,
                ai_status
            )

            cursor.execute(
                sql,
                values
            )

            self.connection.commit()

            article.id = cursor.lastrowid

            logger.info(
                "Article saved: "
                f"id={article.id}, "
                f"document_id={document_id}"
            )

            return True

        except Exception as e:

            self.connection.rollback()

            logger.exception(
                f"Article save failed: {e}"
            )

            return False

        finally:

            cursor.close()

    # ==================================================
    # Insert
    # ==================================================

    def insert(
        self,
        article
    ):
        """
        Compatibility Layer。

        舊：

            repository.insert(article)

        新：

            repository.save(article)

        統一使用 save()。
        """

        if not self.save(
            article
        ):

            return None

        return article

    # ==================================================
    # Query All
    # ==================================================

    def find_all(
        self,
        limit=None
    ):
        """
        取得 Article。
        """

        cursor = self.connection.cursor(
            dictionary=True
        )

        try:

            sql = """
                SELECT *
                FROM articles
                ORDER BY id DESC
            """

            if limit is not None:

                sql += """
                    LIMIT %s
                """

                cursor.execute(
                    sql,
                    (
                        int(limit),
                    )
                )

            else:

                cursor.execute(
                    sql
                )

            return cursor.fetchall()

        finally:

            cursor.close()

    # ==================================================
    # Query By ID
    # ==================================================

    def find_by_id(
        self,
        article_id
    ):
        """
        依 Database ID 查詢 Article。
        """

        cursor = self.connection.cursor(
            dictionary=True
        )

        try:

            cursor.execute(
                """
                SELECT *
                FROM articles
                WHERE id=%s
                """,
                (
                    article_id,
                )
            )

            return cursor.fetchone()

        finally:

            cursor.close()

    # ==================================================
    # Query Article Model By ID
    # ==================================================

    def find_model_by_id(
        self,
        article_id
    ):
        """
        Database Row
            ↓
        Article Model

        主要供：

            AI Worker
            AI Service

        使用。
        """

        row = self.find_by_id(
            article_id
        )

        if row is None:

            logger.warning(
                f"Article not found: id={article_id}"
            )

            return None

        article = Article(
            keyword=row.get(
                "keyword",
                ""
            ),

            title=row.get(
                "title",
                ""
            ),

            url=row.get(
                "url",
                ""
            ),

            published=row.get(
                "published"
            ),

            source=row.get(
                "source",
                ""
            ),

            content=row.get(
                "content",
                ""
            ),

            crawl_time=row.get(
                "crawl_time"
            ),

            status=row.get(
                "status",
                "Success"
            ),

            document_id=row.get(
                "document_id",
                ""
            )
        )

        article.id = row.get(
            "id"
        )

        article.ai_status = row.get(
            "ai_status",
            "pending"
        )

        ai_summary = row.get(
            "ai_summary"
        )

        if ai_summary is None:

            article.ai_analysis = None

            return article

        try:

            keywords = row.get(
                "ai_keywords"
            )

            if isinstance(
                keywords,
                str
            ):

                try:

                    keywords = json.loads(
                        keywords
                    )

                except json.JSONDecodeError:

                    keywords = []

            if keywords is None:

                keywords = []

            analysis = AIAnalysis(

                article_id=article.id,

                summary=ai_summary,

                category=row.get(
                    "ai_category"
                ),

                keywords=keywords,

                importance=row.get(
                    "ai_importance"
                ),

                ai_model=row.get(
                    "ai_model"
                ),

                ai_version=row.get(
                    "ai_version"
                ),

                analyze_time=row.get(
                    "ai_analyze_time"
                ),

                confidence=row.get(
                    "ai_confidence"
                )
            )

            article.ai_analysis = analysis

        except Exception as e:

            logger.exception(
                "Restore AI Analysis failed: "
                f"{e}"
            )

            article.ai_analysis = None

        return article

    # ==================================================
    # Query By URL
    # ==================================================

    def find_by_url(
        self,
        url
    ):
        """
        依 URL 查詢目前 Article。
        """

        cursor = self.connection.cursor(
            dictionary=True
        )

        try:

            cursor.execute(
                """
                SELECT *
                FROM articles
                WHERE url=%s
                ORDER BY id DESC
                LIMIT 1
                """,
                (
                    url,
                )
            )

            return cursor.fetchone()

        finally:

            cursor.close()

    # ==================================================
    # Query By Document ID
    # ==================================================

    def find_by_document_id(
        self,
        document_id
    ):
        """
        依 Document ID 查詢 Article。
        """

        cursor = self.connection.cursor(
            dictionary=True
        )

        try:

            cursor.execute(
                """
                SELECT *
                FROM articles
                WHERE document_id=%s
                LIMIT 1
                """,
                (
                    document_id,
                )
            )

            return cursor.fetchone()

        finally:

            cursor.close()

    # ==================================================
    # Compatibility
    # ==================================================

    def get_by_document_id(
        self,
        document_id
    ):
        """
        Compatibility Alias。

        舊程式可能使用：

            get_by_document_id()

        統一轉向：

            find_by_document_id()
        """

        return self.find_by_document_id(
            document_id
        )

    # ==================================================
    # Duplicate Detection
    # ==================================================

    def exists(
        self,
        document_id
    ):
        """
        檢查 document_id 是否已存在。
        """

        cursor = self.connection.cursor()

        try:

            cursor.execute(
                """
                SELECT COUNT(*)
                FROM articles
                WHERE document_id=%s
                """,
                (
                    document_id,
                )
            )

            result = cursor.fetchone()

            if result is None:

                return False

            return result[0] > 0

        finally:

            cursor.close()

    # ==================================================
    # Query By Keyword
    # ==================================================

    def find_by_keyword(
        self,
        keyword
    ):
        """
        依 Keyword 查詢 Article。
        """

        cursor = self.connection.cursor(
            dictionary=True
        )

        try:

            cursor.execute(
                """
                SELECT *
                FROM articles
                WHERE keyword=%s
                ORDER BY id DESC
                """,
                (
                    keyword,
                )
            )

            return cursor.fetchall()

        finally:

            cursor.close()

    # ==================================================
    # Query By Source
    # ==================================================

    def find_by_source(
        self,
        source
    ):
        """
        依 Source 查詢 Article。
        """

        cursor = self.connection.cursor(
            dictionary=True
        )

        try:

            cursor.execute(
                """
                SELECT *
                FROM articles
                WHERE source=%s
                ORDER BY id DESC
                """,
                (
                    source,
                )
            )

            return cursor.fetchall()

        finally:

            cursor.close()

    # ==================================================
    # Query By AI Importance
    # ==================================================

    def find_by_importance(
        self,
        level
    ):
        """
        取得 AI Importance >= level。
        """

        cursor = self.connection.cursor(
            dictionary=True
        )

        try:

            cursor.execute(
                """
                SELECT *
                FROM articles
                WHERE ai_importance >= %s
                ORDER BY ai_importance DESC, id DESC
                """,
                (
                    level,
                )
            )

            return cursor.fetchall()

        finally:

            cursor.close()

    # ==================================================
    # Query By AI Category
    # ==================================================

    def find_by_category(
        self,
        category
    ):
        """
        依 AI Category 查詢。
        """

        cursor = self.connection.cursor(
            dictionary=True
        )

        try:

            cursor.execute(
                """
                SELECT *
                FROM articles
                WHERE ai_category=%s
                ORDER BY id DESC
                """,
                (
                    category,
                )
            )

            return cursor.fetchall()

        finally:

            cursor.close()

    # ==================================================
    # Query By AI Keyword
    # ==================================================

    def find_by_ai_keyword(
        self,
        keyword
    ):
        """
        依 AI Keyword 搜尋。

        ai_keywords 儲存為 JSON。

        使用 LIKE 而非 JSON_CONTAINS，
        保持對既有資料格式的相容性。
        """

        cursor = self.connection.cursor(
            dictionary=True
        )

        try:

            pattern = f"%{keyword}%"

            cursor.execute(
                """
                SELECT *
                FROM articles
                WHERE ai_keywords LIKE %s
                ORDER BY id DESC
                """,
                (
                    pattern,
                )
            )

            return cursor.fetchall()

        finally:

            cursor.close()

    # ==================================================
    # AI Top
    # ==================================================

    def get_top_ai_articles(
        self,
        limit=10
    ):
        """
        取得 AI Importance 最高的 Article。
        """

        cursor = self.connection.cursor(
            dictionary=True
        )

        try:

            cursor.execute(
                """
                SELECT *
                FROM articles
                WHERE ai_importance IS NOT NULL
                ORDER BY
                    ai_importance DESC,
                    ai_confidence DESC,
                    id DESC
                LIMIT %s
                """,
                (
                    int(limit),
                )
            )

            return cursor.fetchall()

        finally:

            cursor.close()

    # ==================================================
    # Current Content Snapshot
    # ==================================================

    def update_content_snapshot(
        self,
        article_id,
        document_id,
        content,
        crawl_time=None,
        status=None
    ):
        """
        更新 Article Current Snapshot。

        Article：

            articles.content
            articles.document_id

        代表：

            目前最新版本。

        歷史版本：

            由 Archive Pipeline
            另外處理。

        本方法不處理：

            AI
            Archive
            Knowledge
        """

        fields = [
            "document_id=%s",
            "content=%s"
        ]

        values = [
            document_id,
            content
        ]

        if crawl_time is not None:

            fields.append(
                "crawl_time=%s"
            )

            values.append(
                crawl_time
            )

        if status is not None:

            fields.append(
                "status=%s"
            )

            values.append(
                status
            )

        values.append(
            article_id
        )

        sql = f"""
            UPDATE articles
            SET {", ".join(fields)}
            WHERE id=%s
        """

        cursor = self.connection.cursor()

        try:

            cursor.execute(
                sql,
                tuple(values)
            )

            affected = cursor.rowcount

            if affected <= 0:

                self.connection.rollback()

                logger.warning(
                    "Article snapshot update failed: "
                    f"id={article_id}"
                )

                return False

            self.connection.commit()

            logger.info(
                "Article snapshot updated: "
                f"id={article_id}, "
                f"document_id={document_id}"
            )

            return True

        except Exception as e:

            self.connection.rollback()

            logger.exception(
                "Article snapshot update failed: "
                f"{e}"
            )

            return False

        finally:

            cursor.close()

    # ==================================================
    # Article Metadata Update
    # ==================================================

    def update(
        self,
        article_id,
        keyword=None,
        title=None,
        url=None,
        source=None,
        published=None,
        status=None
    ):
        """
        更新 Article Metadata。

        只處理 Article 基本欄位。

        不處理：

            AI Analysis
            Archive
            Knowledge
            AI Task
        """

        if article_id is None:

            return False

        fields = []
        values = []

        if keyword is not None:

            fields.append(
                "keyword=%s"
            )

            values.append(
                keyword
            )

        if title is not None:

            fields.append(
                "title=%s"
            )

            values.append(
                title
            )

        if url is not None:

            fields.append(
                "url=%s"
            )

            values.append(
                url
            )

        if source is not None:

            fields.append(
                "source=%s"
            )

            values.append(
                source
            )

        if published is not None:

            fields.append(
                "published=%s"
            )

            values.append(
                self._normalize_datetime(
                    published
                )
            )

        if status is not None:

            fields.append(
                "status=%s"
            )

            values.append(
                status
            )

        if not fields:

            logger.warning(
                "Article update skipped: "
                "no fields provided"
            )

            return False

        values.append(
            article_id
        )

        sql = f"""
            UPDATE articles
            SET {", ".join(fields)}
            WHERE id=%s
        """

        cursor = self.connection.cursor()

        try:

            cursor.execute(
                sql,
                tuple(values)
            )

            affected = cursor.rowcount

            if affected <= 0:

                self.connection.rollback()

                logger.warning(
                    "Article metadata update failed: "
                    f"id={article_id}"
                )

                return False

            self.connection.commit()

            logger.info(
                "Article metadata updated: "
                f"id={article_id}"
            )

            return True

        except Exception as e:

            self.connection.rollback()

            logger.exception(
                "Article metadata update failed: "
                f"{e}"
            )

            return False

        finally:

            cursor.close()

    # ==================================================
    # Async AI
    # ==================================================

    def find_pending_ai(
        self,
        limit=20
    ):
        """
        取得尚未完成 AI Analysis 的 Article。

        狀態：

            NULL
            pending

        都視為待分析。
        """

        cursor = self.connection.cursor(
            dictionary=True
        )

        try:

            cursor.execute(
                """
                SELECT *
                FROM articles
                WHERE
                    ai_status IS NULL
                    OR ai_status='pending'
                ORDER BY id ASC
                LIMIT %s
                """,
                (
                    int(limit),
                )
            )

            return cursor.fetchall()

        finally:

            cursor.close()

    # ==================================================
    # Update AI Status
    # ==================================================

    def update_ai_status(
        self,
        article_id,
        status
    ):
        """
        更新 Article AI Status。

        可能狀態：

            pending
            processing
            completed
            failed
        """

        cursor = self.connection.cursor()

        try:

            cursor.execute(
                """
                UPDATE articles
                SET ai_status=%s
                WHERE id=%s
                """,
                (
                    status,
                    article_id
                )
            )

            affected = cursor.rowcount

            if affected <= 0:

                self.connection.rollback()

                logger.warning(
                    "AI status update failed: "
                    f"id={article_id}"
                )

                return False

            self.connection.commit()

            logger.info(
                "AI status updated: "
                f"id={article_id}, "
                f"status={status}"
            )

            return True

        except Exception as e:

            self.connection.rollback()

            logger.exception(
                "AI status update failed: "
                f"{e}"
            )

            return False

        finally:

            cursor.close()

    # ==================================================
    # Get AI Status
    # ==================================================

    def get_ai_status(
        self,
        article_id
    ):
        """
        取得 Article AI Status。
        """

        cursor = self.connection.cursor(
            dictionary=True
        )

        try:

            cursor.execute(
                """
                SELECT
                    id,
                    ai_status
                FROM articles
                WHERE id=%s
                """,
                (
                    article_id,
                )
            )

            return cursor.fetchone()

        finally:

            cursor.close()

    # ==================================================
    # Update AI Analysis
    # ==================================================

    def update_ai_analysis(
        self,
        article
    ):
        """
        儲存 AI Analysis Result。

        AI Worker 完成：

            Article
              ↓
            AIAnalysis
              ↓
            update_ai_analysis()
              ↓
            articles
        """

        if article is None:

            logger.error(
                "AI Analysis update failed: "
                "article is None"
            )

            return False

        if article.id is None:

            logger.error(
                "AI Analysis update failed: "
                "article.id is None"
            )

            return False

        analysis = getattr(
            article,
            "ai_analysis",
            None
        )

        if analysis is None:

            logger.warning(
                "AI Analysis update skipped: "
                "no AI Analysis"
            )

            return False

        cursor = self.connection.cursor()

        sql = """
            UPDATE articles
            SET
                ai_summary=%s,
                ai_category=%s,
                ai_keywords=%s,
                ai_importance=%s,
                ai_model=%s,
                ai_version=%s,
                ai_analyze_time=%s,
                ai_confidence=%s,
                ai_status=%s
            WHERE id=%s
        """

        try:

            keywords = getattr(
                analysis,
                "keywords",
                None
            )

            if keywords is not None:

                ai_keywords = json.dumps(
                    keywords,
                    ensure_ascii=False
                )

            else:

                ai_keywords = None

            importance = getattr(
                analysis,
                "importance",
                None
            )

            if importance is not None:

                importance = int(
                    importance
                )

            confidence = getattr(
                analysis,
                "confidence",
                None
            )

            if confidence is not None:

                confidence = float(
                    confidence
                )

            values = (
                getattr(
                    analysis,
                    "summary",
                    None
                ),

                getattr(
                    analysis,
                    "category",
                    None
                ),

                ai_keywords,

                importance,

                getattr(
                    analysis,
                    "ai_model",
                    None
                ),

                getattr(
                    analysis,
                    "ai_version",
                    None
                ),

                getattr(
                    analysis,
                    "analyze_time",
                    None
                ),

                confidence,

                "completed",

                article.id
            )

            cursor.execute(
                sql,
                values
            )

            affected = cursor.rowcount

            if affected <= 0:

                self.connection.rollback()

                logger.warning(
                    "AI Analysis update failed: "
                    f"article not found id={article.id}"
                )

                return False

            self.connection.commit()

            logger.info(
                "AI Analysis saved: "
                f"article={article.id}"
            )

            return True

        except Exception as e:

            self.connection.rollback()

            logger.exception(
                "AI Analysis update failed: "
                f"{e}"
            )

            return False

        finally:

            cursor.close()

    # ==================================================
    # Find Failed AI
    # ==================================================

    def find_failed_ai(
        self,
        limit=20
    ):
        """
        取得 AI Analysis Failed Articles。
        """

        cursor = self.connection.cursor(
            dictionary=True
        )

        try:

            cursor.execute(
                """
                SELECT *
                FROM articles
                WHERE ai_status='failed'
                ORDER BY id ASC
                LIMIT %s
                """,
                (
                    int(limit),
                )
            )

            return cursor.fetchall()

        finally:

            cursor.close()

    # ==================================================
    # Delete
    # ==================================================

    def delete(
        self,
        article_id
    ):
        """
        刪除 Article。

        注意：

            ArticleService 不直接操作 SQL。

            Repository 在刪除前，
            先確認 Article 是否存在。

        若 Database Schema 已透過
        Foreign Key 保護相關資料，
        DELETE 失敗時直接 rollback。

        Repository 不主動刪除：

            Archive
            Raw Document
            AI Task
            Knowledge Archive
        """

        if article_id is None:

            return False

        cursor = self.connection.cursor()

        try:

            cursor.execute(
                """
                SELECT id
                FROM articles
                WHERE id=%s
                """,
                (
                    article_id,
                )
            )

            row = cursor.fetchone()

            if row is None:

                logger.warning(
                    "Article delete failed: "
                    f"id={article_id} not found"
                )

                return False

            cursor.execute(
                """
                DELETE FROM articles
                WHERE id=%s
                """,
                (
                    article_id,
                )
            )

            affected = cursor.rowcount

            if affected <= 0:

                self.connection.rollback()

                logger.warning(
                    "Article delete failed: "
                    f"id={article_id}"
                )

                return False

            self.connection.commit()

            logger.info(
                "Article deleted: "
                f"id={article_id}"
            )

            return True

        except Exception as e:

            self.connection.rollback()

            logger.exception(
                "Article delete failed: "
                f"id={article_id}, "
                f"error={e}"
            )

            return False

        finally:

            cursor.close()

    # ==================================================
    # Count
    # ==================================================

    def count(
        self
    ):
        """
        取得 Article 總數。
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

        finally:

            cursor.close()

    # ==================================================
    # Datetime Normalization
    # ==================================================

    @staticmethod
    def _normalize_datetime(
        value
    ):
        """
        將不同格式的日期轉成 datetime。

        支援：

            datetime
            None
            YYYY-MM-DD HH:MM:SS
            YYYY-MM-DD
            RFC 822
            RSS datetime
        """

        if value is None:

            return None

        if isinstance(
            value,
            datetime
        ):

            return value

        if not isinstance(
            value,
            str
        ):

            return None

        value = value.strip()

        if not value:

            return None

        formats = [

            "%Y-%m-%d %H:%M:%S",

            "%Y-%m-%d",

            "%a, %d %b %Y %H:%M:%S %Z",

            "%a, %d %b %Y %H:%M:%S GMT",

            "%a, %d %b %Y %H:%M:%S +0000",

            "%a, %d %b %Y %H:%M:%S %z"
        ]

        for fmt in formats:

            try:

                return datetime.strptime(
                    value,
                    fmt
                )

            except ValueError:

                continue

        logger.warning(
            "Unable to normalize datetime: "
            f"{value}"
        )

        return None

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
                    "ArticleRepository connection closed."
                )

        except Exception as e:

            logger.exception(
                "ArticleRepository close failed: "
                f"{e}"
            )


__all__ = [
    "ArticleRepository",
]
