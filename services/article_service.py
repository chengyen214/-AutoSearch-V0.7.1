"""
services/article_service.py

AutoSearch V3

P4.5.1

Article Service Layer


用途:

    API 與 Database 中間服務層


負責:

    - Article 查詢邏輯
    - AI Retrieval
    - 資料整理


支援:

    V2.5 Database

    V3 AI Analysis


Flow:


FastAPI

    |

Article Service

    |

Article Repository

    |

MySQL



"""





from database.article_repository import ArticleRepository

from utils.logger import logger







class ArticleService:
    """
    Article Service


    不直接操作 SQL

    所有資料透過 Repository

    """





    def __init__(self):


        self.repo = ArticleRepository()







    # ==================================================
    # 查詢全部文章
    # ==================================================


    def get_all(
        self,
        limit=None
    ):

        """
        取得全部文章


        Args:

            limit:
                限制筆數


        Return:

            List[Dict]

        """


        try:


            return self.repo.find_all(

                limit

            )


        except Exception as e:


            logger.error(

                f"Service get_all error: {e}"

            )


            return []









    # ==================================================
    # ID 查詢
    # ==================================================


    def get_by_id(
        self,
        article_id
    ):

        """
        使用 ID 查詢文章
        """


        try:


            return self.repo.find_by_id(

                article_id

            )


        except Exception as e:


            logger.error(

                f"Service get_by_id error: {e}"

            )


            return None










    # ==================================================
    # Keyword 查詢
    # ==================================================


    def get_by_keyword(
        self,
        keyword
    ):

        """
        搜尋文章 keyword
        """


        try:


            return self.repo.find_by_keyword(

                keyword

            )


        except Exception as e:


            logger.error(

                f"Service keyword error: {e}"

            )


            return []









    # ==================================================
    # Source 查詢
    # ==================================================


    def get_by_source(
        self,
        source
    ):

        """
        依來源查詢
        """


        try:


            return self.repo.find_by_source(

                source

            )


        except Exception as e:


            logger.error(

                f"Service source error: {e}"

            )


            return []









    # ==================================================
    # AI Importance
    # ==================================================


    def get_by_importance(
        self,
        level
    ):

        """
        AI重要程度查詢


        Example:

            importance >= 8


        """


        try:


            return self.repo.find_by_importance(

                level

            )


        except Exception as e:


            logger.error(

                f"AI importance error: {e}"

            )


            return []









    # ==================================================
    # AI Category
    # ==================================================


    def get_by_category(
        self,
        category
    ):

        """
        AI分類查詢


        Example:

            Semiconductor


        """


        try:


            return self.repo.find_by_category(

                category

            )


        except Exception as e:


            logger.error(

                f"AI category error: {e}"

            )


            return []









    # ==================================================
    # AI Keyword
    # ==================================================


    def get_by_ai_keyword(
        self,
        keyword
    ):

        """
        AI Keyword 搜尋


        Example:


            CoWoS

            AI Chip

            2nm


        """


        try:


            return self.repo.find_by_ai_keyword(

                keyword

            )


        except Exception as e:


            logger.error(

                f"AI keyword error: {e}"

            )


            return []









    # ==================================================
    # AI Top Ranking
    # ==================================================


    def get_ai_top(
        self,
        limit=10
    ):

        """
        AI重要度排行


        依:

            ai_importance


        DESC


        """


        try:



            articles = self.repo.find_all()



            articles.sort(

                key=lambda x:

                x.get(

                    "ai_importance",

                    0

                ),


                reverse=True

            )



            return articles[:limit]




        except Exception as e:


            logger.error(

                f"AI top error: {e}"

            )


            return []









    # ==================================================
    # Count
    # ==================================================


    def count(self):

        """
        文章總數
        """


        try:


            return self.repo.count()


        except Exception as e:


            logger.error(

                f"Count error: {e}"

            )


            return 0










    # ==================================================
    # Close Database
    # ==================================================


    def close(self):


        try:


            self.repo.close()



        except Exception as e:


            logger.error(

                f"Service close error: {e}"

            )