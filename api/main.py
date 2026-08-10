"""
api/main.py

AutoSearch V4

FastAPI API + Web UI Layer


功能:

V2.5:

    Article API


V3:

    AI Analysis Retrieval API


V4 P1:

    P1.4:
        Knowledge Retrieval API

    P1.5:
        Knowledge Ranking API

    P1.6:
        Knowledge Intelligence API

    P1.7:
        Intelligent Search API
        Semantic Search API


V4 P2:

    P2.1:
        Hybrid Search API

    P2.2:
        Search Index API

    P2.3:
        Knowledge Archive API
        Knowledge Archive Web UI

    P2.4.1:
        Knowledge Archive Management API

    P2.4.2:
        Composite Archive Search Service

    P2.4.3:
        Composite Archive Search Web UI


Web UI:

    /
        AutoSearch V4 Dashboard

    /archive/ui
        Knowledge Archive

    /archive/search
        Composite Archive Search


Swagger:

    /docs


Run:

    uvicorn api.main:app --reload

"""


from fastapi import (
    FastAPI,
    Request
)

from fastapi.templating import Jinja2Templates


# ==================================
# Templates
# ==================================

templates = Jinja2Templates(
    directory="templates"
)


# ==================================
# OpenAPI Tags
# ==================================

tags_metadata = [

    {
        "name": "Article API",
        "description":
            "文章資料與 AI 分析相關 API"
    },

    {
        "name": "Knowledge API",
        "description":
            "Knowledge Archive 查詢 API"
    },

    {
        "name": "Ranking API",
        "description":
            "Knowledge Ranking 與評分 API"
    },

    {
        "name": "Intelligence API",
        "description":
            "Knowledge Intelligence Service API"
    },

    {
        "name": "Search API",
        "description":
            "Keyword / Semantic / Hybrid Search API"
    },

    {
        "name": "Search Index",
        "description":
            "Search Index 建立、更新與查詢 API"
    },

    {
        "name": "Archive",
        "description":
            "Knowledge Archive API 與 Web UI"
    },

    {
        "name": "Archive Management",
        "description":
            "Knowledge Archive Management API"
    },

    {
        "name": "System",
        "description":
            "System Status API"
    }

]


# ==================================
# Routers
# ==================================

from api.routes import (

    articles,

    knowledge,

    knowledge_ranking,

    intelligence,

    intelligent_search,

    semantic_search,

    hybrid_search,

    search_index,

    archive,

    archive_management

)


# ==================================
# FastAPI Application
# ==================================

app = FastAPI(

    title="AutoSearch V4 API",

    version="4.0",

    openapi_tags=tags_metadata

)


# ==================================
# Web Dashboard
# ==================================

@app.get(
    "/",
    include_in_schema=False
)
def dashboard(
    request: Request
):
    """
    AutoSearch V4 Web Dashboard。

    Example:

        GET /

    功能:

        開啟 AutoSearch V4 主頁。
    """

    return templates.TemplateResponse(

        request=request,

        name="index.html",

        context={

            "project":
                "AutoSearch V4",

            "version":
                "4.0"

        }

    )


# ==================================
# P2.4.3
#
# Composite Archive Search Web UI
# ==================================

@app.get(
    "/archive/search",
    include_in_schema=False
)
def archive_search_page(
    request: Request
):
    """
    AutoSearch V4

    P2.4.3

    Composite Archive Search Web UI。

    Template:

        templates/archive/search.html
    """

    return templates.TemplateResponse(

        request=request,

        name="archive/search.html",

        context={

            "project":
                "AutoSearch V4",

            "version":
                "4.0",

            "page":
                "Composite Archive Search"

        }

    )


# ==================================
# API Root
# ==================================

@app.get(
    "/api",
    tags=[
        "System"
    ]
)
def api_root():
    """
    AutoSearch V4 API Root。
    """

    return {

        "project":
            "AutoSearch V4",

        "version":
            "4.0",

        "modules": [

            "Article API",

            "Knowledge Retrieval",

            "Knowledge Ranking",

            "Knowledge Intelligence",

            "Intelligent Search",

            "Semantic Search",

            "Hybrid Search",

            "Search Index",

            "Knowledge Archive",

            "Knowledge Archive Management",

            "Composite Archive Search"

        ],

        "links": {

            "dashboard":
                "/",

            "docs":
                "/docs",

            "archive":
                "/archive/ui",

            "archive_search":
                "/archive/search",

            "archive_management":
                "/management/archive"

        },

        "status":
            "running"

    }


# ==================================
# Router Register
# ==================================


# ----------------------------------
# V2.5 + V3
#
# Article API
# ----------------------------------

app.include_router(
    articles.router
)


# ----------------------------------
# V4 P1.4
#
# Knowledge Retrieval API
# ----------------------------------

app.include_router(
    knowledge.router
)


# ----------------------------------
# V4 P1.5
#
# Knowledge Ranking API
# ----------------------------------

app.include_router(
    knowledge_ranking.router
)


# ----------------------------------
# V4 P1.6
#
# Knowledge Intelligence API
# ----------------------------------

app.include_router(
    intelligence.router
)


# ----------------------------------
# V4 P1.7
#
# Intelligent Search API
# ----------------------------------

app.include_router(
    intelligent_search.router
)


# ----------------------------------
# V4 P1.7
#
# Semantic Search API
# ----------------------------------

app.include_router(
    semantic_search.router
)


# ----------------------------------
# V4 P2.1
#
# Hybrid Search API
# ----------------------------------

app.include_router(
    hybrid_search.router
)


# ----------------------------------
# V4 P2.2
#
# Search Index API
# ----------------------------------

app.include_router(
    search_index.router
)


# ----------------------------------
# V4 P2.3.9
#
# Knowledge Archive API
#
# Knowledge Archive Web UI
# ----------------------------------

app.include_router(
    archive.router
)


# ----------------------------------
# V4 P2.4.1
#
# Knowledge Archive Management API
# ----------------------------------

app.include_router(
    archive_management.router
)