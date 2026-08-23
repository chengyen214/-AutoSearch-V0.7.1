"""
search/google_search_provider.py

AutoSearch V5

V5.6.3

Google Search Provider
SerpApi Implementation

用途：

    使用 SerpApi Google Search API
    執行 Google Web Search。

架構：

    User Keyword
        ↓
    GoogleSearchProvider
        ↓
    SerpApi
        ↓
    Google Search Results
        ↓
    SearchResult
        ↓
    ProviderSearchAdapter
        ↓
    SearchExecutionBridge


支援：

    1. Keyword Search

        keyword
            ↓
        Google Search


    2. URL + Keyword Search

        keyword + url
            ↓
        site:domain keyword
            ↓
        Google Search


例如：

    search(
        "IC semiconductor",
        url="https://www.intel.com/"
    )


會轉換成：

    q = "site:intel.com IC semiconductor"


本模組負責：

    - SerpApi Request
    - Google Search Request
    - API Response Parsing
    - SearchResult 建立
    - Result Limit
    - URL / Site Search
    - API Configuration


不負責：

    - SearchAdapter
    - SearchAdapterManager
    - Provider Resolution
    - SearchExecutionBridge
    - URL Deduplication
    - Crawler
    - Parser
    - Archive
    - AI
"""


# ==================================================
#
# Imports
#
# ==================================================

import os

from urllib.parse import urlparse

import requests

from models.search_result import (
    SearchResult,
)

from search.search_provider import (
    SearchProvider,
)

from dotenv import load_dotenv

load_dotenv()

from urllib.parse import urlparse

import requests

# ==================================================
#
# Google Search Provider
#
# ==================================================

