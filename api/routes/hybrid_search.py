"""
api/routes/hybrid_search.py

AutoSearch V4

P2.1 Step 3

Hybrid Search API


Endpoint:


GET /knowledge/search/hybrid?q=keyword



Flow:


Query

 |

 v


HybridSearchService

 |

 v


Hybrid Ranked Knowledge Result


"""


from fastapi import APIRouter, Query


from services.hybrid_search_service import (
    HybridSearchService
)


from utils.logger import logger





# ==================================
# Router
# ==================================


router = APIRouter(

    prefix="/knowledge/search",

    tags=[
        "Knowledge Search"
    ]

)







# ==================================
# Service
# ==================================


service = HybridSearchService()







# ==================================
# Hybrid Search API
# ==================================


@router.get(

    "/hybrid"

)

def hybrid_search(


    q: str = Query(

        ...,

        description="Search keyword"

    ),


    top_k: int = Query(

        10,

        ge=1,

        le=100,

        description="Maximum result count"

    )


):


    """
    
    Hybrid Search


    Combine:


    - Keyword Search

    - Semantic Search

    - Knowledge Ranking



    Example:


    GET

    /knowledge/search/hybrid?q=CoWoS



    """



    results = service.search(

        q,

        top_k

    )






    logger.info(

        f"Hybrid Search API: {q}, count={len(results)}"

    )






    return {


        "success": True,


        "keyword": q,


        "count": len(results),


        "top_k": top_k,


        "data": results


    }