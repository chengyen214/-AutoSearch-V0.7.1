"""
pipeline/knowledge_pipeline.py

AutoSearch V4

P1.6 Step 4

Knowledge Persistence Pipeline


Flow:

Article

    |

    v

AI Analyzer

    |

    v

AI Analysis


    |

    v


Knowledge Extractor


    |

    v


KnowledgeRepository


    |

    v


knowledge_archive



功能:

1. Article AI Analysis

2. Knowledge Extraction

3. Knowledge Persistence

"""


from ai.analyzer import AIAnalyzer

from ai.knowledge_extractor import KnowledgeExtractor


from database.knowledge_repository import (
    KnowledgeRepository
)


from models.knowledge import Knowledge


from utils.logger import logger






class KnowledgePipeline:




    def __init__(self):


        # ==========================
        # AI Layer
        # ==========================


        self.analyzer = AIAnalyzer()


        self.extractor = KnowledgeExtractor()





        # ==========================
        # Persistence Layer
        # ==========================


        self.repository = KnowledgeRepository()







    # ==================================================
    # Convert Dict -> Knowledge
    # ==================================================


    def _to_knowledge(

        self,

        data

    ):


        """
        Database Dict

        ->

        Knowledge Object

        """



        if data is None:


            return None




        knowledge = Knowledge(


            article_id=data["article_id"],


            topic=data["topic"],


            entities=(

                data["entities"].split(",")

                if data["entities"]

                else []

            ),



            relations=(

                data["relations"].split(",")

                if data["relations"]

                else []

            ),



            knowledge_version=data["knowledge_version"],


            created_time=data["created_time"]

        )



        knowledge.id = data["id"]



        return knowledge







    # ==================================================
    # Run Pipeline
    # ==================================================


    def run(

        self,

        article

    ):


        """
        
        Article

        ->

        Knowledge


        return:

            Knowledge Object


        """




        # ==================================
        # Step 1
        #
        # AI Analysis
        #
        # ==================================


        ai_analysis = self.analyzer.analyze(

            article.content

        )



        logger.info(

            f"AI Analysis completed: {ai_analysis.category}"

        )







        # ==================================
        # Step 2
        #
        # Knowledge Extraction
        #
        # ==================================


        knowledge = self.extractor.extract(

            article.id,

            ai_analysis

        )



        logger.info(

            f"Knowledge extracted: {knowledge.topic}"

        )







        # ==================================
        # Step 3
        #
        # Persistence
        #
        # knowledge_archive
        #
        # ==================================



        if self.repository.exists(

            article.id

        ):



            logger.info(

                f"Knowledge exists: article_id={article.id}"

            )



            data = self.repository.get_by_article_id(

                article.id

            )



            return self._to_knowledge(

                data

            )








        else:



            result = self.repository.insert(

                knowledge

            )



            logger.info(

                f"Knowledge saved: id={result.id}"

            )



            return result