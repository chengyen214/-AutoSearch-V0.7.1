"""
ai/knowledge_extractor.py

AutoSearch V4

P1.6 Step 2

Knowledge Extractor


功能:

1. AIAnalysis -> Knowledge

2. Entity Extraction

3. Relation Extraction

4. Topic Detection


Pipeline:

AIAnalysis

      |

      v

KnowledgeExtractor

      |

      v

Knowledge Model


"""


from models.knowledge import Knowledge

from utils.logger import logger






class KnowledgeExtractor:
    """
    Rule Based Knowledge Extractor

    V4 P1.6

    """




    def __init__(self):


        # ==========================
        # Entity Dictionary
        # ==========================


        self.entities = [


            "TSMC",

            "台積電",

            "2nm",

            "3nm",

            "CoWoS",

            "HBM",

            "AI",

            "AI Chip",

            "IC",

            "半導體",

            "晶圓",

            "先進製程"


        ]







    # ==================================
    # Main Extract
    # ==================================


    def extract(

        self,

        article_id,

        ai_analysis

    ):


        """
        Article ID + AIAnalysis

                |

                v

            Knowledge

        """



        topic = self.extract_topic(

            ai_analysis

        )



        entities = self.extract_entities(

            ai_analysis

        )



        relations = self.extract_relations(

            ai_analysis

        )






        knowledge = Knowledge(


            article_id=article_id,


            topic=topic,


            entities=entities,


            relations=relations,


            knowledge_version="1.0"


        )





        logger.info(

            f"Knowledge extracted: {topic}"

        )





        return knowledge







    # ==================================
    # Topic
    # ==================================


    def extract_topic(

        self,

        ai_analysis

    ):


        return ai_analysis.category










    # ==================================
    # Entity Extraction
    # ==================================


    def extract_entities(

        self,

        ai_analysis

    ):


        result = []



        text = (

            ai_analysis.summary

            +

            " "

            +

            " ".join(

                ai_analysis.keywords

            )

        )





        for entity in self.entities:



            if entity.lower() in text.lower():


                result.append(

                    entity

                )






        return list(

            dict.fromkeys(

                result

            )

        )









    # ==================================
    # Relation Extraction
    # ==================================


    def extract_relations(

        self,

        ai_analysis

    ):


        relations = []



        text = ai_analysis.summary





        if any(

            word in text

            for word in [

                "需求",

                "成長",

                "增加",

                "提升"

            ]

        ):


            relations.append(

                "市場需求推動技術發展"

            )







        if any(

            word in text

            for word in [

                "量產",

                "製程",

                "2nm",

                "3nm"

            ]

        ):


            relations.append(

                "先進製程技術演進"

            )








        if not relations:


            relations.append(

                "產業資訊關聯"

            )




        return relations