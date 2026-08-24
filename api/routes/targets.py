"""
api/routes/targets.py

AutoSearch V5

Target Management API

V5.3 P3.4 + Direct URL Execution Integration

用途：

    管理使用者建立的 Target。

架構：

    Web UI
        ↓
    Target API
        ↓
    TargetService
        ↓
    TargetValidator
        ↓
    TargetRepository
        ↓
    MySQL

Direct URL 建立後立即執行：

    Web UI
        ↓
    POST /targets
        ↓
    TargetService
        ↓
    TargetExecutionService
        ↓
    CrawlService
        ↓
    ParserService
        ↓
    ArticleService
        ↓
    SQL / Archive / AI Task

支援：

    1. Direct URL Target
    2. Keyword Search Target
    3. Google Search Target
    4. Google News Target
    5. Target Query
    6. Target Update
    7. Target Status Management
    8. Target Enable / Disable
    9. Target Delete
    10. Direct URL Target Execution

重要：

    Direct URL Target：

        建立 Target 成功後
            ↓
        立即執行 Direct URL Crawl

    Search Target：

        建立 Target
            ↓
        不立即 Search / Crawl

    已建立的 Direct URL Target：

        POST /targets/{target_id}/execute

    可再次執行。

    Router 不直接實作：

        Crawl
        Parser
        Article

    所有執行流程統一交給：

        TargetExecutionService
"""


# ============================================================
#
# Imports
#
# ============================================================

from typing import Optional

from fastapi import (
    APIRouter,
    HTTPException,
)

from pydantic import (
    BaseModel,
)

from models.target import (
    Target,
)

from services.target_service import (
    TargetService,
)

from services.target_execution_service import (
    TargetExecutionService,
)


# ============================================================
#
# Router
#
# ============================================================

router = APIRouter(
    prefix="/targets",
    tags=[
        "Target Management",
    ],
)


# ============================================================
#
# Request Models
#
# ============================================================


class TargetCreateRequest(
    BaseModel
):
    """
    Target 建立 Request。

    支援：

        Direct URL
        Keyword Search
        Google Search
        Google News
    """

    name: Optional[str] = ""

    target_type: str = (
        Target.TYPE_URL
    )

    url: Optional[str] = ""

    keyword: Optional[str] = ""

    search_provider: Optional[str] = ""

    description: Optional[str] = ""

    status: Optional[str] = (
        Target.DEFAULT_STATUS
    )


class TargetUpdateRequest(
    BaseModel
):
    """
    Target Update Request。
    """

    name: Optional[str] = None

    target_type: Optional[str] = None

    url: Optional[str] = None

    keyword: Optional[str] = None

    search_provider: Optional[str] = None

    description: Optional[str] = None

    status: Optional[str] = None


class TargetStatusRequest(
    BaseModel
):
    """
    Target Status 更新 Request。
    """

    status: str


# ============================================================
#
# Services
#
# ============================================================


def get_target_service():
    """
    建立 TargetService。
    """

    return TargetService()


def get_target_execution_service():
    """
    建立 TargetExecutionService。

    TargetExecutionService 內部：

        Target
          ↓
        JobExecutorBridge
          ↓
        CrawlService
          ↓
        ParserService
          ↓
        ArticleService
    """

    return TargetExecutionService()


# ============================================================
#
# Helpers
#
# ============================================================


def _raise_service_error(
    operation,
    error,
):
    """
    將 Service Exception 轉換成 HTTP 500。
    """

    raise HTTPException(
        status_code=500,
        detail=(
            f"Failed to {operation}: "
            f"{error}"
        ),
    )


def _normalize_optional(
    value,
):
    """
    Normalize Optional Request Field。
    """

    if value is None:
        return None

    return str(
        value
    ).strip()


# ============================================================
#
# Create Target
#
# ============================================================


