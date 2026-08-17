"""
api/routes/search.py

AutoSearch V4

P3.8

Search API Router

功能:

1. Full Search
2. Keyword Search
3. Entity Search
4. Hybrid Search
5. Search Pagination
6. Hybrid Search Pagination
7. Search Index Inspection

Architecture:

    Search API
        |
        v
    SearchService
        |
        +-----------------------------+
        |                             |
        v                             v
    SearchIndexRepository      SearchRankingService
        |                             |
        v                             v
    Search Candidates        KnowledgeSearchScore
                                      |
                                      v
                                Final Search Score
                                      |
                                      v
                                  Ranking
"""


from fastapi import (
    APIRouter,
    Query
)


from services.search_service import (
    SearchService
)


# ==================================================
# Router
# ==================================================

router = APIRouter(

    prefix="/search",

    tags=[
        "Search API"
    ]

)


# ==================================================
# Service
# ==================================================

service = SearchService()


# ==================================================
# Helper
# ==================================================

def _serialize(
    value
):
    """
    將 Model / Search Score
    轉換成 API 可輸出的資料。
    """

    if value is None:

        return None


    # ==================================
    # Model
    # ==================================

    if hasattr(
        value,
        "to_dict"
    ):

        return value.to_dict()


    # ==================================
    # List
    # ==================================

    if isinstance(
        value,
        list
    ):

        return [

            _serialize(
                item
            )

            for item in value

        ]


    # ==================================
    # Dictionary
    # ==================================

    if isinstance(
        value,
        dict
    ):

        return {

            key:
                _serialize(
                    item
                )

            for key, item in value.items()

        }


    return value


# ==================================================
# P3.8.1
# Full Search
# ==================================================

@router.get(
    ""
)
def search(
    q: str = Query(
        ...,
        min_length=1
    )
):
    """
    Full Knowledge Search。

    Flow:

        Query
          ↓
        Search Index
          ↓
        Search Ranking
          ↓
        Final Score
          ↓
        Sorted Result
    """

    result = service.search(
        q
    )

    return {

        "success": True,

        "keyword": q,

        "count": len(
            result
        ),

        "data": _serialize(
            result
        )

    }


# ==================================================
# P3.8.2
# Keyword Search
# ==================================================

@router.get(
    "/keyword/{keyword}"
)
def keyword_search(
    keyword: str
):
    """
    Keyword Search。

    搜尋:

        search_text
        keywords
    """

    result = service.search_keyword(
        keyword
    )

    return {

        "success": True,

        "keyword": keyword,

        "count": len(
            result
        ),

        "data": _serialize(
            result
        )

    }


# ==================================================
# P3.8.3
# Entity Search
# ==================================================

@router.get(
    "/entity/{entity}"
)
def entity_search(
    entity: str
):
    """
    Entity Search。
    """

    result = service.search_entity(
        entity
    )

    return {

        "success": True,

        "entity": entity,

        "count": len(
            result
        ),

        "data": _serialize(
            result
        )

    }


# ==================================================
# P3.8.4
# Hybrid Search
# ==================================================

@router.get(
    "/hybrid"
)
def hybrid_search(
    q: str = Query(
        ...,
        min_length=1
    )
):
    """
    Hybrid Search。

    Keyword
        +
    Entity
        ↓
    Merge
        ↓
    Ranking
        ↓
    Final Score
    """

    result = service.hybrid_search(
        q
    )

    return {

        "success": True,

        "keyword": q,

        "count": len(
            result
        ),

        "data": _serialize(
            result
        )

    }


# ==================================================
# P3.8.5
# Search Pagination
# ==================================================

@router.get(
    "/paginated"
)
def search_paginated(
    q: str = Query(
        ...,
        min_length=1
    ),
    page: int = Query(
        1,
        ge=1
    ),
    page_size: int = Query(
        20,
        ge=1,
        le=100
    )
):
    """
    Search + Ranking + Pagination。
    """

    result = service.search_paginated(

        q,

        page,

        page_size

    )

    return {

        "success": True,

        "keyword":
            result["query"],

        "page":
            result["page"],

        "page_size":
            result["page_size"],

        "count":
            result["count"],

        "total":
            result["total"],

        "data":
            _serialize(
                result["data"]
            )

    }


# ==================================================
# P3.8.6
# Hybrid Search Pagination
# ==================================================

@router.get(
    "/hybrid/paginated"
)
def hybrid_search_paginated(
    q: str = Query(
        ...,
        min_length=1
    ),
    page: int = Query(
        1,
        ge=1
    ),
    page_size: int = Query(
        20,
        ge=1,
        le=100
    )
):
    """
    Hybrid Search
    +
    Ranking
    +
    Pagination。
    """

    result = service.hybrid_search_paginated(

        q,

        page,

        page_size

    )

    return {

        "success": True,

        "keyword":
            result["query"],

        "page":
            result["page"],

        "page_size":
            result["page_size"],

        "count":
            result["count"],

        "total":
            result["total"],

        "data":
            _serialize(
                result["data"]
            )

    }


# ==================================================
# P3.8.7
# Search Index All
# ==================================================

@router.get(
    "/all"
)
def get_all_search_index():
    """
    取得所有 Search Index。

    用於:

        Management
        Debug
        Testing
    """

    result = service.get_all()

    return {

        "success": True,

        "count": len(
            result
        ),

        "data": _serialize(
            result
        )

    }