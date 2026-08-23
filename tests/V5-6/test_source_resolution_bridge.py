"""
tests/V5-6/test_source_resolution_bridge.py

AutoSearch V5

V5.6.2

Source Resolution Bridge Tests

測試：

    1. Direct URL Resolution
    2. Google Search Provider Resolution
    3. Google News Provider Resolution
    4. Provider → Adapter Bridge
    5. Provider Validation
    6. Source Type Detection
    7. Invalid Source Definition
    8. Invalid Provider
    9. Missing Keyword
    10. Missing URL
    11. Custom Provider Injection

注意：

    本測試不執行真正的 Google Search API。

    P5.6.2 測試目標：

        Source Definition
            ↓
        SourceResolutionBridge
            ↓
        Provider
            ↓
        ProviderSearchAdapter
"""

import pytest

from models.target import Target
from search.google_search_provider import GoogleSearchProvider
from search.google_news_provider import GoogleNewsProvider
from search.provider_adapter import ProviderSearchAdapter

from services.target_source_service import (
    TargetSourceService,
)

from services.source_resolution_bridge import (
    SourceResolutionBridge,
)


# ==================================================
# Fixtures
# ==================================================


@pytest.fixture
def bridge():
    """
    建立 SourceResolutionBridge。
    """

    return SourceResolutionBridge()


@pytest.fixture
def google_search_definition():
    """
    Google Search Source Definition。
    """

    return {
        "source_type": "search",
        "keyword": "semiconductor",
        "provider": "google_search",
    }


@pytest.fixture
def google_news_definition():
    """
    Google News Source Definition。
    """

    return {
        "source_type": "search",
        "keyword": "semiconductor",
        "provider": "google_news",
    }


@pytest.fixture
def direct_url_definition():
    """
    Direct URL Source Definition。
    """

    return {
        "source_type": "direct_url",
        "url": "https://example.com",
    }


# ==================================================
# Direct URL
# ==================================================


def test_resolve_direct_url(
    bridge,
    direct_url_definition,
):
    """
    P5.6.2

    Direct URL：

        Source Definition
            ↓
        Direct URL Definition
    """

    result = bridge.resolve(
        direct_url_definition
    )

    assert result["source_type"] == "direct_url"

    assert (
        result["url"]
        == "https://example.com"
    )


def test_resolve_direct_url_does_not_create_provider(
    bridge,
    direct_url_definition,
):
    """
    Direct URL 不應建立 Search Provider。
    """

    result = bridge.resolve(
        direct_url_definition
    )

    assert "provider" not in result
    assert "provider_instance" not in result
    assert "adapter" not in result


def test_is_direct_url(
    bridge,
    direct_url_definition,
):
    """
    判斷 Direct URL Source。
    """

    assert (
        bridge.is_direct_url(
            direct_url_definition
        )
        is True
    )

    assert (
        bridge.is_search(
            direct_url_definition
        )
        is False
    )


# ==================================================
# Google Search
# ==================================================


def test_resolve_google_search(
    bridge,
    google_search_definition,
):
    """
    Google Search：

        Source Definition
            ↓
        GoogleSearchProvider
            ↓
        ProviderSearchAdapter
    """

    result = bridge.resolve(
        google_search_definition
    )

    assert result["source_type"] == "search"

    assert (
        result["keyword"]
        == "semiconductor"
    )

    assert (
        result["provider"]
        == "google_search"
    )


def test_google_search_provider_instance(
    bridge,
    google_search_definition,
):
    """
    Provider Resolution：

        google_search
            ↓
        GoogleSearchProvider
    """

    result = bridge.resolve(
        google_search_definition
    )

    provider = result[
        "provider_instance"
    ]

    assert isinstance(
        provider,
        GoogleSearchProvider,
    )


def test_google_search_adapter(
    bridge,
    google_search_definition,
):
    """
    Provider → Adapter。

        GoogleSearchProvider
            ↓
        ProviderSearchAdapter
    """

    result = bridge.resolve(
        google_search_definition
    )

    adapter = result[
        "adapter"
    ]

    assert isinstance(
        adapter,
        ProviderSearchAdapter,
    )

    assert (
        adapter.provider
        is result["provider_instance"]
    )


# ==================================================
# Google News
# ==================================================


def test_resolve_google_news(
    bridge,
    google_news_definition,
):
    """
    Google News：

        Source Definition
            ↓
        GoogleNewsProvider
            ↓
        ProviderSearchAdapter
    """

    result = bridge.resolve(
        google_news_definition
    )

    assert result["source_type"] == "search"

    assert (
        result["keyword"]
        == "semiconductor"
    )

    assert (
        result["provider"]
        == "google_news"
    )


