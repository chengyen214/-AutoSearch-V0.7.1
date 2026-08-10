"""
models/ai_analysis.py

AutoSearch V4

P4.4.3 + P1.6 + P2.2.5

AI Analysis Result Model


用途:

    儲存 AI 分析結果


支援:

    - Article Relation
    - Summary
    - Category
    - Keywords
    - Importance
    - AI Metadata
    - Entity Extraction
    - Relation Extraction
    - Async AI Pipeline Status


Database:

    ai_analysis table


Future:

    - LangChain
    - Vector Database
    - RAG
    - Knowledge Graph

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


        # ==========================
        # Article Relation
        # ==========================

        article_id=None,



        # ==========================
        # Basic AI Result
        # ==========================

        summary: str = "",


        category: str = "",


        keywords: List[str] = None,


        importance: int = 0,



        # ==========================
        # Knowledge Extraction
        # P2.2.5
        # ==========================

        entities: List[str] = None,


        relations: List[str] = None,



        # ==========================
        # AI Metadata
        # ==========================

        ai_model: str = "RuleBased-V3",


        ai_version: str = "4.0",


        confidence: float = 0.9,


        analyze_time=None,



        # ==========================
        # Async Pipeline
        # P2.2.5
        # ==========================

        status: str = "pending",


        error_message: str = "",



        id=None

    ):



        # ==========================
        # ID
        # ==========================

        self.id = id



        # ==========================
        # Article Relation
        # ==========================

        self.article_id = article_id





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
        # Knowledge Extraction
        # ==========================

        self.entities = (

            entities

            if entities is not None

            else []

        )



        self.relations = (

            relations

            if relations is not None

            else []

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







        # ==========================
        # Async Pipeline
        # ==========================

        self.status = status


        self.error_message = error_message







    # ==================================================
    # Object -> Dictionary
    # ==================================================

    def to_dict(

        self

    ) -> Dict:



        return {



            "id":

                self.id,



            "article_id":

                self.article_id,



            "summary":

                self.summary,



            "category":

                self.category,



            "keywords":

                self.keywords,



            "importance":

                self.importance,



            "entities":

                self.entities,



            "relations":

                self.relations,



            "ai_model":

                self.ai_model,



            "ai_version":

                self.ai_version,



            "confidence":

                self.confidence,



            "analyze_time":

                self.analyze_time,



            "status":

                self.status,



            "error_message":

                self.error_message


        }







    # ==================================================
    # Object -> JSON
    # ==================================================

    def to_json(

        self

    ) -> str:



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



        return cls(



            id=data.get(

                "id",

                None

            ),



            article_id=data.get(

                "article_id",

                None

            ),



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



            entities=data.get(

                "entities",

                []

            ),



            relations=data.get(

                "relations",

                []

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

            ),



            status=data.get(

                "status",

                "pending"

            ),



            error_message=data.get(

                "error_message",

                ""

            )


        )







    # ==================================================
    # Validation
    # ==================================================

    def is_valid(

        self

    ) -> bool:



        return bool(



            self.summary


            or


            self.category


            or


            self.keywords


            or


            self.entities


        )







    # ==================================================
    # Pipeline Status
    # ==================================================

    def mark_completed(

        self

    ):



        self.status = "completed"


        self.error_message = ""







    def mark_failed(

        self,

        error

    ):



        self.status = "failed"


        self.error_message = str(

            error

        )







    # ==================================================
    # Display
    # ==================================================

    def __repr__(

        self

    ):



        return (

            "AIAnalysis("


            f"id={self.id}, "


            f"article_id={self.article_id}, "


            f"category={self.category}, "


            f"importance={self.importance}, "


            f"keywords={len(self.keywords)}, "


            f"entities={len(self.entities)}, "


            f"status={self.status}, "


            f"model={self.ai_model}, "


            f"confidence={self.confidence}"


            ")"

        )