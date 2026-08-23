"""
tests/V5-3/test_website_source.py

AutoSearch V5

V5.3 P3.8

Website Source Tests

測試：

    - Default Configuration
    - Custom Configuration
    - String Normalization
    - Numeric Normalization
    - Query Search
    - Path Search
    - Dictionary Conversion
    - Representation
    - Validation
    - Invalid Configuration

注意：

    本測試只確認 WebsiteSource Model。

    不測試：

        - HTTP Request
        - Search
        - Search Provider
        - SearchAdapter
        - Generic Source Handler
        - Crawler
        - Parser
        - Article
        - Archive
        - AI
        - Database
        - Scheduler
"""


import pytest

from models.website_source import (
    WebsiteSource,
)


# ==================================================
# Default Configuration
# ==================================================


def test_default_configuration():

    source = WebsiteSource(
        name="TSMC",
        base_url="https://www.tsmc.com",
        search_url="https://www.tsmc.com/search",
    )

    assert source.name == "TSMC"

    assert (
        source.base_url
        == "https://www.tsmc.com"
    )

    assert (
        source.search_url
        == "https://www.tsmc.com/search"
    )

    assert (
        source.search_method
        == WebsiteSource.SEARCH_METHOD_QUERY
    )

    assert (
        source.keyword_parameter
        == "q"
    )

    assert source.max_results == 20

    assert source.timeout == 7


# ==================================================
# Custom Configuration
# ==================================================


def test_custom_configuration():

    source = WebsiteSource(
        name="Intel",
        base_url="https://www.intel.com",
        search_url="https://www.intel.com/search",
        search_method="path",
        keyword_parameter="query",
        max_results=50,
        timeout=10,
    )

    assert source.name == "Intel"

    assert (
        source.base_url
        == "https://www.intel.com"
    )

    assert (
        source.search_url
        == "https://www.intel.com/search"
    )

    assert (
        source.search_method
        == "path"
    )

    assert (
        source.keyword_parameter
        == "query"
    )

    assert source.max_results == 50

    assert source.timeout == 10


# ==================================================
# String Normalization
# ==================================================


def test_string_normalization():

    source = WebsiteSource(
        name="  TSMC  ",
        base_url="  https://www.tsmc.com  ",
        search_url="  https://www.tsmc.com/search  ",
        search_method=" QUERY ",
        keyword_parameter=" q ",
    )

    assert source.name == "TSMC"

    assert (
        source.base_url
        == "https://www.tsmc.com"
    )

    assert (
        source.search_url
        == "https://www.tsmc.com/search"
    )

    assert source.search_method == "query"

    assert source.keyword_parameter == "q"


# ==================================================
# Numeric Normalization
# ==================================================


def test_numeric_string_normalization():

    source = WebsiteSource(
        name="TSMC",
        base_url="https://www.tsmc.com",
        search_url="https://www.tsmc.com/search",
        max_results="30",
        timeout="12.5",
    )

    assert source.max_results == 30

    assert source.timeout == 12.5


# ==================================================
# Query Search
# ==================================================


def test_query_search():

    source = WebsiteSource(
        name="TSMC",
        base_url="https://www.tsmc.com",
        search_url="https://www.tsmc.com/search",
        search_method="query",
    )

    assert source.is_query_search is True

    assert source.is_path_search is False


# ==================================================
# Path Search
# ==================================================


def test_path_search():

    source = WebsiteSource(
        name="Intel",
        base_url="https://www.intel.com",
        search_url="https://www.intel.com/search",
        search_method="path",
    )

    assert source.is_path_search is True

    assert source.is_query_search is False


# ==================================================
# Dictionary
# ==================================================


def test_to_dict():

    source = WebsiteSource(
        name="TSMC",
        base_url="https://www.tsmc.com",
        search_url="https://www.tsmc.com/search",
        search_method="query",
        keyword_parameter="q",
        max_results=20,
        timeout=7,
    )

    data = source.to_dict()

    assert data == {
        "name": "TSMC",
        "base_url": "https://www.tsmc.com",
        "search_url": "https://www.tsmc.com/search",
        "search_method": "query",
        "keyword_parameter": "q",
        "max_results": 20,
        "timeout": 7,
    }


# ==================================================
# Representation
# ==================================================


def test_repr():

    source = WebsiteSource(
        name="TSMC",
        base_url="https://www.tsmc.com",
        search_url="https://www.tsmc.com/search",
    )

    result = repr(source)

    assert "WebsiteSource(" in result

    assert "TSMC" in result

    assert (
        "https://www.tsmc.com"
        in result
    )


