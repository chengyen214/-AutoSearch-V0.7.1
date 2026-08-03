"""
article_repository.py

Article Repository

AutoSearch V2.5

功能：

    管理 Article 與 MySQL articles table 的 CRUD 操作

"""

from database.connection import get_connection

from datetime import datetime

from utils.logger import logger


class ArticleRepository:


    def __init__(self):

        self.connection = get_connection()

        if self.connection is None:

            raise Exception(
                "Database connection failed."
            )



    # ==========================
    # Create
    # ==========================

    def save(self, article):


        # 檢查是否重複

        if self.exists(article.document_id):

            print(
                "Article already exists:",
                article.title
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
            status
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
            %s
        )

        """

        # ==========================
        # datetime format conversion
        # ==========================

        if article.published:

            try:

                article.published = datetime.strptime(
                    article.published,
                    "%a, %d %b %Y %H:%M:%S %Z"
                )

            except Exception:

                article.published = None

        values = (

            article.document_id,

            article.keyword,

            article.title,

            article.url,

            article.source,

            article.published,

            article.content,

            article.crawl_time,

            article.status

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





    # ==========================
    # Read
    # ==========================


    def find_all(self):


        cursor = self.connection.cursor(
            dictionary=True
        )



        sql = """

        SELECT *

        FROM articles

        ORDER BY id DESC

        """



        cursor.execute(sql)



        rows = cursor.fetchall()



        cursor.close()



        return rows





    def find_by_id(self, article_id):


        cursor = self.connection.cursor(
            dictionary=True
        )



        sql = """

        SELECT *

        FROM articles

        WHERE id = %s

        """



        cursor.execute(

            sql,

            (article_id,)

        )



        row = cursor.fetchone()



        cursor.close()



        return row





    def find_by_document_id(self, document_id):


        cursor = self.connection.cursor(
            dictionary=True
        )



        sql = """

        SELECT *

        FROM articles

        WHERE document_id = %s

        """



        cursor.execute(

            sql,

            (document_id,)

        )



        row = cursor.fetchone()



        cursor.close()



        return row





    def find_by_keyword(self, keyword):


        cursor = self.connection.cursor(
            dictionary=True
        )



        sql = """

        SELECT *

        FROM articles

        WHERE keyword = %s

        ORDER BY id DESC

        """



        cursor.execute(

            sql,

            (keyword,)

        )



        rows = cursor.fetchall()



        cursor.close()



        return rows





    def find_by_source(self, source):


        cursor = self.connection.cursor(
            dictionary=True
        )



        sql = """

        SELECT *

        FROM articles

        WHERE source = %s

        ORDER BY id DESC

        """



        cursor.execute(

            sql,

            (source,)

        )



        rows = cursor.fetchall()



        cursor.close()



        return rows





    # ==========================
    # Update
    # ==========================


    def update_status(
        self,
        article_id,
        status
    ):


        cursor = self.connection.cursor()



        sql = """

        UPDATE articles

        SET status = %s

        WHERE id = %s

        """



        cursor.execute(

            sql,

            (
                status,
                article_id
            )

        )



        self.connection.commit()



        cursor.close()





    # ==========================
    # Delete
    # ==========================


    def delete(self, article_id):


        cursor = self.connection.cursor()



        sql = """

        DELETE FROM articles

        WHERE id = %s

        """



        cursor.execute(

            sql,

            (article_id,)

        )



        self.connection.commit()



        cursor.close()





    # ==========================
    # Utility
    # ==========================


    def count(self):


        cursor = self.connection.cursor()



        sql = """

        SELECT COUNT(*)

        FROM articles

        """



        cursor.execute(sql)



        total = cursor.fetchone()[0]



        cursor.close()



        return total





    def exists(self, document_id):


        cursor = self.connection.cursor()



        sql = """

        SELECT COUNT(*)

        FROM articles

        WHERE document_id = %s

        """



        cursor.execute(

            sql,

            (document_id,)

        )



        result = cursor.fetchone()[0]



        cursor.close()



        return result > 0





    def close(self):


        if self.connection:


            self.connection.close()