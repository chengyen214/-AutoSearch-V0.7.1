"""
tests/V5-3/test_generic_source_handler.py

AutoSearch V5

V5.3 P3.9

Generic Source Handler Tests

測試：

    - GenericSourceHandler 建立
    - Query Search Request
    - Path Search Request
    - Keyword Normalization
    - URL Encoding
    - Existing Query String
    - Max Results
    - Timeout
    - Source Validation
    - Empty Keyword
    - Invalid Source
    - Query / Path Isolation

注意：

    本測試只確認 Generic Source Handler。

    不測試：

        - HTTP Request
        - Search Provider
        - SearchAdapter
        - Crawler
        - Parser
        - Article
        - Archive
        - AI
        - Database
"""


import pytest

from models.website_source import (
    WebsiteSource,
)

from services.generic_source_handler import (
    GenericSourceHandler,
)


# ==================================================
# Fixtures
# ==================================================


@pytest.fixture
def handler():

    return GenericSourceHandler()


@pytest.fixture
def query_source():

    return WebsiteSource(
        name="TSMC",
        base_url="https://www.tsmc.com",
        search_url="https://www.tsmc.com/search",
        search_method="query",
        keyword_parameter="q",
        max_results=20,
        timeout=7,
    )


@pytest.fixture
def path_source():

    return WebsiteSource(
        name="Intel",
        base_url="https://www.intel.com",
        search_url="https://www.intel.com/search",
        search_method="path",
        keyword_parameter="q",
        max_results=10,
        timeout=5,
    )


# ==================================================
# Handler Creation
# ==================================================


def test_handler_can_be_created():

    handler = GenericSourceHandler()

    assert handler is not None


# ==================================================
# Query Request
# ==================================================


def test_query_request_builds_search_url(
    handler,
    query_source,
):

    result = handler.handle(
        query_source,
        "AI",
    )

    assert (
        result["url"]
        == "https://www.tsmc.com/search?q=AI"
    )

    assert result["keyword"] == "AI"

    assert (
        result["search_method"]
        == "query"
    )


def test_query_request_contains_source_definition(
    handler,
    query_source,
):

    result = handler.handle(
        query_source,
        "semiconductor",
    )

    assert (
        result["source_name"]
        == "TSMC"
    )

    assert (
        result["base_url"]
        == "https://www.tsmc.com"
    )

    assert (
        result["search_url"]
        == "https://www.tsmc.com/search"
    )

    assert (
        result["keyword_parameter"]
        == "q"
    )


# ==================================================
# Query Keyword Parameter
# ==================================================


def test_query_request_uses_custom_keyword_parameter(
    handler,
):

    source = WebsiteSource(
        name="Example",
        base_url="https://example.com",
        search_url="https://example.com/search",
        search_method="query",
        keyword_parameter="keyword",
    )

    result = handler.handle(
        source,
        "AI",
    )

    assert (
        result["url"]
        == "https://example.com/search?keyword=AI"
    )


# ==================================================
# Existing Query String
# ==================================================


def test_query_request_preserves_existing_query(
    handler,
):

    source = WebsiteSource(
        name="Example",
        base_url="https://example.com",
        search_url=(
            "https://example.com/search?page=1"
        ),
        search_method="query",
        keyword_parameter="q",
    )

    result = handler.handle(
        source,
        "AI",
    )

    assert (
        result["url"]
        == (
            "https://example.com/"
            "search?page=1&q=AI"
        )
    )


# ==================================================
# Path Request
# ==================================================


def test_path_request_builds_search_url(
    handler,
    path_source,
):

    result = handler.handle(
        path_source,
        "AI",
    )

    assert (
        result["url"]
        == "https://www.intel.com/search/AI"
    )

    assert result["keyword"] == "AI"

    assert (
        result["search_method"]
        == "path"
    )


def test_path_request_removes_trailing_slash(
    handler,
):

    source = WebsiteSource(
        name="Example",
        base_url="https://example.com",
        search_url="https://example.com/search/",
        search_method="path",
    )

    result = handler.handle(
        source,
        "AI",
    )

    assert (
        result["url"]
        == "https://example.com/search/AI"
    )


# ==================================================
# Keyword Normalization
# ==================================================


def test_keyword_surrounding_spaces_are_removed(
    handler,
    query_source,
):

    result = handler.handle(
        query_source,
        "  AI  ",
    )

    assert result["keyword"] == "AI"

    assert (
        result["url"]
        == "https://www.tsmc.com/search?q=AI"
    )


def test_multiple_spaces_are_normalized(
    handler,
    query_source,
):

    result = handler.handle(
        query_source,
        "  IC   semiconductor  ",
    )

    assert (
        result["keyword"]
        == "IC semiconductor"
    )


def test_non_string_keyword_is_normalized(
    handler,
    query_source,
):

    result = handler.handle(
        query_source,
        123,
    )

    assert result["keyword"] == "123"


