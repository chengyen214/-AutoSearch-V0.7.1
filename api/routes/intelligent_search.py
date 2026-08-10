"""
api/routes/intelligent_search.py

AutoSearch V4

P1.7 Step 2

Knowledge Intelligent Search API


功能:

1. Keyword Intelligent Search

2. Ranking Result


"""


from fastapi import APIRouter, Query


from services.knowledge_intelligent_search_service import (
    KnowledgeIntelligentSearchService
)





router = APIRouter(

    prefix="/knowledge/search",

    tags=["Knowledge Search"]

)





service = KnowledgeIntelligentSearchService()







# ==================================================
# Intelligent Search
# ==================================================


@router.get("")
def intelligent_search(


    q: str = Query(...)

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