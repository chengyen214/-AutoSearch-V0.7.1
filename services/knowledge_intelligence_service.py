"""
services/knowledge_intelligence_service.py

AutoSearch V4

P2.2.6

Knowledge Intelligence Service

Responsibilities:

1. Knowledge Score Generation

2. Knowledge Ranking

3. Intelligence Query

4. Search Index Update


Flow:

knowledge_archive

    |
    v

Knowledge Intelligence

    |
    +--> knowledge_scores

    |
    +--> ranking

    |
    +--> search_index

"""


from database.knowledge_repository import (
    KnowledgeRepository
)


from database.knowledge_score_repository import (
    KnowledgeScoreRepository
)


from models.knowledge_score import (
    KnowledgeScore
)


from utils.logger import logger





class KnowledgeIntelligenceService:



    def __init__(self):


        self.knowledge_repository = (

            KnowledgeRepository()

        )


        self.score_repository = (

            KnowledgeScoreRepository()

        )







    # ==================================
    #
    # Analyze Knowledge
    #
    # P2.2.6 Core
    #
    # ==================================


    def analyze_knowledge(

        self,

        knowledge,

        analysis=None

    ):


        """
        Knowledge Intelligence Pipeline


        Knowledge

        +

        AI Analysis


        |

        v


        Knowledge Score


        |

        v


        Ranking


        """



        try:



            # --------------------------
            # AI Score Source
            # --------------------------


            importance = 0


            confidence = 0





            if analysis:



                importance = getattr(

                    analysis,

                    "importance",

                    0

                )



                confidence = getattr(

                    analysis,

                    "confidence",

                    0

                )





            # --------------------------
            # Quality Score
            # --------------------------


            quality_score = (

                importance

                *

                confidence

            )







            # --------------------------
            # Freshness
            # --------------------------


            freshness_score = 10







            # --------------------------
            # Ranking Score
            #
            # importance 50%
            # confidence 30%
            # quality 20%
            #
            # --------------------------


            ranking_score = (

                importance * 0.5

                +

                confidence * 0.3

                +

                quality_score * 0.2

            )







            score = KnowledgeScore(



                knowledge_id=knowledge.id,



                importance=importance,



                confidence=confidence,



                quality_score=quality_score,



                freshness_score=freshness_score,



                ranking_score=ranking_score


            )







            result = (

                self.score_repository
                .insert(

                    score

                )

            )







            logger.info(

                f"Knowledge score created knowledge={knowledge.id}"

            )





            return result








        except Exception as e:



            logger.exception(

                f"Knowledge intelligence error {e}"

            )


            return None










    # ==================================
    #
    # Get Knowledge Intelligence
    #
    # ==================================


    def get_knowledge(

        self,

        article_id

    ):



        knowledge = (

            self.knowledge_repository
            .get_by_article_id(

                article_id

            )

        )



        if knowledge is None:


            return None






        score = (

            self.score_repository
            .get_by_knowledge_id(

                knowledge["id"]

            )

        )





        return {


            "knowledge":

                knowledge,


            "score":

                score


        }









    # ==================================
    #
    # Top Intelligence
    #
    # ==================================


    def get_top_intelligence(

        self,

        limit=10

    ):



        scores = (

            self.score_repository
            .top_ranking(

                limit

            )

        )



        results = []



        for score in scores:



            knowledge = (

                self.knowledge_repository
                .get_by_id(

                    score["knowledge_id"]

                )

            )



            results.append({


                "knowledge":

                    knowledge,


                "score":

                    score


            })







        logger.info(

            f"Top intelligence count={len(results)}"

        )



        return results









    # ==================================
    #
    # High Quality Knowledge
    #
    # ==================================


    def get_high_quality(

        self,

        score=8

    ):



        return (

            self.score_repository
            .find_by_score(

                score

            )

        )









    # ==================================
    #
    # Run Pipeline Entry
    #
    # ==================================


    def run(self):


        """
        Main Entry

        For app/main.py

        """

        try:


            result = self.get_top_intelligence(

                10

            )


            logger.info(

                f"Knowledge Intelligence run count={len(result)}"

            )


            return result



        except Exception as e:


            logger.exception(

                f"Knowledge intelligence run failed {e}"

            )


            return []