"""
tests/V5/test_target_api.py

AutoSearch V5

Target Management API Integration Test

測試：

    POST   /targets
    GET    /targets
    GET    /targets/active
    GET    /targets/{target_id}
    PATCH  /targets/{target_id}/status
    DELETE /targets/{target_id}

Validation：

    - URL Target 缺少 URL
    - Search Target 缺少 keyword
    - Search Target 缺少 search_provider
    - Invalid target_type
    - 查詢不存在 Target

重要：

    本測試會自動清理建立的測試 Target。

    測試完成後：
        測試 Target 會被 DELETE。

    不應留下測試資料。
"""


# ============================================================
#
# Imports
#
# ============================================================

import uuid

import pytest

import requests


# ============================================================
#
# Configuration
#
# ============================================================

BASE_URL = "http://127.0.0.1:8000"

TARGETS_URL = (
    f"{BASE_URL}/targets"
)


# ============================================================
#
# Helper
#
# ============================================================


def unique_name(
    prefix="pytest-target",
):
    """
    建立唯一測試 Target 名稱。
    """

    return (
        f"{prefix}-"
        f"{uuid.uuid4().hex[:12]}"
    )


def assert_success_response(
    response,
):
    """
    確認 API 回傳 HTTP 2xx。
    """

    assert response.status_code < 300, (
        f"Unexpected status code: "
        f"{response.status_code}\n"
        f"Response: {response.text}"
    )


# ============================================================
#
# Fixture
#
# ============================================================


@pytest.fixture
def cleanup_targets():

    """
    測試 Target Cleanup。

    測試開始：
        建立空的 cleanup list。

    測試期間：
        測試建立的 Target ID
        加入 cleanup list。

    測試結束：
        DELETE 所有測試 Target。

    即使測試失敗，
    pytest finalizer 仍會執行。
    """

    created_target_ids = []

    yield created_target_ids

    # ========================================================
    # Cleanup
    # ========================================================

    for target_id in created_target_ids:

        try:

            response = requests.delete(
                f"{TARGETS_URL}/{target_id}",
                timeout=10,
            )

            # 404 代表可能已經被測試本身刪除。
            assert response.status_code in (
                200,
                204,
                404,
            )

        except requests.RequestException:

            # Cleanup 不應該覆蓋原本的測試錯誤。
            pass


# ============================================================
#
# API Availability
#
# ============================================================


def test_target_api_available():
    """
    確認 Target API 可以連線。
    """

    response = requests.get(
        TARGETS_URL,
        timeout=10,
    )

    assert_success_response(
        response
    )

    data = response.json()

    assert data["status"] == "success"
    assert "targets" in data
    assert "count" in data


# ============================================================
#
# Create Target
#
# ============================================================


def test_create_url_target(
    cleanup_targets,
):
    """
    測試建立 Direct URL Target。
    """

    payload = {

        "name": unique_name(
            "pytest-url"
        ),

        "target_type": "url",

        "url": (
            "https://example.com"
        ),

        "keyword": "",

        "search_provider": "",

        "description": (
            "pytest temporary target"
        ),
    }

    response = requests.post(
        TARGETS_URL,
        json=payload,
        timeout=10,
    )

    assert response.status_code == 200, (
        f"Response: {response.text}"
    )

    data = response.json()

    assert data["status"] == "success"
    assert "target" in data

    target = data["target"]

    assert target["name"] == payload["name"]
    assert target["target_type"] == "url"
    assert target["url"] == payload["url"]

    assert "id" in target

    cleanup_targets.append(
        target["id"]
    )


def test_create_search_target(
    cleanup_targets,
):
    """
    測試建立 Keyword Search Target。
    """

    payload = {

        "name": unique_name(
            "pytest-search"
        ),

        "target_type": "search",

        "url": "",

        "keyword": "semiconductor",

        "search_provider": "google_news",

        "description": (
            "pytest temporary search target"
        ),
    }

    response = requests.post(
        TARGETS_URL,
        json=payload,
        timeout=10,
    )

    assert response.status_code == 200, (
        f"Response: {response.text}"
    )

    data = response.json()

    assert data["status"] == "success"

    target = data["target"]

    assert target["name"] == payload["name"]
    assert target["target_type"] == "search"
    assert target["keyword"] == payload["keyword"]
    assert (
        target["search_provider"]
        == payload["search_provider"]
    )

    cleanup_targets.append(
        target["id"]
    )


