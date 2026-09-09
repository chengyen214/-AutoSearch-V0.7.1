"""
tests/test_api_main.py

AutoSearch V4

API Main Integration Test

測試:

1. FastAPI Application
2. API Root
3. Dashboard
4. Archive Search Web UI
5. OpenAPI
6. Router Registration
7. AI Analysis Router
8. Article Router
9. Knowledge Router
10. Ranking Router
11. Intelligence Router
12. Search Routers
13. Archive Routers
14. Historical Search Router
15. AI Task Router
"""

from fastapi.testclient import TestClient


from api.main import (
    app
)


# ==================================================
# Test Client
# ==================================================

client = TestClient(
    app
)


# ==================================================
# Application
# ==================================================

def test_app_exists():

    assert app is not None


def test_app_title():

    assert (
        app.title
        == "AutoSearch V4 API"
    )


def test_app_version():

    assert (
        app.version
        == "4.0"
    )


# ==================================================
# API Root
# ==================================================

def test_api_root():

    response = client.get(
        "/api"
    )

    assert (
        response.status_code
        == 200
    )

    data = response.json()

    assert data["project"] == (
        "AutoSearch V4"
    )

    assert data["version"] == (
        "4.0"
    )

    assert data["status"] == (
        "running"
    )


def test_api_root_modules():

    response = client.get(
        "/api"
    )

    assert (
        response.status_code
        == 200
    )

    data = response.json()

    modules = data["modules"]

    assert "Article API" in modules

    assert "AI Analysis" in modules

    assert "Knowledge Retrieval" in modules

    assert "Knowledge Ranking" in modules

    assert "Knowledge Intelligence" in modules

    assert "Intelligent Search" in modules

    assert "Semantic Search" in modules

    assert "Hybrid Search" in modules

    assert "Search Index" in modules

    assert "Knowledge Archive" in modules

    assert (
        "Knowledge Archive Management"
        in modules
    )

    assert "Historical Search" in modules

    assert "Composite Archive Search" in modules

    assert (
        "AI Task Management"
        in modules
    )


def test_api_root_links():

    response = client.get(
        "/api"
    )

    assert (
        response.status_code
        == 200
    )

    data = response.json()

    links = data["links"]

    assert links["dashboard"] == "/"

    assert links["docs"] == "/docs"

    assert links["archive"] == (
        "/archive/ui"
    )

    assert links["archive_search"] == (
        "/archive/search"
    )

    assert links["historical_search"] == (
        "/historical-search"
    )

    assert links["archive_management"] == (
        "/management/archive"
    )

    assert links["ai_tasks"] == (
        "/ai/tasks"
    )

    assert links["ai_analysis"] == (
        "/ai/analysis"
    )


# ==================================================
# Dashboard
# ==================================================

def test_dashboard():

    response = client.get(
        "/"
    )

    assert (
        response.status_code
        == 200
    )

    assert (
        "AutoSearch V4"
        in response.text
    )


# ==================================================
# Archive Search Web UI
# ==================================================

def test_archive_search_page():

    response = client.get(
        "/archive/search"
    )

    assert (
        response.status_code
        == 200
    )

    assert (
        "Composite Archive Search"
        in response.text
    )


# ==================================================
# OpenAPI
# ==================================================

def test_openapi_json():

    response = client.get(
        "/openapi.json"
    )

    assert (
        response.status_code
        == 200
    )

    data = response.json()

    assert (
        data["info"]["title"]
        == "AutoSearch V4 API"
    )

    assert (
        data["info"]["version"]
        == "4.0"
    )


def test_docs():

    response = client.get(
        "/docs"
    )

    assert (
        response.status_code
        == 200
    )


# ==================================================
# OpenAPI Tags
# ==================================================

def test_openapi_tags():

    response = client.get(
        "/openapi.json"
    )

    assert (
        response.status_code
        == 200
    )

    data = response.json()

    tags = data.get(
        "tags",
        []
    )

    tag_names = {

        tag["name"]

        for tag in tags

    }

    assert "Article API" in tag_names

    assert "AI Analysis" in tag_names

    assert "Knowledge API" in tag_names

    assert "Ranking API" in tag_names

    assert "Intelligence API" in tag_names

    assert "Search API" in tag_names

    assert "Search Index" in tag_names

    assert "Archive" in tag_names

    assert (
        "Archive Management"
        in tag_names
    )

    assert (
        "Historical Search"
        in tag_names
    )

    assert (
        "AI Task Management"
        in tag_names
    )

    assert "System" in tag_names