# ==================================================
# URL Encoding
# ==================================================


def test_query_keyword_is_url_encoded(
    handler,
    query_source,
):

    result = handler.handle(
        query_source,
        "AI semiconductor",
    )

    assert (
        result["url"]
        == (
            "https://www.tsmc.com/"
            "search?q=AI+semiconductor"
        )
    )


def test_path_keyword_is_url_encoded(
    handler,
    path_source,
):

    result = handler.handle(
        path_source,
        "AI semiconductor",
    )

    assert (
        result["url"]
        == (
            "https://www.intel.com/"
            "search/AI+semiconductor"
        )
    )


# ==================================================
# Configuration
# ==================================================


def test_max_results_is_preserved(
    handler,
    query_source,
):

    result = handler.handle(
        query_source,
        "AI",
    )

    assert result["max_results"] == 20


def test_timeout_is_preserved(
    handler,
    query_source,
):

    result = handler.handle(
        query_source,
        "AI",
    )

    assert result["timeout"] == 7


def test_custom_configuration_is_preserved(
    handler,
):

    source = WebsiteSource(
        name="Custom",
        base_url="https://example.com",
        search_url="https://example.com/search",
        search_method="query",
        keyword_parameter="keyword",
        max_results=50,
        timeout=15,
    )

    result = handler.handle(
        source,
        "AI",
    )

    assert result["max_results"] == 50

    assert result["timeout"] == 15

    assert (
        result["keyword_parameter"]
        == "keyword"
    )


# ==================================================
# Build Request Alias
# ==================================================


def test_build_request_matches_handle(
    handler,
    query_source,
):

    first = handler.handle(
        query_source,
        "AI",
    )

    second = handler.build_request(
        query_source,
        "AI",
    )

    assert first == second


# ==================================================
# Direct Query / Path Methods
# ==================================================


def test_build_query_request(
    handler,
    query_source,
):

    result = handler.build_query_request(
        query_source,
        "AI",
    )

    assert (
        result["url"]
        == "https://www.tsmc.com/search?q=AI"
    )


def test_build_path_request(
    handler,
    path_source,
):

    result = handler.build_path_request(
        path_source,
        "AI",
    )

    assert (
        result["url"]
        == "https://www.intel.com/search/AI"
    )


# ==================================================
# Empty Keyword
# ==================================================


def test_empty_keyword_is_rejected(
    handler,
    query_source,
):

    with pytest.raises(
        ValueError,
        match="keyword cannot be empty",
    ):

        handler.handle(
            query_source,
            "",
        )


def test_whitespace_keyword_is_rejected(
    handler,
    query_source,
):

    with pytest.raises(
        ValueError,
        match="keyword cannot be empty",
    ):

        handler.handle(
            query_source,
            "   ",
        )


def test_none_keyword_is_rejected(
    handler,
    query_source,
):

    with pytest.raises(
        ValueError,
        match="keyword cannot be empty",
    ):

        handler.handle(
            query_source,
            None,
        )


# ==================================================
# Invalid Source
# ==================================================


def test_invalid_source_type_is_rejected(
    handler,
):

    with pytest.raises(
        TypeError,
        match=(
            "source must be an instance "
            "of WebsiteSource"
        ),
    ):

        handler.handle(
            {},
            "AI",
        )


def test_none_source_is_rejected(
    handler,
):

    with pytest.raises(
        TypeError,
        match=(
            "source must be an instance "
            "of WebsiteSource"
        ),
    ):

        handler.handle(
            None,
            "AI",
        )


# ==================================================
# Query / Path Isolation
# ==================================================


def test_query_source_does_not_use_path_format(
    handler,
    query_source,
):

    result = handler.handle(
        query_source,
        "AI",
    )

    assert (
        result["url"]
        == "https://www.tsmc.com/search?q=AI"
    )

    assert "/AI" not in result["url"]


def test_path_source_does_not_use_query_format(
    handler,
    path_source,
):

    result = handler.handle(
        path_source,
        "AI",
    )

    assert (
        result["url"]
        == "https://www.intel.com/search/AI"
    )

    assert "?q=AI" not in result["url"]


# ==================================================
# Request Definition
# ==================================================


def test_request_definition_contains_required_fields(
    handler,
    query_source,
):

    result = handler.handle(
        query_source,
        "AI",
    )

    required_fields = {
        "source_name",
        "base_url",
        "search_url",
        "url",
        "keyword",
        "search_method",
        "keyword_parameter",
        "max_results",
        "timeout",
    }

    assert required_fields.issubset(
        result.keys()
    )


# ==================================================
# Convenience Function
# ==================================================


def test_default_handler_can_build_request(
    query_source,
):

    from services.generic_source_handler import (
        build_source_request,
    )

    result = build_source_request(
        query_source,
        "AI",
    )

    assert (
        result["url"]
        == "https://www.tsmc.com/search?q=AI"
    )