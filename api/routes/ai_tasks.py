"""
api/routes/ai_tasks.py

AutoSearch V4

P3.4

AI Task Management API

功能:

1. AI Task List
2. AI Task Detail
3. Pending Task Count
4. Claim AI Task
5. Mark AI Task Done
6. Mark AI Task Failed

P3.4.1:
    Task List API

P3.4.2:
    Task Detail API

P3.4.3:
    Pending Task API

P3.4.4:
    Task Claim API

P3.4.5:
    Task Completion API

P3.4.6:
    Task Failure API


Repository:

    database.ai_task_repository.AITaskRepository


Task Lifecycle:

    WAITING
        |
        | claim
        v
    RUNNING
        |
        +------> DONE
        |
        +------> FAILED
"""

from fastapi import (
    APIRouter,
    Query,
    HTTPException
)

from database.ai_task_repository import (
    AITaskRepository
)


# ==================================================
# Router
# ==================================================

router = APIRouter(

    prefix="/ai/tasks",

    tags=[
        "AI Task Management"
    ]

)


# ==================================================
# Repository
# ==================================================

repository = AITaskRepository()


# ==================================================
# AI Task List
# ==================================================

@router.get("")
def get_ai_tasks(

    limit: int = Query(
        10,
        ge=1,
        le=100
    )

):
    """
    取得目前 WAITING AI Tasks。

    GET /ai/tasks

    Parameters
    ----------

    limit:
        最大取得 Task 數量。

    Returns
    -------

    success:
        API 是否成功。

    count:
        回傳 Task 數量。

    data:
        AI Task List。
    """

    tasks = (
        repository
        .get_waiting_tasks(
            limit=limit
        )
    )

    return {

        "success": True,

        "count": len(tasks),

        "data": tasks

    }


# ==================================================
# Pending Task Count
# ==================================================

@router.get(
    "/pending/count"
)
def get_pending_task_count():
    """
    取得目前 WAITING AI Task 數量。

    GET /ai/tasks/pending/count

    用途:

        AIBatchTriggerService
        Dashboard
        Monitoring
    """

    count = (
        repository
        .count_waiting_tasks()
    )

    return {

        "success": True,

        "waiting": count

    }


# ==================================================
# AI Task Detail
# ==================================================

@router.get(
    "/{task_id}"
)
def get_ai_task(

    task_id: int

):
    """
    取得單一 AI Task。

    GET /ai/tasks/{task_id}
    """

    task = (
        repository
        .find_by_id(
            task_id
        )
    )

    if task is None:

        raise HTTPException(

            status_code=404,

            detail={
                "success": False,
                "message": "AI Task not found"
            }

        )

    return {

        "success": True,

        "data": task

    }


# ==================================================
# Claim AI Task
# ==================================================

@router.post(
    "/{task_id}/claim"
)
def claim_ai_task(

    task_id: int

):
    """
    Claim 一個 WAITING AI Task。

    POST /ai/tasks/{task_id}/claim

    Lifecycle:

        WAITING
            ↓
        RUNNING

    Worker Safety:

        只有第一個 Worker
        可以成功 Claim。

        其他 Worker
        會收到 409。
    """

    task = (
        repository
        .claim_task(
            task_id
        )
    )

    if task is None:

        raise HTTPException(

            status_code=409,

            detail={
                "success": False,
                "message":
                    "AI Task cannot be claimed. "
                    "It may not exist or is no longer WAITING."
            }

        )

    return {

        "success": True,

        "message":
            "AI Task claimed successfully",

        "data":
            task

    }


# ==================================================
# Mark AI Task Done
# ==================================================

@router.post(
    "/{task_id}/done"
)
def mark_ai_task_done(

    task_id: int

):
    """
    將 RUNNING AI Task 標記為 DONE。

    POST /ai/tasks/{task_id}/done

    Lifecycle:

        RUNNING
            ↓
          DONE

    finished_time
    由 Repository 自動寫入。
    """

    success = (
        repository
        .mark_done(
            task_id
        )
    )

    if not success:

        raise HTTPException(

            status_code=409,

            detail={
                "success": False,
                "message":
                    "AI Task cannot be marked DONE. "
                    "It may not exist or is not RUNNING."
            }

        )

    task = (
        repository
        .find_by_id(
            task_id
        )
    )

    return {

        "success": True,

        "message":
            "AI Task marked as DONE",

        "data":
            task

    }


# ==================================================
# Mark AI Task Failed
# ==================================================

@router.post(
    "/{task_id}/failed"
)
def mark_ai_task_failed(

    task_id: int

):
    """
    將 RUNNING AI Task 標記為 FAILED。

    POST /ai/tasks/{task_id}/failed

    Lifecycle:

        RUNNING
            ↓
         FAILED

    同時:

        retry_count + 1
    """

    success = (
        repository
        .mark_failed(
            task_id
        )
    )

    if not success:

        raise HTTPException(

            status_code=409,

            detail={
                "success": False,
                "message":
                    "AI Task cannot be marked FAILED. "
                    "It may not exist or is not RUNNING."
            }

        )

    task = (
        repository
        .find_by_id(
            task_id
        )
    )

    return {

        "success": True,

        "message":
            "AI Task marked as FAILED",

        "data":
            task

    }
