"""
api/routes/ai_analysis.py

AutoSearch V4

P3.5

AI Analysis API

功能:

1. AI Analysis Detail
2. AI Analysis Status
3. AI Analysis by Importance
4. AI Analysis by Category
5. AI Analysis by Keyword
6. AI Top Articles

P3.5.1:
    AI Analysis Detail API

P3.5.2:
    AI Analysis Status API

P3.5.3:
    AI Analysis Importance API

P3.5.4:
    AI Analysis Category API

P3.5.5:
    AI Analysis Keyword API

P3.5.6:
    AI Top Articles API


資料來源:

    articles

AI Analysis 欄位:

    ai_summary
    ai_category
    ai_keywords
    ai_importance
    ai_model
    ai_version
    ai_analyze_time
    ai_confidence
    ai_status
"""


import json


from fastapi import (
    APIRouter,
    Query,
    HTTPException
)


from database.article_repository import (
    ArticleRepository
)


# ==================================================
# Router
# ==================================================

router = APIRouter(

    prefix="/ai/analysis",

    tags=[
        "AI Analysis"
    ]

)


# ==================================================
# Repository
# ==================================================

repository = ArticleRepository()


# ==================================================
# Helper
# ==================================================

def _article_to_ai_analysis(
    article
):
    """
    將 Article Database Row
    轉換成 AI Analysis API Response。

    ArticleRepository.find_by_id()
    等方法目前回傳 dictionary。

    因此這裡直接使用 dict.get()。

    不直接暴露完整 Article。
    """

    if article is None:

        return None

    # ----------------------------------------------
    # AI Keywords
    # ----------------------------------------------

    keywords = article.get(
        "ai_keywords",
        []
    )

    if isinstance(
        keywords,
        str
    ):

        try:

            keywords = json.loads(
                keywords
            )

        except (
            json.JSONDecodeError,
            TypeError
        ):

            keywords = []

    if keywords is None:

        keywords = []

    # ----------------------------------------------
    # Response
    # ----------------------------------------------

    return {

        "article_id":
            article.get(
                "id"
            ),

        "summary":
            article.get(
                "ai_summary"
            ),

        "category":
            article.get(
                "ai_category"
            ),

        "keywords":
            keywords,

        "importance":
            article.get(
                "ai_importance"
            ),

        "model":
            article.get(
                "ai_model"
            ),

        "version":
            article.get(
                "ai_version"
            ),

        "analyze_time":
            article.get(
                "ai_analyze_time"
            ),

        "confidence":
            article.get(
                "ai_confidence"
            ),

        "status":
            article.get(
                "ai_status"
            )

    }


# ==================================================
# AI Analysis Status
# ==================================================

@router.get(
    "/{article_id}/status"
)
def get_ai_analysis_status(
    article_id: int
):
    """
    取得指定 Article 的 AI Analysis Status。

    GET /ai/analysis/{article_id}/status
    """

    article = (
        repository
        .find_by_id(
            article_id
        )
    )

    if article is None:

        raise HTTPException(

            status_code=404,

            detail={
                "success": False,
                "message": "Article not found"
            }

        )

    return {

        "success":
            True,

        "article_id":
            article_id,

        "status":
            article.get(
                "ai_status"
            ),

        "analyze_time":
            article.get(
                "ai_analyze_time"
            )

    }


# ==================================================
# AI Analysis by Importance
# ==================================================

@router.get(
    "/importance/{level}"
)
def get_ai_analysis_by_importance(
    level: int
):
    """
    取得指定 Importance 以上的文章。

    GET /ai/analysis/importance/{level}

    Example:

        GET /ai/analysis/importance/8
    """

    if level < 0 or level > 10:

        raise HTTPException(

            status_code=400,

            detail={
                "success": False,
                "message":
                    "Importance level must be between 0 and 10"
            }

        )

    articles = (
        repository
        .find_by_importance(
            level
        )
    )

    data = [

        _article_to_ai_analysis(
            article
        )

        for article in articles

    ]

    return {

        "success":
            True,

        "level":
            level,

        "count":
            len(data),

        "data":
            data

    }


# ==================================================
# AI Analysis by Category
# ==================================================

@router.get(
    "/category/{category}"
)
def get_ai_analysis_by_category(
    category: str
):
    """
    依 AI Category 查詢。

    GET /ai/analysis/category/{category}

    Example:

        GET /ai/analysis/category/AI
    """

    if not category.strip():

        raise HTTPException(

            status_code=400,

            detail={
                "success": False,
                "message":
                    "Category cannot be empty"
            }

        )

    articles = (
        repository
        .find_by_category(
            category
        )
    )

    data = [

        _article_to_ai_analysis(
            article
        )

        for article in articles

    ]

    return {

        "success":
            True,

        "category":
            category,

        "count":
            len(data),

        "data":
            data

    }


# ==================================================
# AI Analysis by Keyword
# ==================================================

@router.get(
    "/keyword/{keyword}"
)
def get_ai_analysis_by_keyword(
    keyword: str
):
    """
    依 AI Keyword 查詢。

    GET /ai/analysis/keyword/{keyword}

    Example:

        GET /ai/analysis/keyword/NVIDIA
    """

    if not keyword.strip():

        raise HTTPException(

            status_code=400,

            detail={
                "success": False,
                "message":
                    "Keyword cannot be empty"
            }

        )

    articles = (
        repository
        .find_by_ai_keyword(
            keyword
        )
    )

    data = [

        _article_to_ai_analysis(
            article
        )

        for article in articles

    ]

    return {

        "success":
            True,

        "keyword":
            keyword,

        "count":
            len(data),

        "data":
            data

    }


# ==================================================
# AI Top Articles
# ==================================================

@router.get(
    "/top"
)
def get_top_ai_analysis(

    limit: int = Query(

        10,

        ge=1,

        le=100

    )

):
    """
    取得 AI Importance 最高的文章。

    GET /ai/analysis/top

    Parameters:

        limit:
            最大回傳數量。
    """

    articles = (
        repository
        .get_top_ai_articles(
            limit=limit
        )
    )

    data = [

        _article_to_ai_analysis(
            article
        )

        for article in articles

    ]

    return {

        "success":
            True,

        "count":
            len(data),

        "limit":
            limit,

        "data":
            data

    }


# ==================================================
# AI Analysis Detail
# ==================================================

@router.get(
    "/{article_id}"
)
def get_ai_analysis(
    article_id: int
):
    """
    取得指定 Article 的 AI Analysis。

    GET /ai/analysis/{article_id}
    """

    article = (
        repository
        .find_by_id(
            article_id
        )
    )

    if article is None:

        raise HTTPException(

            status_code=404,

            detail={
                "success": False,
                "message": "Article not found"
            }

        )

    analysis = (
        _article_to_ai_analysis(
            article
        )
    )

    return {

        "success":
            True,

        "data":
            analysis

    }