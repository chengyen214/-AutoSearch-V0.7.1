"""
services/knowledge_ranking_service.py

AutoSearch V4

P1.5 Step 4

Knowledge Ranking Service


功能:

1. Knowledge Ranking

2. Top Knowledge Retrieval

3. Score Calculation

4. Score Update


Layer:

API
 |
Service
 |
Repository


"""


from database.knowledge_score_repository import (
    KnowledgeScoreRepository
)



class KnowledgeRankingService:



    def __init__(self):


        self.repository = (
            KnowledgeScoreRepository()
        )





    # ==================================
    # Top Ranking Knowledge
    # ==================================


    def get_top_ranking(

        self,

        limit=10

    ):


        """
        取得最高 Ranking Knowledge

        """


        return self.repository.top_ranking(

            limit

        )







    # ==================================
    # Score Threshold
    # ==================================


    def get_by_score(

        self,

        score=8

    ):


        """
        取得指定分數以上 Knowledge

        """


        return self.repository.find_by_score(

            score

        )







    # ==================================
    # Ranking Calculation
    # ==================================


    def calculate_ranking(

        self,

        importance,

        confidence,

        quality_score,

        freshness_score

    ):


        """
        Ranking Formula


        Importance:
            40%


        Confidence:
            20%


        Quality:
            20%


        Freshness:
            20%


        """


        ranking = (

            importance * 0.4

            +

            confidence * 10 * 0.2

            +

            quality_score * 0.2

            +

            freshness_score * 0.2

        )


        return round(

            ranking,

            2

        )








    # ==================================
    # Update Ranking
    # ==================================


    def update_score(

        self,

        score_id,

        score

    ):


        """
        更新 Knowledge Score

        """


        return self.repository.update(

            score_id,

            score

        )