# ==================================================
# Router Registration Helper
# ==================================================

def _get_routes():

    """
    取得 FastAPI 最終註冊的 API Routes。

    FastAPI 0.141.1 + Starlette 1.3.x
    使用 include_router() 時，

        app.routes

    可能包含：

        _IncludedRouter

    而不是直接展開成 APIRoute。

    因此不能只使用：

        route.path

    取得完整 Router。

    OpenAPI schema 的 paths
    才是 FastAPI 最終建立的 API route mapping。

    回傳:

        set[str]

    Example:

        {
            "/articles",
            "/ai/analysis/{article_id}",
            "/knowledge/intelligence/article/{article_id}",
            "/knowledge/search",
            "/knowledge/search-index/keyword",
            ...
        }
    """

    openapi = app.openapi()

    return set(
        openapi.get(
            "paths",
            {}
        ).keys()
    )


# ==================================================
# Article Router
# ==================================================

def test_article_router_registered():

    routes = _get_routes()

    assert any(
        route.startswith(
            "/articles"
        )
        for route in routes
    )


# ==================================================
# AI Analysis Router
# ==================================================

def test_ai_analysis_router_registered():

    routes = _get_routes()

    assert any(
        route.startswith(
            "/ai/analysis"
        )
        for route in routes
    )


def test_ai_analysis_detail_route_registered():

    routes = _get_routes()

    assert (
        "/ai/analysis/{article_id}"
        in routes
    )


def test_ai_analysis_status_route_registered():

    routes = _get_routes()

    assert (
        "/ai/analysis/{article_id}/status"
        in routes
    )


def test_ai_analysis_importance_route_registered():

    routes = _get_routes()

    assert (
        "/ai/analysis/importance/{level}"
        in routes
    )


def test_ai_analysis_category_route_registered():

    routes = _get_routes()

    assert (
        "/ai/analysis/category/{category}"
        in routes
    )


def test_ai_analysis_keyword_route_registered():

    routes = _get_routes()

    assert (
        "/ai/analysis/keyword/{keyword}"
        in routes
    )


def test_ai_analysis_top_route_registered():

    routes = _get_routes()

    assert (
        "/ai/analysis/top"
        in routes
    )


# ==================================================
# Knowledge Router
# ==================================================

def test_knowledge_router_registered():

    routes = _get_routes()

    assert any(
        route.startswith(
            "/knowledge"
        )
        for route in routes
    )


# ==================================================
# Ranking Router
# ==================================================

def test_knowledge_ranking_router_registered():

    routes = _get_routes()

    assert any(
        (
            route.startswith(
                "/knowledge/ranking"
            )
            or
            route.startswith(
                "/ranking"
            )
        )
        for route in routes
    )


# ==================================================
# Intelligence Router
# ==================================================

def test_intelligence_router_registered():

    routes = _get_routes()

    assert any(
        route.startswith(
            "/knowledge/intelligence"
        )
        for route in routes
    )


def test_intelligence_article_route_registered():

    routes = _get_routes()

    assert (
        "/knowledge/intelligence/article/{article_id}"
        in routes
    )


def test_intelligence_top_route_registered():

    routes = _get_routes()

    assert (
        "/knowledge/intelligence/top"
        in routes
    )


def test_intelligence_high_quality_route_registered():

    routes = _get_routes()

    assert (
        "/knowledge/intelligence/high-quality"
        in routes
    )


# ==================================================
# Intelligent Search Router
# ==================================================

def test_intelligent_search_router_registered():

    routes = _get_routes()

    assert any(
        route.startswith(
            "/knowledge/search"
        )
        for route in routes
    )


def test_intelligent_search_route_registered():

    routes = _get_routes()

    assert (
        "/knowledge/search"
        in routes
    )


# ==================================================
# Semantic Search Router
# ==================================================

def test_semantic_search_router_registered():

    routes = _get_routes()

    assert any(
        (
            "semantic"
            in route.lower()
        )
        for route in routes
    )


# ==================================================
# Hybrid Search Router
# ==================================================

def test_hybrid_search_router_registered():

    routes = _get_routes()

    assert any(
        (
            "hybrid"
            in route.lower()
        )
        for route in routes
    )


# ==================================================
# Search Index Router
# ==================================================

