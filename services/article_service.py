"""
article_service.py

AutoSearch V2.5 P5

Article Service Layer

用途：

    封裝 Article 查詢邏輯

    API 不直接操作 Repository

流程：

    API
     |
     v
    Service
     |
     v
    Repository
     |
     v
    MySQL

"""


from database.article_repository import ArticleRepository



class ArticleService:


    def __init__(self):

        self.repository = ArticleRepository()



    # ==================================
    # 取得全部文章
    # ==================================

    def get_all_articles(self):

        return self.repository.find_all()



    # ==================================
    # 依 ID 查詢
    # ==================================

    def get_article_by_id(
        self,
        article_id
    ):

        return self.repository.find_by_id(
            article_id
        )



    # ==================================
    # 依關鍵字查詢
    # ==================================

    def search_by_keyword(
        self,
        keyword
    ):

        return self.repository.find_by_keyword(
            keyword
        )



    # ==================================
    # 依來源查詢
    # ==================================

    def search_by_source(
        self,
        source
    ):

        return self.repository.find_by_source(
            source
        )



    # ==================================
    # 取得文章數量
    # ==================================

    def count_articles(self):

        return self.repository.count()



    # ==================================
    # 關閉 Database
    # ==================================

    def close(self):

        self.repository.close()