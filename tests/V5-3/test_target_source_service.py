"""
tests/V5-3/test_target_source_service.py

AutoSearch V5

V5.3 P3.4

Target Source Resolution Tests

測試：

    - TargetSourceService
    - URL Target → Direct URL
    - Search Target → Search Provider
    - Google Search
    - Google News
    - Target Type Resolution
    - Provider Resolution
    - Invalid Target
    - Invalid Provider
"""


import pytest

from models.target import Target

from services.target_source_service import (
    TargetSourceService,
)


# ==================================================
# Fixtures
# ==================================================


@pytest.fixture
def service():
    """
    建立 TargetSourceService。
    """

    return TargetSourceService()


@pytest.fixture
def url_target():
    """
    建立 URL Target。
    """

    return Target(
        name="Example",
        target_type="url",
        url="https://example.com",
        description="Example URL",
        status="active",
    )


@pytest.fixture
def search_target():
    """
    建立 Google Search Target。
    """

    return Target(
        name="Semiconductor Search",
        target_type="search",
        keyword="semiconductor",
        search_provider="google_search",
        description="Semiconductor search",
        status="active",
    )


@pytest.fixture
def google_search_target():
    """
    建立 Google Search Target。
    """

    return Target(
        name="Google Search",
        target_type="search",
        keyword="TSMC",
        search_provider="google_search",
        status="active",
    )


@pytest.fixture
def google_news_target():
    """
    建立 Google News Target。
    """

    return Target(
        name="Google News",
        target_type="search",
        keyword="AI",
        search_provider="google_news",
        status="active",
    )


# ==================================================
# Service Instance
# ==================================================


def test_service_instance():
    """
    TargetSourceService 可以正常建立。
    """

    service = TargetSourceService()

    assert isinstance(
        service,
        TargetSourceService,
    )


# ==================================================
# Resolve
# ==================================================


def test_resolve_url_target(
    service,
    url_target,
):
    """
    URL Target 應解析成 Direct URL Source。
    """

    source = service.resolve(
        url_target
    )

    assert source["source_type"] == "direct_url"
    assert source["url"] == "https://example.com"


def test_resolve_search_target(
    service,
    search_target,
):
    """
    Search Target 應解析成 Search Source。
    """

    source = service.resolve(
        search_target
    )

    assert source["source_type"] == "search"
    assert source["keyword"] == "semiconductor"
    assert source["provider"] == "google_search"


# ==================================================
# URL Target
# ==================================================


def test_resolve_url_target_direct_url(
    service,
    url_target,
):
    """
    resolve_url_target() 應建立 Direct URL Source。
    """

    source = service.resolve_url_target(
        url_target
    )

    assert source == {
        "source_type": "direct_url",
        "url": "https://example.com",
    }


def test_is_url_target(
    service,
    url_target,
):
    """
    URL Target 應判斷為 True。
    """

    assert service.is_url_target(
        url_target
    ) is True


def test_url_target_is_not_search_target(
    service,
    url_target,
):
    """
    URL Target 不應被判斷為 Search Target。
    """

    assert service.is_search_target(
        url_target
    ) is False


# ==================================================
# Search Target
# ==================================================


def test_is_search_target(
    service,
    search_target,
):
    """
    Search Target 應判斷為 True。
    """

    assert service.is_search_target(
        search_target
    ) is True


def test_search_target_is_not_url_target(
    service,
    search_target,
):
    """
    Search Target 不應被判斷為 URL Target。
    """

    assert service.is_url_target(
        search_target
    ) is False


# ==================================================
# Google Search
# ==================================================


def test_resolve_google_search(
    service,
    google_search_target,
):
    """
    Google Search Target 應解析成 google_search。
    """

    source = service.resolve_google_search(
        google_search_target
    )

    assert source["source_type"] == "search"
    assert source["keyword"] == "TSMC"
    assert source["provider"] == "google_search"


def test_is_google_search(
    service,
    google_search_target,
):
    """
    Google Search Target 應判斷為 True。
    """

    assert service.is_google_search(
        google_search_target
    ) is True


def test_google_search_is_not_google_news(
    service,
    google_search_target,
):
    """
    Google Search 不應判斷為 Google News。
    """

    assert service.is_google_news(
        google_search_target
    ) is False


# ==================================================
# Google News
# ==================================================


def test_resolve_google_news(
    service,
    google_news_target,
):
    """
    Google News Target 應解析成 google_news。
    """

    source = service.resolve_google_news(
        google_news_target
    )

    assert source["source_type"] == "search"
    assert source["keyword"] == "AI"
    assert source["provider"] == "google_news"


def test_is_google_news(
    service,
    google_news_target,
):
    """
    Google News Target 應判斷為 True。
    """

    assert service.is_google_news(
        google_news_target
    ) is True


def test_google_news_is_not_google_search(
    service,
    google_news_target,
):
    """
    Google News 不應判斷為 Google Search。
    """

    assert service.is_google_search(
        google_news_target
    ) is False


# ==================================================
# Source Type
# ==================================================


def test_get_source_type_for_url(
    service,
    url_target,
):
    """
    URL Target 對應 direct_url。
    """

    assert service.get_source_type(
        url_target
    ) == "direct_url"


