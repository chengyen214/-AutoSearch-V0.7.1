"""
retrieval_repository.py

AutoSearch V3

AI Retrieval Repository

功能：

    依照 AI 分析結果查詢文章

支援：

    - AI分類查詢
    - 重要度查詢
    - AI Keyword搜尋
    - AI Summary搜尋

"""


from database.connection import get_connection

from utils.logger import logger




class RetrievalRepository:
    """
    AI文章檢索 Repository
    """



    def __init__(self):

        self.connection = get_connection()


        if self.connection is None:

            raise Exception(
                "Database connection failed."
            )





    # =================================
    # Category Search
    # =================================


    def find_by_category(
        self,
        category
    ):
        """
        依 AI Category 查詢

        Example:

            AI Chip
            Semiconductor

        """


        cursor = self.connection.cursor(
            dictionary=True
        )


        sql = """
        SELECT *

        FROM articles

        WHERE ai_category = %s

        ORDER BY ai_importance DESC
        """



        cursor.execute(

            sql,

            (
                category,
            )

        )


        rows = cursor.fetchall()


        cursor.close()


        logger.info(

            f"Retrieval category: {category}"

        )


        return rows





    # =================================
    # Importance Search
    # =================================


    def find_by_importance(
        self,
        level
    ):
        """
        查詢重要度以上文章

        Example:

            importance >= 8

        """



        cursor = self.connection.cursor(
            dictionary=True
        )



        sql = """
        SELECT *

        FROM articles

        WHERE ai_importance >= %s

        ORDER BY ai_importance DESC
        """



        cursor.execute(

            sql,

            (
                level,
            )

        )


        rows = cursor.fetchall()


        cursor.close()


        logger.info(

            f"Retrieval importance >= {level}"

        )


        return rows





    # =================================
    # AI Keyword Search
    # =================================


    def search_ai_keyword(
        self,
        keyword
    ):
        """
        搜尋 AI keywords

        MySQL JSON文字搜尋版本

        """



        cursor = self.connection.cursor(
            dictionary=True
        )



        sql = """
        SELECT *

        FROM articles

        WHERE ai_keywords LIKE %s

        ORDER BY ai_importance DESC
        """



        cursor.execute(

            sql,

            (

                f"%{keyword}%",

            )

        )


        rows = cursor.fetchall()


        cursor.close()


        logger.info(

            f"Retrieval keyword: {keyword}"

        )


        return rows






    # =================================
    # AI Summary Search
    # =================================


    def search_summary(
        self,
        keyword
    ):
        """
        搜尋 AI摘要
        """



        cursor = self.connection.cursor(
            dictionary=True
        )



        sql = """
        SELECT *

        FROM articles

        WHERE ai_summary LIKE %s

        ORDER BY ai_importance DESC
        """



        cursor.execute(

            sql,

            (

                f"%{keyword}%",

            )

        )


        rows = cursor.fetchall()


        cursor.close()


        return rows





    # =================================
    # Close
    # =================================


    def close(self):

        if self.connection:

            self.connection.close()