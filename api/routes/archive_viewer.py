"""
api/routes/archive_viewer.py

AutoSearch V5

Archive Viewer

用途：

    提供獨立的 Archive Article Viewer。

核心設計：

    Search UI
        |
        | 點擊文章標題
        v
    /archive/view?url=...
        |
        v
    MongoDB
        |
        v
    raw_html collection
        |
        +-----------------------------+
        |                             |
        v                             v
    Snapshot History              HTML = None
        |                             |
        v                             v
    viewer.html

使用者選擇 Snapshot：

    /archive/view?
        url=...
        &version=2026-08-29T14:20:00Z
        |
        v
    viewer.html
        |
        v
    iframe
        |
        v
    /archive/snapshot?
        url=...
        &version=...
        |
        v
    MongoDB raw_html
        |
        v
    Raw HTML Response
        |
        v
    Browser Render

重要設計：

    1. 本 Router 不使用 api/routes/archive.py。

    2. 本 Router 不使用 ArchiveWebService。

    3. 本 Router 不使用 ArchiveViewerService。

    4. 本 Router 不使用 RawHTMLRepository。

    5. 本 Router 直接使用 MongoDB。

    6. Snapshot Identity：

           URL
           +
           created_at

    7. version 不代表：

           1
           2
           3

       version 代表：

           created_at

    8. 初次進入：

           /archive/view?url=...

       只查詢 Snapshot History。

       不載入 HTML。

    9. 指定版本：

           /archive/view?
               url=...
               &version=2026-08-29T14:20:00Z

       Viewer UI 載入後，
       iframe 再向：

           /archive/snapshot

       取得 MongoDB 中的 Raw HTML。

    10. /archive/snapshot：

           不使用 srcdoc。

           直接：

               MongoDB
                   ↓
               Raw HTML
                   ↓
               HTTP text/html
                   ↓
               Browser Render

    11. 為了讓原網站 HTML 中的相對資源：

           /images/...
           images/...
           ../images/...
           css/...
           js/...

       維持原本網站的 URL 基準，

       /archive/snapshot 會在 HTML <head>
       中補入：

           <base href="原始 URL">

    12. MongoDB Snapshot 本身不修改。

MongoDB：

    Database:
        autosearch

    Collection:
        raw_html

MongoDB Configuration：

    使用：

        config.mongo_config.MONGO_URI
        config.mongo_config.MONGO_DATABASE
        config.mongo_config.MONGO_RAW_HTML_COLLECTION


不負責：

    - Crawl
    - HTTP Download
    - Parser
    - Article
    - AI
    - Knowledge Archive
    - Archive Version Creation
    - Search
    - Search Ranking
    - archive.py
    - RawHTMLRepository
"""


# ============================================================
#
# Standard Library
#
# ============================================================

from datetime import (
    datetime,
    timezone,
)

from html import (
    escape,
)

from typing import (
    Any,
    Optional,
)


# ============================================================
#
# Third Party
#
# ============================================================

from fastapi import (
    APIRouter,
    HTTPException,
    Query,
    Request,
)

from fastapi.responses import (
    Response,
)

from fastapi.templating import (
    Jinja2Templates,
)

from pymongo import (
    MongoClient,
)


# ============================================================
#
# Project
#
# ============================================================

from config.mongo_config import (
    MONGO_URI,
    MONGO_DATABASE,
    MONGO_RAW_HTML_COLLECTION,
)

from utils.logger import (
    logger,
)


# ============================================================
#
# Router
#
# ============================================================

router = APIRouter(
    prefix="/archive",
    tags=["Archive Viewer"],
)


# ============================================================
#
# Templates
#
# ============================================================

templates = Jinja2Templates(
    directory="templates",
)


# ============================================================
#
# MongoDB
#
# ============================================================

_client: Optional[MongoClient] = None