# ============================================================
#
# Get Targets
#
# ============================================================


def test_get_targets(
    cleanup_targets,
):
    """
    測試 GET /targets。
    """

    payload = {

        "name": unique_name(
            "pytest-get"
        ),

        "target_type": "url",

        "url": (
            "https://example.com"
        ),

        "description": (
            "pytest temporary target"
        ),
    }

    create_response = requests.post(
        TARGETS_URL,
        json=payload,
        timeout=10,
    )

    assert create_response.status_code == 200

    target_id = (
        create_response
        .json()["target"]["id"]
    )

    cleanup_targets.append(
        target_id
    )

    response = requests.get(
        TARGETS_URL,
        timeout=10,
    )

    assert_success_response(
        response
    )

    data = response.json()

    assert data["status"] == "success"
    assert isinstance(
        data["targets"],
        list,
    )

    ids = [
        target["id"]
        for target in data["targets"]
    ]

    assert target_id in ids


# ============================================================
#
# Get Active Targets
#
# ============================================================


def test_get_active_targets(
    cleanup_targets,
):
    """
    測試 GET /targets/active。
    """

    payload = {

        "name": unique_name(
            "pytest-active"
        ),

        "target_type": "url",

        "url": (
            "https://example.com"
        ),

        "description": (
            "pytest temporary active target"
        ),
    }

    create_response = requests.post(
        TARGETS_URL,
        json=payload,
        timeout=10,
    )

    assert create_response.status_code == 200

    target_id = (
        create_response
        .json()["target"]["id"]
    )

    cleanup_targets.append(
        target_id
    )

    response = requests.get(
        f"{TARGETS_URL}/active",
        timeout=10,
    )

    assert_success_response(
        response
    )

    data = response.json()

    assert data["status"] == "success"
    assert isinstance(
        data["targets"],
        list,
    )

    ids = [
        target["id"]
        for target in data["targets"]
    ]

    assert target_id in ids


# ============================================================
#
# Get Target By ID
#
# ============================================================


def test_get_target_by_id(
    cleanup_targets,
):
    """
    測試 GET /targets/{target_id}。
    """

    payload = {

        "name": unique_name(
            "pytest-by-id"
        ),

        "target_type": "url",

        "url": (
            "https://example.com"
        ),
    }

    create_response = requests.post(
        TARGETS_URL,
        json=payload,
        timeout=10,
    )

    assert create_response.status_code == 200

    target_id = (
        create_response
        .json()["target"]["id"]
    )

    cleanup_targets.append(
        target_id
    )

    response = requests.get(
        f"{TARGETS_URL}/{target_id}",
        timeout=10,
    )

    assert response.status_code == 200, (
        f"Response: {response.text}"
    )

    data = response.json()

    assert data["status"] == "success"

    target = data["target"]

    assert target["id"] == target_id
    assert target["name"] == payload["name"]


# ============================================================
#
# Update Status
#
# ============================================================


def test_update_target_status(
    cleanup_targets,
):
    """
    測試 PATCH /targets/{target_id}/status。
    """

    payload = {

        "name": unique_name(
            "pytest-status"
        ),

        "target_type": "url",

        "url": (
            "https://example.com"
        ),
    }

    create_response = requests.post(
        TARGETS_URL,
        json=payload,
        timeout=10,
    )

    assert create_response.status_code == 200

    target_id = (
        create_response
        .json()["target"]["id"]
    )

    cleanup_targets.append(
        target_id
    )

    response = requests.patch(
        f"{TARGETS_URL}/{target_id}/status",
        json={
            "status": "inactive"
        },
        timeout=10,
    )

    assert response.status_code == 200, (
        f"Response: {response.text}"
    )

    data = response.json()

    assert data["status"] == "success"
    assert data["target"]["id"] == target_id
    assert data["target"]["status"] == "inactive"


