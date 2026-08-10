"""
api/routes/semantic_search.py

AutoSearch V4

P1.7 Step 4.4

Semantic Search API


Endpoint:

GET /semantic-search?q=keyword


Flow:

Query

 |

 v

SemanticSearchService

 |

 v

Semantic Result


"""


from fastapi import APIRouter, Query


from services.semantic_search_service import (
    SemanticSearchService
)


from utils.logger import logger




router = APIRouter(

    prefix="/knowledge/search",

    tags=["Semantic Search"]

)


service = SemanticSearchService()





# ==================================================
# Semantic Search
# ==================================================


@router.get(
    "/semantic-search"
)
def semantic_search(

    q: str = Query(

        ...,

        description="Semantic search keyword"

    )

):


    results = service.search(

        q

    )


    logger.info(

        f"Semantic Search API: {q}, count={len(results)}"

    )


    return {


        "success": True,


        "keyword": q,


        "count": len(results),


        "data": [

            {

                "knowledge":

                    item["knowledge"].to_dict(),



                "semantic_score":

                    item["semantic_score"]


            }

            for item in results

        ]


    }