def get_mongo_collection():
    """
    取得 MongoDB Raw HTML Collection。

    使用 Lazy Initialization。

    Configuration：

        MONGO_URI
        MONGO_DATABASE
        MONGO_RAW_HTML_COLLECTION

    Returns
    -------
    Collection

        MongoDB raw_html collection。
    """

    global _client

    # ========================================================
    # Validate Configuration
    # ========================================================

    if not MONGO_URI:

        raise RuntimeError(
            "MONGO_URI is not configured."
        )

    if not MONGO_DATABASE:

        raise RuntimeError(
            "MONGO_DATABASE is not configured."
        )

    if not MONGO_RAW_HTML_COLLECTION:

        raise RuntimeError(
            "MONGO_RAW_HTML_COLLECTION "
            "is not configured."
        )

    # ========================================================
    # Lazy MongoClient
    # ========================================================

    if _client is None:

        logger.info(
            "Archive Viewer connecting to MongoDB: "
            f"database={MONGO_DATABASE}, "
            f"collection={MONGO_RAW_HTML_COLLECTION}"
        )

        _client = MongoClient(
            MONGO_URI,
        )

    # ========================================================
    # Collection
    # ========================================================

    database = _client[
        MONGO_DATABASE
    ]

    collection = database[
        MONGO_RAW_HTML_COLLECTION
    ]

    return collection


# ============================================================
#
# Normalize URL
#
# ============================================================

def normalize_url(
    url: str | None,
) -> str | None:
    """
    正規化 Archive Viewer URL。

    支援：

        正常 URL

        Markdown Link：

            [https://example.com](https://example.com)

    Parameters
    ----------
    url:
        原始 URL。

    Returns
    -------
    str | None

        正規化後 URL。
    """

    if url is None:

        return None

    url = str(
        url
    ).strip()

    if not url:

        return None

    # ========================================================
    # Markdown Link
    # ========================================================

    if (
        url.startswith("[")
        and "](" in url
        and url.endswith(")")
    ):

        close_bracket = url.find(
            "]("
        )

        if close_bracket > 0:

            markdown_url = url[
                close_bracket + 2:
                -1
            ].strip()

            if markdown_url:

                url = markdown_url

    return url


# ============================================================
#
# Normalize Created At
#
# ============================================================

def normalize_created_at(
    created_at: Any,
) -> datetime | None:
    """
    將 created_at 統一成：

        timezone-aware UTC datetime。

    支援：

        datetime
        ISO 8601 string
        ISO 8601 + Z
        ISO 8601 + timezone offset

    規則：

        naive datetime
            ->
        視為 UTC

        aware datetime
            ->
        轉換為 UTC

        naive ISO string
            ->
        視為 UTC

        aware ISO string
            ->
        轉換為 UTC
    """

    if created_at is None:

        return None

    # ========================================================
    # datetime
    # ========================================================

    if isinstance(
        created_at,
        datetime,
    ):

        if created_at.tzinfo is None:

            return created_at.replace(
                tzinfo=timezone.utc,
            )

        return created_at.astimezone(
            timezone.utc,
        )

    # ========================================================
    # ISO 8601 String
    # ========================================================

    if isinstance(
        created_at,
        str,
    ):

        value = created_at.strip()

        if not value:

            return None

        try:

            parsed = datetime.fromisoformat(
                value.replace(
                    "Z",
                    "+00:00",
                )
            )

        except (
            TypeError,
            ValueError,
        ):

            logger.warning(
                "Archive Viewer invalid "
                "created_at: "
                f"{created_at}"
            )

            return None

        if parsed.tzinfo is None:

            return parsed.replace(
                tzinfo=timezone.utc,
            )

        return parsed.astimezone(
            timezone.utc,
        )

    # ========================================================
    # Unsupported Type
    # ========================================================

    logger.warning(
        "Archive Viewer unsupported "
        "created_at type: "
        f"{type(created_at)}"
    )

    return None


# ============================================================
#
# Format Created At
#
# ============================================================

def format_created_at(
    created_at: Any,
) -> str | None:
    """
    將 created_at 格式化成 Viewer 使用的 ISO 8601 UTC。

    例如：

        2026-08-29T14:20:00+00:00
    """

    normalized = normalize_created_at(
        created_at
    )

    if normalized is None:

        return None

    return normalized.isoformat()


# ============================================================
#
# Build Snapshot History
#
# ============================================================