def test_search_index_router_registered():

    routes = _get_routes()

    assert any(
        (
            "search-index"
            in route.lower()
        )
        for route in routes
    )


def test_search_index_keyword_route_registered():

    routes = _get_routes()

    assert (
        "/knowledge/search-index/keyword"
        in routes
    )


def test_search_index_entity_route_registered():

    routes = _get_routes()

    assert (
        "/knowledge/search-index/entity"
        in routes
    )


def test_search_index_build_route_registered():

    routes = _get_routes()

    assert (
        "/knowledge/search-index/build/{knowledge_id}"
        in routes
    )


def test_search_index_rebuild_route_registered():

    routes = _get_routes()

    assert (
        "/knowledge/search-index/rebuild/{knowledge_id}"
        in routes
    )


def test_search_index_get_route_registered():

    routes = _get_routes()

    assert (
        "/knowledge/search-index/{index_id}"
        in routes
    )


# ==================================================
# Archive Router
# ==================================================

def test_archive_router_registered():

    routes = _get_routes()

    assert any(
        route.startswith(
            "/archive"
        )
        for route in routes
    )


# ==================================================
# Archive Management Router
# ==================================================

def test_archive_management_router_registered():

    routes = _get_routes()

    assert any(
        (
            "management/archive"
            in route.lower()
        )
        for route in routes
    )


# ==================================================
# Historical Search Router
# ==================================================

def test_historical_search_router_registered():

    routes = _get_routes()

    assert any(
        (
            "historical"
            in route.lower()
        )
        for route in routes
    )


# ==================================================
# AI Task Router
# ==================================================

def test_ai_tasks_router_registered():

    routes = _get_routes()

    assert any(
        route.startswith(
            "/ai/tasks"
        )
        for route in routes
    )


# ==================================================
# Required API Routes
# ==================================================

def test_required_api_routes():

    routes = _get_routes()

    required_prefixes = [

        "/articles",

        "/ai/analysis",

        "/knowledge",

        "/archive",

        "/ai/tasks"

    ]

    for prefix in required_prefixes:

        assert any(
            route.startswith(
                prefix
            )
            for route in routes
        )


# ==================================================
# Required Search Routes
# ==================================================

def test_required_search_routes():

    routes = _get_routes()

    required_routes = [

        "/knowledge/search",

        "/knowledge/search-index/keyword",

        "/knowledge/search-index/entity",

        "/knowledge/search-index/build/{knowledge_id}",

        "/knowledge/search-index/rebuild/{knowledge_id}",

        "/knowledge/search-index/{index_id}"

    ]

    for route in required_routes:

        assert route in routes


# ==================================================
# Intelligence Routes
# ==================================================

def test_required_intelligence_routes():

    routes = _get_routes()

    required_routes = [

        "/knowledge/intelligence/article/{article_id}",

        "/knowledge/intelligence/top",

        "/knowledge/intelligence/high-quality"

    ]

    for route in required_routes:

        assert route in routes


# ==================================================
# AI Analysis OpenAPI Paths
# ==================================================

def test_ai_analysis_openapi_paths():

    response = client.get(
        "/openapi.json"
    )

    assert (
        response.status_code
        == 200
    )

    data = response.json()

    paths = data.get(
        "paths",
        {}
    )

    assert (
        "/ai/analysis/{article_id}"
        in paths
    )

    assert (
        "/ai/analysis/{article_id}/status"
        in paths
    )

    assert (
        "/ai/analysis/importance/{level}"
        in paths
    )

    assert (
        "/ai/analysis/category/{category}"
        in paths
    )

    assert (
        "/ai/analysis/keyword/{keyword}"
        in paths
    )

    assert (
        "/ai/analysis/top"
        in paths
    )


# ==================================================
# AI Analysis HTTP Methods
# ==================================================

def test_ai_analysis_http_methods():

    response = client.get(
        "/openapi.json"
    )

    assert (
        response.status_code
        == 200
    )

    paths = response.json()["paths"]

    assert "get" in paths[
        "/ai/analysis/{article_id}"
    ]

    assert "get" in paths[
        "/ai/analysis/{article_id}/status"
    ]

    assert "get" in paths[
        "/ai/analysis/importance/{level}"
    ]

    assert "get" in paths[
        "/ai/analysis/category/{category}"
    ]

    assert "get" in paths[
        "/ai/analysis/keyword/{keyword}"
    ]

    assert "get" in paths[
        "/ai/analysis/top"
    ]