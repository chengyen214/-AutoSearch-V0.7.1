"""
models/article.py

AutoSearch V4

Article Data Model

支援:

V2.5 Database

V3 AI Analysis

V3 API

V4 Knowledge Archive

P2.2.5 Async AI Analysis Pipeline
"""

from datetime import datetime



class Article:


    def __init__(

        self,

        keyword="",

        title="",

        url="",

        published=None,

        source="",

        content="",


        crawl_time=None,


        status="Success",


        document_id=""

    ):


        # ==============================
        # Database ID
        # ==============================

        self.id = None



        # ==============================
        # Article Basic Data
        # ==============================

        self.keyword = keyword

        self.title = title

        self.url = url

        self.published = published

        self.source = source

        self.content = content



        self.crawl_time = (

            crawl_time

            if crawl_time

            else datetime.now()

        )



        self.status = status



        self.document_id = document_id



        # ==============================
        # P2.2.5 Async AI Pipeline Status
        #
        # pending
        # processing
        # completed
        # failed
        #
        # ==============================

        self.ai_status = "pending"




        # ==============================
        # V3 AI Analysis
        # ==============================

        self.ai_analysis = None




        # ==============================
        # V4 Archive
        # ==============================

        self.raw_document = None


        self.metadata = None


        self.knowledge = None







    # ==================================
    # AI Property
    # ==================================


    @property
    def ai_summary(self):


        if self.ai_analysis:


            return getattr(

                self.ai_analysis,

                "summary",

                ""

            )


        return ""





    @property
    def ai_category(self):


        if self.ai_analysis:


            return getattr(

                self.ai_analysis,

                "category",

                ""

            )


        return ""





    @property
    def ai_keywords(self):


        if self.ai_analysis:


            return getattr(

                self.ai_analysis,

                "keywords",

                []

            )


        return []





    @property
    def ai_importance(self):


        if self.ai_analysis:


            return int(

                getattr(

                    self.ai_analysis,

                    "importance",

                    0

                )

            )


        return 0





    @property
    def ai_model(self):


        if self.ai_analysis:


            return getattr(

                self.ai_analysis,

                "ai_model",

                ""

            )


        return ""





    @property
    def ai_version(self):


        if self.ai_analysis:


            return getattr(

                self.ai_analysis,

                "ai_version",

                ""

            )


        return ""





    @property
    def ai_analyze_time(self):


        if self.ai_analysis:


            return getattr(

                self.ai_analysis,

                "analyze_time",

                None

            )


        return None





    @property
    def ai_confidence(self):


        if self.ai_analysis:


            return float(

                getattr(

                    self.ai_analysis,

                    "confidence",

                    0.0

                )

            )


        return 0.0







    # ==================================
    # V4 Archive Property
    # ==================================


    @property
    def archive_path(self):


        if self.raw_document:


            return getattr(

                self.raw_document,

                "storage_path",

                ""

            )


        return ""






    @property
    def knowledge_topic(self):


        if self.knowledge:


            return getattr(

                self.knowledge,

                "topic",

                ""

            )


        return ""







    # ==================================
    # Dictionary
    # ==================================


    def to_dict(self):


        return {


            "id":

            self.id,


            "document_id":

            self.document_id,


            "keyword":

            self.keyword,


            "title":

            self.title,


            "url":

            self.url,


            "source":

            self.source,


            "published":

            self.published,


            "content":

            self.content,


            "crawl_time":

            self.crawl_time,


            "status":

            self.status,


            # ======================
            # P2.2.5 Async AI
            # ======================


            "ai_status":

            self.ai_status,



            # ======================
            # V3 AI
            # ======================


            "ai_summary":

            self.ai_summary,


            "ai_category":

            self.ai_category,


            "ai_keywords":

            self.ai_keywords,


            "ai_importance":

            self.ai_importance,


            "ai_model":

            self.ai_model,


            "ai_version":

            self.ai_version,


            "ai_analyze_time":

            self.ai_analyze_time,


            "ai_confidence":

            self.ai_confidence,



            # ======================
            # V4 Archive
            # ======================


            "archive_path":

            self.archive_path,


            "knowledge_topic":

            self.knowledge_topic


        }






    def __repr__(self):


        return (

            f"Article("

            f"id={self.id}, "

            f"title={self.title}, "

            f"AI={self.ai_category}, "

            f"importance={self.ai_importance}, "

            f"status={self.ai_status}"

            ")"

        )