class GoogleSearchProvider(
    SearchProvider
):
    """
    Google Search Provider。

    Backend:

        SerpApi

    支援：

        keyword

        keyword + optional url
    """

    # ==================================================
    #
    # Provider Name
    #
    # ==================================================

    provider_name = (
        "google_search"
    )

    # ==================================================
    #
    # Default Result Limit
    #
    # ==================================================

    max_results = 20

    # ==================================================
    #
    # API Endpoint
    #
    # ==================================================

    API_URL = (
        "https://serpapi.com/search"
    )

    # ==================================================
    #
    # Constructor
    #
    # ==================================================

    def __init__(
        self,
        api_key=None,
        timeout=7,
    ):
        """
        建立 Google Search Provider。

        Parameters
        ----------

        api_key:

            SerpApi API Key。

            如果沒有直接傳入，
            則從：

                SERPAPI_API_KEY

            讀取。

        timeout:

            HTTP Request Timeout。
        """

        self.api_key = (
            api_key
            or os.getenv(
                "SERPAPI_API_KEY"
            )
        )

        self.timeout = timeout

    # ==================================================
    #
    # Configuration Validation
    #
    # ==================================================

    def is_configured(
        self,
    ):
        """
        判斷 SerpApi 是否已設定 API Key。
        """

        return bool(
            self.api_key
        )

    # ==================================================
    #
    # Normalize URL
    #
    # ==================================================

    @staticmethod
    def _normalize_url(
        url,
    ):
        """
        將 URL 正規化成 hostname。

        Example:

            https://www.intel.com/
                ↓
            www.intel.com

            https://www.intel.com/news/
                ↓
            www.intel.com

            www.intel.com
                ↓
            www.intel.com

        None / 空字串：

            None
        """

        if url is None:

            return None

        url = str(
            url
        ).strip()

        if not url:

            return None

        # ----------------------------------------------
        #
        # Add scheme
        #
        # ----------------------------------------------

        parse_target = url

        if not (
            parse_target.startswith(
                "http://"
            )
            or
            parse_target.startswith(
                "https://"
            )
        ):

            parse_target = (
                "https://"
                + parse_target
            )

        # ----------------------------------------------
        #
        # Parse URL
        #
        # ----------------------------------------------

        parsed = urlparse(
            parse_target
        )

        hostname = (
            parsed.hostname
        )

        if not hostname:

            return None

        hostname = (
            hostname.strip()
        )

        if not hostname:

            return None

        return hostname

    # ==================================================
    #
    # Build Query
    #
    # ==================================================

    @classmethod
    def _build_query(
        cls,
        keyword,
        url=None,
    ):
        """
        建立 SerpApi Google Search Query。

        Keyword:

            IC semiconductor

        URL + Keyword:

            site:intel.com IC semiconductor
        """

        keyword = str(
            keyword
        ).strip()

        site = cls._normalize_url(
            url
        )

        if site:

            return (
                f"site:{site} {keyword}"
            )

        return keyword

    # ==================================================
    #
    # Search
    #
    # ==================================================

    def search(
        self,
        keyword,
        max_results=None,
        url=None,
    ):
        """
        執行 SerpApi Google Search。

        Parameters
        ----------

        keyword:

            Search keyword。

        max_results:

            最大搜尋結果數量。

        url:

            Optional website URL。

            例如：

                https://www.intel.com/

            會轉換成：

                site:intel.com keyword


        Returns
        -------

        list[SearchResult]
        """

        # ==================================================
        #
        # Keyword
        #
        # ==================================================

        if keyword is None:

            return []

        keyword = str(
            keyword
        ).strip()

        if not keyword:

            return []

        # ==================================================
        #
        # Result Limit
        #
        # ==================================================

        if max_results is None:

            max_results = (
                self.max_results
            )

        try:

            max_results = int(
                max_results
            )

        except (
            TypeError,
            ValueError,
        ):

            max_results = (
                self.max_results
            )

        if max_results <= 0:

            return []

        # ==================================================
        #
        # Configuration
        #
        # ==================================================

        if not self.is_configured():

            raise ValueError(
                "SerpApi API key "
                "is not configured. "
                "Please set SERPAPI_API_KEY "
                "in .env."
            )

        # ==================================================
        #
        # Build Query
        #
        # ==================================================

        query = (
            self._build_query(
                keyword,
                url=url,
            )
        )

        # ==================================================
        #
        # SerpApi Parameters
        #
        # ==================================================

        params = {

            "engine":
                "google",

            "q":
                query,

            "api_key":
                self.api_key,

            "num":
                min(
                    max_results,
                    100,
                ),

            "output":
                "json",

        }

        # ==================================================
        #
        # Request
        #
        # ==================================================

        response = requests.get(

            self.API_URL,

            params=params,

            timeout=self.timeout,

        )

        # ==================================================
        #
        # HTTP Validation
        #
        # ==================================================

        response.raise_for_status()

        # ==================================================
        #
        # JSON
        #
        # ==================================================

        data = response.json()

        if not isinstance(
            data,
            dict,
        ):

            return []

        # ==================================================
        #
        # SerpApi Error
        #
        # ==================================================

        error = data.get(
            "error"
        )

        if error:

            raise ValueError(
                "SerpApi Google Search "
                f"error: {error}"
            )

        # ==================================================
        #
        # Organic Results
        #
        # ==================================================

        organic_results = data.get(
            "organic_results",
            [],
        )

        if not isinstance(
            organic_results,
            list,
        ):

            return []

        # ==================================================
        #
        # SearchResult
        #
        # ==================================================

        results = []

        for item in organic_results:

            if not isinstance(
                item,
                dict,
            ):

                continue

            # ----------------------------------------------
            #
            # URL
            #
            # ----------------------------------------------

            result_url = item.get(
                "link",
                "",
            )

            if not result_url:

                continue

            # ----------------------------------------------
            #
            # Title
            #
            # ----------------------------------------------

            title = item.get(
                "title",
                "",
            )

            # ----------------------------------------------
            #
            # Snippet
            #
            # ----------------------------------------------

            snippet = item.get(
                "snippet",
                "",
            )

            # ----------------------------------------------
            #
            # Source
            #
            # ----------------------------------------------

            source = ""

            displayed_link = item.get(
                "displayed_link",
                "",
            )

            if displayed_link:

                source = displayed_link

            else:

                parsed_url = urlparse(
                    result_url
                )

                source = (
                    parsed_url.netloc
                    or ""
                )

            # ----------------------------------------------
            #
            # SearchResult
            #
            # ----------------------------------------------

            result = SearchResult(

                keyword=keyword,

                title=title,

                url=result_url,

                source=source,

                published=None,

                search_source=self.provider_name,

                rank=len(results) + 1,

            )

            # ----------------------------------------------
            #
            # Preserve Result
            #
            # ----------------------------------------------

            results.append(
                result
            )

            # ----------------------------------------------
            #
            # Result Limit
            #
            # ----------------------------------------------

            if (
                len(results)
                >= max_results
            ):

                break

        return results


# ==================================================
#
# Public API
#
# ==================================================

__all__ = [
    "GoogleSearchProvider",
]