@router.post(
    "",
)
def create_target(
    request: TargetCreateRequest,
):
    """
    建立 Target。

    Direct URL：

        建立 Target
            ↓
        立即執行 Direct URL
            ↓
        TargetExecutionService
            ↓
        CrawlService
            ↓
        ParserService
            ↓
        ArticleService
            ↓
        SQL / Archive / AI Task

    Search Target：

        只建立 Target。
    """

    target_type = (
        str(
            request.target_type
        ).strip()
    )

    url = (
        str(
            request.url or ""
        ).strip()
    )

    keyword = (
        str(
            request.keyword or ""
        ).strip()
    )

    search_provider = (
        str(
            request.search_provider or ""
        ).strip()
    )

    name = (
        request.name or ""
    ).strip()

    description = (
        request.description or ""
    ).strip()

    status = (
        request.status
        or Target.DEFAULT_STATUS
    ).strip()

    service = (
        get_target_service()
    )

    # ========================================================
    #
    # Execution Result
    #
    # ========================================================

    execution_result = None

    try:

        # ====================================================
        #
        # URL Target
        #
        # ====================================================

        if target_type == Target.TYPE_URL:

            if not url:

                raise HTTPException(
                    status_code=400,
                    detail=(
                        "URL Target requires 'url'."
                    ),
                )

            # ------------------------------------------------
            # 建立 Target
            # ------------------------------------------------

            target = (
                service.create_url_target(
                    url=url,
                    name=name,
                    description=description,
                    status=status,
                )
            )

            # ------------------------------------------------
            # 建立成功後立即執行 Direct URL
            # ------------------------------------------------

            execution_service = (
                get_target_execution_service()
            )

            try:

                execution_result = (
                    execution_service
                    .execute_direct_url(
                        target
                    )
                )

            except ValueError as e:

                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Target created successfully, "
                        "but Direct URL execution failed: "
                        f"{e}"
                    ),
                )

            except Exception as e:

                raise HTTPException(
                    status_code=500,
                    detail=(
                        "Target created successfully, "
                        "but Direct URL execution failed: "
                        f"{e}"
                    ),
                )

        # ====================================================
        #
        # Search Target
        #
        # ====================================================

        elif target_type == Target.TYPE_SEARCH:

            if not keyword:

                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Search Target requires "
                        "'keyword'."
                    ),
                )

            if not search_provider:

                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Search Target requires "
                        "'search_provider'."
                    ),
                )

            # ------------------------------------------------
            # Search Target 目前只建立
            # ------------------------------------------------

            target = (
                service.create_search_target(
                    keyword=keyword,
                    search_provider=search_provider,
                    name=name,
                    description=description,
                    status=status,
                )
            )

        # ====================================================
        #
        # Invalid Target Type
        #
        # ====================================================

        else:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Invalid target_type. "
                    "Supported values: "
                    "'url', 'search'."
                ),
            )

    # ========================================================
    #
    # HTTP Exception
    #
    # ========================================================

    except HTTPException:

        raise

    # ========================================================
    #
    # Value Error
    #
    # ========================================================

    except ValueError as e:

        message = str(
            e
        )

        if (
            "already exists"
            in message.lower()
        ):

            raise HTTPException(
                status_code=409,
                detail=message,
            )

        raise HTTPException(
            status_code=400,
            detail=message,
        )

    # ========================================================
    #
    # Unexpected Error
    #
    # ========================================================

    except Exception as e:

        _raise_service_error(
            "create target",
            e,
        )

    # ========================================================
    #
    # Response
    #
    # ========================================================

    response = {

        "status": "success",

        "message": (
            "Target created successfully."
        ),

        "target": (
            target.to_dict()
        ),

    }

    # ========================================================
    #
    # Direct URL Execution Result
    #
    # ========================================================

    if (
        target_type == Target.TYPE_URL
        and execution_result is not None
    ):

        response["message"] = (
            "Target created and "
            "Direct URL executed successfully."
        )

        response["execution"] = (
            execution_result
        )

    return response


# ============================================================
#
# Get All Targets
#
# ============================================================


@router.get(
    "",
)
def get_targets():

    service = (
        get_target_service()
    )

    try:

        targets = (
            service.find_all()
        )

    except Exception as e:

        _raise_service_error(
            "load targets",
            e,
        )

    return {

        "status": "success",

        "count": len(
            targets
        ),

        "targets": [
            target.to_dict()
            for target in targets
        ],

    }


# ============================================================
#
# Get Active Targets
#
# ============================================================


@router.get(
    "/active",
)
def get_active_targets():

    service = (
        get_target_service()
    )

    try:

        targets = (
            service.find_active()
        )

    except Exception as e:

        _raise_service_error(
            "load active targets",
            e,
        )

    return {

        "status": "success",

        "count": len(
            targets
        ),

        "targets": [
            target.to_dict()
            for target in targets
        ],

    }


# ============================================================
#
# Get URL Targets
#
# ============================================================


@router.get(
    "/type/url",
)
def get_url_targets():

    service = (
        get_target_service()
    )

    try:

        targets = (
            service.find_url_targets()
        )

    except Exception as e:

        _raise_service_error(
            "load URL targets",
            e,
        )

    return {

        "status": "success",

        "count": len(
            targets
        ),

        "targets": [
            target.to_dict()
            for target in targets
        ],

    }