def find_snapshot_history(
    url: str,
) -> list[dict[str, Any]]:
    """
    查詢指定 URL 的所有 Raw HTML Snapshot。

    MongoDB：

        raw_html

    Query：

        {
            "url": url
        }

    回傳：

        [
            {
                "version":
                    "2026-08-29T14:20:00+00:00",

                "created_at":
                    "2026-08-29T14:20:00+00:00"
            },
            ...
        ]

    排序：

        created_at DESC

    注意：

        本方法只查詢 Snapshot Metadata。

        不載入 Raw HTML。
    """

    collection = get_mongo_collection()

    try:

        cursor = collection.find(
            {
                "url": url,
            },
            {
                "_id": 1,
                "created_at": 1,
            },
        ).sort(
            "created_at",
            -1,
        )

        versions = []

        seen_versions = set()

        for document in cursor:

            created_at = normalize_created_at(
                document.get(
                    "created_at"
                )
            )

            if created_at is None:

                continue

            version = created_at.isoformat()

            # =================================================
            # Prevent duplicate created_at
            # =================================================

            if version in seen_versions:

                continue

            seen_versions.add(
                version
            )

            versions.append({

                "version":
                    version,

                "created_at":
                    version,

            })

        logger.info(
            "Archive Viewer snapshot history: "
            f"url={url}, "
            f"count={len(versions)}"
        )

        return versions

    except Exception as e:

        logger.exception(
            "Archive Viewer failed to query "
            "Snapshot History: "
            f"url={url}, "
            f"error={e}"
        )

        raise


# ============================================================
#
# Find Snapshot
#
# ============================================================

def find_snapshot(
    url: str,
    created_at: datetime,
) -> dict[str, Any] | None:
    """
    查詢指定 Snapshot。

    Snapshot Identity：

        URL
        +
        created_at
    """

    collection = get_mongo_collection()

    normalized_created_at = normalize_created_at(
        created_at
    )

    if normalized_created_at is None:

        return None

    query = {
        "url": url,
        "created_at": normalized_created_at,
    }

    try:

        document = collection.find_one(
            query
        )

        if document is None:

            logger.warning(
                "Archive Viewer Snapshot not found: "
                f"url={url}, "
                f"created_at={normalized_created_at}"
            )

            return None

        return document

    except Exception as e:

        logger.exception(
            "Archive Viewer Snapshot lookup failed: "
            f"url={url}, "
            f"created_at={normalized_created_at}, "
            f"error={e}"
        )

        raise


# ============================================================
#
# Extract Raw HTML
#
# ============================================================

def extract_html(
    snapshot: dict[str, Any] | None,
) -> str | None:
    """
    從 MongoDB Snapshot 取得 Raw HTML。

    為了兼容既有資料，
    嘗試幾個常見欄位：

        html
        raw_html
        content

    優先：

        html
        raw_html
        content
    """

    if not snapshot:

        return None

    # ========================================================
    # Preferred: html
    # ========================================================

    html = snapshot.get(
        "html"
    )

    if isinstance(
        html,
        str,
    ) and html:

        return html

    # ========================================================
    # raw_html
    # ========================================================

    raw_html = snapshot.get(
        "raw_html"
    )

    if isinstance(
        raw_html,
        str,
    ) and raw_html:

        return raw_html

    # ========================================================
    # content
    # ========================================================

    content = snapshot.get(
        "content"
    )

    if isinstance(
        content,
        str,
    ) and content:

        return content

    return None


# ============================================================
#
# Build Snapshot Metadata
#
# ============================================================

def build_snapshot_metadata(
    snapshot: dict[str, Any] | None,
) -> dict[str, Any]:
    """
    建立 Viewer Snapshot Metadata。

    不直接將 MongoDB ObjectId
    傳給 Template。
    """

    if not snapshot:

        return {

            "mongo_id":
                None,

            "document_id":
                None,

            "content_hash":
                None,

            "resolved_url":
                None,

            "created_at":
                None,

        }

    mongo_id = snapshot.get(
        "_id"
    )

    created_at = normalize_created_at(
        snapshot.get(
            "created_at"
        )
    )

    return {

        "mongo_id":
            str(mongo_id)
            if mongo_id is not None
            else None,

        "document_id":
            snapshot.get(
                "document_id"
            ),

        "content_hash":
            snapshot.get(
                "content_hash"
            ),

        "resolved_url":
            snapshot.get(
                "resolved_url"
            ),

        "created_at":
            created_at.isoformat()
            if created_at is not None
            else None,

    }


# ============================================================
#
# Prepare Snapshot HTML
#
# ============================================================

