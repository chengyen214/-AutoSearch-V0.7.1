"""
retrieval_service.py

AutoSearch V3

Retrieval Service

負責：
    Article 查詢服務
"""


from database.article_repository import ArticleRepository



class RetrievalService:


    def __init__(self):

        self.repo = ArticleRepository()



    def get_all(self):

        return self.repo.find_all()



    def search_importance(
        self,
        level
    ):

        return self.repo.find_by_importance(
            level
        )



    def search_category(
        self,
        category
    ):

        return self.repo.find_by_category(
            category
        )



    def search_keyword(
        self,
        keyword
    ):

        return self.repo.find_by_ai_keyword(
            keyword
        )