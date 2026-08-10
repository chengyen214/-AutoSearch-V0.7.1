"""
api/routes/archive_management.py

AutoSearch V4

P2.4.1 Management API Foundation

用途:

    提供 Knowledge Archive Management API。

功能:

    1. Archive Management Status
    2. Archive Statistics
    3. Archive Article Management
    4. Knowledge Management
    5. Search Index Management

架構:

    Management API
        ↓
    ArchiveWebService
        ↓
    Repository / Knowledge History
        ↓
    Database

注意:

    API Layer 不直接操作 Database。
"""

from fastapi import (
    APIRouter,
    HTTPException
)

from services.archive_web_service import (
    ArchiveWebService
)


# ============================================================
# Router
# ============================================================

router = APIRouter(

    prefix="/management/archive",

    tags=[
        "Archive Management"
    ]

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
# Management Status
# ============================================================

@router.get(
    "/status"
)
def management_status():
    """
    取得 Archive Management API 狀態。

    Example:

        GET /management/archive/status
    """

    return {

        "status":
            "ok",

        "service":
            "archive-management",

        "version":
            "V4-P2.4.1"

    }


# ============================================================
# Archive Statistics
# ============================================================

@router.get(
    "/statistics"
)
def get_management_statistics():
    """
    取得 Archive Management Statistics。

    Example:

        GET /management/archive/statistics
    """

    service = get_archive_service()

    return service.get_statistics()


# ============================================================
# Article Management
# ============================================================

@router.get(
    "/articles"
)
def get_management_articles():
    """
    取得 Archive Article Management 資料。

    Example:

        GET /management/archive/articles
    """

    service = get_archive_service()

    return service.get_articles()


# ============================================================
# Article Management By ID
# ============================================================

@router.get(
    "/articles/{article_id}"
)
def get_management_article(
    article_id: int
):
    """
    取得指定 Archive Article。

    Example:

        GET /management/archive/articles/1
    """

    service = get_archive_service()

    result = service.get_article(

        article_id

    )

    if result is None:

        raise HTTPException(

            status_code=404,

            detail="Archive article not found"

        )

    return result


# ============================================================
# Article Versions
# ============================================================

@router.get(
    "/articles/{article_id}/versions"
)
def get_management_article_versions(
    article_id: int
):
    """
    取得指定 Article 的 Archive Versions。

    Example:

        GET /management/archive/articles/1/versions
    """

    service = get_archive_service()

    return service.get_versions(

        article_id

    )


# ============================================================
# Knowledge Management
# ============================================================

@router.get(
    "/knowledge/{article_id}"
)
def get_management_knowledge(
    article_id: int
):
    """
    取得 Article Knowledge Management 資料。

    包含:

        Knowledge History
        Latest Knowledge
        Knowledge Evolution

    Example:

        GET /management/archive/knowledge/1
    """

    service = get_archive_service()

    history = service.get_knowledge_history(

        article_id

    )

    latest = service.get_latest_knowledge(

        article_id

    )

    evolution = service.get_knowledge_evolution(

        article_id

    )

    return {

        "article_id":
            article_id,

        "history":
            history,

        "latest":
            latest,

        "evolution":
            evolution

    }


# ============================================================
# Knowledge History
# ============================================================

@router.get(
    "/knowledge/{article_id}/history"
)
def get_management_knowledge_history(
    article_id: int
):
    """
    取得 Knowledge History。

    Example:

        GET /management/archive/knowledge/1/history
    """

    service = get_archive_service()

    return service.get_knowledge_history(

        article_id

    )


# ============================================================
# Knowledge Evolution
# ============================================================

@router.get(
    "/knowledge/{article_id}/evolution"
)
def get_management_knowledge_evolution(
    article_id: int
):
    """
    取得 Knowledge Evolution。

    Example:

        GET /management/archive/knowledge/1/evolution
    """

    service = get_archive_service()

    return service.get_knowledge_evolution(

        article_id

    )


# ============================================================
# Composite Archive Search
# ============================================================

@router.get(
    "/search"
)
def composite_archive_search(
    keyword: str = None,
    source: str = None,
    date_from: str = None,
    date_to: str = None,
    year: int = None,
    month: int = None,
    category: str = None,
    importance_min: float = None,
    importance_max: float = None,
    page: int = 1,
    page_size: int = 20
):
    """
    P2.4.2

    Composite Archive Search。

    支援：

        keyword
        source
        date_from
        date_to
        year
        month
        category
        importance_min
        importance_max

    Pagination:

        page
        page_size

    Example:

        GET /management/archive/search?keyword=TSMC

        GET /management/archive/search?keyword=TSMC&source=CNA

        GET /management/archive/search?
            keyword=TSMC&
            category=Semiconductor&
            importance_min=8

    API Layer 不直接操作 Database。
    """

    service = get_archive_service()

    return service.composite_search(

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

        page_size=page_size

    )



# ============================================================
# Search Index Management
# ============================================================

@router.get(
    "/index"
)
def get_index_management():
    """
    取得 Search Index Management 狀態。

    P2.4.1 Foundation 階段先提供基本狀態。

    Example:

        GET /management/archive/index
    """

    return {

        "status":
            "available",

        "service":
            "archive-search-index",

        "version":
            "V4-P2.4.1",

        "operations": [

            "status",

            "refresh",

            "rebuild"

        ]

    }


# ============================================================
# Management Health
# ============================================================

@router.get(
    "/health"
)
def management_health():
    """
    Archive Management Health Check。

    Example:

        GET /management/archive/health
    """

    return {

        "status":
            "ok",

        "service":
            "archive-management",

        "version":
            "V4-P2.4.1"

    }