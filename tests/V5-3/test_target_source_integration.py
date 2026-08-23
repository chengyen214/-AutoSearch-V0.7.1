"""
tests/V5-3/test_target_source_integration.py

AutoSearch V5

V5.3 P3 Integration

Target → Source Configuration → Generic Source Handler

測試：

    P3.1 Target Model
    P3.2 Target Validation
    P3.3 Target Repository Model Boundary
    P3.4 Target Source Resolution
    P3.5 Target Deduplication Boundary
    P3.6 URL Normalization Boundary
    P3.7 Keyword Matching
    P3.8 Website Source
    P3.9 Generic Source Handler

本測試確認：

    Target
        ↓
    TargetSourceService
        ↓
    WebsiteSource
        ↓
    GenericSourceHandler

注意：

    本測試不執行：

        - HTTP Request
        - Search API
        - SearchAdapter
        - Crawler
        - Parser
        - Article
        - Archive
        - AI
        - Database I/O
"""
from urllib.parse import urlparse, parse_qs

import pytest

from models.target import Target
from models.website_source import WebsiteSource

from services.target_source_service import (
    TargetSourceService,
)

from services.generic_source_handler import (
    GenericSourceHandler,
)


# ==================================================
# Fixtures
# ==================================================


@pytest.fixture
def source_service():
    return TargetSourceService()


@pytest.fixture
def generic_handler():
    return GenericSourceHandler()


@pytest.fixture
def google_news_target():
    return Target(
        name="Google News",
        target_type="search",
        keyword="IC semiconductor",
        search_provider="google_news",
        description="Google News search target",
        status="active",
    )


@pytest.fixture
def intel_target():
    return Target(
        name="Intel",
        target_type="url",
        url="https://www.intel.com/",
        description="Intel website target",
        status="active",
    )


@pytest.fixture
def tsmc_target():
    return Target(
        name="TSMC",
        target_type="url",
        url="https://www.tsmc.com/",
        description="TSMC website target",
        status="active",
    )


# ==================================================
# Target → Source Resolution
# ==================================================


def test_google_news_target_resolves_to_search_source(
    source_service,
    google_news_target,
):
    result = source_service.resolve(
        google_news_target
    )

    assert result["source_type"] == "search"
    assert result["keyword"] == "IC semiconductor"
    assert result["provider"] == "google_news"


def test_intel_target_resolves_to_direct_url_source(
    source_service,
    intel_target,
):
    result = source_service.resolve(
        intel_target
    )

    assert result["source_type"] == "direct_url"
    assert result["url"] == "https://www.intel.com/"


def test_tsmc_target_resolves_to_direct_url_source(
    source_service,
    tsmc_target,
):
    result = source_service.resolve(
        tsmc_target
    )

    assert result["source_type"] == "direct_url"
    assert result["url"] == "https://www.tsmc.com/"


# ==================================================
# Target Classification
# ==================================================


def test_google_news_is_search_target(
    source_service,
    google_news_target,
):
    assert (
        source_service.is_search_target(
            google_news_target
        )
        is True
    )

    assert (
        source_service.is_url_target(
            google_news_target
        )
        is False
    )


def test_intel_is_url_target(
    source_service,
    intel_target,
):
    assert (
        source_service.is_url_target(
            intel_target
        )
        is True
    )

    assert (
        source_service.is_search_target(
            intel_target
        )
        is False
    )


def test_tsmc_is_url_target(
    source_service,
    tsmc_target,
):
    assert (
        source_service.is_url_target(
            tsmc_target
        )
        is True
    )

    assert (
        source_service.is_search_target(
            tsmc_target
        )
        is False
    )


# ==================================================
# Provider Resolution
# ==================================================


def test_google_news_provider_is_resolved(
    source_service,
    google_news_target,
):
    assert (
        source_service.get_provider(
            google_news_target
        )
        == "google_news"
    )

    assert (
        source_service.is_google_news(
            google_news_target
        )
        is True
    )

    assert (
        source_service.is_google_search(
            google_news_target
        )
        is False
    )


def test_url_target_has_no_search_provider(
    source_service,
    intel_target,
):
    assert (
        source_service.get_provider(
            intel_target
        )
        is None
    )


# ==================================================
# WebsiteSource Configuration
# ==================================================


def test_tsmc_target_can_be_mapped_to_website_source(
    tsmc_target,
):
    source = WebsiteSource(
        name=tsmc_target.name,
        base_url="https://www.tsmc.com",
        search_url="https://www.tsmc.com/search",
        search_method="query",
        keyword_parameter="q",
        max_results=20,
        timeout=7,
    )

    assert source.name == "TSMC"
    assert source.base_url == "https://www.tsmc.com"
    assert source.search_url == "https://www.tsmc.com/search"
    assert source.search_method == "query"


def test_intel_target_can_be_mapped_to_website_source(
    intel_target,
):
    source = WebsiteSource(
        name=intel_target.name,
        base_url="https://www.intel.com",
        search_url="https://www.intel.com/search",
        search_method="path",
        keyword_parameter="q",
        max_results=20,
        timeout=7,
    )

    assert source.name == "Intel"
    assert source.base_url == "https://www.intel.com"
    assert source.search_url == "https://www.intel.com/search"
    assert source.search_method == "path"


# ==================================================
# WebsiteSource → GenericSourceHandler
# ==================================================


