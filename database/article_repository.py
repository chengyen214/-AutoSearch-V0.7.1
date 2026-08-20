"""
database/article_repository.py

AutoSearch V4

Article Repository

功能:

- Article CRUD
- Article Query
- AI Analysis Persistence
- Async AI Pipeline Support
- Article Management
- Current Article Snapshot

P2.4.1:

- Article Storage 與 AI Analysis 解耦
- Article 可以在沒有 AI Analysis 時先存入 Database
- 未分析 AI fields 使用 NULL
- ai_status 管理 Article AI Analysis 狀態

Database:

MySQL
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
    Article Repository

    負責:

        Article CRUD
        Article Query
        AI Analysis Persistence
        Async AI Pipeline Support
        Article Management

    不負責:

        AI Analysis
        Archive Version Creation
        Knowledge Processing
        Worker Scheduling
    """

    # ==================================================
    # Initialize
    # ==================================================

    def __init__(
        self
    ):

        self.connection = (
            get_connection()
        )

        if self.connection is None:

            raise Exception(
                "Database connection failed."
            )

    # ==================================================
    # Create Article
    #
    # P2.4.1
    #
    # Article Storage 與 AI Analysis 解耦
    # ==================================================

    def save(
        self,
        article
    ):
        """
        儲存 Article。

        P2.4.1 核心行為:

            Article 不存在
                ↓
            直接 INSERT
                ↓
            不要求 AI Analysis

        尚未 AI Analysis:

            ai_summary      = NULL
            ai_category     = NULL
            ai_keywords     = NULL
            ai_importance   = NULL
            ai_model        = NULL
            ai_version      = NULL
            ai_analyze_time = NULL
            ai_confidence   = NULL

            ai_status       = pending

        已有 AI Analysis:

            AI fields 正常保存
            ai_status = completed

        Duplicate:

            document_id 已存在
            → 不重複 INSERT

        回傳:

            True
                成功

            False
                失敗 / Duplicate
        """

        # ==================================================
        # Validate Article
        # ==================================================

        if article is None:

            logger.error(
                "Article save failed: "
                "article is None"
            )

            return False

        # ==================================================
        # Document ID
        # ==================================================

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

        # ==================================================
        # Duplicate Protection
        #
        # document_id 是 Article 唯一識別依據
        # ==================================================

        if self.exists(
            document_id
        ):

            logger.info(
                "Article exists: "
                f"{getattr(article, 'title', '')}, "
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

            # ==================================================
            # Published
            # ==================================================

            published = self._normalize_datetime(
                getattr(
                    article,
                    "published",
                    None
                )
            )

            # ==================================================
            # P2.4.1
            #
            # Default AI Fields
            #
            # 尚未分析:
            #
            #     NULL
            #
            # 不再使用:
            #
            #     ""
            #     "[]"
            #     0
            #     0.0
            #
            # 因為這些值可能是合法 AI 結果。
            # ==================================================

            ai_summary = None

            ai_category = None

            ai_keywords = None

            ai_importance = None

            ai_model = None

            ai_version = None

            ai_analyze_time = None

            ai_confidence = None

            ai_status = "pending"

            # ==================================================
            # Existing AI Analysis
            #
            # 如果 Article 在進入 Repository 前
            # 已經存在 AI Analysis，
            # 則直接保存 AI 結果。
            # ==================================================

            analysis = getattr(
                article,
                "ai_analysis",
                None
            )

            if analysis is not None:

                # ==============================================
                # AI Summary
                # ==============================================

                ai_summary = getattr(
                    analysis,
                    "summary",
                    None
                )

                # ==============================================
                # AI Category
                # ==============================================

                ai_category = getattr(
                    analysis,
                    "category",
                    None
                )

                # ==============================================
                # AI Keywords
                # ==============================================

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

                # ==============================================
                # AI Importance
                # ==============================================

                ai_importance = getattr(
                    analysis,
                    "importance",
                    None
                )

                if ai_importance is not None:

                    ai_importance = int(
                        ai_importance
                    )

                # ==============================================
                # AI Model
                # ==============================================

                ai_model = getattr(
                    analysis,
                    "ai_model",
                    None
                )

                # ==============================================
                # AI Version
                # ==============================================

                ai_version = getattr(
                    analysis,
                    "ai_version",
                    None
                )

                # ==============================================
                # AI Analyze Time
                # ==============================================

                ai_analyze_time = getattr(
                    analysis,
                    "analyze_time",
                    None
                )

                # ==============================================
                # AI Confidence
                # ==============================================

                ai_confidence = getattr(
                    analysis,
                    "confidence",
                    None
                )

                if ai_confidence is not None:

                    ai_confidence = float(
                        ai_confidence
                    )

                # ==============================================
                # AI Status
                # ==============================================

                ai_status = "completed"

            # ==================================================
            # Values
            # ==================================================

            values = (

                # ----------------------------------------------
                # Article
                # ----------------------------------------------

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

                getattr(
                    article,
                    "crawl_time",
                    None
                ),

                getattr(
                    article,
                    "status",
                    "Success"
                ),

                # ----------------------------------------------
                # AI
                # ----------------------------------------------

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

            # ==================================================
            # INSERT
            # ==================================================

            cursor.execute(
                sql,
                values
            )

            self.connection.commit()

            # ==================================================
            # Database ID
            # ==================================================

            article.id = (
                cursor.lastrowid
            )

            logger.info(
                "Database saved: "
                f"title={getattr(article, 'title', '')}, "
                f"id={article.id}, "
                f"ai_status={ai_status}"
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
    # Insert Article
    #
    # P2.2.6 Compatibility Layer
    # ==================================================

    def insert(
        self,
        article
    ):
        """
        新 Pipeline:

            repo.insert(article)

        舊 Pipeline:

            repo.save(article)

        統一導向 save()。
        """

        result = self.save(
            article
        )

        if result is False:

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
        取得全部 Article。
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
        依 ID 查詢 Article。
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
    # Find Article Model By ID
    #
    # AI Worker
    # ==================================================

    def find_model_by_id(
        self,
        article_id
    ):
        """
        Database Row
            ↓
        Article Model

        AI Worker 使用。
        """

        row = self.find_by_id(
            article_id
        )

        if row is None:

            logger.warning(
                f"Article not found id={article_id}"
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
                "published",
                None
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
                "crawl_time",
                None
            ),

            status=row.get(
                "status",
                "Success"
            )
        )

        # ==================================================
        # Database Identity
        # ==================================================

        article.id = row.get(
            "id"
        )

        article.document_id = row.get(
            "document_id",
            ""
        )

        # ==================================================
        # AI Status
        # ==================================================

        article.ai_status = row.get(
            "ai_status",
            "pending"
        )

        # ==================================================
        # Restore AI Analysis
        # ==================================================

        ai_summary = row.get(
            "ai_summary",
            None
        )

        if ai_summary is not None:

            try:

                keywords = row.get(
                    "ai_keywords",
                    None
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
                        "ai_category",
                        None
                    ),

                    keywords=keywords,

                    importance=row.get(
                        "ai_importance",
                        None
                    ),

                    ai_model=row.get(
                        "ai_model",
                        None
                    ),

                    ai_version=row.get(
                        "ai_version",
                        None
                    ),

                    analyze_time=row.get(
                        "ai_analyze_time",
                        None
                    ),

                    confidence=row.get(
                        "ai_confidence",
                        None
                    )
                )

                article.ai_analysis = (
                    analysis
                )

            except Exception as e:

                logger.exception(
                    "Restore AI Analysis failed: "
                    f"{e}"
                )

                article.ai_analysis = None

        else:

            article.ai_analysis = None

        return article

    # ==================================================
    # Query By Source
    # ==================================================

    def find_by_source(
        self,
        source
    ):
        """
        依 Source 查詢。
        """

        cursor = self.connection.cursor(
            dictionary=True
        )

        try:

            cursor.execute(

                """

                SELECT *

                FROM articles

                WHERE source LIKE %s

                ORDER BY id DESC

                """,

                (
                    "%" + source + "%",
                )

            )

            return cursor.fetchall()

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
        依一般 Keyword 查詢。
        """

        cursor = self.connection.cursor(
            dictionary=True
        )

        try:

            cursor.execute(

                """

                SELECT *

                FROM articles

                WHERE keyword LIKE %s

                ORDER BY id DESC

                """,

                (
                    "%" + keyword + "%",
                )

            )

            return cursor.fetchall()

        finally:

            cursor.close()

    # ==================================================
    # Find Article By URL
    #
    # V4 Archive History
    # ==================================================

    def find_by_url(
        self,
        url
    ):
        """
        URL 是 Article History
        Detection 的主要識別依據。
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
    # Find Article By Document ID
    # ==================================================

    def find_by_document_id(
        self,
        document_id
    ):
        """
        依目前 Document Hash 查詢 Article。
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
    # Duplicate Check
    # ==================================================

    def exists(
        self,
        document_id
    ):
        """
        檢查 document_id 是否存在。
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

            return (
                result is not None
                and result[0] > 0
            )

        finally:

            cursor.close()

    # ==================================================
    # Update Current Content Snapshot
    #
    # V4 Archive History
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
        更新 Article 目前版本 Snapshot。

        Archive:

            archive_versions
            ↓
            保存歷史

        Article:

            articles.content
            articles.document_id
            ↓
            保存目前版本

        不修改:

            AI fields
            Archive fields
        """

        if self.find_by_id(
            article_id
        ) is None:

            logger.warning(
                "Snapshot update failed: "
                f"article not found id={article_id}"
            )

            return False

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

        SET

            {", ".join(fields)}

        WHERE id=%s

        """

        cursor = self.connection.cursor()

        try:

            cursor.execute(
                sql,
                tuple(values)
            )

            self.connection.commit()

            affected = cursor.rowcount

            if affected > 0:

                logger.info(
                    "Article snapshot updated: "
                    f"id={article_id}, "
                    f"document_id={document_id}"
                )

            return affected > 0

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
    # Find Pending AI
    #
    # Async AI Worker Compatibility
    # ==================================================

    def find_pending_ai(
        self,
        limit=20
    ):
        """
        取得尚未完成 AI Analysis 的 Article。

        P2.4.1:

            NULL / pending
            都視為尚未完成 AI。
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

        使用 UPDATE rowcount
        判斷 Article 是否存在。

        注意:

            不先呼叫 find_by_id()，
            避免產生額外 SQL。
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
                    "Update AI status failed: "
                    f"article not found id={article_id}"
                )

                return False

            self.connection.commit()

            logger.info(
                "AI status updated: "
                f"article={article_id}, "
                f"status={status}"
            )

            return True

        except Exception as e:

            self.connection.rollback()

            logger.exception(
                "Update AI status failed: "
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
        取得 AI Status。
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

        AI Worker 完成分析後呼叫。

        P2.4.1:

            AI Analysis 完成後，
            將 NULL AI fields 更新成實際結果。
        """

        if article is None:

            logger.error(
                "AI Update failed: "
                "article is None"
            )

            return False

        if article.id is None:

            logger.error(
                "AI Update failed: "
                "Article ID None"
            )

            return False

        analysis = getattr(
            article,
            "ai_analysis",
            None
        )

        if analysis is None:

            logger.warning(
                "AI Update skipped: "
                "No Analysis"
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

            # ==================================================
            # Keywords
            # ==================================================

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

            # ==================================================
            # Importance
            # ==================================================

            importance = getattr(
                analysis,
                "importance",
                None
            )

            if importance is not None:

                importance = int(
                    importance
                )

            # ==================================================
            # Confidence
            # ==================================================

            confidence = getattr(
                analysis,
                "confidence",
                None
            )

            if confidence is not None:

                confidence = float(
                    confidence
                )

            # ==================================================
            # Values
            # ==================================================

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

            self.connection.commit()

            affected = cursor.rowcount

            logger.info(
                "AI Analysis updated: "
                f"article={article.id}"
            )

            return affected > 0

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
    # AI Importance
    # ==================================================

    def find_by_importance(
        self,
        level
    ):
        """
        AI Importance >= level。
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

                ORDER BY ai_importance DESC

                """,

                (
                    level,
                )

            )

            return cursor.fetchall()

        finally:

            cursor.close()

    # ==================================================
    # AI Category
    # ==================================================

    def find_by_category(
        self,
        category
    ):
        """
        AI Category 查詢。
        """

        cursor = self.connection.cursor(
            dictionary=True
        )

        try:

            cursor.execute(

                """

                SELECT *

                FROM articles

                WHERE LOWER(ai_category)=LOWER(%s)

                ORDER BY ai_importance DESC

                """,

                (
                    category,
                )

            )

            return cursor.fetchall()

        finally:

            cursor.close()

    # ==================================================
    # AI Keyword
    # ==================================================

    def find_by_ai_keyword(
        self,
        keyword
    ):
        """
        AI Keyword 查詢。

        ai_keywords 目前以 JSON
        儲存在資料庫。
        """

        cursor = self.connection.cursor(
            dictionary=True
        )

        try:

            cursor.execute(

                """

                SELECT *

                FROM articles

                WHERE ai_keywords LIKE %s

                ORDER BY ai_importance DESC

                """,

                (
                    "%" + keyword + "%",
                )

            )

            return cursor.fetchall()

        finally:

            cursor.close()

    # ==================================================
    # AI Top Articles
    #
    # P3.5.6 AI Analysis API
    # ==================================================

    def get_top_ai_articles(
        self,
        limit=10
    ):
        """
        取得 AI Importance 最高的 Articles。

        只取得已完成 AI Analysis 的文章。

        排序:

            1. ai_importance DESC
            2. ai_confidence DESC
            3. ai_analyze_time DESC
        """

        cursor = self.connection.cursor(
            dictionary=True
        )

        try:

            cursor.execute(

                """

                SELECT *

                FROM articles

                WHERE ai_status='completed'

                ORDER BY

                    ai_importance DESC,

                    ai_confidence DESC,

                    ai_analyze_time DESC

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
    # Update Article Metadata
    #
    # P3.2 Article Management
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

        可更新:

            keyword
            title
            url
            source
            published
            status

        不更新:

            document_id
            content
            AI fields
            Archive fields
        """

        if self.find_by_id(
            article_id
        ) is None:

            logger.warning(
                "Article update failed: "
                f"article not found id={article_id}"
            )

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

            normalized_published = (
                self._normalize_datetime(
                    published
                )
            )

            if normalized_published is None:

                logger.warning(
                    "Invalid published datetime: "
                    f"{published}"
                )

                return False

            fields.append(
                "published=%s"
            )

            values.append(
                normalized_published
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
                f"no fields provided, "
                f"id={article_id}"
            )

            return False

        values.append(
            article_id
        )

        sql = f"""

        UPDATE articles

        SET

            {", ".join(fields)}

        WHERE id=%s

        """

        cursor = self.connection.cursor()

        try:

            cursor.execute(
                sql,
                tuple(values)
            )

            self.connection.commit()

            affected = cursor.rowcount

            logger.info(
                "Article updated: "
                f"id={article_id}, "
                f"fields={fields}"
            )

            return affected > 0

        except Exception as e:

            self.connection.rollback()

            logger.exception(
                f"Article update failed: {e}"
            )

            return False

        finally:

            cursor.close()

    # ==================================================
    # Delete Article
    #
    # P3.2 Article Management
    # ==================================================

    def delete(
        self,
        article_id
    ):
        """
        刪除 Article。

        Archive Protection:

            archive_versions
            raw_documents
            ai_tasks
            knowledge_archive

        任一存在時拒絕刪除。
        """

        article = self.find_by_id(
            article_id
        )

        if article is None:

            logger.warning(
                "Article delete failed: "
                f"article not found id={article_id}"
            )

            return False

        cursor = self.connection.cursor(
            dictionary=True
        )

        try:

            # ==================================================
            # Archive Versions
            # ==================================================

            cursor.execute(

                """

                SELECT COUNT(*) AS count

                FROM archive_versions

                WHERE article_id=%s

                """,

                (
                    article_id,
                )

            )

            archive_count = (
                cursor.fetchone()["count"]
            )

            # ==================================================
            # Raw Documents
            # ==================================================

            cursor.execute(

                """

                SELECT COUNT(*) AS count

                FROM raw_documents

                WHERE article_id=%s

                """,

                (
                    article_id,
                )

            )

            raw_count = (
                cursor.fetchone()["count"]
            )

            # ==================================================
            # AI Tasks
            # ==================================================

            cursor.execute(

                """

                SELECT COUNT(*) AS count

                FROM ai_tasks

                WHERE article_id=%s

                """,

                (
                    article_id,
                )

            )

            task_count = (
                cursor.fetchone()["count"]
            )

            # ==================================================
            # Knowledge Archive
            # ==================================================

            cursor.execute(

                """

                SELECT COUNT(*) AS count

                FROM knowledge_archive

                WHERE article_id=%s

                """,

                (
                    article_id,
                )

            )

            knowledge_count = (
                cursor.fetchone()["count"]
            )

            # ==================================================
            # Archive Protection
            # ==================================================

            if (
                archive_count > 0
                or raw_count > 0
                or task_count > 0
                or knowledge_count > 0
            ):

                logger.warning(

                    "Article delete blocked: "
                    f"id={article_id}, "
                    f"archive_versions={archive_count}, "
                    f"raw_documents={raw_count}, "
                    f"ai_tasks={task_count}, "
                    f"knowledge_archive="
                    f"{knowledge_count}"

                )

                return False

            # ==================================================
            # Delete Article
            # ==================================================

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

            self.connection.commit()

            if affected > 0:

                logger.info(
                    f"Article deleted: id={article_id}"
                )

                return True

            return False

        except Exception as e:

            self.connection.rollback()

            logger.exception(
                f"Article delete failed: {e}"
            )

            return False

        finally:

            cursor.close()

    # ==================================================
    # Count Articles
    # ==================================================

    def count(
        self
    ):
        """
        Article Count。
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
    # Normalize Datetime
    # ==================================================

    @staticmethod
    def _normalize_datetime(
        value
    ):
        """
        將不同格式的日期轉成 datetime。

        支援:

            datetime
            None
            YYYY-MM-DD HH:MM:SS
            YYYY-MM-DD
            RFC 822 / RSS
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

        注意:

            保留 self.connection 物件參照，
            不設為 None。

            這樣可以讓測試及其他生命週期
            管理程式確認 close() 是否被呼叫。
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
