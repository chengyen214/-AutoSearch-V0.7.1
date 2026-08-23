"""
config/search_api_config.py

AutoSearch V5

V5.2 P2.4

Search API Configuration

功能：

1. Google Search API 設定
2. Google Search Engine ID
3. Google Search API Timeout
4. Google Search Result Limit
5. Google News Provider Timeout
6. Environment Variable Configuration

Configuration Flow：

    .env
      ↓
    search_api_config.py
      ↓
    Search Provider

不負責：

- Search Provider
- SearchAdapter
- SearchAdapterManager
- SearchResult
- Crawler
- Parser
- Archive
- AI
"""


import os

from dotenv import load_dotenv


# ==================================================
#
# Environment
#
# ==================================================

load_dotenv()


# ==================================================
#
# Internal Environment Helper
#
# ==================================================


def _get_int_env(
    name,
    default,
):
    """
    從 Environment Variable
    讀取整數設定。

    如果設定不存在、
    或無法轉換成整數，

    使用 default。

    Parameters
    ----------
    name :
        Environment Variable 名稱。

    default :
        預設值。

    Returns
    -------

    int
    """

    value = os.getenv(
        name,
        str(default),
    )

    try:

        return int(value)

    except (
        TypeError,
        ValueError,
    ):

        return default


# ==================================================
#
# Google Search API
#
# ==================================================

GOOGLE_SEARCH_API_KEY = os.getenv(
    "GOOGLE_SEARCH_API_KEY",
    "",
)


# ==================================================
#
# Google Search Engine ID
#
# ==================================================

GOOGLE_SEARCH_ENGINE_ID = os.getenv(
    "GOOGLE_SEARCH_ENGINE_ID",
    "",
)


# ==================================================
#
# Google Search Timeout
#
# ==================================================

GOOGLE_SEARCH_TIMEOUT = _get_int_env(
    "GOOGLE_SEARCH_TIMEOUT",
    7,
)


# ==================================================
#
# Google Search Result Limit
#
# ==================================================

GOOGLE_SEARCH_RESULTS = _get_int_env(
    "GOOGLE_SEARCH_RESULTS",
    20,
)


# ==================================================
#
# Google News Timeout
#
# ==================================================

GOOGLE_NEWS_TIMEOUT = _get_int_env(
    "GOOGLE_NEWS_TIMEOUT",
    7,
)


# ==================================================
#
# Google News Result Limit
#
# ==================================================

GOOGLE_NEWS_RESULTS = _get_int_env(
    "GOOGLE_NEWS_RESULTS",
    20,
)


# ==================================================
#
# Validation
#
# ==================================================


def is_google_search_configured():
    """
    判斷 Google Search API
    是否已完成必要設定。

    必要設定：

        GOOGLE_SEARCH_API_KEY
        GOOGLE_SEARCH_ENGINE_ID

    Returns
    -------

    bool
    """

    return bool(
        GOOGLE_SEARCH_API_KEY
        and
        GOOGLE_SEARCH_ENGINE_ID
    )


# ==================================================
#
# Public API
#
# ==================================================

__all__ = [

    "GOOGLE_SEARCH_API_KEY",

    "GOOGLE_SEARCH_ENGINE_ID",

    "GOOGLE_SEARCH_TIMEOUT",

    "GOOGLE_SEARCH_RESULTS",

    "GOOGLE_NEWS_TIMEOUT",

    "GOOGLE_NEWS_RESULTS",

    "is_google_search_configured",

]