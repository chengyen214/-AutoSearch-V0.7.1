"""
tests/p4/test_crawler.py

AutoSearch V4

P4.5 Generic Web Crawler

測試目前 crawler.py：

1. resolve_url()
2. fix_encoding()
3. download()
4. Redirect
5. HTML Download
6. Encoding Fix
7. Retry
8. 非 HTML
9. Download Failure
10. Custom Headers

注意：

本測試不修改 crawler.py。
不直接存取外部網站。
使用 mock 模擬 requests.get。
"""

from unittest.mock import Mock, patch

import requests


from crawler.crawler import (
    DEFAULT_HEADERS,
    resolve_url,
    fix_encoding,
    download,
)


# ==================================================
#
# resolve_url()
#
# ==================================================


def test_resolve_url_returns_redirected_url():
    """
    resolve_url()

    應回傳 requests 最終解析後的 URL。
    """

    response = Mock()

    response.url = (
        "https://example.com/article"
    )

    with patch(
        "crawler.crawler.requests.get",
        return_value=response,
    ) as mock_get:

        result = resolve_url(
            "https://example.com/redirect"
        )

    assert result == (
        "https://example.com/article"
    )

    mock_get.assert_called_once_with(
        "https://example.com/redirect",
        headers=DEFAULT_HEADERS,
        allow_redirects=True,
        timeout=10,
    )


def test_resolve_url_returns_original_url_on_failure():
    """
    resolve_url()

    requests 失敗時：
        回傳原始 URL。
    """

    url = (
        "https://example.com/redirect"
    )

    with patch(
        "crawler.crawler.requests.get",
        side_effect=requests.RequestException(
            "connection failed"
        ),
    ):

        result = resolve_url(
            url
        )

    assert result == url


def test_resolve_url_uses_custom_headers():
    """
    resolve_url()

    支援自訂 headers。
    """

    response = Mock()

    response.url = (
        "https://example.com/final"
    )

    headers = {
        "User-Agent": "Test-Agent"
    }

    with patch(
        "crawler.crawler.requests.get",
        return_value=response,
    ) as mock_get:

        result = resolve_url(
            "https://example.com/start",
            headers=headers,
        )

    assert result == (
        "https://example.com/final"
    )

    mock_get.assert_called_once_with(
        "https://example.com/start",
        headers=headers,
        allow_redirects=True,
        timeout=10,
    )


# ==================================================
#
# fix_encoding()
#
# ==================================================


def test_fix_encoding_sets_apparent_encoding():
    """
    fix_encoding()

    應使用 apparent_encoding
    修正 response.encoding。
    """

    response = Mock()

    response.apparent_encoding = (
        "utf-8"
    )

    response.text = (
        "<html>IC semiconductor</html>"
    )

    result = fix_encoding(
        response
    )

    assert response.encoding == "utf-8"

    assert result == (
        "<html>IC semiconductor</html>"
    )


def test_fix_encoding_without_apparent_encoding():
    """
    apparent_encoding 不存在時：

    不修改 encoding，
    仍回傳 response.text。
    """

    response = Mock()

    response.apparent_encoding = None

    response.text = (
        "<html>Test</html>"
    )

    result = fix_encoding(
        response
    )

    assert result == (
        "<html>Test</html>"
    )


# ==================================================
#
# download()
#
# ==================================================


def test_download_success():
    """
    download()

    正常 HTML：

        resolve_url
            ↓
        requests.get
            ↓
        raise_for_status
            ↓
        fix_encoding
            ↓
        return HTML
    """

    redirect_response = Mock()

    redirect_response.url = (
        "https://example.com/article"
    )

    html_response = Mock()

    html_response.headers = {
        "Content-Type":
        "text/html; charset=utf-8"
    }

    html_response.apparent_encoding = (
        "utf-8"
    )

    html_response.text = (
        "<html>"
        "<body>"
        "IC semiconductor"
        "</body>"
        "</html>"
    )

    with patch(
        "crawler.crawler.requests.get",
        side_effect=[
            redirect_response,
            html_response,
        ],
    ) as mock_get:

        with patch(
            "crawler.crawler.time.sleep"
        ):

            result = download(
                "https://example.com/redirect"
            )

    assert result == (
        "<html>"
        "<body>"
        "IC semiconductor"
        "</body>"
        "</html>"
    )

    assert mock_get.call_count == 2

    html_response.raise_for_status.assert_called_once()


