"""
analyzer.py

AutoSearch V3

P4.4.3

AI Analyzer


流程:

Article Content

        |
        v

AI Analyzer

        |
        v

AIAnalysis


功能:

    1. Summary
    2. Category Detection
    3. Keyword Extraction
    4. Importance Score
    5. AI Metadata


Future:

    P5 LangChain / LLM
"""



from models.ai_analysis import AIAnalysis

from utils.logger import logger






class AIAnalyzer:
    """
    Rule Based AI Analyzer


    P4.4.3

    """



    def __init__(self):


        # ==========================
        # AI Metadata
        # ==========================


        self.ai_model = "RuleBased-V3"

        self.ai_version = "3.0"

        self.confidence = 0.9






        # ==========================
        # Category Dictionary
        # ==========================


        self.categories = {


            "Semiconductor":

            [

                "IC",

                "半導體",

                "晶片",

                "Chip",

                "AI Chip",

                "TSMC",

                "台積電",

                "晶圓",

                "2nm",

                "3nm",

                "CoWoS",

                "HBM",

                "封裝",

                "先進製程"

            ],




            "AI":

            [

                "AI",

                "人工智慧",

                "Machine Learning",

                "Deep Learning",

                "LLM",

                "GPT",

                "生成式AI"

            ],




            "Software":

            [

                "Software",

                "Cloud",

                "SaaS",

                "平台",

                "系統"

            ]

        }







        # ==========================
        # Keyword Priority
        # ==========================


        self.keyword_priority = [

            "2nm",

            "3nm",

            "AI Chip",

            "HBM",

            "CoWoS",

            "TSMC",

            "台積電",

            "半導體",

            "IC",

            "AI",

            "封裝"

        ]









    # ==================================================
    # Main Analyze
    # ==================================================


    def analyze(
        self,
        content
    ):


        category = self.detect_category(

            content

        )



        summary = self.generate_summary(

            content

        )



        keywords = self.extract_keywords(

            content

        )



        importance = self.calculate_importance(

            content,

            keywords,

            category

        )







        # ==========================
        # P4.4.3
        # AIAnalysis Object
        # ==========================


        result = AIAnalysis(


            summary=summary,


            category=category,


            keywords=keywords,


            importance=importance,



            ai_model=self.ai_model,


            ai_version=self.ai_version,


            confidence=self.confidence


        )







        logger.info(

            f"AI Analyze complete: {category}"

        )



        return result










    # ==================================================
    # Summary
    # ==================================================


    def generate_summary(
        self,
        content
    ):


        if not content:

            return ""



        text = content.replace(

            "\n",

            " "

        )



        text = " ".join(

            text.split()

        )



        return text[:200]









    # ==================================================
    # Category
    # ==================================================


    def detect_category(
        self,
        content
    ):


        if not content:

            return "Unknown"



        text = content.lower()



        scores = {}



        for category, words in self.categories.items():


            score = 0



            for word in words:


                if word.lower() in text:

                    score += 1



            scores[category] = score






        result = max(

            scores,

            key=scores.get

        )



        if scores[result] == 0:

            return "Other"



        return result










    # ==================================================
    # Keyword Extraction
    # ==================================================


    def extract_keywords(
        self,
        content
    ):


        if not content:

            return []



        text = content.lower()



        keywords = []



        for words in self.categories.values():


            for word in words:


                if word.lower() in text:


                    keywords.append(word)






        # Remove duplicate


        keywords = list(

            dict.fromkeys(

                keywords

            )

        )






        # Remove generic word


        remove_words = [

            "Chip"

        ]



        keywords = [

            k

            for k in keywords

            if k not in remove_words

        ]







        # Priority Sort


        keywords.sort(

            key=lambda x:

            self.keyword_priority.index(x)

            if x in self.keyword_priority

            else 99

        )



        return keywords[:8]











    # ==================================================
    # Importance
    # ==================================================


    def calculate_importance(
        self,
        content,
        keywords,
        category
    ):


        score = 0




        # keyword bonus

        score += len(

            keywords

        )





        # category bonus


        if category in [

            "Semiconductor",

            "AI"

        ]:


            score += 2





        # important event


        important_words = [

            "2nm",

            "3nm",

            "量產",

            "IPO",

            "投資",

            "收購",

            "突破",

            "重大"

        ]




        text = content.lower()




        for word in important_words:


            if word.lower() in text:


                score += 1






        # limit 10


        if score > 10:

            score = 10



        if score < 1:

            score = 1



        return score