"""
api/routes/intelligence.py

AutoSearch V4

P1.6 Step 6

Knowledge Intelligence API Router


功能:

1. Article Intelligence Query

2. Top Intelligence Ranking

3. High Quality Knowledge


Endpoints:

    GET /intelligence/article/{article_id}

    GET /intelligence/top

    GET /intelligence/high-quality?score=8
"""


from fastapi import (
    APIRouter,
    Query
)


from services.knowledge_intelligence_service import (
    KnowledgeIntelligenceService
)





# ==================================================
# Router
# ==================================================

router = APIRouter(

    prefix="/knowledge/intelligence",

    tags=["Intelligence API"]

)





# ==================================================
# Service
# ==================================================

service = KnowledgeIntelligenceService()





# ==================================================
# Article Intelligence
# ==================================================

@router.get(
    "/article/{article_id}"
)
def get_article_intelligence(

    article_id: int

):
    """
    取得指定 Article 的 Knowledge Intelligence。

    GET:

        /intelligence/article/{article_id}
    """

    result = service.get_knowledge(

        article_id

    )


    return {

        "success": True,

        "data": result

    }





# ==================================================
# Top Intelligence
# ==================================================

@router.get(
    "/top"
)
def get_top_intelligence(

    limit: int = Query(
        10,
        ge=1
    )

):
    """
    取得最高 Intelligence Ranking。

    GET:

        /intelligence/top

    Query:

        limit
    """

    result = service.get_top_intelligence(

        limit

    )


    return {

        "success": True,

        "count": len(result),

        "data": result

    }





# ==================================================
# High Quality Knowledge
# ==================================================

@router.get(
    "/high-quality"
)
def get_high_quality(

    score: float = Query(
        8.0,
        ge=0
    )

):
    """
    取得高品質 Knowledge。

    GET:

        /intelligence/high-quality?score=8
    """

    result = service.get_high_quality(

        score

    )


    return {

        "success": True,

        "score": score,

        "count": len(result),

        "data": result

    }
