"""
api/routes/knowledge_ranking.py

AutoSearch V4

P3.7

Knowledge Ranking API Router


功能:

1. Top Ranking Knowledge

2. Score Filter

3. Ranking API Validation

4. OpenAPI Documentation


API:

GET /knowledge/ranking/top
GET /knowledge/ranking/score/{score}


Architecture:

API
 ↓
KnowledgeRankingService
 ↓
KnowledgeScoreRepository
 ↓
knowledge_scores


"""


from fastapi import (
    APIRouter,
    Query,
    Path
)


from services.knowledge_ranking_service import (
    KnowledgeRankingService
)





# ==================================================
# Router
# ==================================================


router = APIRouter(

    prefix="/knowledge/ranking",

    tags=[
        "Knowledge Ranking"
    ]

)





# ==================================================
# Service
# ==================================================


service = KnowledgeRankingService()





# ==================================================
# Top Ranking
#
# P3.7.1
#
# GET
#
# /knowledge/ranking/top
#
# Query:
#
# limit
#
# default = 10
# minimum = 1
# maximum = 100
#
# ==================================================


@router.get(
    "/top"
)
def top_ranking(

    limit: int = Query(

        10,

        ge=1,

        le=100,

        description=(
            "Maximum number of "
            "ranking results"
        )

    )

):


    result = service.get_top_ranking(

        limit

    )


    return {

        "success": True,

        "limit": limit,

        "count": len(result),

        "data": result

    }





# ==================================================
# Score Filter
#
# P3.7.2
#
# GET
#
# /knowledge/ranking/score/{score}
#
# score:
#
# ranking_score >= score
#
# ==================================================


@router.get(
    "/score/{score}"
)
def score_filter(

    score: float = Path(

        ...,

        ge=0,

        description=(
            "Minimum ranking score"
        )

    )

):


    result = service.find_by_score(

        score

    )


    return {

        "success": True,

        "score": score,

        "count": len(result),

        "data": result

    }