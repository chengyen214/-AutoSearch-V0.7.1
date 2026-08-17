"""
tests/test_ai_tasks_api.py

AutoSearch V4

P3.4

AI Task Management API Test

測試:

1. AI Task List
2. Pending Task Count
3. AI Task Detail
4. Claim AI Task
5. Mark AI Task Done
6. Mark AI Task Failed

測試方式:

    FastAPI TestClient
        +
    Mock AITaskRepository

不直接連接 MySQL。

Run:

    python -m pytest tests/test_ai_tasks_api.py -v
"""


from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from fastapi.testclient import TestClient

from api.main import app

from api.routes import ai_tasks


# ==================================================
# Test Client
# ==================================================

client = TestClient(app)


# ==================================================
# Mock Task Factory
# ==================================================


def create_mock_task(
    task_id=1,
    article_id=100,
    task_type="analysis",
    status="WAITING",
    priority=0,
    retry_count=0
):
    """
    建立 Mock AITask。

    使用 SimpleNamespace
    模擬 AITask Model。

    Returns
    -------

    SimpleNamespace
    """

    return SimpleNamespace(

        id=task_id,

        article_id=article_id,

        task_type=task_type,

        status=status,

        priority=priority,

        retry_count=retry_count,

        created_time=None,

        finished_time=None

    )


# ==================================================
# Fixture
# ==================================================


@pytest.fixture
def mock_repository(monkeypatch):
    """
    Mock AITaskRepository。

    不連接 MySQL。

    每個 Test 都建立
    全新的 Mock Repository。
    """

    repository = MagicMock()

    monkeypatch.setattr(

        ai_tasks,

        "repository",

        repository

    )

    return repository


# ==================================================
# P3.4.1
#
# AI Task List API
# ==================================================


