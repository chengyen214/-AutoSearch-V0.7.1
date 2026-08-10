"""
services/knowledge_intelligent_search_service.py

AutoSearch V4

P1.7 Step 3

Knowledge Intelligent Search Service


Flow:

Query

 |

 v

Knowledge Repository

 |

 v

Knowledge Score

 |

 v

Knowledge Search Score

 |

 v

Ranking Result


"""


from database.knowledge_repository import (
    KnowledgeRepository
)


from database.knowledge_score_repository import (
    KnowledgeScoreRepository
)


from models.knowledge_search_score import (
    KnowledgeSearchScore
)


from utils.logger import logger





class KnowledgeIntelligentSearchService:



    def __init__(self):


        self.knowledge_repository = (
            KnowledgeRepository()
        )


        self.score_repository = (
            KnowledgeScoreRepository()
        )






    # ==================================
    # Calculate Search Score
    # ==================================


    def calculate_search_score(

        self,

        keyword,

        knowledge,

        score

    ):


        text = (

            str(knowledge.get("topic", ""))

            +

            str(knowledge.get("entities", ""))

            +

            str(knowledge.get("relations", ""))

        ).lower()



        keyword = keyword.lower()



        # --------------------------
        # Keyword Match
        # --------------------------


        keyword_score = (

            10

            if keyword in text

            else 0

        )





        # --------------------------
        # Entity Match
        # --------------------------


        entity_score = 0


        entities = str(

            knowledge.get(

                "entities",

                ""

            )

        ).lower()



        if keyword in entities:


            entity_score = 10






        # --------------------------
        # Topic Match
        # --------------------------


        topic_score = 0


        topic = str(

            knowledge.get(

                "topic",

                ""

            )

        ).lower()



        if keyword in topic:


            topic_score = 10






        # --------------------------
        # Knowledge Quality Score
        # --------------------------


        importance = (

            score.get(

                "importance",

                0

            )

            if score

            else 0

        )



        confidence = (

            score.get(

                "confidence",

                0

            )

            * 10

            if score

            else 0

        )



        freshness = (

            score.get(

                "freshness_score",

                0

            )

            if score

            else 0

        )



        ranking = (

            score.get(

                "ranking_score",

                0

            )

            if score

            else 0

        )






        return KnowledgeSearchScore(


            keyword_score=keyword_score,


            entity_score=entity_score,


            topic_score=topic_score,


            importance_score=importance,


            confidence_score=confidence,


            freshness_score=freshness,


            ranking_score=ranking


        )









    # ==================================
    # Intelligent Search
    # ==================================


    def search(

        self,

        keyword

    ):



        knowledge_list = (

            self.knowledge_repository.search(

                keyword

            )

        )



        results = []





        for knowledge in knowledge_list:



            score = (

                self.score_repository

                .get_by_knowledge_id(

                    knowledge["id"]

                )

            )





            search_score = (

                self.calculate_search_score(

                    keyword,

                    knowledge,

                    score

                )

            )






            results.append({



                "knowledge": knowledge,



                "score": score,



                "search_score":

                    search_score.to_dict()



            })







        # ==============================
        # Final Ranking
        # ==============================


        results.sort(


            key=lambda x:


            x["search_score"]

            ["final_score"],


            reverse=True


        )






        logger.info(


            f"Intelligent search ranking: {keyword}, count={len(results)}"


        )



        return results