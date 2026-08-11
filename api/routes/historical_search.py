"""
api/routes/historical_search.py

AutoSearch V4

P2.3.5
P2.3.7
Historical Search API

用途:

    提供 Knowledge Archive Historical Search API。

支援:

    1. Historical Search
    2. Article Historical Search
    3. Version Search
    4. Source Search
    5. Date Range Search
    6. Article History
    7. Latest Version
    8. Historical Search Count

Architecture:

    Client
        ↓
    FastAPI
        ↓
    HistoricalSearchService
        ↓
    HistoricalSearchRepository
        ↓
    archive_versions
        ↓
    articles / raw_documents

注意:

    API Layer 不直接操作 Database。
"""

from fastapi import (
    APIRouter,
    HTTPException,
    Query
)

from services.historical_search_service import (
    HistoricalSearchService
)


# ============================================================
# Router
# ============================================================

router = APIRouter(
    prefix="/historical-search",
    tags=["Historical Search"]
)


# ============================================================
# Service
# ============================================================

_service = None


def get_historical_search_service():
    """
    取得 HistoricalSearchService。

    使用 Lazy Initialization，
    避免 API import 時立即建立 Repository。
    """

    global _service

    if _service is None:

        _service = HistoricalSearchService()

    return _service


# ============================================================
# Historical Search
# ============================================================

@router.get(
    ""
)
def historical_search(
    keyword: str | None = Query(
        None,
        min_length=1
    ),

    article_id: int | None = Query(
        None,
        ge=1
    ),

    source: str | None = Query(
        None,
        min_length=1
    ),

    start_date: str | None = Query(
        None
    ),

    end_date: str | None = Query(
        None
    ),

    version_number: int | None = Query(
        None,
        ge=1
    ),

    limit: int = Query(
        50,
        ge=1,
        le=1000
    ),

    offset: int = Query(
        0,
        ge=0
    )
):
    """
    Historical Archive Search。

    Endpoint:

        GET /historical-search

    支援:

        keyword
        article_id
        source
        start_date
        end_date
        version_number
        limit
        offset

    Examples:

        GET /historical-search

        GET /historical-search?keyword=TSMC

        GET /historical-search?article_id=10

        GET /historical-search?source=CNA

        GET /historical-search?start_date=2026-08-01
            &end_date=2026-08-11

        GET /historical-search?version_number=2

        GET /historical-search?
            keyword=TSMC
            &source=CNA
            &limit=20
            &offset=0
    """

    service = (
        get_historical_search_service()
    )

    # ========================================================
    # Validate Date Range
    # ========================================================

    if (
        start_date is not None
        and end_date is not None
        and start_date > end_date
    ):

        raise HTTPException(
            status_code=400,
            detail=(
                "start_date cannot be "
                "greater than end_date"
            )
        )

    # ========================================================
    # Search
    # ========================================================

    return service.search(

        keyword=keyword,

        article_id=article_id,

        source=source,

        start_date=start_date,

        end_date=end_date,

        version_number=version_number,

        limit=limit,

        offset=offset

    )


# ============================================================
# Search By Article
# ============================================================

@router.get(
    "/article/{article_id}"
)
def historical_search_by_article(
    article_id: int,
    keyword: str | None = Query(
        None,
        min_length=1
    ),
    limit: int = Query(
        50,
        ge=1,
        le=1000
    ),
    offset: int = Query(
        0,
        ge=0
    )
):
    """
    取得指定 Article 的歷史版本。

    Endpoint:

        GET /historical-search/article/{article_id}

    如果提供 keyword：

        搜尋指定 Article 的歷史資料。

    如果沒有 keyword：

        回傳 Article 所有歷史版本。
    """

    service = (
        get_historical_search_service()
    )

    result = service.search_by_article(

        article_id=article_id,

        keyword=keyword,

        limit=limit,

        offset=offset

    )

    return result


# ============================================================
# Article History
# ============================================================

@router.get(
    "/article/{article_id}/history"
)
def get_article_history(
    article_id: int
):
    """
    取得指定 Article 完整歷史版本。

    Endpoint:

        GET /historical-search/article/{article_id}/history
    """

    service = (
        get_historical_search_service()
    )

    result = service.get_history(
        article_id
    )

    return {
        "article_id": article_id,
        "count": len(result),
        "results": result
    }


# ============================================================
# Specific Version
# ============================================================

