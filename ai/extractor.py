"""
ai/extractor.py

AutoSearch V4

P1.6 Step 1

Knowledge Extractor


功能:

1. AI Analysis -> Knowledge

2. 建立 Knowledge Archive Object


Input:

AIAnalysis


Output:

Knowledge


"""


from models.knowledge import Knowledge





class KnowledgeExtractor:




    """
    Knowledge Extractor


    將 AI 分析結果

    轉換成 Knowledge Model


    """





    def extract(

        self,

        ai_analysis

    ):


        """
        AI Analysis

        →

        Knowledge


        Args:

            ai_analysis:

                models.ai_analysis.AIAnalysis


        Returns:

            Knowledge


        """



        knowledge = Knowledge(



            article_id=

                ai_analysis.article_id,



            topic=

                ai_analysis.category,



            entities=

                self.build_entities(

                    ai_analysis

                ),



            relations=

                self.build_relation(

                    ai_analysis

                ),



            knowledge_version=

                "1.0"


        )



        return knowledge







    # ==================================
    # Entity Builder
    # ==================================


    def build_entities(

        self,

        ai_analysis

    ):


        """
        建立 Knowledge Entity


        來源:

        AI keywords


        """


        keywords = ai_analysis.keywords



        if keywords is None:


            return ""




        if isinstance(

            keywords,

            list

        ):


            return ",".join(

                keywords

            )



        return keywords







    # ==================================
    # Relation Builder
    # ==================================


    def build_relation(

        self,

        ai_analysis

    ):


        """
        建立 Knowledge Relation


        目前使用 Summary


        後續 P2:

        使用 LLM Relation Extraction


        """



        return ai_analysis.summary