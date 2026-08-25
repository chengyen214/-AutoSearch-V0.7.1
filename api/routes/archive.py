"""
api/routes/archive.py

AutoSearch V4

P2.3.9 API/UI Integration
P2.4.2 Composite Archive Search API
P2.4.3 Composite Search Web UI

用途:

    提供 Knowledge Archive Web API
    提供 Knowledge Archive Web UI
    提供 Composite Archive Search API
    提供 Composite Archive Search Web UI

架構:

    Browser
        ↓
    Archive Web UI
        ↓
    FastAPI
        ↓
    Archive API
        ↓
    ArchiveWebService
        ↓
    Repository / Knowledge History
        ↓
    Database

注意:

    API Layer 不直接操作 Database。

路由:

    GET /archive/ui
        Knowledge Archive Web UI

    GET /archive/search/ui
        Composite Archive Search Web UI

    GET /archive/search
        Basic Archive Search API

    GET /archive/search/api
        Composite Archive Search API
"""

from fastapi import (
    APIRouter,
    HTTPException,
    Query,
    Request,
)

from fastapi.templating import Jinja2Templates

from services.archive_web_service import (
    ArchiveWebService,
)


# ============================================================
# Router
# ============================================================

router = APIRouter(
    prefix="/archive",
    tags=["Archive"],
)


# ============================================================
# Templates
# ============================================================

templates = Jinja2Templates(
    directory="templates",
)


# ============================================================
# Service
# ============================================================

_service = None


def get_archive_service():
    """
    取得 ArchiveWebService。

    使用 Lazy Initialization，
    避免 API import 時立即建立 Repository。
    """

    global _service

    if _service is None:
        _service = ArchiveWebService()

    return _service


# ============================================================
# Archive Web UI
# ============================================================

@router.get(
    "/ui",
    include_in_schema=False,
)
def archive_ui(
    request: Request,
):
    """
    Knowledge Archive Web UI。

    GET /archive/ui
    """

    service = get_archive_service()

    statistics = service.get_statistics()

    articles = service.get_articles(
        limit=20,
    )

    return templates.TemplateResponse(
        request=request,
        name="archive/index.html",
        context={
            "statistics": statistics,
            "articles": articles,
            "version": "V4-P2.4.3",
        },
    )


# ============================================================
# Composite Archive Search Web UI
# ============================================================

@router.get(
    "/search/ui",
    include_in_schema=False,
)
def search_ui(
    request: Request,
):
    """
    P2.4.3

    Composite Archive Search Web UI。

    GET /archive/search/ui

    Composite Search API:

        GET /archive/search/api
    """

    return templates.TemplateResponse(
        request=request,
        name="archive/search.html",
        context={
            "project": "AutoSearch V4",
            "version": "4.0",
            "page": "Composite Archive Search",
        },
    )


# ============================================================
# Article List
# ============================================================

@router.get(
    "/articles",
)
def get_articles(
    limit: int = Query(
        100,
        ge=1,
        le=1000,
    ),
):
    """
    取得 Archive Article。

    GET /archive/articles
    """

    service = get_archive_service()

    return service.get_articles(
        limit=limit,
    )


# ============================================================
# Pagination
# ============================================================

@router.get(
    "/articles/page",
)
def get_articles_with_pagination(
    page: int = Query(
        1,
        ge=1,
    ),
    page_size: int = Query(
        20,
        ge=1,
        le=100,
    ),
):
    """
    分頁取得 Archive Articles。

    GET /archive/articles/page
    """

    service = get_archive_service()

    return service.get_articles_with_pagination(
        page=page,
        page_size=page_size,
    )


# ============================================================
# Article Versions
# ============================================================

@router.get(
    "/articles/{article_id}/versions",
)
def get_versions(
    article_id: int,
):
    """
    取得 Article 所有 Archive Versions。
    """

    service = get_archive_service()

    return service.get_versions(
        article_id,
    )


# ============================================================
# Latest Version
# ============================================================

@router.get(
    "/articles/{article_id}/versions/latest",
)
def get_latest_version(
    article_id: int,
):
    """
    取得 Article 最新 Version。
    """

    service = get_archive_service()

    result = service.get_latest_version(
        article_id,
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Latest archive version not found",
        )

    return result


# ============================================================
# Article
# ============================================================

@router.get(
    "/articles/{article_id}",
)
def get_article(
    article_id: int,
):
    """
    取得指定 Article。
    """

    service = get_archive_service()

    result = service.get_article(
        article_id,
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Archive article not found",
        )

    return result


# ============================================================
# Archive By Date
# ============================================================

@router.get(
    "/date/{archive_date}",
)
def get_by_date(
    archive_date: str,
):
    """
    依日期取得 Archive。
    """

    service = get_archive_service()

    return service.get_by_date(
        archive_date,
    )


# ============================================================
# Archive By Month
# ============================================================

@router.get(
    "/month/{year}/{month}",
)
def get_by_month(
    year: int,
    month: int,
):
    """
    依月份取得 Archive。
    """

    if month < 1 or month > 12:
        raise HTTPException(
            status_code=400,
            detail="Month must be between 1 and 12",
        )

    service = get_archive_service()

    return service.get_by_month(
        year,
        month,
    )


# ============================================================
# Archive By Year
# ============================================================

@router.get(
    "/year/{year}",
)
def get_by_year(
    year: int,
):
    """
    依年份取得 Archive。
    """

    service = get_archive_service()

    return service.get_by_year(
        year,
    )


# ============================================================
# Archive By Source
# ============================================================