@router.get(
    "/article/{article_id}/version/{version_number}"
)
def get_historical_version(
    article_id: int,
    version_number: int
):
    """
    取得指定 Article 的指定歷史版本。

    Endpoint:

        GET
        /historical-search/article/10/version/2
    """

    service = (
        get_historical_search_service()
    )

    result = service.get_version(

        article_id=article_id,

        version_number=version_number

    )

    if result is None:

        raise HTTPException(
            status_code=404,
            detail=(
                "Historical version not found"
            )
        )

    return result


# ============================================================
# Latest Historical Version
# ============================================================

@router.get(
    "/article/{article_id}/latest"
)
def get_latest_historical_version(
    article_id: int
):
    """
    取得指定 Article 最新歷史版本。

    Endpoint:

        GET
        /historical-search/article/{article_id}/latest
    """

    service = (
        get_historical_search_service()
    )

    result = service.get_latest_version(
        article_id
    )

    if result is None:

        raise HTTPException(
            status_code=404,
            detail=(
                "Latest historical version "
                "not found"
            )
        )

    return result


# ============================================================
# Search By Source
# ============================================================

@router.get(
    "/source/{source}"
)
def historical_search_by_source(
    source: str,
    limit: int = Query(
        50,
        ge=1,
        le=1000
    ),
    offset: int = Query(
        0,
        ge=0
    )
):
    """
    依 Source 搜尋 Historical Archive。

    Endpoint:

        GET /historical-search/source/CNA
    """

    service = (
        get_historical_search_service()
    )

    return service.search_by_source(

        source=source,

        limit=limit,

        offset=offset

    )


# ============================================================
# Search By Date
# ============================================================

@router.get(
    "/date"
)
def historical_search_by_date(
    start_date: str = Query(
        ...,
        min_length=1
    ),

    end_date: str = Query(
        ...,
        min_length=1
    ),

    limit: int = Query(
        50,
        ge=1,
        le=1000
    ),

    offset: int = Query(
        0,
        ge=0
    )
):
    """
    依日期範圍搜尋 Historical Archive。

    Endpoint:

        GET /historical-search/date

    Example:

        /historical-search/date
        ?start_date=2026-08-01
        &end_date=2026-08-11
    """

    if start_date > end_date:

        raise HTTPException(
            status_code=400,
            detail=(
                "start_date cannot be "
                "greater than end_date"
            )
        )

    service = (
        get_historical_search_service()
    )

    return service.search_by_date(

        start_date=start_date,

        end_date=end_date,

        limit=limit,

        offset=offset

    )


# ============================================================
# Search By Version
# ============================================================

@router.get(
    "/version/{version_number}"
)
def historical_search_by_version(
    version_number: int,
    limit: int = Query(
        50,
        ge=1,
        le=1000
    ),
    offset: int = Query(
        0,
        ge=0
    )
):
    """
    搜尋指定 Version Number 的所有 Article。

    Endpoint:

        GET /historical-search/version/2
    """

    service = (
        get_historical_search_service()
    )

    return service.search_by_version(

        version_number=version_number,

        limit=limit,

        offset=offset

    )


# ============================================================
# Search Count
# ============================================================

@router.get(
    "/count"
)
def historical_search_count(
    keyword: str | None = Query(
        None,
        min_length=1
    ),

    article_id: int | None = Query(
        None,
        ge=1
    ),

    source: str | None = Query(
        None,
        min_length=1
    ),

    start_date: str | None = Query(
        None
    ),

    end_date: str | None = Query(
        None
    ),

    version_number: int | None = Query(
        None,
        ge=1
    )
):
    """
    計算 Historical Search 結果數量。

    Endpoint:

        GET /historical-search/count
    """

    if (
        start_date is not None
        and end_date is not None
        and start_date > end_date
    ):

        raise HTTPException(
            status_code=400,
            detail=(
                "start_date cannot be "
                "greater than end_date"
            )
        )

    service = (
        get_historical_search_service()
    )

    count = service.count(

        keyword=keyword,

        article_id=article_id,

        source=source,

        start_date=start_date,

        end_date=end_date,

        version_number=version_number

    )

    return {
        "count": count
    }


# ============================================================
# Health
# ============================================================

@router.get(
    "/health"
)
def historical_search_health():
    """
    Historical Search API Health Check。
    """

    return {
        "status": "ok",
        "service": "historical-search",
        "version": "V4-P2.3"
    }