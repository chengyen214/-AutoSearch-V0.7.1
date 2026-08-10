"""
api/routes/intelligence.py

AutoSearch V4

P1.6 Step 6

Knowledge Intelligence API Router


功能:

1. Article Intelligence Query

2. Top Intelligence Ranking

3. High Quality Knowledge


"""


from fastapi import APIRouter, Query


from services.knowledge_intelligence_service import (
    KnowledgeIntelligenceService
)





router = APIRouter(

    prefix="/knowledge/intelligence",

    tags=["Knowledge Intelligence"]

)






service = KnowledgeIntelligenceService()







# ==================================================
# Article Intelligence
# ==================================================


@router.get(
    "/article/{article_id}"
)
def get_article_intelligence(


    article_id:int


):


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


    limit:int = 10


):


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


    score:float = Query(8.0)


):


    result = service.get_high_quality(


        score


    )



    return {


        "success": True,


        "score": score,


        "count": len(result),


        "data": result


    }