def test_google_news_provider_instance(
    bridge,
    google_news_definition,
):
    """
    Provider Resolution：

        google_news
            ↓
        GoogleNewsProvider
    """

    result = bridge.resolve(
        google_news_definition
    )

    provider = result[
        "provider_instance"
    ]

    assert isinstance(
        provider,
        GoogleNewsProvider,
    )


def test_google_news_adapter(
    bridge,
    google_news_definition,
):
    """
    Provider → Adapter。
    """

    result = bridge.resolve(
        google_news_definition
    )

    adapter = result[
        "adapter"
    ]

    assert isinstance(
        adapter,
        ProviderSearchAdapter,
    )

    assert (
        adapter.provider
        is result["provider_instance"]
    )


# ==================================================
# Provider Resolution
# ==================================================


def test_resolve_google_search_provider(
    bridge,
):
    """
    直接解析 Google Search Provider。
    """

    provider = bridge.resolve_provider(
        "google_search"
    )

    assert isinstance(
        provider,
        GoogleSearchProvider,
    )


def test_resolve_google_news_provider(
    bridge,
):
    """
    直接解析 Google News Provider。
    """

    provider = bridge.resolve_provider(
        "google_news"
    )

    assert isinstance(
        provider,
        GoogleNewsProvider,
    )


def test_supported_provider(
    bridge,
):
    """
    Provider 支援判斷。
    """

    assert (
        bridge.is_supported_provider(
            "google_search"
        )
        is True
    )

    assert (
        bridge.is_supported_provider(
            "google_news"
        )
        is True
    )

    assert (
        bridge.is_supported_provider(
            "unknown"
        )
        is False
    )

    assert (
        bridge.is_supported_provider(
            None
        )
        is False
    )


# ==================================================
# Source Type
# ==================================================


def test_is_search(
    bridge,
    google_search_definition,
):
    """
    判斷 Search Source。
    """

    assert (
        bridge.is_search(
            google_search_definition
        )
        is True
    )

    assert (
        bridge.is_direct_url(
            google_search_definition
        )
        is False
    )


# ==================================================
# Custom Provider Injection
# ==================================================


def test_custom_provider_injection():
    """
    確認 Bridge 支援 Provider Dependency Injection。

    P5.6.2 不應強制只能使用預設 Provider。
    """

    google_search = GoogleSearchProvider()

    google_news = GoogleNewsProvider()

    bridge = SourceResolutionBridge(
        google_search_provider=google_search,
        google_news_provider=google_news,
    )

    assert (
        bridge.google_search_provider
        is google_search
    )

    assert (
        bridge.google_news_provider
        is google_news
    )


def test_custom_provider_is_used(
    google_search_definition,
):
    """
    resolve() 必須使用注入的 Provider。
    """

    google_search = GoogleSearchProvider()

    bridge = SourceResolutionBridge(
        google_search_provider=google_search,
    )

    result = bridge.resolve(
        google_search_definition
    )

    assert (
        result["provider_instance"]
        is google_search
    )

    assert (
        result["adapter"].provider
        is google_search
    )


# ==================================================
# Invalid Definition
# ==================================================


def test_invalid_definition_type(
    bridge,
):
    """
    Source Definition 必須為 dict。
    """

    with pytest.raises(
        TypeError,
        match="source_definition must be a dict",
    ):
        bridge.resolve(None)


def test_missing_source_type(
    bridge,
):
    """
    缺少 source_type。
    """

    with pytest.raises(
        ValueError,
        match="source_definition requires source_type",
    ):
        bridge.resolve({})


def test_unsupported_source_type(
    bridge,
):
    """
    不支援的 Source Type。
    """

    definition = {
        "source_type": "unknown",
    }

    with pytest.raises(
        ValueError,
        match="Unsupported source type",
    ):
        bridge.resolve(definition)


# ==================================================
# Direct URL Validation
# ==================================================


def test_direct_url_missing_url(
    bridge,
):
    """
    Direct URL 缺少 URL。
    """

    definition = {
        "source_type": "direct_url",
    }

    with pytest.raises(
        ValueError,
        match="Direct URL source requires url",
    ):
        bridge.resolve(definition)


def test_resolve_direct_url_wrong_type(
    bridge,
):
    """
    resolve_direct_url()
    只能處理 direct_url。
    """

    definition = {
        "source_type": "search",
        "keyword": "semiconductor",
        "provider": "google_search",
    }

    with pytest.raises(
        ValueError,
        match="direct_url source",
    ):
        bridge.resolve_direct_url(
            definition
        )