# ============================================================
#
# Get Search Targets
#
# ============================================================


@router.get(
    "/type/search",
)
def get_search_targets():

    service = (
        get_target_service()
    )

    try:

        targets = (
            service.find_search_targets()
        )

    except Exception as e:

        _raise_service_error(
            "load search targets",
            e,
        )

    return {

        "status": "success",

        "count": len(
            targets
        ),

        "targets": [
            target.to_dict()
            for target in targets
        ],

    }


# ============================================================
#
# Execute Direct URL Target
#
# ============================================================


@router.post(
    "/{target_id}/execute",
)
def execute_target(
    target_id: int,
):
    """
    執行 Target。

    目前只允許 Direct URL Target。

    Pipeline：

        API
          ↓
        TargetService
          ↓
        TargetExecutionService
          ↓
        JobExecutorBridge
          ↓
        CrawlService
          ↓
        ParserService
          ↓
        ArticleService
          ↓
        SQL / Archive / AI Task

    注意：

        Router 不直接呼叫：

            CrawlService
            ParserService
            ArticleService

        所有執行流程統一交給：

            TargetExecutionService
    """

    # ========================================================
    #
    # Load Target
    #
    # ========================================================

    target_service = (
        get_target_service()
    )

    try:

        target = (
            target_service.get_by_id(
                target_id
            )
        )

    except Exception as e:

        _raise_service_error(
            "load target for execution",
            e,
        )

    if target is None:

        raise HTTPException(
            status_code=404,
            detail=(
                f"Target not found: "
                f"{target_id}"
            ),
        )

    # ========================================================
    #
    # Direct URL Only
    #
    # ========================================================

    if target.target_type != Target.TYPE_URL:

        raise HTTPException(
            status_code=400,
            detail=(
                "Target execution currently "
                "supports Direct URL Target only."
            ),
        )

    # ========================================================
    #
    # Execute
    #
    # ========================================================

    execution_service = (
        get_target_execution_service()
    )

    try:

        result = (
            execution_service
            .execute_direct_url(
                target
            )
        )

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    except Exception as e:

        logger_message = (
            "Target execution failed: "
            f"target_id={target_id}, "
            f"error={e}"
        )

        # 使用 execution service 內部 logging，
        # Router 只負責轉換 API error。
        raise HTTPException(
            status_code=500,
            detail=logger_message,
        )

    # ========================================================
    #
    # Response
    #
    # ========================================================

    return {

        "status": "success",

        "message": (
            "Direct URL Target executed successfully."
        ),

        "target_id": target_id,

        "target": (
            target.to_dict()
        ),

        "execution": result,

    }


# ============================================================
#
# Get Target By ID
#
# ============================================================


@router.get(
    "/{target_id}",
)
def get_target(
    target_id: int,
):

    service = (
        get_target_service()
    )

    try:

        target = (
            service.get_by_id(
                target_id
            )
        )

    except Exception as e:

        _raise_service_error(
            "load target",
            e,
        )

    if target is None:

        raise HTTPException(
            status_code=404,
            detail=(
                f"Target not found: "
                f"{target_id}"
            ),
        )

    return {

        "status": "success",

        "target": (
            target.to_dict()
        ),

    }


# ============================================================
#
# Update Target
#
# ============================================================


@router.put(
    "/{target_id}",
)
def update_target(
    target_id: int,
    request: TargetUpdateRequest,
):

    service = (
        get_target_service()
    )

    try:

        target = (
            service.get_by_id(
                target_id
            )
        )

    except Exception as e:

        _raise_service_error(
            "load target",
            e,
        )

    if target is None:

        raise HTTPException(
            status_code=404,
            detail=(
                f"Target not found: "
                f"{target_id}"
            ),
        )

    if request.name is not None:
        target.name = (
            request.name.strip()
        )

    if request.target_type is not None:
        target.target_type = (
            request.target_type.strip()
        )

    if request.url is not None:
        target.url = (
            request.url.strip()
        )

    if request.keyword is not None:
        target.keyword = (
            request.keyword.strip()
        )

    if request.search_provider is not None:
        target.search_provider = (
            request.search_provider.strip()
        )

    if request.description is not None:
        target.description = (
            request.description.strip()
        )

    if request.status is not None:
        target.status = (
            request.status.strip()
        )

    try:

        updated = (
            service.update(
                target
            )
        )

    except ValueError as e:

        message = str(
            e
        )

        if (
            "already exists"
            in message.lower()
        ):

            raise HTTPException(
                status_code=409,
                detail=message,
            )

        raise HTTPException(
            status_code=400,
            detail=message,
        )

    except Exception as e:

        _raise_service_error(
            "update target",
            e,
        )

    return {

        "status": "success",

        "message": (
            "Target updated successfully."
        ),

        "target": (
            updated.to_dict()
        ),

    }