def test_tsmc_source_handler_builds_keyword_request(
    generic_handler,
):
    source = WebsiteSource(
        name="TSMC",
        base_url="https://www.tsmc.com",
        search_url="https://www.tsmc.com/search",
        search_method="query",
        keyword_parameter="q",
        max_results=20,
        timeout=7,
    )

    result = generic_handler.handle(
        source,
        "IC semiconductor",
    )

    assert (
        result["url"]
        == (
            "https://www.tsmc.com/"
            "search?q=IC+semiconductor"
        )
    )

    assert result["keyword"] == "IC semiconductor"
    assert result["source_name"] == "TSMC"
    assert result["max_results"] == 20
    assert result["timeout"] == 7


def test_intel_source_handler_builds_keyword_request(
    generic_handler,
):
    source = WebsiteSource(
        name="Intel",
        base_url="https://www.intel.com",
        search_url="https://www.intel.com/search",
        search_method="path",
        keyword_parameter="q",
        max_results=20,
        timeout=7,
    )

    result = generic_handler.handle(
        source,
        "IC semiconductor",
    )

    assert (
        result["url"]
        == (
            "https://www.intel.com/"
            "search/IC+semiconductor"
        )
    )

    assert result["keyword"] == "IC semiconductor"
    assert result["source_name"] == "Intel"


# ==================================================
# Search Keyword Boundary
# ==================================================


def test_search_target_preserves_ic_semiconductor_keyword(
    source_service,
    google_news_target,
):
    result = source_service.resolve_search_target(
        google_news_target
    )

    assert result["keyword"] == "IC semiconductor"


def test_website_keyword_is_runtime_input(
    generic_handler,
):
    """
    WebsiteSource 本身不保存使用者本次搜尋 Keyword。

    Keyword 是 GenericSourceHandler.handle()
    的 runtime input。
    """

    source = WebsiteSource(
        name="TSMC",
        base_url="https://www.tsmc.com",
        search_url="https://www.tsmc.com/search",
        search_method="query",
        keyword_parameter="q",
    )

    result = generic_handler.handle(
        source,
        "IC semiconductor",
    )

    assert result["keyword"] == "IC semiconductor"


# ==================================================
# URL Structure Verification
# ==================================================


def test_tsmc_request_contains_expected_query_parameter(
    generic_handler,
):
    source = WebsiteSource(
        name="TSMC",
        base_url="https://www.tsmc.com",
        search_url="https://www.tsmc.com/search",
        search_method="query",
        keyword_parameter="q",
    )

    result = generic_handler.handle(
        source,
        "IC semiconductor",
    )

    parsed = urlparse(result["url"])
    query = parse_qs(parsed.query)

    assert parsed.scheme == "https"
    assert parsed.netloc == "www.tsmc.com"
    assert parsed.path == "/search"
    assert query["q"] == ["IC semiconductor"]


def test_intel_request_contains_expected_path(
    generic_handler,
):
    source = WebsiteSource(
        name="Intel",
        base_url="https://www.intel.com",
        search_url="https://www.intel.com/search",
        search_method="path",
        keyword_parameter="q",
    )

    result = generic_handler.handle(
        source,
        "IC semiconductor",
    )

    parsed = urlparse(result["url"])

    assert parsed.scheme == "https"
    assert parsed.netloc == "www.intel.com"
    assert parsed.path == "/search/IC+semiconductor"


# ==================================================
# Isolation
# ==================================================


def test_target_resolution_does_not_execute_search(
    source_service,
    google_news_target,
):
    result = source_service.resolve(
        google_news_target
    )

    assert result["source_type"] == "search"

    # TargetSourceService 只提供 Source Definition。
    # 不應該產生搜尋結果。
    assert "results" not in result
    assert "articles" not in result


def test_generic_handler_does_not_execute_http_request(
    generic_handler,
):
    source = WebsiteSource(
        name="TSMC",
        base_url="https://www.tsmc.com",
        search_url="https://www.tsmc.com/search",
        search_method="query",
        keyword_parameter="q",
    )

    result = generic_handler.handle(
        source,
        "IC semiconductor",
    )

    # Handler 只建立 Request Definition。
    assert "response" not in result
    assert "html" not in result
    assert "articles" not in result


# ==================================================
# Invalid Target
# ==================================================


def test_invalid_target_is_rejected(
    source_service,
):
    with pytest.raises(
        TypeError,
        match="target must be an instance of Target",
    ):
        source_service.resolve({})


def test_invalid_search_provider_is_rejected(
    source_service,
):
    target = Target(
        name="Invalid",
        target_type="search",
        keyword="IC semiconductor",
        search_provider="unknown_provider",
    )

    with pytest.raises(
        ValueError,
        match="Unsupported search provider",
    ):
        source_service.resolve(target)


# ==================================================
# Final Architecture Check
# ==================================================


def test_p3_target_source_chain_is_complete(
    source_service,
    generic_handler,
    tsmc_target,
):
    """
    P3 最重要的整合測試：

        Target
            ↓
        TargetSourceService
            ↓
        WebsiteSource
            ↓
        GenericSourceHandler
    """

    source_definition = (
        source_service.resolve(
            tsmc_target
        )
    )

    assert (
        source_definition["source_type"]
        == "direct_url"
    )

    website_source = WebsiteSource(
        name=tsmc_target.name,
        base_url="https://www.tsmc.com",
        search_url="https://www.tsmc.com/search",
        search_method="query",
        keyword_parameter="q",
    )

    request = generic_handler.handle(
        website_source,
        "IC semiconductor",
    )

    assert request["source_name"] == "TSMC"
    assert request["keyword"] == "IC semiconductor"

    assert (
        request["url"]
        == (
            "https://www.tsmc.com/"
            "search?q=IC+semiconductor"
        )
    )