def test_get_ai_tasks(
    mock_repository
):
    """
    測試:

        GET /ai/tasks

    預期:

        HTTP 200

        success=True

        count 正確

        data 為 Task List
    """

    tasks = [

        create_mock_task(
            task_id=1,
            article_id=101
        ),

        create_mock_task(
            task_id=2,
            article_id=102
        )

    ]

    mock_repository.get_waiting_tasks.return_value = tasks

    response = client.get(
        "/ai/tasks"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    assert data["count"] == 2

    assert len(
        data["data"]
    ) == 2

    mock_repository.get_waiting_tasks.assert_called_once_with(
        limit=10
    )


# ==================================================
# P3.4.1
#
# AI Task List API
#
# Custom Limit
# ==================================================


def test_get_ai_tasks_with_limit(
    mock_repository
):
    """
    測試:

        GET /ai/tasks?limit=5

    確認 limit 正確傳給 Repository。
    """

    mock_repository.get_waiting_tasks.return_value = []

    response = client.get(
        "/ai/tasks?limit=5"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    assert data["count"] == 0

    mock_repository.get_waiting_tasks.assert_called_once_with(
        limit=5
    )


# ==================================================
# P3.4.1
#
# AI Task List API
#
# Invalid Limit
# ==================================================


def test_get_ai_tasks_invalid_limit(
    mock_repository
):
    """
    測試非法 limit。

    limit 必須:

        1 <= limit <= 100
    """

    response = client.get(
        "/ai/tasks?limit=0"
    )

    assert response.status_code == 422

    mock_repository.get_waiting_tasks.assert_not_called()


def test_get_ai_tasks_limit_over_max(
    mock_repository
):
    """
    測試超過最大 limit。
    """

    response = client.get(
        "/ai/tasks?limit=101"
    )

    assert response.status_code == 422

    mock_repository.get_waiting_tasks.assert_not_called()


# ==================================================
# P3.4.3
#
# Pending Task Count
# ==================================================


def test_get_pending_task_count(
    mock_repository
):
    """
    測試:

        GET /ai/tasks/pending/count
    """

    mock_repository.count_waiting_tasks.return_value = 25

    response = client.get(
        "/ai/tasks/pending/count"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    assert data["waiting"] == 25

    mock_repository.count_waiting_tasks.assert_called_once_with()


# ==================================================
# P3.4.3
#
# Pending Task Count = 0
# ==================================================


def test_get_pending_task_count_zero(
    mock_repository
):
    """
    測試沒有 WAITING Task。
    """

    mock_repository.count_waiting_tasks.return_value = 0

    response = client.get(
        "/ai/tasks/pending/count"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    assert data["waiting"] == 0


# ==================================================
# P3.4.2
#
# AI Task Detail
# ==================================================


def test_get_ai_task(
    mock_repository
):
    """
    測試:

        GET /ai/tasks/{task_id}
    """

    task = create_mock_task(
        task_id=10,
        article_id=500,
        status="WAITING"
    )

    mock_repository.find_by_id.return_value = task

    response = client.get(
        "/ai/tasks/10"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    assert data["data"]["id"] == 10

    assert data["data"]["article_id"] == 500

    assert data["data"]["status"] == "WAITING"

    mock_repository.find_by_id.assert_called_once_with(
        10
    )


# ==================================================
# P3.4.2
#
# AI Task Not Found
# ==================================================


def test_get_ai_task_not_found(
    mock_repository
):
    """
    測試不存在的 AI Task。

    預期:

        HTTP 404
    """

    mock_repository.find_by_id.return_value = None

    response = client.get(
        "/ai/tasks/999999"
    )

    assert response.status_code == 404

    data = response.json()

    assert data["detail"]["success"] is False

    assert (
        data["detail"]["message"]
        == "AI Task not found"
    )


# ==================================================
# P3.4.4
#
# Claim AI Task
# ==================================================


def test_claim_ai_task(
    mock_repository
):
    """
    測試:

        POST /ai/tasks/{task_id}/claim

    Lifecycle:

        WAITING
            ↓
        RUNNING
    """

    task = create_mock_task(
        task_id=20,
        article_id=600,
        status="RUNNING"
    )

    mock_repository.claim_task.return_value = task

    response = client.post(
        "/ai/tasks/20/claim"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    assert (
        data["message"]
        == "AI Task claimed successfully"
    )

    assert data["data"]["id"] == 20

    assert data["data"]["status"] == "RUNNING"

    mock_repository.claim_task.assert_called_once_with(
        20
    )


# ==================================================
# P3.4.4
#
# Claim Failed
# ==================================================


def test_claim_ai_task_conflict(
    mock_repository
):
    """
    測試 Claim 失敗。

    可能原因:

        Task 不存在

        或

        Task 已被其他 Worker Claim

    預期:

        HTTP 409
    """

    mock_repository.claim_task.return_value = None

    response = client.post(
        "/ai/tasks/20/claim"
    )

    assert response.status_code == 409

    data = response.json()

    assert data["detail"]["success"] is False

    assert (
        "cannot be claimed"
        in data["detail"]["message"]
    )


# ==================================================
# P3.4.5
#
# Mark AI Task Done
# ==================================================


def test_mark_ai_task_done(
    mock_repository
):
    """
    測試:

        POST /ai/tasks/{task_id}/done

    Lifecycle:

        RUNNING
            ↓
        DONE
    """

    completed_task = create_mock_task(
        task_id=30,
        article_id=700,
        status="DONE"
    )

    mock_repository.mark_done.return_value = True

    mock_repository.find_by_id.return_value = (
        completed_task
    )

    response = client.post(
        "/ai/tasks/30/done"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    assert (
        data["message"]
        == "AI Task marked as DONE"
    )

    assert data["data"]["id"] == 30

    assert data["data"]["status"] == "DONE"

    mock_repository.mark_done.assert_called_once_with(
        30
    )

    mock_repository.find_by_id.assert_called_once_with(
        30
    )


# ==================================================
# P3.4.5
#
# Mark Done Conflict
# ==================================================


def test_mark_ai_task_done_conflict(
    mock_repository
):
    """
    測試非法 DONE。

    例如:

        WAITING -> DONE

    Repository 應拒絕。

    預期:

        HTTP 409
    """

    mock_repository.mark_done.return_value = False

    response = client.post(
        "/ai/tasks/30/done"
    )

    assert response.status_code == 409

    data = response.json()

    assert data["detail"]["success"] is False

    assert (
        "cannot be marked DONE"
        in data["detail"]["message"]
    )

    mock_repository.find_by_id.assert_not_called()


# ==================================================
# P3.4.6
#
# Mark AI Task Failed
# ==================================================


def test_mark_ai_task_failed(
    mock_repository
):
    """
    測試:

        POST /ai/tasks/{task_id}/failed

    Lifecycle:

        RUNNING
            ↓
        FAILED

    同時:

        retry_count + 1
    """

    failed_task = create_mock_task(
        task_id=40,
        article_id=800,
        status="FAILED",
        retry_count=1
    )

    mock_repository.mark_failed.return_value = True

    mock_repository.find_by_id.return_value = (
        failed_task
    )

    response = client.post(
        "/ai/tasks/40/failed"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    assert (
        data["message"]
        == "AI Task marked as FAILED"
    )

    assert data["data"]["id"] == 40

    assert data["data"]["status"] == "FAILED"

    assert data["data"]["retry_count"] == 1

    mock_repository.mark_failed.assert_called_once_with(
        40
    )

    mock_repository.find_by_id.assert_called_once_with(
        40
    )


# ==================================================
# P3.4.6
#
# Mark Failed Conflict
# ==================================================


def test_mark_ai_task_failed_conflict(
    mock_repository
):
    """
    測試非法 FAILED。

    例如:

        WAITING -> FAILED

    Repository 應拒絕。

    預期:

        HTTP 409
    """

    mock_repository.mark_failed.return_value = False

    response = client.post(
        "/ai/tasks/40/failed"
    )

    assert response.status_code == 409

    data = response.json()

    assert data["detail"]["success"] is False

    assert (
        "cannot be marked FAILED"
        in data["detail"]["message"]
    )

    mock_repository.find_by_id.assert_not_called()


# ==================================================
# P3.4
#
# Task ID Validation
# ==================================================


def test_ai_task_invalid_task_id():
    """
    測試 task_id 必須為整數。
    """

    response = client.get(
        "/ai/tasks/abc"
    )

    assert response.status_code == 422


# ==================================================
# P3.4
#
# OpenAPI Registration
# ==================================================


def test_ai_task_routes_registered():
    """
    確認 P3.4 API 已註冊到 FastAPI OpenAPI。
    """

    openapi = app.openapi()

    paths = openapi["paths"]

    expected_paths = [

        "/ai/tasks",

        "/ai/tasks/pending/count",

        "/ai/tasks/{task_id}",

        "/ai/tasks/{task_id}/claim",

        "/ai/tasks/{task_id}/done",

        "/ai/tasks/{task_id}/failed"

    ]

    for path in expected_paths:

        assert path in paths


# ==================================================
# P3.4
#
# API Tags
# ==================================================


def test_ai_task_management_tag_registered():
    """
    確認 Swagger OpenAPI
    已註冊 AI Task Management Tag。
    """

    openapi = app.openapi()

    tags = openapi.get(
        "tags",
        []
    )

    tag_names = [

        tag["name"]

        for tag in tags

    ]

    assert (
        "AI Task Management"
        in tag_names
    )
