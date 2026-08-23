"""
tests/V5-2/test_search_api_config.py

AutoSearch V5

V5.2 P2.4

Search API Configuration Tests

測試：

    - Google Search API Key
    - Google Search Engine ID
    - Google Search Timeout
    - Google Search Result Limit
    - Google News Timeout
    - Google News Result Limit
    - Google Search Configuration Validation
    - Integer Environment Variable Handling
"""


import importlib

import config.search_api_config as search_api_config


# ==================================
# Google Search API Key
# ==================================


def test_google_search_api_key():

    assert hasattr(
        search_api_config,
        "GOOGLE_SEARCH_API_KEY",
    )


# ==================================
# Google Search Engine ID
# ==================================


def test_google_search_engine_id():

    assert hasattr(
        search_api_config,
        "GOOGLE_SEARCH_ENGINE_ID",
    )


# ==================================
# Google Search Timeout
# ==================================


def test_google_search_timeout():

    assert (
        search_api_config.GOOGLE_SEARCH_TIMEOUT
        == 7
    )

    assert isinstance(
        search_api_config.GOOGLE_SEARCH_TIMEOUT,
        int,
    )


# ==================================
# Google Search Result Limit
# ==================================


def test_google_search_results():

    assert (
        search_api_config.GOOGLE_SEARCH_RESULTS
        == 20
    )

    assert isinstance(
        search_api_config.GOOGLE_SEARCH_RESULTS,
        int,
    )


# ==================================
# Google News Timeout
# ==================================


def test_google_news_timeout():

    assert (
        search_api_config.GOOGLE_NEWS_TIMEOUT
        == 7
    )

    assert isinstance(
        search_api_config.GOOGLE_NEWS_TIMEOUT,
        int,
    )


# ==================================
# Google News Result Limit
# ==================================


def test_google_news_results():

    assert (
        search_api_config.GOOGLE_NEWS_RESULTS
        == 20
    )

    assert isinstance(
        search_api_config.GOOGLE_NEWS_RESULTS,
        int,
    )


# ==================================
# Configuration Validation
# ==================================


def test_google_search_not_configured():

    assert (
        search_api_config.is_google_search_configured()
        is False
    )


# ==================================
# Integer Environment Helper
# ==================================


def test_get_int_env_default():

    result = (
        search_api_config._get_int_env(
            "NON_EXISTENT_TEST_SETTING",
            123,
        )
    )

    assert result == 123


# ==================================
# Invalid Integer Environment
# ==================================


def test_get_int_env_invalid():

    import os

    original = os.environ.get(
        "TEST_INVALID_INTEGER",
    )

    try:

        os.environ[
            "TEST_INVALID_INTEGER"
        ] = "invalid"

        result = (
            search_api_config._get_int_env(
                "TEST_INVALID_INTEGER",
                7,
            )
        )

        assert result == 7

    finally:

        if original is None:

            os.environ.pop(
                "TEST_INVALID_INTEGER",
                None,
            )

        else:

            os.environ[
                "TEST_INVALID_INTEGER"
            ] = original


# ==================================
# Integer Environment
# ==================================


def test_get_int_env_value():

    import os

    original = os.environ.get(
        "TEST_INTEGER_SETTING",
    )

    try:

        os.environ[
            "TEST_INTEGER_SETTING"
        ] = "15"

        result = (
            search_api_config._get_int_env(
                "TEST_INTEGER_SETTING",
                7,
            )
        )

        assert result == 15

    finally:

        if original is None:

            os.environ.pop(
                "TEST_INTEGER_SETTING",
                None,
            )

        else:

            os.environ[
                "TEST_INTEGER_SETTING"
            ] = original


# ==================================
# Public API
# ==================================


def test_public_api():

    public_api = (
        search_api_config.__all__
    )

    assert (
        "GOOGLE_SEARCH_API_KEY"
        in public_api
    )

    assert (
        "GOOGLE_SEARCH_ENGINE_ID"
        in public_api
    )

    assert (
        "GOOGLE_SEARCH_TIMEOUT"
        in public_api
    )

    assert (
        "GOOGLE_SEARCH_RESULTS"
        in public_api
    )

    assert (
        "GOOGLE_NEWS_TIMEOUT"
        in public_api
    )

    assert (
        "GOOGLE_NEWS_RESULTS"
        in public_api
    )

    assert (
        "is_google_search_configured"
        in public_api
    )