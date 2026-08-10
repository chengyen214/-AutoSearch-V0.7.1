"""
api/routes/knowledge.py

AutoSearch V4

P1.4 Step 3

Knowledge Retrieval API Router


功能:

1. Article Knowledge Query

2. Topic Search

3. Entity Search

4. Relation Search

5. Full Knowledge Search

6. Latest Knowledge


"""



from fastapi import APIRouter, Query


from services.knowledge_service import (
    KnowledgeService
)





router = APIRouter(

    prefix="/knowledge",

    tags=[
        "Knowledge API"
    ]

)





service = KnowledgeService()







# ==================================================
# Get Knowledge By Article
# ==================================================


@router.get(
    "/article/{article_id}"
)
def get_article_knowledge(

    article_id:int

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
# ==================================================


@router.get(
    "/topic/{keyword}"
)
def search_topic(

    keyword:str

):


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
# ==================================================


@router.get(
    "/entity/{keyword}"
)
def search_entity(

    keyword:str

):


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
# ==================================================


@router.get(
    "/relation/{keyword}"
)
def search_relation(

    keyword:str

):


    result = service.search_relation(

        keyword

    )


    return {

        "success": True,

        "count": len(result),

        "data": result

    }








# ==================================================
# Full Search
# ==================================================


@router.get(
    "/search"
)
def search_knowledge(

    q:str = Query(...)

):


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
# ==================================================


@router.get(
    "/latest"
)
def latest_knowledge(

    limit:int = 20

):


    result = service.latest(

        limit

    )


    return {

        "success": True,

        "count": len(result),

        "data": result

    }