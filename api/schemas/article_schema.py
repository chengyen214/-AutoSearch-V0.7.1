"""
article_schema.py

AutoSearch V3

API Response Schema

P3.8

用途:

    FastAPI Response Model

功能:

    1. Database Object -> API Response
    2. datetime 格式轉換
    3. ai_keywords JSON -> List
    4. 支援:
        - dict
        - SQLAlchemy ORM
        - SQLAlchemy Row
    5. Pydantic V2 Compatible

"""


from pydantic import BaseModel, Field, ConfigDict

from typing import List, Optional

import json






class ArticleResponse(BaseModel):


    # =========================
    # Database Fields
    # =========================


    id: int


    document_id: str


    keyword: Optional[str] = ""


    title: Optional[str] = ""


    url: Optional[str] = ""


    source: Optional[str] = ""



    published: Optional[str] = None


    content: Optional[str] = None


    crawl_time: Optional[str] = None


    status: Optional[str] = "Success"





    # =========================
    # AI Analysis
    # =========================


    ai_summary: str = ""


    ai_category: str = ""


    ai_keywords: List[str] = Field(

        default_factory=list

    )


    ai_importance: int = 0





    # Pydantic V2

    model_config = ConfigDict(

        from_attributes=True

    )







    # ==================================================
    # Database Convert
    #
    # 支援:
    #
    # dict
    # SQLAlchemy Row
    # ORM Object
    #
    # ==================================================


    @classmethod
    def from_db(
        cls,
        article
    ):


        # -------------------------
        # dict
        # -------------------------

        if isinstance(
            article,
            dict
        ):

            data = article.copy()



        # -------------------------
        # SQLAlchemy Row
        # -------------------------

        elif hasattr(
            article,
            "_mapping"
        ):

            data = dict(

                article._mapping

            )



        # -------------------------
        # SQLAlchemy ORM
        # -------------------------

        elif hasattr(
            article,
            "__dict__"
        ):

            data = article.__dict__.copy()



        else:

            raise TypeError(

                f"Unsupported type: {type(article)}"

            )







        # =========================
        # Remove SQLAlchemy State
        # =========================


        data.pop(

            "_sa_instance_state",

            None

        )







        # =========================
        # datetime convert
        # =========================


        for field in [

            "published",

            "crawl_time"

        ]:


            if data.get(field):

                data[field] = str(

                    data[field]

                )







        # =========================
        # ai_keywords
        # =========================


        keywords = data.get(

            "ai_keywords",

            []

        )



        if keywords is None:


            keywords = []



        elif isinstance(

            keywords,

            str

        ):


            try:

                keywords = json.loads(

                    keywords

                )


            except Exception:


                keywords = []





        # 保證一定是 list

        if not isinstance(

            keywords,

            list

        ):


            keywords = []



        data["ai_keywords"] = keywords







        # =========================
        # AI default
        # =========================


        data["ai_summary"] = (

            data.get(

                "ai_summary"

            )

            or ""

        )



        data["ai_category"] = (

            data.get(

                "ai_category"

            )

            or ""

        )



        data["ai_importance"] = int(

            data.get(

                "ai_importance",

                0

            )

            or 0

        )








        return cls(

            **data

        )