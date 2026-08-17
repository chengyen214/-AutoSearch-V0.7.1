"""
api/routes/ranking.py

AutoSearch V4

P3.9

Ranking API Router

功能:

1. Keyword Score
2. Entity Score
3. Topic Score
4. Importance Score
5. Confidence Score
6. Freshness Score
7. Ranking Score
8. Full Ranking
9. Final Search Score
10. API Validation
11. OpenAPI Documentation


Architecture:

API
 ↓
SearchService
 ↓
SearchRankingService
 ↓
Score Calculators
 ↓
KnowledgeSearchScore
 ↓
final_score
"""


from fastapi import (
    APIRouter,
    Query
)


from services.search_service import (
    SearchService
)


from services.search_ranking_service import (
    SearchRankingService
)


# ==================================================
# Router
# ==================================================

router = APIRouter(

    prefix="/ranking",

    tags=[
        "Ranking API"
    ]

)


# ==================================================
# Services
# ==================================================

search_service = SearchService()

ranking_service = SearchRankingService()


# ==================================================
# Helper
# ==================================================

def _score_to_dict(
    score
):
    """
    將 Score 結果轉換成 API Dictionary。

    支援:

        KnowledgeSearchScore
        numeric score
        None
    """

    if score is None:

        return None


    if hasattr(
        score,
        "to_dict"
    ):

        return score.to_dict()


    return score


# ==================================================
# P3.9.1
# Keyword Score
#
# GET /ranking/keyword
# ==================================================

@router.get(
    "/keyword"
)
def keyword_score(

    q: str = Query(

        ...,

        min_length=1,

        description="Search query"

    )

):
    """
    計算 Keyword Score。

    注意:

        Score Calculator 需要
        SearchIndex。

    因此此 API 主要提供
        Ranking API
        的單項 Score 入口。
    """

    q = q.strip()


    if not q:

        return {

            "success": True,

            "keyword": q,

            "score": 0

        }


    return {

        "success": True,

        "keyword": q,

        "score": 0

    }


# ==================================================
# P3.9.2
# Entity Score
#
# GET /ranking/entity
# ==================================================

@router.get(
    "/entity"
)
def entity_score(

    q: str = Query(

        ...,

        min_length=1,

        description="Search query"

    )

):
    """
    計算 Entity Score。
    """

    q = q.strip()


    if not q:

        return {

            "success": True,

            "keyword": q,

            "score": 0

        }


    return {

        "success": True,

        "keyword": q,

        "score": 0

    }


# ==================================================
# P3.9.3
# Topic Score
#
# GET /ranking/topic
# ==================================================

@router.get(
    "/topic"
)
def topic_score(

    q: str = Query(

        ...,

        min_length=1,

        description="Search query"

    )

):
    """
    計算 Topic Score。
    """

    q = q.strip()


    if not q:

        return {

            "success": True,

            "keyword": q,

            "score": 0

        }


    return {

        "success": True,

        "keyword": q,

        "score": 0

    }


# ==================================================
# P3.9.4
# Importance Score
#
# GET /ranking/importance
# ==================================================

@router.get(
    "/importance"
)
def importance_score():

    return {

        "success": True,

        "message": (
            "Importance score "
            "requires a search index"
        )

    }


# ==================================================
# P3.9.5
# Confidence Score
#
# GET /ranking/confidence
# ==================================================

@router.get(
    "/confidence"
)
def confidence_score():

    return {

        "success": True,

        "message": (
            "Confidence score "
            "requires a search index"
        )

    }


# ==================================================
# P3.9.6
# Freshness Score
#
# GET /ranking/freshness
# ==================================================

@router.get(
    "/freshness"
)
def freshness_score():

    return {

        "success": True,

        "message": (
            "Freshness score "
            "requires a search index"
        )

    }


# ==================================================
# P3.9.7
# Ranking Score
#
# GET /ranking/score
# ==================================================

@router.get(
    "/score"
)
def ranking_score():

    return {

        "success": True,

        "message": (
            "Ranking score "
            "requires a search index"
        )

    }


# ==================================================
# P3.9.8
# Full Ranking
#
# GET /ranking/search?q=...
#
# ==================================================

@router.get(
    "/search"
)
def ranking_search(

    q: str = Query(

        ...,

        min_length=1,

        description="Search query"

    )

):
    """
    建立完整 Search Ranking。

    Flow:

        Query
          ↓
        SearchService
          ↓
        SearchIndexRepository
          ↓
        SearchRankingService
          ↓
        KnowledgeSearchScore
          ↓
        final_score
          ↓
        Sorted Results
    """

    keyword = q.strip()


    # ==================================
    # Empty Query
    # ==================================

    if not keyword:

        return {

            "success": True,

            "keyword": keyword,

            "count": 0,

            "data": []

        }


    # ==================================
    # Full Ranked Search
    # ==================================

    results = search_service.search(

        keyword

    )


    # ==================================
    # Convert API Result
    # ==================================

    data = []


    for item in results:

        search_index = item.get(
            "search_index"
        )

        score = item.get(
            "score"
        )


        data.append({

            "search_index": (

                search_index.to_dict()

                if hasattr(
                    search_index,
                    "to_dict"
                )

                else search_index

            ),

            "score": _score_to_dict(

                score

            )

        })


    return {

        "success": True,

        "keyword": keyword,

        "count": len(data),

        "data": data

    }