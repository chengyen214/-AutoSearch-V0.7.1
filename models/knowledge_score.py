"""
models/knowledge_score.py

AutoSearch V4

Knowledge Score Model


用途:

    保存 Knowledge Intelligence 評分結果


Database:

    knowledge_scores


V4 P1.5


"""


from datetime import datetime





class KnowledgeScore:




    def __init__(

        self,


        knowledge_id=None,


        importance=0,


        confidence=0.0,


        quality_score=0.0,


        freshness_score=0.0,


        ranking_score=0.0,


        created_time=None


    ):



        # ==========================
        # Database ID
        # ==========================


        self.id = None




        # ==========================
        # Knowledge Relation
        # ==========================


        self.knowledge_id = knowledge_id




        # ==========================
        # AI Score
        # ==========================


        self.importance = importance


        self.confidence = confidence




        # ==========================
        # Intelligence Score
        # ==========================


        self.quality_score = quality_score


        self.freshness_score = freshness_score


        self.ranking_score = ranking_score




        # ==========================
        # Time
        # ==========================


        self.created_time = (

            created_time

            if created_time

            else datetime.now()

        )




    # ==================================
    # Score Property
    # ==================================


    @property
    def is_high_quality(self):


        return (

            self.ranking_score >= 8

        )





    @property
    def score_level(self):


        if self.ranking_score >= 8:

            return "HIGH"


        elif self.ranking_score >= 5:

            return "MEDIUM"


        else:

            return "LOW"






    # ==================================
    # Dictionary
    # ==================================


    def to_dict(self):


        return {


            "id":

            self.id,



            "knowledge_id":

            self.knowledge_id,



            "importance":

            self.importance,



            "confidence":

            self.confidence,



            "quality_score":

            self.quality_score,



            "freshness_score":

            self.freshness_score,



            "ranking_score":

            self.ranking_score,



            "created_time":

            self.created_time


        }





    def __repr__(self):


        return (

            f"KnowledgeScore("

            f"knowledge_id={self.knowledge_id}, "

            f"ranking={self.ranking_score}"

            ")"

        )