# ============================================================
#
# Update Target Status
#
# ============================================================


@router.patch(
    "/{target_id}/status",
)
def update_target_status(
    target_id: int,
    request: TargetStatusRequest,
):

    status = (
        str(
            request.status
        ).strip()
    )

    if not status:

        raise HTTPException(
            status_code=400,
            detail=(
                "status cannot be empty."
            ),
        )

    service = (
        get_target_service()
    )

    try:

        target = (
            service.get_by_id(
                target_id
            )
        )

    except Exception as e:

        _raise_service_error(
            "load target",
            e,
        )

    if target is None:

        raise HTTPException(
            status_code=404,
            detail=(
                f"Target not found: "
                f"{target_id}"
            ),
        )

    target.status = status

    try:

        updated = (
            service.update(
                target
            )
        )

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    except Exception as e:

        _raise_service_error(
            "update target status",
            e,
        )

    return {

        "status": "success",

        "message": (
            "Target status updated successfully."
        ),

        "target": (
            updated.to_dict()
        ),

    }


# ============================================================
#
# Enable Target
#
# ============================================================


@router.patch(
    "/{target_id}/enable",
)
def enable_target(
    target_id: int,
):

    service = (
        get_target_service()
    )

    try:

        target = (
            service.get_by_id(
                target_id
            )
        )

    except Exception as e:

        _raise_service_error(
            "load target",
            e,
        )

    if target is None:

        raise HTTPException(
            status_code=404,
            detail=(
                f"Target not found: "
                f"{target_id}"
            ),
        )

    try:

        updated = (
            service.enable(
                target_id
            )
        )

    except Exception as e:

        _raise_service_error(
            "enable target",
            e,
        )

    if not updated:

        raise HTTPException(
            status_code=404,
            detail=(
                f"Target not found: "
                f"{target_id}"
            ),
        )

    target = (
        service.get_by_id(
            target_id
        )
    )

    return {

        "status": "success",

        "message": (
            "Target enabled successfully."
        ),

        "target": (
            target.to_dict()
            if target
            else None
        ),

    }


# ============================================================
#
# Disable Target
#
# ============================================================


@router.patch(
    "/{target_id}/disable",
)
def disable_target(
    target_id: int,
):

    service = (
        get_target_service()
    )

    try:

        target = (
            service.get_by_id(
                target_id
            )
        )

    except Exception as e:

        _raise_service_error(
            "load target",
            e,
        )

    if target is None:

        raise HTTPException(
            status_code=404,
            detail=(
                f"Target not found: "
                f"{target_id}"
            ),
        )

    try:

        updated = (
            service.disable(
                target_id
            )
        )

    except Exception as e:

        _raise_service_error(
            "disable target",
            e,
        )

    if not updated:

        raise HTTPException(
            status_code=404,
            detail=(
                f"Target not found: "
                f"{target_id}"
            ),
        )

    target = (
        service.get_by_id(
            target_id
        )
    )

    return {

        "status": "success",

        "message": (
            "Target disabled successfully."
        ),

        "target": (
            target.to_dict()
            if target
            else None
        ),

    }


# ============================================================
#
# Delete Target
#
# ============================================================


@router.delete(
    "/{target_id}",
)
def delete_target(
    target_id: int,
):

    service = (
        get_target_service()
    )

    try:

        exists = (
            service.exists(
                target_id
            )
        )

    except Exception as e:

        _raise_service_error(
            "check target",
            e,
        )

    if not exists:

        raise HTTPException(
            status_code=404,
            detail=(
                f"Target not found: "
                f"{target_id}"
            ),
        )

    try:

        deleted = (
            service.delete(
                target_id
            )
        )

    except Exception as e:

        _raise_service_error(
            "delete target",
            e,
        )

    if not deleted:

        raise HTTPException(
            status_code=404,
            detail=(
                f"Target not found: "
                f"{target_id}"
            ),
        )

    return {

        "status": "success",

        "message": (
            "Target deleted successfully."
        ),

        "target_id": target_id,

    }


# ============================================================
#
# Public API
#
# ============================================================

__all__ = [
    "router",
]