def prepare_snapshot_html(
    html: str,
    original_url: str,
) -> str:
    """
    準備 Snapshot HTML 供 Browser 直接 Render。

    目的：

        讓 MongoDB 儲存的 Raw HTML
        以原網站 URL 作為 URL Base。

    例如：

        Original URL:

            https://www.tca.org.tw/news_detail.php?n=2449&t=h

        Snapshot HTML：

            <img src="/images/logo.png">

        Browser 將解析成：

            https://www.tca.org.tw/images/logo.png

    注意：

        不修改 MongoDB 中的原始 HTML。

        只在 HTTP Response 前，
        動態加入 <base href="...">。

    如果 Snapshot 本身已經存在 <base>：

        不重複加入。
    """

    if not html:

        return html

    if not original_url:

        return html

    # ========================================================
    # Escape Base URL
    # ========================================================

    safe_base_url = escape(
        original_url,
        quote=True,
    )

    base_tag = (
        f'<base href="{safe_base_url}">'
    )

    # ========================================================
    # Detect Existing Base
    # ========================================================

    lower_html = html.lower()

    if "<base " in lower_html:

        return html

    # ========================================================
    # Inject into <head>
    # ========================================================

    head_start = lower_html.find(
        "<head"
    )

    if head_start != -1:

        head_end = lower_html.find(
            ">",
            head_start,
        )

        if head_end != -1:

            return (
                html[:head_end + 1]
                + "\n"
                + base_tag
                + "\n"
                + html[head_end + 1:]
            )

    # ========================================================
    # No <head>
    # ========================================================

    return (
        "<head>\n"
        + base_tag
        + "\n</head>\n"
        + html
    )


# ============================================================
#
# Archive Viewer UI
#
# ============================================================

@router.get(
    "/view",
    include_in_schema=False,
)
def archive_view(
    request: Request,
    url: str = Query(
        ...,
        min_length=1,
        description="Original article URL.",
    ),
    version: str | None = Query(
        None,
        description=(
            "Snapshot created_at in ISO 8601 format. "
            "If omitted, only Snapshot History is loaded."
        ),
    ),
):
    """
    Archive Article Viewer UI。

    初次：

        /archive/view?url=...

    只顯示 Snapshot History。

    選擇版本後：

        /archive/view?
            url=...
            &version=...

    Viewer iframe 將自行載入：

        /archive/snapshot?
            url=...
            &version=...
    """

    # ========================================================
    # Normalize URL
    # ========================================================

    normalized_url = normalize_url(
        url
    )

    if not normalized_url:

        raise HTTPException(
            status_code=400,
            detail="Invalid archive article URL.",
        )

    # ========================================================
    # Normalize Version
    # ========================================================

    requested_created_at = None

    if version is not None:

        requested_created_at = normalize_created_at(
            version
        )

        if requested_created_at is None:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Invalid archive version. "
                    "Version must be a valid "
                    "ISO 8601 created_at datetime."
                ),
            )

    # ========================================================
    # Snapshot History
    # ========================================================

    try:

        versions = find_snapshot_history(
            normalized_url
        )

    except Exception:

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to query Archive "
                "Snapshot History."
            ),
        )

    # ========================================================
    # Initial View
    #
    # 不載入 HTML。
    # ========================================================

    if requested_created_at is None:

        logger.info(
            "Archive Viewer initial view: "
            f"url={normalized_url}, "
            f"versions={len(versions)}, "
            "html=False"
        )

        return templates.TemplateResponse(
            request=request,
            name="archive/viewer.html",
            context={

                "title":
                    "Article Archive",

                "url":
                    normalized_url,

                "versions":
                    versions,

                "selected_version":
                    None,

                "selected_created_at":
                    None,

                "html":
                    None,

                "mongo_id":
                    None,

                "document_id":
                    None,

                "content_hash":
                    None,

                "resolved_url":
                    None,

            },
        )

    # ========================================================
    # Verify Requested Version Exists
    # ========================================================

    requested_version = (
        requested_created_at.isoformat()
    )

    selected_version = None

    for item in versions:

        if (
            item.get(
                "version"
            )
            == requested_version
        ):

            selected_version = item

            break

    # ========================================================
    # Requested Snapshot Does Not Exist
    # ========================================================

    if selected_version is None:

        logger.warning(
            "Archive Viewer requested version "
            "does not exist: "
            f"url={normalized_url}, "
            f"version={requested_version}"
        )

        raise HTTPException(
            status_code=404,
            detail=(
                "Archive snapshot version not found."
            ),
        )

    # ========================================================
    # Viewer UI
    #
    # IMPORTANT:
    #
    # 不再在這裡載入 HTML。
    #
    # HTML 改由 iframe：
    #
    #     /archive/snapshot
    #
    # 直接取得。
    # ========================================================

    logger.info(
        "Archive Viewer selected snapshot UI: "
        f"url={normalized_url}, "
        f"version={requested_version}"
    )

    return templates.TemplateResponse(
        request=request,
        name="archive/viewer.html",
        context={

            "title":
                "Article Archive",

            "url":
                normalized_url,

            "versions":
                versions,

            "selected_version":
                selected_version.get(
                    "version"
                ),

            "selected_created_at":
                selected_version.get(
                    "created_at"
                ),

            # =================================================
            # HTML no longer embedded into Template.
            # =================================================

            "html":
                None,

            "mongo_id":
                None,

            "document_id":
                None,

            "content_hash":
                None,

            "resolved_url":
                normalized_url,

        },
    )