# ============================================================
#
# Delete Target
#
# ============================================================


def test_delete_target(
    cleanup_targets,
):
    """
    測試 DELETE /targets/{target_id}。

    注意：

        Target 在測試本身中刪除。

        Cleanup fixture 收到 404
        時視為正常。
    """

    payload = {

        "name": unique_name(
            "pytest-delete"
        ),

        "target_type": "url",

        "url": (
            "https://example.com"
        ),
    }

    create_response = requests.post(
        TARGETS_URL,
        json=payload,
        timeout=10,
    )

    assert create_response.status_code == 200

    target_id = (
        create_response
        .json()["target"]["id"]
    )

    cleanup_targets.append(
        target_id
    )

    response = requests.delete(
        f"{TARGETS_URL}/{target_id}",
        timeout=10,
    )

    assert response.status_code == 200, (
        f"Response: {response.text}"
    )

    data = response.json()

    assert data["status"] == "success"
    assert data["target_id"] == target_id

    # --------------------------------------------------------
    # Confirm deleted
    # --------------------------------------------------------

    get_response = requests.get(
        f"{TARGETS_URL}/{target_id}",
        timeout=10,
    )

    assert get_response.status_code == 404


# ============================================================
#
# Validation Tests
#
# ============================================================


def test_create_url_target_without_url():
    """
    URL Target 沒有 URL。

    預期：
        400
    """

    payload = {

        "name": unique_name(
            "pytest-invalid-url"
        ),

        "target_type": "url",

        "url": "",

    }

    response = requests.post(
        TARGETS_URL,
        json=payload,
        timeout=10,
    )

    assert response.status_code == 400

    data = response.json()

    assert (
        "requires 'url'"
        in data["detail"]
    )


def test_create_search_target_without_keyword():
    """
    Search Target 沒有 keyword。

    預期：
        400
    """

    payload = {

        "name": unique_name(
            "pytest-invalid-keyword"
        ),

        "target_type": "search",

        "url": "",

        "keyword": "",

        "search_provider": (
            "google_news"
        ),

    }

    response = requests.post(
        TARGETS_URL,
        json=payload,
        timeout=10,
    )

    assert response.status_code == 400

    data = response.json()

    assert (
        "requires 'keyword'"
        in data["detail"]
    )


def test_create_search_target_without_provider():
    """
    Search Target 沒有 search_provider。

    預期：
        400
    """

    payload = {

        "name": unique_name(
            "pytest-invalid-provider"
        ),

        "target_type": "search",

        "url": "",

        "keyword": "semiconductor",

        "search_provider": "",

    }

    response = requests.post(
        TARGETS_URL,
        json=payload,
        timeout=10,
    )

    assert response.status_code == 400

    data = response.json()

    assert (
        "requires 'search_provider'"
        in data["detail"]
    )


def test_create_target_invalid_type():
    """
    Invalid target_type。

    預期：
        400
    """

    payload = {

        "name": unique_name(
            "pytest-invalid-type"
        ),

        "target_type": "invalid",

        "url": "",
        "keyword": "",
        "search_provider": "",

    }

    response = requests.post(
        TARGETS_URL,
        json=payload,
        timeout=10,
    )

    assert response.status_code == 400

    data = response.json()

    assert (
        "Invalid target_type"
        in data["detail"]
    )


# ============================================================
#
# Not Found Tests
#
# ============================================================


def test_get_nonexistent_target():
    """
    查詢不存在 Target。

    預期：
        404
    """

    target_id = 999999999

    response = requests.get(
        f"{TARGETS_URL}/{target_id}",
        timeout=10,
    )

    assert response.status_code == 404


def test_delete_nonexistent_target():
    """
    刪除不存在 Target。

    預期：
        404
    """

    target_id = 999999999

    response = requests.delete(
        f"{TARGETS_URL}/{target_id}",
        timeout=10,
    )

    assert response.status_code == 404


# ============================================================
#
# End
#
# ============================================================
