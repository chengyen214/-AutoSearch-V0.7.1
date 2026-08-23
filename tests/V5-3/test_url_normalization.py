"""
tests/V5-3/test_url_normalization.py

AutoSearch V5

V5.3 P3.6

URL Normalization Tests

測試：

    - URL 前後空白移除
    - HTTP URL
    - HTTPS URL
    - Query String 保留
    - Path 保留
    - Fragment 保留
    - URL 大小寫不自行修改
    - URL 原始結構不被重新組裝
    - None URL 拒絕
    - Empty URL 拒絕
    - Invalid Scheme 拒絕
    - Missing Host 拒絕
    - Normalization Idempotency

注意：

    P3.6 目前的 URL Normalization
    只負責：

        1. 驗證 URL
        2. 去除前後空白

    不負責：

        - 自動補 /
        - 移除 /
        - hostname lowercase
        - query parameter 排序
        - query parameter 移除
        - fragment 移除
        - www 統一
        - tracking parameter 移除

    以上行為目前不屬於 P3.6 的既有規格。
"""


import pytest

from utils.target_validator import (
    TargetValidator,
)


# ==================================================
# Basic Normalization
# ==================================================


def test_normalize_url_removes_surrounding_spaces():
    """
    URL 前後空白應該被移除。
    """

    result = TargetValidator.normalize_url(
        "  https://example.com  "
    )

    assert result == (
        "https://example.com"
    )


def test_normalize_url_removes_newline_and_tab_spaces():
    """
    URL 前後的 whitespace 應該被移除。
    """

    result = TargetValidator.normalize_url(
        "\n\thttps://example.com\t\n"
    )

    assert result == (
        "https://example.com"
    )


# ==================================================
# HTTP / HTTPS
# ==================================================


def test_normalize_http_url():
    """
    HTTP URL 應該保持 http scheme。
    """

    url = (
        "http://example.com"
    )

    result = TargetValidator.normalize_url(
        url
    )

    assert result == url


def test_normalize_https_url():
    """
    HTTPS URL 應該保持 https scheme。
    """

    url = (
        "https://example.com"
    )

    result = TargetValidator.normalize_url(
        url
    )

    assert result == url


# ==================================================
# Path
# ==================================================


def test_normalize_url_preserves_path():
    """
    URL Path 不應該被修改。
    """

    url = (
        "https://example.com/"
        "news/semiconductor/article"
    )

    result = TargetValidator.normalize_url(
        url
    )

    assert result == url


def test_normalize_url_preserves_nested_path():
    """
    Nested Path 不應該被修改。
    """

    url = (
        "https://example.com/"
        "company/news/2026/08/article"
    )

    result = TargetValidator.normalize_url(
        url
    )

    assert result == url


# ==================================================
# Query String
# ==================================================


def test_normalize_url_preserves_query_string():
    """
    Query String 必須保留。
    """

    url = (
        "https://example.com/search"
        "?keyword=semiconductor"
    )

    result = TargetValidator.normalize_url(
        url
    )

    assert result == url


def test_normalize_url_preserves_multiple_query_parameters():
    """
    Multiple Query Parameters 必須保留。
    """

    url = (
        "https://example.com/search"
        "?keyword=semiconductor"
        "&page=2"
        "&limit=20"
    )

    result = TargetValidator.normalize_url(
        url
    )

    assert result == url


# ==================================================
# Fragment
# ==================================================


def test_normalize_url_preserves_fragment():
    """
    Fragment 目前不應該被自行移除。
    """

    url = (
        "https://example.com/article"
        "#section-1"
    )

    result = TargetValidator.normalize_url(
        url
    )

    assert result == url


# ==================================================
# Case Preservation
# ==================================================


def test_normalize_url_does_not_change_hostname_case():
    """
    P3.6 目前不負責 hostname lowercase。

    因此：

        EXAMPLE.COM

    不應該被自行轉成：

        example.com
    """

    url = (
        "https://EXAMPLE.COM/article"
    )

    result = TargetValidator.normalize_url(
        url
    )

    assert result == url


