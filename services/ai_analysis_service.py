"""
services/ai_analysis_service.py

AutoSearch V4

P2.2.5

Async AI Analysis Pipeline

Step 1:

AI Analysis Service

功能:

Article Content
|
▼
AI Analysis Result


輸出:

summary
keywords
entities
relations
category
importance

"""


from utils.logger import logger

from models.ai_analysis import AIAnalysis



class AIAnalysisService:
    """
    AI Analysis Service

    負責:

        文章智慧分析


    不負責:

        Database
        API
        Queue

    """



    def __init__(self):

        pass





    # ==================================================
    #
    # Main Analyze Function
    #
    # ==================================================


    def analyze(
        self,
        article
    ):
        """
        分析文章


        Input:

            Article Model

            or

            dict


        Return:

            AIAnalysis Object

        """


        try:


            content = self._get_content(

                article

            )



            result = {



                "summary":

                    self.generate_summary(

                        content

                    ),



                "keywords":

                    self.extract_keywords(

                        content

                    ),



                "entities":

                    self.extract_entities(

                        content

                    ),



                "relations":

                    self.extract_relations(

                        content

                    ),



                "category":

                    self.classify_category(

                        content

                    ),



                "importance":

                    self.calculate_importance(

                        content

                    )

            }





            return AIAnalysis(


                article_id=self._get_article_id(

                    article

                ),



                summary=result["summary"],



                category=result["category"],



                keywords=result["keywords"],



                # ===============================
                # FIX P2.2.5
                # Entity / Relation Mapping
                # ===============================


                entities=result["entities"],



                relations=result["relations"],



                importance=result["importance"],



                ai_model="RuleBased-V4",



                ai_version="4.0",



                confidence=0.8


            )





        except Exception as e:


            logger.error(

                f"AI Analysis error: {e}"

            )


            return None









    # ==================================================
    #
    # Article ID
    #
    # ==================================================


    def _get_article_id(
        self,
        article
    ):


        if isinstance(

            article,

            dict

        ):


            return article.get(

                "id"

            )



        return getattr(

            article,

            "id",

            None

        )










    # ==================================================
    #
    # Content Extract
    #
    # ==================================================


    def _get_content(
        self,
        article
    ):



        if isinstance(

            article,

            dict

        ):



            title = article.get(

                "title",

                ""

            )



            content = article.get(

                "content",

                ""

            )



        else:



            title = getattr(

                article,

                "title",

                ""

            )



            content = getattr(

                article,

                "content",

                ""

            )




        return title + "\n" + content










    # ==================================================
    #
    # Summary
    #
    # ==================================================


    def generate_summary(
        self,
        content
    ):



        if len(content) <= 200:

            return content



        return content[:200]









    # ==================================================
    #
    # Keyword Extraction
    #
    # ==================================================


    def extract_keywords(
        self,
        content
    ):


        keywords = []



        candidates = [


            "AI",

            "Semiconductor",

            "GPU",

            "NVIDIA",

            "TSMC",

            "2nm",

            "CoWoS"


        ]



        for word in candidates:



            if word.lower() in content.lower():

                keywords.append(

                    word

                )



        return keywords










    # ==================================================
    #
    # Entity Extraction
    #
    # ==================================================


    def extract_entities(
        self,
        content
    ):


        entities = []



        candidates = [


            "台積電",

            "NVIDIA",

            "TSMC",

            "Intel",

            "AMD"


        ]



        for entity in candidates:



            if entity.lower() in content.lower():

                entities.append(

                    entity

                )



        return entities










    # ==================================================
    #
    # Relation Extraction
    #
    # ==================================================


    def extract_relations(
        self,
        content
    ):


        relations = []



        if (

            "台積電" in content

            and

            "AI" in content

        ):


            relations.append(

                "台積電 -> 生產 -> AI晶片"

            )



        return relations










    # ==================================================
    #
    # Category Classification
    #
    # ==================================================


    def classify_category(
        self,
        content
    ):


        text = content.lower()



        if (

            "chip" in text

            or

            "semiconductor" in text

            or

            "晶片" in content

        ):


            return "Semiconductor"





        if (

            "ai" in text

            or

            "人工智慧" in content

        ):


            return "AI"





        return "Technology"









    # ==================================================
    #
    # Importance Score
    #
    # ==================================================


    def calculate_importance(
        self,
        content
    ):


        score = 0



        important_words = [


            "AI",

            "NVIDIA",

            "TSMC",

            "台積電",

            "突破",

            "量產"


        ]



        for word in important_words:



            if word.lower() in content.lower():

                score += 1



        if score > 10:

            score = 10



        return score