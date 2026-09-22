"""
tests/V7_6/test_archive_link.py

AutoSearch V7

Archive Viewer
/archive/link Route Unit Test

用途：
    不連 MongoDB。

    使用正式 FastAPI app 測試：

        /archive/link

    並 mock：

        find_latest_snapshot_version()

    驗證：

    1. MongoDB 有 Snapshot
       -> 導向 /archive/snapshot

    2. MongoDB 沒有 Snapshot
       -> 導向原始外部 URL

    3. 原始 URL 包含 fragment
       -> 有 Snapshot 時 fragment 保留

    4. 原始 URL 包含 query + fragment
       -> Snapshot URL 正確建立

    5. HTTP URL
       -> 正確導向 Snapshot

執行：

    python -m tests.V7_6.test_archive_link
"""


# ============================================================
# Imports
# ============================================================

from fastapi.testclient import TestClient

import api.routes.archive_viewer as archive_viewer
from api.main import app


# ============================================================
# Test Client
# ============================================================

client = TestClient(
    app,
    follow_redirects=False,
)


# ============================================================
# Test Helper
# ============================================================

def run_test(
    name: str,
    target_url: str,
    snapshot_version,
    expected_status: int,
    expected_location: str,
):
    """
    執行單一 /archive/link 測試。

    注意：
        不連 MongoDB。

        透過 monkey patch：

            find_latest_snapshot_version()

        模擬 MongoDB 查詢結果。
    """

    print("=" * 70)
    print(f"TEST: {name}")
    print("=" * 70)

    # --------------------------------------------------------
    # 保存原始函式
    # --------------------------------------------------------

    original_function = (
        archive_viewer.find_latest_snapshot_version
    )

    try:

        # ----------------------------------------------------
        # Mock MongoDB Snapshot Lookup
        # ----------------------------------------------------

        archive_viewer.find_latest_snapshot_version = (
            lambda url: snapshot_version
        )

        # ----------------------------------------------------
        # 呼叫正式 FastAPI App
        # ----------------------------------------------------

        response = client.get(
            "/archive/link",
            params={
                "url": target_url,
            },
        )

    finally:

        # ----------------------------------------------------
        # 還原原始函式
        # ----------------------------------------------------

        archive_viewer.find_latest_snapshot_version = (
            original_function
        )

    # ========================================================
    # Output
    # ========================================================

    print()
    print("TARGET URL:")
    print(target_url)

    print()
    print("STATUS:")
    print(response.status_code)

    print()
    print("LOCATION:")
    print(response.headers.get("location"))

    print()
    print("EXPECTED STATUS:")
    print(expected_status)

    print()
    print("EXPECTED LOCATION:")
    print(expected_location)

    print()

    # ========================================================
    # Status Validation
    # ========================================================

    if response.status_code != expected_status:

        print("❌ FAILED")

        raise AssertionError(
            "Unexpected status code: "
            f"{response.status_code}"
        )

    # ========================================================
    # Location Validation
    # ========================================================

    actual_location = response.headers.get(
        "location"
    )

    if actual_location != expected_location:

        print("❌ FAILED")

        print()
        print("Actual:")
        print(repr(actual_location))

        print()
        print("Expected:")
        print(repr(expected_location))

        raise AssertionError(
            f"Unexpected redirect location: {name}"
        )

    # ========================================================
    # PASS
    # ========================================================

    print("✅ PASSED")
    print()


# ============================================================
# Main
# ============================================================

def main():

    # ========================================================
    # 1. Snapshot Exists
    # ========================================================

    target_url = (
        "https://example.com/news/article-001"
    )

    expected_location = (
        "/archive/snapshot"
        "?url="
        "https%3A%2F%2Fexample.com%2Fnews%2Farticle-001"
        "&version=v1"
    )

    run_test(
        name=(
            "Snapshot exists -> "
            "archive snapshot"
        ),
        target_url=target_url,
        snapshot_version="v1",
        expected_status=307,
        expected_location=expected_location,
    )

    # ========================================================
    # 2. Snapshot Does Not Exist
    # ========================================================

    target_url = (
        "https://example.com/news/article-002"
    )

    expected_location = target_url

    run_test(
        name=(
            "Snapshot does not exist -> "
            "external URL"
        ),
        target_url=target_url,
        snapshot_version=None,
        expected_status=307,
        expected_location=expected_location,
    )

    # ========================================================
    # 3. Snapshot + Fragment
    # ========================================================

    target_url = (
        "https://example.com/news/article-003"
        "#comments"
    )

    expected_location = (
        "/archive/snapshot"
        "?url="
        "https%3A%2F%2Fexample.com%2Fnews%2Farticle-003"
        "&version=v2"
        "#comments"
    )

    run_test(
        name=(
            "Snapshot exists -> "
            "fragment preserved"
        ),
        target_url=target_url,
        snapshot_version="v2",
        expected_status=307,
        expected_location=expected_location,
    )

    # ========================================================
    # 4. Query + Fragment
    # ========================================================

    target_url = (
        "https://example.com/news/article-004"
        "?page=2"
        "#comments"
    )

    expected_location = (
        "/archive/snapshot"
        "?url="
        "https%3A%2F%2Fexample.com%2Fnews%2Farticle-004"
        "%3Fpage%3D2"
        "&version=v3"
        "#comments"
    )

    run_test(
        name=(
            "Snapshot exists -> "
            "query and fragment preserved"
        ),
        target_url=target_url,
        snapshot_version="v3",
        expected_status=307,
        expected_location=expected_location,
    )

    # ========================================================
    # 5. HTTP URL
    # ========================================================

    target_url = (
        "http://example.com/news/article-005"
    )

    expected_location = (
        "/archive/snapshot"
        "?url="
        "http%3A%2F%2Fexample.com%2Fnews%2Farticle-005"
        "&version=v4"
    )

    run_test(
        name=(
            "HTTP URL -> "
            "archive snapshot"
        ),
        target_url=target_url,
        snapshot_version="v4",
        expected_status=307,
        expected_location=expected_location,
    )

    # ========================================================
    # Completed
    # ========================================================

    print("=" * 70)
    print(
        "ALL ARCHIVE LINK ROUTE TESTS PASSED"
    )
    print("=" * 70)


# ============================================================
# Entry Point
# ============================================================

if __name__ == "__main__":
    main()