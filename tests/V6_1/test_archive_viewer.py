"""
tests/V6_1/test_archive_viewer.py

AutoSearch V6.1

Archive Viewer Test

Test URL:
https://news.pchome.com.tw/finance/sunmedia/20260330/index-77484256473773329003.html
"""

from fastapi.testclient import TestClient

from api.main import app

from api.routes.archive_viewer import (
    normalize_url,
    find_snapshot_history,
    find_snapshot,
    extract_html,
)


# ============================================================
# Test URL
# ============================================================

TEST_URL = (
    "https://news.pchome.com.tw/finance/sunmedia/"
    "20260330/index-77484256473773329003.html"
)


# ============================================================
# FastAPI Test Client
# ============================================================

client = TestClient(app)


# ============================================================
# Test normalize_url
# ============================================================

def test_normalize_url():

    result = normalize_url(
        TEST_URL
    )

    print()
    print("=== Normalize URL ===")
    print(result)

    assert result == TEST_URL


# ============================================================
# Test Snapshot History
# ============================================================

def test_find_snapshot_history():

    versions = find_snapshot_history(
        TEST_URL
    )

    print()
    print("=== Snapshot History ===")
    print(versions)

    assert isinstance(
        versions,
        list,
    )

    # --------------------------------------------------------
    # 如果 MongoDB 已經有 Snapshot
    # --------------------------------------------------------

    if versions:

        for version in versions:

            assert "version" in version

            assert "created_at" in version

            assert version["version"]

            assert version["created_at"]

        print(
            f"Snapshot count: {len(versions)}"
        )

    else:

        print(
            "No Snapshot found."
        )


# ============================================================
# Test Snapshot + HTML
# ============================================================

def test_find_snapshot_and_html():

    versions = find_snapshot_history(
        TEST_URL
    )

    print()
    print("=== Snapshot Count ===")
    print(len(versions))

    # --------------------------------------------------------
    # MongoDB 尚未有 Snapshot
    # --------------------------------------------------------

    if not versions:

        print(
            "No Snapshot found."
        )

        return

    # --------------------------------------------------------
    # 取得最新 Snapshot
    # --------------------------------------------------------

    latest_version = versions[0]

    created_at = latest_version[
        "created_at"
    ]

    print()
    print("=== Latest Snapshot ===")
    print(
        created_at
    )

    # --------------------------------------------------------
    # Find Snapshot
    # --------------------------------------------------------

    snapshot = find_snapshot(
        TEST_URL,
        created_at,
    )

    assert snapshot is not None

    print()
    print("=== Snapshot ===")

    print(
        {
            key: value
            for key, value in snapshot.items()
            if key != "html"
        }
    )

    # --------------------------------------------------------
    # Extract HTML
    # --------------------------------------------------------

    html = extract_html(
        snapshot
    )

    assert html is not None

    assert isinstance(
        html,
        str,
    )

    assert len(html) > 0

    print()
    print("=== HTML ===")
    print(
        f"HTML length: {len(html)}"
    )

    print(
        html[:500]
    )


# ============================================================
# Test GET /archive/view?url=...
# ============================================================

def test_archive_view_endpoint():

    """
    測試：

        GET /archive/view?url=...

    驗證：

        1. Endpoint 可以正常回應
        2. HTTP Status = 200
        3. 回傳 HTML
        4. Article Archive 頁面存在
        5. 原始 URL 存在
        6. Snapshot History 存在
        7. 初次進入不載入 Raw HTML
    """

    response = client.get(
        "/archive/view",
        params={
            "url": TEST_URL,
        },
    )

    print()
    print("=== Archive View Endpoint ===")

    print(
        "Status:",
        response.status_code,
    )

    print(
        "Content-Type:",
        response.headers.get(
            "content-type"
        ),
    )

    print(
        "Response length:",
        len(response.text),
    )

    # --------------------------------------------------------
    # HTTP Status
    # --------------------------------------------------------

    assert response.status_code == 200

    # --------------------------------------------------------
    # Content-Type
    # --------------------------------------------------------

    assert (
        "text/html"
        in response.headers.get(
            "content-type",
            "",
        )
    )

    # --------------------------------------------------------
    # Page
    # --------------------------------------------------------

    assert (
        "Article Archive"
        in response.text
    )

    # --------------------------------------------------------
    # URL
    # --------------------------------------------------------

    assert (
        TEST_URL
        in response.text
    )

    # --------------------------------------------------------
    # Snapshot History
    # --------------------------------------------------------

    assert (
        "歷史版本"
        in response.text
    )

    # --------------------------------------------------------
    # 初次進入：
    #
    # GET /archive/view?url=...
    #
    # 沒有指定 version
    # 因此不應該直接載入 Snapshot HTML
    #
    # viewer 應該顯示：
    #
    # 「選擇歷史版本」
    # --------------------------------------------------------

    assert (
        "選擇歷史版本"
        in response.text
    )