def test_normalize_url_does_not_change_path_case():
    """
    URL Path 大小寫不應該被修改。
    """

    url = (
        "https://example.com/"
        "News/Semiconductor"
    )

    result = TargetValidator.normalize_url(
        url
    )

    assert result == url


# ==================================================
# Trailing Slash
# ==================================================


def test_normalize_url_does_not_add_trailing_slash():
    """
    P3.6 目前不自動補 trailing slash。
    """

    url = (
        "https://example.com"
    )

    result = TargetValidator.normalize_url(
        url
    )

    assert result == (
        "https://example.com"
    )


def test_normalize_url_does_not_remove_trailing_slash():
    """
    P3.6 目前不移除 trailing slash。
    """

    url = (
        "https://example.com/"
    )

    result = TargetValidator.normalize_url(
        url
    )

    assert result == (
        "https://example.com/"
    )


def test_urls_with_and_without_trailing_slash_are_currently_distinct():
    """
    目前規格不會把：

        https://example.com

    與：

        https://example.com/

    自動視為相同 URL。
    """

    without_slash = (
        TargetValidator.normalize_url(
            "https://example.com"
        )
    )

    with_slash = (
        TargetValidator.normalize_url(
            "https://example.com/"
        )
    )

    assert without_slash != with_slash


# ==================================================
# Invalid URL
# ==================================================


def test_normalize_none_url_is_rejected():
    """
    None URL 應該被拒絕。
    """

    with pytest.raises(
        ValueError,
        match="url cannot be empty",
    ):

        TargetValidator.normalize_url(
            None
        )


def test_normalize_empty_url_is_rejected():
    """
    Empty URL 應該被拒絕。
    """

    with pytest.raises(
        ValueError,
        match="url cannot be empty",
    ):

        TargetValidator.normalize_url(
            ""
        )


def test_normalize_whitespace_only_url_is_rejected():
    """
    只有 whitespace 的 URL 應該被拒絕。
    """

    with pytest.raises(
        ValueError,
        match="url cannot be empty",
    ):

        TargetValidator.normalize_url(
            "   "
        )


def test_normalize_url_without_scheme_is_rejected():
    """
    缺少 scheme 的 URL 應該被拒絕。
    """

    with pytest.raises(
        ValueError,
        match="url must use http or https",
    ):

        TargetValidator.normalize_url(
            "example.com"
        )


def test_normalize_url_with_invalid_scheme_is_rejected():
    """
    非 HTTP / HTTPS scheme 應該被拒絕。
    """

    with pytest.raises(
        ValueError,
        match="url must use http or https",
    ):

        TargetValidator.normalize_url(
            "ftp://example.com"
        )


def test_normalize_url_without_host_is_rejected():
    """
    缺少 host 的 URL 應該被拒絕。
    """

    with pytest.raises(
        ValueError,
        match="url must contain a valid host",
    ):

        TargetValidator.normalize_url(
            "https:///article"
        )


# ==================================================
# Idempotency
# ==================================================


def test_normalize_url_is_idempotent():
    """
    URL Normalization 應該具備 Idempotency。

    normalize(
        normalize(url)
    )

    應該等於：

        normalize(url)
    """

    url = (
        "  https://example.com/"
        "news?id=100#section  "
    )

    first = (
        TargetValidator.normalize_url(
            url
        )
    )

    second = (
        TargetValidator.normalize_url(
            first
        )
    )

    assert second == first


# ==================================================
# Different URLs
# ==================================================


def test_normalize_different_urls_remain_different():
    """
    不同 URL 不應該被錯誤合併。
    """

    first = (
        TargetValidator.normalize_url(
            "https://example.com/a"
        )
    )

    second = (
        TargetValidator.normalize_url(
            "https://example.com/b"
        )
    )

    assert first != second


def test_normalize_different_query_values_remain_different():
    """
    不同 Query Value 不應該被合併。
    """

    first = (
        TargetValidator.normalize_url(
            "https://example.com/search?q=AI"
        )
    )

    second = (
        TargetValidator.normalize_url(
            "https://example.com/search?q=TSMC"
        )
    )

    assert first != second
