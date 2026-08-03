"""
article_repository.py

AutoSearch V3

P4.4.3

Article Repository

功能:

    Database CRUD

支援:

    V2.5 Article Database

    V3 AI Analysis

    V3 AI Metadata


Database:

    MySQL

"""


from database.connection import get_connection

from datetime import datetime

import json

from utils.logger import logger





class ArticleRepository:



    def __init__(self):


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

            ai_confidence

        )


        VALUES

        (

            %s,%s,%s,%s,%s,

            %s,%s,%s,%s,

            %s,%s,%s,%s,

            %s,%s,%s,%s

        )

        """





        # =====================================
        # Published Convert
        # =====================================


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








        # =====================================
        # Default AI Data
        # =====================================


        ai_summary = ""

        ai_category = ""

        ai_keywords = "[]"

        ai_importance = 0


        ai_model = ""

        ai_version = ""

        ai_analyze_time = None

        ai_confidence = 0.0







        # =====================================
        # AI Analysis
        # =====================================


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




            # ================================
            # FIX IMPORTANT
            # ================================


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





        # Debug

        print()

        print("==========================")

        print("Repository AI Data")

        print("==========================")

        print(

            "Importance:",

            ai_importance

        )

        print(

            "Model:",

            ai_model

        )

        print(

            "Version:",

            ai_version

        )

        print(

            "Confidence:",

            ai_confidence

        )

        print("==========================")

        print()





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


            ai_confidence


        )






        cursor.execute(

            sql,

            values

        )



        self.connection.commit()



        cursor.close()





        logger.info(

            f"Database saved: {article.title}"

        )



        return True











    # ==================================================
    # Query
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
    # AI Retrieval
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
    # Utility
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











    def count(self):


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











    def close(self):


        if self.connection:


            self.connection.close()