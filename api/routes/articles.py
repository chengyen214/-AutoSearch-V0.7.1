"""
api/routes/articles.py

AutoSearch V3

P4.5.2

Article API Router


功能:

    FastAPI Article Retrieval API


支援:

    Article Query

    AI Retrieval


API:

    GET /articles/

    GET /articles/{id}

    GET /articles/keyword/{keyword}

    GET /articles/source/{source}


    GET /articles/ai/importance/{level}

    GET /articles/ai/category/{category}

    GET /articles/ai/keyword/{keyword}

    GET /articles/ai/top



"""



from fastapi import APIRouter, HTTPException


from services.article_service import ArticleService


from utils.logger import logger







# ==================================================
# Router
# ==================================================

router = APIRouter(
    
    prefix="/articles",

    tags=[
        "Article API"
    ]

)







# ==================================================
# Service
# ==================================================


service = ArticleService()







# ==================================================
# GET ALL
# ==================================================


@router.get("/")
def get_articles(
    limit: int = 20
):

    """
    取得文章列表


    Example:

        GET /articles/?limit=10


    """


    return service.get_all(

        limit

    )










# ==================================================
# GET BY ID
# ==================================================


@router.get(
    "/{article_id}"
)
def get_article_by_id(
    article_id: int
):


    """
    使用 ID 查詢文章
    """


    result = service.get_by_id(

        article_id

    )



    if result is None:


        raise HTTPException(

            status_code=404,

            detail="Article not found"

        )



    return result










# ==================================================
# SEARCH KEYWORD
# ==================================================


@router.get(
    "/search/keyword/{keyword}"
)
def search_keyword(
    keyword: str
):


    """
    搜尋文章 Keyword
    """


    return service.get_by_keyword(

        keyword

    )









# ==================================================
# SEARCH SOURCE
# ==================================================


@router.get(
    "/search/source/{source}"
)
def search_source(
    source: str
):


    """
    依來源查詢
    """


    return service.get_by_source(

        source

    )









# ==================================================
# AI IMPORTANCE
# ==================================================


@router.get(
    "/ai/importance/{level}"
)
def ai_importance(
    level: int
):


    """
    AI重要度查詢


    Example:


        /articles/ai/importance/8


    回傳:

        ai_importance >= 8


    """


    return service.get_by_importance(

        level

    )









# ==================================================
# AI CATEGORY
# ==================================================


@router.get(
    "/ai/category/{category}"
)
def ai_category(
    category: str
):


    """
    AI分類查詢


    Example:


        /articles/ai/category/Semiconductor


    """


    return service.get_by_category(

        category

    )









# ==================================================
# AI KEYWORD
# ==================================================


@router.get(
    "/ai/keyword/{keyword}"
)
def ai_keyword(
    keyword: str
):


    """
    AI Keyword Retrieval


    Example:


        /articles/ai/keyword/CoWoS


    """


    return service.get_by_ai_keyword(

        keyword

    )









# ==================================================
# AI TOP
# ==================================================


@router.get(
    "/ai/top"
)
def ai_top(
    limit: int = 10
):


    """
    AI Importance Ranking


    Example:


        /articles/ai/top?limit=5


    """


    return service.get_ai_top(

        limit

    )









# ==================================================
# Health Check
# ==================================================


@router.get(
    "/health/check"
)
def health_check():


    return {


        "status":

        "ok",


        "service":

        "AutoSearch V3 Article API"


    }