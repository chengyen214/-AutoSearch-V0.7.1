"""
services/hybrid_search_service.py

AutoSearch V4

P2.1

Hybrid Search Engine


Flow:


Query

    |

    +----------------+

    |                |

    v                v


Keyword Search    Semantic Search


    |                |

    +-------+--------+

            |

            v


Knowledge Ranking Fusion


            |

            v


Hybrid Score


            |

            v


Final Result


"""


from services.knowledge_intelligent_search_service import (
    KnowledgeIntelligentSearchService
)


from services.semantic_search_service import (
    SemanticSearchService
)


from database.knowledge_score_repository import (
    KnowledgeScoreRepository
)


from utils.logger import logger







class HybridSearchService:



    def __init__(self):


        # ==========================
        # Search Services
        # ==========================


        self.keyword_service = (

            KnowledgeIntelligentSearchService()

        )


        self.semantic_service = (

            SemanticSearchService()

        )



        # ==========================
        # Ranking
        # ==========================


        self.score_repository = (

            KnowledgeScoreRepository()

        )








    # ==================================
    # Helper
    # ==================================


    def _get_knowledge_id(

        self,

        knowledge

    ):


        """
        Support:

        dict

        or

        Knowledge object

        """


        if isinstance(

            knowledge,

            dict

        ):


            return knowledge.get(

                "id"

            )


        return knowledge.id







    def _normalize_knowledge(

        self,

        knowledge

    ):


        """
        Keep output format consistent

        """


        if isinstance(

            knowledge,

            dict

        ):


            return knowledge


        return knowledge.to_dict()









    # ==================================
    # Hybrid Search
    # ==================================


    def search(

        self,

        query,

        top_k=10

    ):



        if not query:


            return []





        # ==========================
        # Keyword Search
        # ==========================


        keyword_results = (

            self.keyword_service.search(

                query

            )

        )



        keyword_map = {}



        for item in keyword_results:


            knowledge = item["knowledge"]


            knowledge_id = (

                self._get_knowledge_id(

                    knowledge

                )

            )


            keyword_map[

                knowledge_id

            ] = item







        # ==========================
        # Semantic Search
        # ==========================


        semantic_results = (

            self.semantic_service.search(

                query,

                top_k

            )

        )



        semantic_map = {}



        for item in semantic_results:


            knowledge = item["knowledge"]


            knowledge_id = (

                self._get_knowledge_id(

                    knowledge

                )

            )


            semantic_map[

                knowledge_id

            ] = item









        # ==========================
        # Merge Result ID
        # ==========================


        knowledge_ids = (

            set(

                keyword_map.keys()

            )

            |

            set(

                semantic_map.keys()

            )

        )





        results = []






        for knowledge_id in knowledge_ids:




            keyword_item = (

                keyword_map.get(

                    knowledge_id

                )

            )



            semantic_item = (

                semantic_map.get(

                    knowledge_id

                )

            )





            # ======================
            # Knowledge
            # ======================


            if semantic_item:


                knowledge = (

                    semantic_item["knowledge"]

                )


            else:


                knowledge = (

                    keyword_item["knowledge"]

                )



            knowledge = (

                self._normalize_knowledge(

                    knowledge

                )

            )







            # ======================
            # Keyword Score
            # ======================


            keyword_score = 0



            if keyword_item:


                keyword_score = 10







            # ======================
            # Semantic Score
            # ======================


            semantic_score = 0



            if semantic_item:


                semantic_score = (

                    semantic_item.get(

                        "semantic_score",

                        0

                    )

                )








            # ======================
            # Ranking Score
            # ======================


            ranking_score = 0



            score = (

                self.score_repository

                .get_by_knowledge_id(

                    knowledge_id

                )

            )



            if score:


                ranking_score = (

                    score.get(

                        "ranking_score",

                        0

                    )

                )








            # ======================
            # Hybrid Score
            # ======================


            final_score = round(

                (

                    keyword_score * 0.3

                )

                +

                (

                    ranking_score * 0.3

                )

                +

                (

                    semantic_score * 10 * 0.4

                ),


                2

            )







            results.append(


                {


                    "knowledge":

                        knowledge,


                    "score":

                        {


                            "keyword_score":

                                keyword_score,


                            "ranking_score":

                                ranking_score,


                            "semantic_score":

                                semantic_score,


                            "final_score":

                                final_score


                        }


                }


            )







        # ==========================
        # Sort
        # ==========================


        results.sort(

            key=lambda x:

            x["score"]["final_score"],


            reverse=True

        )






        logger.info(

            f"Hybrid search: {query}, count={len(results)}"

        )



        return results[:top_k]