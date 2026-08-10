"""
services/knowledge_service.py

AutoSearch V4

P1.4 Knowledge Retrieval Layer

+

P2.2.5 Step 4

Knowledge Auto Index Pipeline


用途:

Knowledge 查詢服務

負責:

Repository 與 API Router 中間層

新增:

AIAnalysis
    |
    v
Knowledge
    |
    v
KnowledgeRepository
    |
    v
SearchIndexService

"""


from database.knowledge_repository import (
    KnowledgeRepository
)


from services.search_index_service import (
    SearchIndexService
)





class KnowledgeService:



    def __init__(self):


        self.repository = KnowledgeRepository()


        # P2.2.5 Step 4

        self.search_index_service = SearchIndexService()







    # ==================================
    #
    # Create Knowledge + Search Index
    #
    # P2.2.5 Step 4
    #
    # ==================================


    def create_with_index(

        self,

        knowledge

    ):


        """
        建立 Knowledge Archive

        並建立 Search Index


        Input:

            Knowledge Model


        Output:

            Knowledge


        """



        if knowledge is None:


            return None





        # ==============================
        #
        # 1.
        # Save knowledge_archive
        #
        # ==============================


        knowledge = self.repository.insert(

            knowledge

        )






        # ==============================
        #
        # 2.
        # Build Search Index
        #
        # ==============================


        self.search_index_service.build_index(

            knowledge

        )






        return knowledge










    # ==================================
    #
    # Article Knowledge
    #
    # ==================================


    def get_by_article_id(

        self,

        article_id

    ):


        return self.repository.get_by_article_id(

            article_id

        )











    # ==================================
    #
    # Exists
    #
    # ==================================


    def exists(

        self,

        article_id

    ):


        return self.repository.exists(

            article_id

        )











    # ==================================
    #
    # Topic Retrieval
    #
    # ==================================


    def search_topic(

        self,

        topic

    ):


        return self.repository.find_by_topic(

            topic

        )











    # ==================================
    #
    # Entity Retrieval
    #
    # ==================================


    def search_entity(

        self,

        entity

    ):


        return self.repository.find_by_entity(

            entity

        )











    # ==================================
    #
    # Relation Retrieval
    #
    # ==================================


    def search_relation(

        self,

        relation

    ):


        return self.repository.find_by_relation(

            relation

        )











    # ==================================
    #
    # Full Knowledge Search
    #
    # ==================================


    def search(

        self,

        keyword

    ):


        return self.repository.search(

            keyword

        )











    # ==================================
    #
    # Latest Knowledge
    #
    # ==================================


    def latest(

        self,

        limit=20

    ):


        return self.repository.find_all(

            limit

        )











    # ==================================
    #
    # Update Knowledge
    #
    # ==================================


    def update(

        self,

        article_id,

        knowledge

    ):


        result = self.repository.update(

            article_id,

            knowledge

        )



        if result:


            self.search_index_service.rebuild_index(

                knowledge

            )



        return result