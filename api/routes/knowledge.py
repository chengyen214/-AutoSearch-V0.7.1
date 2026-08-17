"""
api/routes/knowledge.py

AutoSearch V4

P3.6

Knowledge API Router


功能:

1. Article Knowledge Query
2. Topic Search
3. Entity Search
4. Relation Search
5. Full Knowledge Search
6. Latest Knowledge


Validation:

7. Empty Topic
8. Empty Entity
9. Empty Relation
10. Empty Search
11. Invalid Latest Limit


"""


from fastapi import (
    APIRouter,
    HTTPException,
    Query
)


from services.knowledge_service import (
    KnowledgeService
)





# ==================================================
# Router
# ==================================================


router = APIRouter(

    prefix="/knowledge",

    tags=[
        "Knowledge API"
    ]

)





# ==================================================
# Service
# ==================================================


service = KnowledgeService()





# ==================================================
# Article Knowledge
#
# GET
#
# /knowledge/article/{article_id}
#
# ==================================================


@router.get(
    "/article/{article_id}"
)
def get_article_knowledge(

    article_id: int

):


    result = service.get_by_article_id(

        article_id

    )


    return {

        "success": True,

        "data": result

    }





# ==================================================
# Topic Search
#
# GET
#
# /knowledge/topic/{keyword}
#
# Validation:
#
# Empty Topic -> 400
#
# ==================================================


@router.get(
    "/topic/{keyword}"
)
def search_topic(

    keyword: str

):


    keyword = keyword.strip()


    if not keyword:

        raise HTTPException(

            status_code=400,

            detail={

                "success": False,

                "message": (
                    "Topic cannot be empty"
                )

            }

        )


    result = service.search_topic(

        keyword

    )


    return {

        "success": True,

        "count": len(result),

        "data": result

    }





# ==================================================
# Entity Search
#
# GET
#
# /knowledge/entity/{keyword}
#
# Validation:
#
# Empty Entity -> 400
#
# ==================================================


@router.get(
    "/entity/{keyword}"
)
def search_entity(

    keyword: str

):


    keyword = keyword.strip()


    if not keyword:

        raise HTTPException(

            status_code=400,

            detail={

                "success": False,

                "message": (
                    "Entity cannot be empty"
                )

            }

        )


    result = service.search_entity(

        keyword

    )


    return {

        "success": True,

        "count": len(result),

        "data": result

    }





# ==================================================
# Relation Search
#
# GET
#
# /knowledge/relation/{keyword}
#
# Validation:
#
# Empty Relation -> 400
#
# ==================================================


@router.get(
    "/relation/{keyword}"
)
def search_relation(

    keyword: str

):


    keyword = keyword.strip()


    if not keyword:

        raise HTTPException(

            status_code=400,

            detail={

                "success": False,

                "message": (
                    "Relation cannot be empty"
                )

            }

        )


    result = service.search_relation(

        keyword

    )


    return {

        "success": True,

        "count": len(result),

        "data": result

    }





# ==================================================
# Full Knowledge Search
#
# GET
#
# /knowledge/search?q=keyword
#
# Validation:
#
# Empty Keyword -> 400
#
# ==================================================


@router.get(
    "/search"
)
def search_knowledge(

    q: str = Query(...)

):


    q = q.strip()


    if not q:

        raise HTTPException(

            status_code=400,

            detail={

                "success": False,

                "message": (
                    "Keyword cannot be empty"
                )

            }

        )


    result = service.search(

        q

    )


    return {

        "success": True,

        "keyword": q,

        "count": len(result),

        "data": result

    }





# ==================================================
# Latest Knowledge
#
# GET
#
# /knowledge/latest
#
# P3.6.6
#
# limit:
#
#     default = 20
#     minimum = 1
#     maximum = 100
#
# ==================================================


@router.get(
    "/latest"
)
def latest_knowledge(

    limit: int = Query(

        20,

        ge=1,

        le=100

    )

):


    result = service.latest(

        limit

    )


    return {

        "success": True,

        "count": len(result),

        "data": result

    }