def test_download_returns_none_for_non_html():
    """
    download()

    Content-Type 不是 text/html：

        應回傳 None。
    """

    redirect_response = Mock()

    redirect_response.url = (
        "https://example.com/file.pdf"
    )

    response = Mock()

    response.headers = {
        "Content-Type":
        "application/pdf"
    }

    with patch(
        "crawler.crawler.requests.get",
        side_effect=[
            redirect_response,
            response,
        ],
    ):

        with patch(
            "crawler.crawler.time.sleep"
        ) as mock_sleep:

            result = download(
                "https://example.com/file.pdf"
            )

    assert result is None

    mock_sleep.assert_not_called()


def test_download_retries_after_request_failure():
    """
    download()

    前兩次失敗，
    第三次成功。

    retry=3
    """

    redirect_response = Mock()

    redirect_response.url = (
        "https://example.com/article"
    )

    success_response = Mock()

    success_response.headers = {
        "Content-Type":
        "text/html; charset=utf-8"
    }

    success_response.apparent_encoding = (
        "utf-8"
    )

    success_response.text = (
        "<html>success</html>"
    )

    with patch(
        "crawler.crawler.requests.get",
        side_effect=[
            redirect_response,

            requests.RequestException(
                "timeout"
            ),

            requests.RequestException(
                "connection error"
            ),

            success_response,
        ],
    ) as mock_get:

        with patch(
            "crawler.crawler.time.sleep"
        ):

            result = download(
                "https://example.com/article",
                retry=3,
            )

    assert result == (
        "<html>success</html>"
    )

    # resolve_url 1 次
    # download retry 3 次
    assert mock_get.call_count == 4

    success_response.raise_for_status.assert_called_once()


def test_download_returns_none_after_all_retries_fail():
    """
    download()

    所有 retry 都失敗：

        應回傳 None。
    """

    redirect_response = Mock()

    redirect_response.url = (
        "https://example.com/article"
    )

    with patch(
        "crawler.crawler.requests.get",
        side_effect=[
            redirect_response,

            requests.RequestException(
                "error 1"
            ),

            requests.RequestException(
                "error 2"
            ),

            requests.RequestException(
                "error 3"
            ),
        ],
    ) as mock_get:

        with patch(
            "crawler.crawler.time.sleep"
        ):

            result = download(
                "https://example.com/article",
                retry=3,
            )

    assert result is None

    # resolve_url 1 次
    # retry 3 次
    assert mock_get.call_count == 4


def test_download_uses_custom_headers():
    """
    download()

    應將自訂 headers
    傳遞給 resolve_url 與 requests.get。
    """

    headers = {
        "User-Agent": "AutoSearch-Test"
    }

    redirect_response = Mock()

    redirect_response.url = (
        "https://example.com/article"
    )

    html_response = Mock()

    html_response.headers = {
        "Content-Type":
        "text/html"
    }

    html_response.apparent_encoding = (
        "utf-8"
    )

    html_response.text = (
        "<html>test</html>"
    )

    with patch(
        "crawler.crawler.requests.get",
        side_effect=[
            redirect_response,
            html_response,
        ],
    ) as mock_get:

        with patch(
            "crawler.crawler.time.sleep"
        ):

            result = download(
                "https://example.com/article",
                headers=headers,
            )

    assert result == (
        "<html>test</html>"
    )

    assert mock_get.call_count == 2

    # resolve_url
    mock_get.call_args_list[0].assert_called_once_with(
        "https://example.com/article",
        headers=headers,
        allow_redirects=True,
        timeout=10,
    )

    # download
    mock_get.call_args_list[1].assert_called_once_with(
        "https://example.com/article",
        headers=headers,
        timeout=7,
    )


# ==================================================
#
# retry=0
#
# ==================================================


def test_download_with_zero_retry_returns_none():
    """
    retry=0

    不執行 download retry loop。
    """

    redirect_response = Mock()

    redirect_response.url = (
        "https://example.com/article"
    )

    with patch(
        "crawler.crawler.requests.get",
        return_value=redirect_response,
    ) as mock_get:

        with patch(
            "crawler.crawler.time.sleep"
        ):

            result = download(
                "https://example.com/article",
                retry=0,
            )

    assert result is None

    # 只有 resolve_url
    assert mock_get.call_count == 1


# ==================================================
#
# Module Export Test
#
# ==================================================


def test_default_headers_exist():
    """
    確認 crawler.py 的
    DEFAULT_HEADERS 正常存在。
    """

    assert isinstance(
        DEFAULT_HEADERS,
        dict,
    )

    assert (
        "User-Agent"
        in DEFAULT_HEADERS
    )

    assert (
        "Accept-Language"
        in DEFAULT_HEADERS
    )