def test_get_source_type_for_search(
    service,
    search_target,
):
    """
    Search Target 對應 search。
    """

    assert service.get_source_type(
        search_target
    ) == "search"


# ==================================================
# Provider
# ==================================================


def test_get_provider_for_search(
    service,
    search_target,
):
    """
    Search Target 應回傳 Provider。
    """

    assert service.get_provider(
        search_target
    ) == "google_search"


def test_get_provider_for_url(
    service,
    url_target,
):
    """
    URL Target 沒有 Provider。
    """

    assert service.get_provider(
        url_target
    ) is None


# ==================================================
# Provider Support
# ==================================================


def test_google_search_provider_supported(
    service,
):
    """
    Google Search Provider 應受支援。
    """

    assert service.is_supported_provider(
        "google_search"
    ) is True


def test_google_news_provider_supported(
    service,
):
    """
    Google News Provider 應受支援。
    """

    assert service.is_supported_provider(
        "google_news"
    ) is True


def test_unknown_provider_not_supported(
    service,
):
    """
    未知 Provider 不應受支援。
    """

    assert service.is_supported_provider(
        "unknown"
    ) is False


def test_none_provider_not_supported(
    service,
):
    """
    None Provider 不應受支援。
    """

    assert service.is_supported_provider(
        None
    ) is False


# ==================================================
# Invalid Target
# ==================================================


@pytest.mark.parametrize(
    "method_name",
    [
        "resolve",
        "resolve_url_target",
        "resolve_search_target",
        "is_url_target",
        "is_search_target",
        "is_google_search",
        "is_google_news",
        "get_source_type",
        "get_provider",
    ],
)
def test_invalid_target_object(
    service,
    method_name,
):
    """
    所有需要 Target 的方法，
    收到非 Target 物件時應拋出 TypeError。
    """

    method = getattr(
        service,
        method_name,
    )

    with pytest.raises(TypeError):
        method("invalid")


# ==================================================
# Invalid Target Type
# ==================================================


def test_unsupported_target_type(
    service,
):
    """
    不支援的 Target Type 應拋出 ValueError。
    """

    target = Target(
        name="Invalid",
        target_type="unknown",
        url="",
        keyword="",
        search_provider="",
        status="active",
    )

    with pytest.raises(ValueError):
        service.resolve(target)


# ==================================================
# Invalid URL Target
# ==================================================


def test_url_target_without_url(
    service,
):
    """
    URL Target 沒有 URL 時應失敗。
    """

    target = Target(
        name="Invalid URL",
        target_type="url",
        url="",
        status="active",
    )

    with pytest.raises(ValueError):
        service.resolve_url_target(target)


def test_search_target_rejected_by_url_resolver(
    service,
    search_target,
):
    """
    Search Target 不應交給 URL Resolver。
    """

    with pytest.raises(ValueError):
        service.resolve_url_target(
            search_target
        )


# ==================================================
# Invalid Search Target
# ==================================================


def test_search_target_without_keyword(
    service,
):
    """
    Search Target 沒有 Keyword 時應失敗。
    """

    target = Target(
        name="Invalid Search",
        target_type="search",
        keyword="",
        search_provider="google_search",
        status="active",
    )

    with pytest.raises(ValueError):
        service.resolve_search_target(target)


def test_search_target_without_provider(
    service,
):
    """
    Search Target 沒有 Provider 時應失敗。
    """

    target = Target(
        name="Invalid Search",
        target_type="search",
        keyword="AI",
        search_provider="",
        status="active",
    )

    with pytest.raises(ValueError):
        service.resolve_search_target(target)


def test_url_target_rejected_by_search_resolver(
    service,
    url_target,
):
    """
    URL Target 不應交給 Search Resolver。
    """

    with pytest.raises(ValueError):
        service.resolve_search_target(
            url_target
        )


# ==================================================
# Invalid Provider
# ==================================================


def test_unknown_search_provider(
    service,
):
    """
    未知 Provider 應失敗。
    """

    target = Target(
        name="Unknown Provider",
        target_type="search",
        keyword="AI",
        search_provider="unknown_provider",
        status="active",
    )

    with pytest.raises(ValueError):
        service.resolve_search_target(
            target
        )


# ==================================================
# Provider-specific Resolver Validation
# ==================================================


def test_google_search_resolver_rejects_google_news(
    service,
    google_news_target,
):
    """
    Google Search Resolver 不接受 Google News Target。
    """

    with pytest.raises(ValueError):
        service.resolve_google_search(
            google_news_target
        )


def test_google_news_resolver_rejects_google_search(
    service,
    google_search_target,
):
    """
    Google News Resolver 不接受 Google Search Target。
    """

    with pytest.raises(ValueError):
        service.resolve_google_news(
            google_search_target
        )


def test_google_search_resolver_rejects_url_target(
    service,
    url_target,
):
    """
    Google Search Resolver 不接受 URL Target。
    """

    with pytest.raises(ValueError):
        service.resolve_google_search(
            url_target
        )


def test_google_news_resolver_rejects_url_target(
    service,
    url_target,
):
    """
    Google News Resolver 不接受 URL Target。
    """

    with pytest.raises(ValueError):
        service.resolve_google_news(
            url_target
        )