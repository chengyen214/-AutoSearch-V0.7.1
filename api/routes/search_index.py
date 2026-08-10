"""
api/routes/search_index.py

AutoSearch V4

P2.2 Step 6.2

Search Index API
"""


from fastapi import APIRouter, HTTPException


from services.search_index_service import (
    SearchIndexService
)


from database.knowledge_repository import (
    KnowledgeRepository
)


from models.knowledge import (
    Knowledge
)



router = APIRouter(

    prefix="/knowledge/search-index",

    tags=[
        "Search API"
    ]

)



service = SearchIndexService()


knowledge_repository = KnowledgeRepository()





# ==================================
# Build Knowledge Model
# ==================================

def build_knowledge_model(data):


    if not data:

        return None



    knowledge = Knowledge(

        article_id=data["article_id"],

        topic=data["topic"],

        entities=data["entities"],

        relations=data["relations"],

        knowledge_version=data["knowledge_version"]

    )


    # Search Index 需要 knowledge_id

    knowledge.id = data["id"]


    return knowledge







# ==================================
# Keyword Search
# ==================================


@router.get(
    "/keyword"
)
def keyword_search(
    q:str
):


    result = service.keyword_search(
        q
    )


    return {

        "success":True,

        "count":len(result),

        "data":result

    }







# ==================================
# Entity Search
# ==================================


@router.get(
    "/entity"
)
def entity_search(
    name:str
):


    result = service.entity_search(
        name
    )


    return {


        "success":True,


        "count":len(result),


        "data":result


    }







# ==================================
# Build Index
# ==================================


@router.post(
    "/build/{knowledge_id}"
)
def build_index(
    knowledge_id:int
):


    data = knowledge_repository.get_by_id(
        knowledge_id
    )


    if not data:

        raise HTTPException(

            status_code=404,

            detail="Knowledge not found"

        )



    knowledge = build_knowledge_model(
        data
    )


    result = service.build_index(
        knowledge
    )



    return {


        "success":True,


        "data":result


    }







# ==================================
# Rebuild Index
# ==================================


@router.post(
    "/rebuild/{knowledge_id}"
)
def rebuild_index(
    knowledge_id:int
):


    data = knowledge_repository.get_by_id(
        knowledge_id
    )


    if not data:

        raise HTTPException(

            status_code=404,

            detail="Knowledge not found"

        )



    knowledge = build_knowledge_model(
        data
    )



    result = service.rebuild_index(
        knowledge
    )



    return {


        "success":True,


        "data":result


    }








# ==================================
# Get Index
#
# 注意:
# 必須放最後
#
# ==================================


@router.get(
    "/{index_id}"
)
def get_index(
    index_id:int
):


    result = service.get_index(
        index_id
    )



    if not result:

        raise HTTPException(

            status_code=404,

            detail="Index not found"

        )



    return {


        "success":True,


        "data":result


    }