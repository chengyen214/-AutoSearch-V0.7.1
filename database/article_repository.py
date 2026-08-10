"""
database/article_repository.py

AutoSearch V4

Article Repository

功能:

Article Database CRUD

支援:

V2.5 Article Database
V3 AI Analysis
V4 Knowledge Archive
V4 Async AI Pipeline

Database:

MySQL
"""

from database.connection import get_connection

from datetime import datetime

import json

from utils.logger import logger

from models.article import Article

from models.ai_analysis import AIAnalysis



class ArticleRepository:
    """
    Article Repository

    負責:

    Database CRUD

    AI Analysis Persistence

    Async AI Pipeline Support

    """



    def __init__(self):

        self.connection = get_connection()

        if self.connection is None:

            raise Exception(
                "Database connection failed."
            )



    # ==================================================
    # Create Article
    # ==================================================

    def save(
        self,
        article
    ):


        if self.exists(
            article.document_id
        ):


            logger.info(
                f"Article exists: {article.title}"
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

            %s,%s,%s,%s,%s,

            %s,%s,%s,%s,

            %s,%s,%s,%s,

            %s,%s,%s,%s,

            %s

        )

        """



        published = getattr(
            article,
            "published",
            None
        )



        if published:

            try:

                published = datetime.strptime(
                    published,
                    "%a, %d %b %Y %H:%M:%S %Z"
                )

            except Exception:

                try:

                    published = datetime.strptime(
                        published,
                        "%Y-%m-%d %H:%M:%S"
                    )

                except Exception:

                    published = None



        ai_summary = ""

        ai_category = ""

        ai_keywords = "[]"

        ai_importance = 0

        ai_model = ""

        ai_version = ""

        ai_analyze_time = None

        ai_confidence = 0.0

        ai_status = "pending"



        if getattr(
            article,
            "ai_analysis",
            None
        ):


            analysis = article.ai_analysis


            ai_summary = getattr(
                analysis,
                "summary",
                ""
            )


            ai_category = getattr(
                analysis,
                "category",
                ""
            )


            ai_keywords = json.dumps(
                getattr(
                    analysis,
                    "keywords",
                    []
                ),
                ensure_ascii=False
            )


            ai_importance = int(
                getattr(
                    analysis,
                    "importance",
                    0
                )
            )


            ai_model = getattr(
                analysis,
                "ai_model",
                "RuleBased-V3"
            )


            ai_version = getattr(
                analysis,
                "ai_version",
                "3.0"
            )


            ai_analyze_time = getattr(
                analysis,
                "analyze_time",
                datetime.now()
            )


            ai_confidence = float(
                getattr(
                    analysis,
                    "confidence",
                    0.9
                )
            )


            ai_status = "completed"



        values = (

            article.document_id,

            article.keyword,

            article.title,

            article.url,

            article.source,

            published,

            article.content,

            article.crawl_time,

            article.status,


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



        cursor.close()



        logger.info(
            f"Database saved: {article.title}"
        )


        return True

    # ==================================================
    # Insert Article
    #
    # P2.2.6 Compatibility Layer
    #
    # ArticleService
    #       |
    #       v
    # ArticleRepository.insert()
    #
    # Legacy:
    # ArticleRepository.save()
    #
    # ==================================================

    def insert(
        self,
        article
    ):
        """
        Article insert wrapper

        新 Pipeline 使用:
            repo.insert(article)

        舊 Pipeline 使用:
            repo.save(article)

        統一導向 save()
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


        cursor = self.connection.cursor(
            dictionary=True
        )


        sql = """

        SELECT *

        FROM articles

        ORDER BY id DESC

        """



        if limit:


            sql += """

            LIMIT %s

            """


            cursor.execute(
                sql,
                (
                    limit,
                )
            )


        else:

            cursor.execute(
                sql
            )



        rows = cursor.fetchall()


        cursor.close()


        return rows




    # ==================================================
    # Query By ID
    # ==================================================

    def find_by_id(
        self,
        article_id
    ):


        cursor = self.connection.cursor(
            dictionary=True
        )


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


        row = cursor.fetchone()


        cursor.close()


        return row
    # ==================================================
    # Convert Database -> Article Model
    #
    # AI Worker 使用
    #
    # MySQL
    #    |
    #    v
    # Article
    #    |
    #    v
    # AIAnalysis
    #
    # ==================================================

    def find_model_by_id(
        self,
        article_id
    ):


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




        # ==============================
        # Database ID
        # ==============================

        article.id = row.get(
            "id"
        )


        article.document_id = row.get(
            "document_id",
            ""
        )




        # ==============================
        # AI Status
        # ==============================

        article.ai_status = row.get(
            "ai_status",
            "pending"
        )





        # ==============================
        # Restore AI Analysis
        #
        # articles
        #
        # ai_summary
        # ai_category
        # ai_keywords
        #
        # ->
        #
        # AIAnalysis Model
        #
        # ==============================


        ai_summary = row.get(
            "ai_summary",
            ""
        )



        if ai_summary:


            try:


                keywords = row.get(
                    "ai_keywords",
                    "[]"
                )


                if isinstance(
                    keywords,
                    str
                ):


                    keywords = json.loads(
                        keywords
                    )



                analysis = AIAnalysis(


                    article_id=article.id,


                    summary=ai_summary,


                    category=row.get(
                        "ai_category",
                        ""
                    ),


                    keywords=keywords,


                    importance=row.get(
                        "ai_importance",
                        0
                    ),


                    ai_model=row.get(
                        "ai_model",
                        ""
                    ),


                    ai_version=row.get(
                        "ai_version",
                        ""
                    ),


                    analyze_time=row.get(
                        "ai_analyze_time",
                        None
                    ),


                    confidence=row.get(
                        "ai_confidence",
                        0.0
                    )

                )


                article.ai_analysis = analysis



            except Exception as e:


                logger.exception(

                    f"Restore AI Analysis failed: {e}"

                )


                article.ai_analysis = None



        else:


            article.ai_analysis = None




        return article







    # ==================================================
    # Find Pending AI
    #
    # Async AI Worker
    #
    # pending
    # NULL
    #
    # ==================================================

    def find_pending_ai(
        self,
        limit=20
    ):


        cursor = self.connection.cursor(
            dictionary=True
        )



        cursor.execute(

            """

            SELECT *

            FROM articles


            WHERE

                ai_status IS NULL

            OR

                ai_status='pending'


            ORDER BY id ASC


            LIMIT %s


            """,

            (
                limit,
            )

        )



        rows = cursor.fetchall()


        cursor.close()


        return rows







    # ==================================================
    # Update AI Status
    #
    # pending
    # processing
    # completed
    # failed
    #
    # ==================================================

    def update_ai_status(
        self,
        article_id,
        status
    ):


        cursor = self.connection.cursor()



        cursor.execute(

            """

            UPDATE articles

            SET

                ai_status=%s


            WHERE id=%s


            """,

            (

                status,

                article_id

            )

        )



        self.connection.commit()



        affected = cursor.rowcount



        cursor.close()



        return affected > 0








    # ==================================================
    # Get AI Status
    # ==================================================

    def get_ai_status(
        self,
        article_id
    ):


        cursor = self.connection.cursor(
            dictionary=True
        )


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


        result = cursor.fetchone()


        cursor.close()


        return result







    # ==================================================
    # Update AI Analysis Result
    #
    # AIWorker
    #
    # AIAnalysis
    #
    # ->
    #
    # articles
    #
    # ==================================================

    def update_ai_analysis(
        self,
        article
    ):


        if article.id is None:


            logger.error(
                "AI Update failed: Article ID None"
            )


            return False





        if article.ai_analysis is None:


            logger.warning(
                "AI Update skipped: No Analysis"
            )


            return False





        analysis = article.ai_analysis



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




        values = (



            getattr(
                analysis,
                "summary",
                ""
            ),



            getattr(
                analysis,
                "category",
                ""
            ),



            json.dumps(

                getattr(
                    analysis,
                    "keywords",
                    []
                ),

                ensure_ascii=False

            ),



            int(

                getattr(
                    analysis,
                    "importance",
                    0
                )

            ),



            getattr(
                analysis,
                "ai_model",
                "RuleBased-V3"
            ),



            getattr(
                analysis,
                "ai_version",
                "3.0"
            ),



            getattr(
                analysis,
                "analyze_time",
                datetime.now()
            ),



            float(

                getattr(
                    analysis,
                    "confidence",
                    0.9
                )

            ),



            "completed",



            article.id

        )




        cursor.execute(

            sql,

            values

        )



        self.connection.commit()



        affected = cursor.rowcount



        cursor.close()



        return affected > 0







    # ==================================================
    # Find Failed AI
    #
    # Retry Worker
    #
    # ==================================================

    def find_failed_ai(
        self,
        limit=20
    ):


        cursor = self.connection.cursor(
            dictionary=True
        )



        cursor.execute(

            """

            SELECT *

            FROM articles


            WHERE ai_status='failed'


            ORDER BY id ASC


            LIMIT %s


            """,

            (
                limit,
            )

        )



        rows = cursor.fetchall()



        cursor.close()



        return rows
    # ==================================================
    # AI Retrieval
    #
    # Importance Ranking
    #
    # ==================================================

    def find_by_importance(
        self,
        level
    ):


        cursor = self.connection.cursor(
            dictionary=True
        )


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


        rows = cursor.fetchall()


        cursor.close()


        return rows







    # ==================================================
    # AI Category Search
    #
    # ==================================================

    def find_by_category(
        self,
        category
    ):


        cursor = self.connection.cursor(
            dictionary=True
        )


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


        rows = cursor.fetchall()


        cursor.close()


        return rows







    # ==================================================
    # AI Keyword Search
    #
    # JSON keyword field
    #
    # ==================================================

    def find_by_ai_keyword(
        self,
        keyword
    ):


        cursor = self.connection.cursor(
            dictionary=True
        )


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


        rows = cursor.fetchall()


        cursor.close()


        return rows







    # ==================================================
    # Normal Keyword Search
    #
    # Article Search API
    #
    # ==================================================

    def find_by_keyword(
        self,
        keyword
    ):


        cursor = self.connection.cursor(
            dictionary=True
        )


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


        rows = cursor.fetchall()


        cursor.close()


        return rows







    # ==================================================
    # Duplicate Check
    #
    # document_id hash
    #
    # ==================================================

    def exists(
        self,
        document_id
    ):


        cursor = self.connection.cursor()



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



        result = cursor.fetchone()[0]


        cursor.close()



        return result > 0







    # ==================================================
    # Count Articles
    #
    # ==================================================

    def count(
        self
    ):


        cursor = self.connection.cursor()



        cursor.execute(

            """

            SELECT COUNT(*)

            FROM articles


            """

        )


        result = cursor.fetchone()[0]


        cursor.close()



        return result







    # ==================================================
    # Close Database Connection
    #
    # ==================================================

    def close(
        self
    ):


        if self.connection:


            self.connection.close()