# ==================================================
# Invalid Name
# ==================================================


def test_empty_name_is_rejected():

    with pytest.raises(
        ValueError,
        match="name cannot be empty",
    ):

        WebsiteSource(
            name="",
            base_url="https://www.tsmc.com",
            search_url="https://www.tsmc.com/search",
        )


# ==================================================
# Invalid Base URL
# ==================================================


def test_empty_base_url_is_rejected():

    with pytest.raises(
        ValueError,
        match="base_url cannot be empty",
    ):

        WebsiteSource(
            name="TSMC",
            base_url="",
            search_url="https://www.tsmc.com/search",
        )


# ==================================================
# Invalid Search URL
# ==================================================


def test_empty_search_url_is_rejected():

    with pytest.raises(
        ValueError,
        match="search_url cannot be empty",
    ):

        WebsiteSource(
            name="TSMC",
            base_url="https://www.tsmc.com",
            search_url="",
        )


# ==================================================
# Invalid Search Method
# ==================================================


def test_invalid_search_method_is_rejected():

    with pytest.raises(
        ValueError,
        match="invalid search_method",
    ):

        WebsiteSource(
            name="TSMC",
            base_url="https://www.tsmc.com",
            search_url="https://www.tsmc.com/search",
            search_method="invalid",
        )


# ==================================================
# Empty Keyword Parameter
# ==================================================


def test_empty_keyword_parameter_is_rejected():

    with pytest.raises(
        ValueError,
        match="keyword_parameter cannot be empty",
    ):

        WebsiteSource(
            name="TSMC",
            base_url="https://www.tsmc.com",
            search_url="https://www.tsmc.com/search",
            keyword_parameter="",
        )


# ==================================================
# Invalid Max Results Type
# ==================================================


def test_invalid_max_results_type_is_rejected():

    with pytest.raises(
        ValueError,
        match="max_results must be an integer",
    ):

        WebsiteSource(
            name="TSMC",
            base_url="https://www.tsmc.com",
            search_url="https://www.tsmc.com/search",
            max_results="abc",
        )


# ==================================================
# Invalid Max Results Value
# ==================================================


def test_invalid_max_results_value_is_rejected():

    with pytest.raises(
        ValueError,
        match="max_results must be greater than 0",
    ):

        WebsiteSource(
            name="TSMC",
            base_url="https://www.tsmc.com",
            search_url="https://www.tsmc.com/search",
            max_results=0,
        )


# ==================================================
# Invalid Timeout Type
# ==================================================


def test_invalid_timeout_type_is_rejected():

    with pytest.raises(
        ValueError,
        match="timeout must be a number",
    ):

        WebsiteSource(
            name="TSMC",
            base_url="https://www.tsmc.com",
            search_url="https://www.tsmc.com/search",
            timeout="abc",
        )


# ==================================================
# Invalid Timeout Value
# ==================================================


def test_invalid_timeout_value_is_rejected():

    with pytest.raises(
        ValueError,
        match="timeout must be greater than 0",
    ):

        WebsiteSource(
            name="TSMC",
            base_url="https://www.tsmc.com",
            search_url="https://www.tsmc.com/search",
            timeout=0,
        )


# ==================================================
# Boolean Max Results
# ==================================================


def test_boolean_max_results_is_rejected():

    with pytest.raises(
        ValueError,
        match="max_results must be an integer",
    ):

        WebsiteSource(
            name="TSMC",
            base_url="https://www.tsmc.com",
            search_url="https://www.tsmc.com/search",
            max_results=True,
        )


# ==================================================
# Boolean Timeout
# ==================================================


def test_boolean_timeout_is_rejected():

    with pytest.raises(
        ValueError,
        match="timeout must be a number",
    ):

        WebsiteSource(
            name="TSMC",
            base_url="https://www.tsmc.com",
            search_url="https://www.tsmc.com/search",
            timeout=True,
        )


# ==================================================
# Normalize Returns Self
# ==================================================


def test_normalize_returns_self():

    source = WebsiteSource(
        name="TSMC",
        base_url="https://www.tsmc.com",
        search_url="https://www.tsmc.com/search",
    )

    result = source.normalize()

    assert result is source


# ==================================================
# Validate Returns True
# ==================================================


def test_validate_returns_true():

    source = WebsiteSource(
        name="TSMC",
        base_url="https://www.tsmc.com",
        search_url="https://www.tsmc.com/search",
    )

    assert source.validate() is True
