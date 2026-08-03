"""
ai_analysis.py

AutoSearch V3

P4.4.3

AI Analysis Result Model


用途:

    儲存 AI 分析結果


支援:

    - Summary
    - Category
    - Keywords
    - Importance
    - AI Metadata


Database:

    MySQL articles table


Future:

    - OpenAI API
    - LangChain
    - Vector Database
    - RAG

"""


from typing import List, Dict

from datetime import datetime

import json






class AIAnalysis:
    """
    AI 分析結果模型
    """



    def __init__(
        self,

        summary: str = "",

        category: str = "",

        keywords: List[str] = None,

        importance: int = 0,


        # ==========================
        # P4.4.3 AI Metadata
        # ==========================

        ai_model: str = "RuleBased-V3",

        ai_version: str = "3.0",

        confidence: float = 0.9,

        analyze_time=None

    ):



        # ==========================
        # Basic AI Result
        # ==========================


        self.summary = summary


        self.category = category



        self.keywords = (

            keywords

            if keywords is not None

            else []

        )



        self.importance = int(

            importance

        )





        # ==========================
        # AI Metadata
        # ==========================


        self.ai_model = ai_model


        self.ai_version = ai_version



        self.confidence = float(

            confidence

        )



        self.analyze_time = (

            analyze_time

            if analyze_time

            else datetime.now()

        )









    # ==================================================
    # Object -> Dictionary
    # ==================================================


    def to_dict(
        self
    ) -> Dict:
        """
        Object轉Dictionary

        用於:

        - MySQL
        - API
        - Debug

        """


        return {


            "summary":

                self.summary,


            "category":

                self.category,


            "keywords":

                self.keywords,


            "importance":

                self.importance,



            "ai_model":

                self.ai_model,


            "ai_version":

                self.ai_version,


            "analyze_time":

                self.analyze_time,


            "confidence":

                self.confidence


        }










    # ==================================================
    # Object -> JSON
    # ==================================================


    def to_json(
        self
    ) -> str:
        """
        JSON輸出
        """


        data = self.to_dict()



        if isinstance(

            data["analyze_time"],

            datetime

        ):


            data["analyze_time"] = (

                data["analyze_time"]

                .strftime(

                    "%Y-%m-%d %H:%M:%S"

                )

            )




        return json.dumps(

            data,

            ensure_ascii=False

        )











    # ==================================================
    # Dictionary -> Object
    # ==================================================


    @classmethod
    def from_dict(
        cls,
        data: Dict
    ):
        """
        Dictionary建立AIAnalysis
        """



        return cls(


            summary=data.get(

                "summary",

                ""

            ),



            category=data.get(

                "category",

                ""

            ),



            keywords=data.get(

                "keywords",

                []

            ),



            importance=data.get(

                "importance",

                0

            ),



            ai_model=data.get(

                "ai_model",

                ""

            ),



            ai_version=data.get(

                "ai_version",

                ""

            ),



            confidence=data.get(

                "confidence",

                0.0

            ),



            analyze_time=data.get(

                "analyze_time",

                None

            )

        )









    # ==================================================
    # Validation
    # ==================================================


    def is_valid(
        self
    ) -> bool:
        """
        AI結果有效性檢查
        """


        return bool(

            self.summary

            or

            self.category

            or

            self.keywords

        )









    # ==================================================
    # Display
    # ==================================================


    def __repr__(
        self
    ):


        return (

            "AIAnalysis("

            f"category={self.category}, "

            f"importance={self.importance}, "

            f"keywords={len(self.keywords)}, "

            f"model={self.ai_model}, "

            f"confidence={self.confidence}"

            ")"

        )