# ============================================================
# Test GET /archive/view?url=...&version=...
# ============================================================

def test_archive_view_endpoint_with_version():

    """
    測試：

        GET /archive/view?url=...&version=...

    驗證：

        1. Endpoint 可以正常回應
        2. HTTP Status = 200
        3. 回傳 HTML
        4. 指定 Snapshot 存在
        5. 指定版本被選取
        6. Raw HTML 被載入
    """

    # --------------------------------------------------------
    # 取得 Snapshot History
    # --------------------------------------------------------

    versions = find_snapshot_history(
        TEST_URL
    )

    print()
    print("=== Archive View Version Test ===")

    print(
        "Snapshot count:",
        len(versions),
    )

    assert isinstance(
        versions,
        list,
    )

    # --------------------------------------------------------
    # 必須至少有一個 Snapshot
    # --------------------------------------------------------

    if not versions:

        print(
            "No Snapshot found."
        )

        return

    # --------------------------------------------------------
    # 使用最新 Snapshot
    # --------------------------------------------------------

    latest_version = versions[0]

    version = latest_version[
        "version"
    ]

    created_at = latest_version[
        "created_at"
    ]

    print(
        "Selected version:",
        version,
    )

    print(
        "Created at:",
        created_at,
    )

    # --------------------------------------------------------
    # GET /archive/view?url=...&version=...
    # --------------------------------------------------------

    response = client.get(
        "/archive/view",
        params={
            "url": TEST_URL,
            "version": version,
        },
    )

    print()
    print(
        "Status:",
        response.status_code,
    )

    print(
        "Content-Type:",
        response.headers.get(
            "content-type"
        ),
    )

    print(
        "Response length:",
        len(response.text),
    )

    # --------------------------------------------------------
    # HTTP Status
    # --------------------------------------------------------

    assert response.status_code == 200

    # --------------------------------------------------------
    # Content-Type
    # --------------------------------------------------------

    assert (
        "text/html"
        in response.headers.get(
            "content-type",
            "",
        )
    )

    # --------------------------------------------------------
    # Page
    # --------------------------------------------------------

    assert (
        "Article Archive"
        in response.text
    )

    # --------------------------------------------------------
    # Snapshot History
    # --------------------------------------------------------

    assert (
        "歷史版本"
        in response.text
    )

    # --------------------------------------------------------
    # 指定版本應該被選取
    # --------------------------------------------------------

    assert (
        "selected"
        in response.text
    )

    # --------------------------------------------------------
    # 指定版本時間應該出現在頁面
    #
    # version 是 ISO datetime string
    # 頁面通常會將它格式化成日期時間。
    # 因此這裡驗證 Snapshot viewer 已經進入
    # selected version 狀態，而不是直接比對完整字串。
    # --------------------------------------------------------

    # --------------------------------------------------------
    # Raw HTML 應該被載入
    #
    # 你的 Archive HTML 有：
    #
    # <!DOCTYPE HTML>
    # <html>
    #
    # 因此 response 應該包含 iframe srcdoc。
    # --------------------------------------------------------

    assert (
        "iframe"
        in response.text
    )

    assert (
        "Archived HTML"
        in response.text
    )

    assert (
        "srcdoc="
        in response.text
    )

    # --------------------------------------------------------
    # 不應顯示「選擇歷史版本」
    #
    # 因為現在已經指定 version。
    # --------------------------------------------------------

    assert (
        "選擇歷史版本"
        not in response.text
    )

    print()
    print(
        "Specified snapshot HTML loaded successfully."
    )