@router.get(
    "/source/{source}",
)
def get_by_source(
    source: str,
):
    """
    依來源取得 Archive。
    """

    service = get_archive_service()

    return service.get_by_source(
        source,
    )


# ============================================================
# Basic Archive Search API
# ============================================================

@router.get(
    "/search",
)
def search_archive(
    q: str = Query(
        ...,
        min_length=1,
    ),
):
    """
    Archive 基本搜尋。

    GET /archive/search?q=TSMC

    回傳 JSON。

    注意:

        /archive/search 是 JSON API。

        Composite Search Web UI:
            /archive/search/ui

        Composite Search API:
            /archive/search/api
    """

    service = get_archive_service()

    return service.search(
        q,
    )


# ============================================================
# P2.4.2
#
# Composite Archive Search API
# ============================================================

@router.get(
    "/search/api",
)
def composite_search(
    keyword: str | None = Query(
        None,
    ),
    source: str | None = Query(
        None,
    ),
    date_from: str | None = Query(
        None,
    ),
    date_to: str | None = Query(
        None,
    ),
    year: int | None = Query(
        None,
    ),
    month: int | None = Query(
        None,
        ge=1,
        le=12,
    ),
    category: str | None = Query(
        None,
    ),
    importance_min: float | None = Query(
        None,
        ge=0,
        le=10,
    ),
    importance_max: float | None = Query(
        None,
        ge=0,
        le=10,
    ),
    page: int = Query(
        1,
        ge=1,
    ),
    page_size: int = Query(
        20,
        ge=1,
        le=100,
    ),
):
    """
    P2.4.2

    Composite Archive Search API。

    Endpoint:

        GET /archive/search/api
    """

    service = get_archive_service()

    # --------------------------------------------------------
    # Validate Importance Range
    # --------------------------------------------------------

    if (
        importance_min is not None
        and importance_max is not None
        and importance_min > importance_max
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                "importance_min cannot be "
                "greater than importance_max"
            ),
        )

    # --------------------------------------------------------
    # Validate Date Range
    # --------------------------------------------------------

    if (
        date_from is not None
        and date_to is not None
        and date_from > date_to
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                "date_from cannot be "
                "greater than date_to"
            ),
        )

    # --------------------------------------------------------
    # Composite Search
    # --------------------------------------------------------

    result = service.composite_search(
        keyword=keyword,
        source=source,
        date_from=date_from,
        date_to=date_to,
        year=year,
        month=month,
        category=category,
        importance_min=importance_min,
        importance_max=importance_max,
        page=page,
        page_size=page_size,
    )

    # --------------------------------------------------------
    # Normalize API Response
    # --------------------------------------------------------

    if result is None:
        return {
            "results": [],
            "total": 0,
            "page": page,
            "page_size": page_size,
            "filters": {
                "keyword": keyword,
                "source": source,
                "date_from": date_from,
                "date_to": date_to,
                "year": year,
                "month": month,
                "category": category,
                "importance_min": importance_min,
                "importance_max": importance_max,
            },
        }

    return result


# ============================================================
# Archive Count
# ============================================================

@router.get(
    "/count",
)
def count_archive():
    """
    取得 Archive 數量。
    """

    service = get_archive_service()

    return {
        "count": service.count(),
    }


# ============================================================
# Article Count
# ============================================================

@router.get(
    "/count/articles",
)
def count_articles():
    """
    取得 Article 數量。
    """

    service = get_archive_service()

    return {
        "count": service.count_articles(),
    }


# ============================================================
# Count By Source
# ============================================================

@router.get(
    "/count/source/{source}",
)
def count_by_source(
    source: str,
):
    """
    取得指定 Source 的 Archive 數量。
    """

    service = get_archive_service()

    return {
        "source": source,
        "count": service.count_by_source(
            source,
        ),
    }


# ============================================================
# Count By Date
# ============================================================

@router.get(
    "/count/date/{archive_date}",
)
def count_by_date(
    archive_date: str,
):
    """
    取得指定日期的 Archive 數量。
    """

    service = get_archive_service()

    return {
        "date": archive_date,
        "count": service.count_by_date(
            archive_date,
        ),
    }


# ============================================================
# Statistics
# ============================================================

@router.get(
    "/statistics",
)
def get_statistics():
    """
    取得 Archive Statistics。
    """

    service = get_archive_service()

    return service.get_statistics()


# ============================================================
# Knowledge History
# ============================================================

@router.get(
    "/knowledge/{article_id}/history",
)
def get_knowledge_history(
    article_id: int,
):
    """
    取得 Article Knowledge History。
    """

    service = get_archive_service()

    return service.get_knowledge_history(
        article_id,
    )


# ============================================================
# Latest Knowledge
# ============================================================

@router.get(
    "/knowledge/{article_id}/latest",
)
def get_latest_knowledge(
    article_id: int,
):
    """
    取得 Article 最新 Knowledge。
    """

    service = get_archive_service()

    result = service.get_latest_knowledge(
        article_id,
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Knowledge not found",
        )

    return result


# ============================================================
# Knowledge Evolution
# ============================================================

@router.get(
    "/knowledge/{article_id}/evolution",
)
def get_knowledge_evolution(
    article_id: int,
):
    """
    取得完整 Knowledge Evolution。
    """

    service = get_archive_service()

    return service.get_knowledge_evolution(
        article_id,
    )


# ============================================================
# Health
# ============================================================

@router.get(
    "/health",
)
def archive_health():
    """
    Archive API Health Check。
    """

    return {
        "status": "ok",
        "service": "archive",
        "version": "V4-P2.4.3",
    }