# ==================================================
# Search Validation
# ==================================================


def test_search_missing_keyword(
    bridge,
):
    """
    Search Source 缺少 Keyword。
    """

    definition = {
        "source_type": "search",
        "provider": "google_search",
    }

    with pytest.raises(
        ValueError,
        match="Search source requires keyword",
    ):
        bridge.resolve(definition)


def test_search_missing_provider(
    bridge,
):
    """
    Search Source 缺少 Provider。
    """

    definition = {
        "source_type": "search",
        "keyword": "semiconductor",
    }

    with pytest.raises(
        ValueError,
        match="Search source requires provider",
    ):
        bridge.resolve(definition)


def test_unsupported_search_provider(
    bridge,
):
    """
    Search Provider 不支援。
    """

    definition = {
        "source_type": "search",
        "keyword": "semiconductor",
        "provider": "bing",
    }

    with pytest.raises(
        ValueError,
        match="Unsupported search provider",
    ):
        bridge.resolve(definition)


def test_empty_provider_name(
    bridge,
):
    """
    Provider 名稱不可為空。
    """

    with pytest.raises(
        ValueError,
        match="provider_name cannot be empty",
    ):
        bridge.resolve_provider("")


# ==================================================
# Provider Adapter
# ==================================================


def test_create_provider_adapter():
    """
    Provider → ProviderSearchAdapter。
    """

    provider = GoogleSearchProvider()

    adapter = (
        SourceResolutionBridge
        .create_provider_adapter(
            provider
        )
    )

    assert isinstance(
        adapter,
        ProviderSearchAdapter,
    )

    assert (
        adapter.provider
        is provider
    )


def test_create_provider_adapter_none():
    """
    None Provider 必須拒絕。
    """

    with pytest.raises(
        ValueError,
        match="provider cannot be None",
    ):
        SourceResolutionBridge.create_provider_adapter(
            None
        )


# ==================================================
# Target → Source Definition Compatibility
# ==================================================


def test_target_source_service_to_bridge_google_search(
    bridge,
):
    """
    驗證：

        Target
            ↓
        TargetSourceService
            ↓
        SourceResolutionBridge

    Google Search 完整 Resolution。
    """

    target = Target(
        name="Semiconductor Search",
        target_type=Target.TYPE_SEARCH,
        keyword="semiconductor",
        search_provider=Target.PROVIDER_GOOGLE_SEARCH,
    )

    source_service = TargetSourceService()

    source_definition = (
        source_service.resolve(
            target
        )
    )

    result = bridge.resolve(
        source_definition
    )

    assert (
        result["source_type"]
        == "search"
    )

    assert (
        result["keyword"]
        == "semiconductor"
    )

    assert (
        result["provider"]
        == "google_search"
    )

    assert isinstance(
        result["provider_instance"],
        GoogleSearchProvider,
    )

    assert isinstance(
        result["adapter"],
        ProviderSearchAdapter,
    )


def test_target_source_service_to_bridge_google_news(
    bridge,
):
    """
    驗證：

        Target
            ↓
        TargetSourceService
            ↓
        SourceResolutionBridge

    Google News 完整 Resolution。
    """

    target = Target(
        name="Semiconductor News",
        target_type=Target.TYPE_SEARCH,
        keyword="semiconductor",
        search_provider=Target.PROVIDER_GOOGLE_NEWS,
    )

    source_service = TargetSourceService()

    source_definition = (
        source_service.resolve(
            target
        )
    )

    result = bridge.resolve(
        source_definition
    )

    assert (
        result["source_type"]
        == "search"
    )

    assert (
        result["keyword"]
        == "semiconductor"
    )

    assert (
        result["provider"]
        == "google_news"
    )

    assert isinstance(
        result["provider_instance"],
        GoogleNewsProvider,
    )

    assert isinstance(
        result["adapter"],
        ProviderSearchAdapter,
    )


def test_target_source_service_to_bridge_direct_url(
    bridge,
):
    """
    驗證：

        Target
            ↓
        TargetSourceService
            ↓
        SourceResolutionBridge

    Direct URL 完整 Resolution。
    """

    target = Target(
        name="Example",
        target_type=Target.TYPE_URL,
        url="https://example.com",
    )

    source_service = TargetSourceService()

    source_definition = (
        source_service.resolve(
            target
        )
    )

    result = bridge.resolve(
        source_definition
    )

    assert (
        result["source_type"]
        == "direct_url"
    )

    assert (
        result["url"]
        == "https://example.com"
    )
