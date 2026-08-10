"""
api/routes/knowledge_ranking.py

AutoSearch V4

P1.5 Step 5

Knowledge Ranking API Router


功能:

1. Top Ranking Knowledge

2. Score Filter


"""


from fastapi import APIRouter


from services.knowledge_ranking_service import (
    KnowledgeRankingService
)



router = APIRouter(

    prefix="/knowledge/ranking",

    tags=["Knowledge Ranking"]

)



service = KnowledgeRankingService()





# ==================================================
# Top Ranking
# ==================================================


@router.get(
    "/top"
)
def top_ranking(

    limit:int = 10

):


    result = service.get_top_ranking(

        limit

    )


    return {

        "success": True,

        "count": len(result),

        "data": result

    }








# ==================================================
# Score Filter
# ==================================================


@router.get(
    "/score/{score}"
)
def score_filter(

    score:float

):


    result = service.repository.find_by_score(

        score

    )


    return {

        "success": True,

        "score": score,

        "count": len(result),

        "data": result

    }