# ============================================================
#
# Archive Snapshot HTML
#
# ============================================================

@router.get(
    "/snapshot",
    include_in_schema=False,
)
def archive_snapshot(
    url: str = Query(
        ...,
        min_length=1,
        description="Original article URL.",
    ),
    version: str = Query(
        ...,
        description=(
            "Snapshot created_at in ISO 8601 format."
        ),
    ),
):
    """
    直接呈現 MongoDB 中的 Snapshot HTML。

    Flow：

        URL
        +
        created_at
             |
             v
        MongoDB raw_html
             |
             v
        Raw HTML
             |
             v
        Inject <base>
             |
             v
        HTTP text/html
             |
             v
        Browser Render

    注意：

        MongoDB 中的原始 HTML 不修改。

        不使用 srcdoc。

        不經過 Parser。

        不經過 Article。

        不經過 Archive Service。
    """

    # ========================================================
    # Normalize URL
    # ========================================================

    normalized_url = normalize_url(
        url
    )

    if not normalized_url:

        raise HTTPException(
            status_code=400,
            detail="Invalid archive article URL.",
        )

    # ========================================================
    # Normalize Version
    # ========================================================

    requested_created_at = normalize_created_at(
        version
    )

    if requested_created_at is None:

        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid archive version. "
                "Version must be a valid "
                "ISO 8601 created_at datetime."
            ),
        )

    # ========================================================
    # Find Snapshot
    # ========================================================

    try:

        snapshot = find_snapshot(
            normalized_url,
            requested_created_at,
        )

    except Exception:

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to query Archive Snapshot."
            ),
        )

    if snapshot is None:

        raise HTTPException(
            status_code=404,
            detail=(
                "Archive snapshot not found."
            ),
        )

    # ========================================================
    # Extract HTML
    # ========================================================

    html = extract_html(
        snapshot
    )

    if html is None:

        logger.warning(
            "Archive Snapshot has no HTML: "
            f"url={normalized_url}, "
            f"version={requested_created_at.isoformat()}"
        )

        raise HTTPException(
            status_code=404,
            detail=(
                "Snapshot HTML not found."
            ),
        )

    # ========================================================
    # Determine Original URL
    #
    # 優先：
    #
    #     resolved_url
    #
    # 其次：
    #
    #     url
    #
    # 最後：
    #
    #     normalized_url
    # ========================================================

    original_url = (
        snapshot.get(
            "resolved_url"
        )
        or snapshot.get(
            "url"
        )
        or normalized_url
    )

    original_url = str(
        original_url
    ).strip()

    # ========================================================
    # Prepare HTML
    # ========================================================

    prepared_html = prepare_snapshot_html(
        html,
        original_url,
    )

    # ========================================================
    # Logging
    # ========================================================

    logger.info(
        "Archive Snapshot HTML served: "
        f"url={normalized_url}, "
        f"version={requested_created_at.isoformat()}, "
        f"original_url={original_url}, "
        f"html_length={len(prepared_html)}"
    )

    # ========================================================
    # Direct HTML Response
    # ========================================================

    return Response(
        content=prepared_html,
        media_type="text/html",
        headers={
            "Content-Disposition": "inline",
            "X-Archive-Snapshot": "true",
        },
    )


# ============================================================
#
# Public API
#
# ============================================================

__all__ = [
    "router",
]