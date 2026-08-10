"""
models/knowledge_search_score.py

AutoSearch V4

P1.7 Step 3

Knowledge Search Ranking Score Model


用途:

    計算搜尋結果相關性


注意:

    knowledge_score.py
    = Knowledge品質評分


    knowledge_search_score.py
    = Query搜尋相關性評分


"""


class KnowledgeSearchScore:



    def __init__(

        self,

        keyword_score=0,

        entity_score=0,

        topic_score=0,

        importance_score=0,

        confidence_score=0,

        freshness_score=0,

        ranking_score=0

    ):



        self.keyword_score = (

            keyword_score

        )


        self.entity_score = (

            entity_score

        )


        self.topic_score = (

            topic_score

        )


        self.importance_score = (

            importance_score

        )


        self.confidence_score = (

            confidence_score

        )


        self.freshness_score = (

            freshness_score

        )


        self.ranking_score = (

            ranking_score

        )







    # ==================================
    # Final Search Score
    # ==================================


    @property
    def final_score(self):


        score = (


            self.keyword_score * 0.25


            +


            self.entity_score * 0.20


            +


            self.topic_score * 0.10


            +


            self.importance_score * 0.15


            +


            self.confidence_score * 0.10


            +


            self.freshness_score * 0.10


            +


            self.ranking_score * 0.10


        )



        return round(

            score,

            2

        )







    # ==================================
    # Dictionary
    # ==================================


    def to_dict(self):


        return {


            "keyword_score":

                self.keyword_score,


            "entity_score":

                self.entity_score,


            "topic_score":

                self.topic_score,


            "importance_score":

                self.importance_score,


            "confidence_score":

                self.confidence_score,


            "freshness_score":

                self.freshness_score,


            "ranking_score":

                self.ranking_score,


            "final_score":

                self.final_score


        }







    def __repr__(self):


        return (

            "KnowledgeSearchScore("

            f"final_score={self.final_score}"

            ")"

        )