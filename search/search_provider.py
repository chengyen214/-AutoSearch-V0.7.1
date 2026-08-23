"""
search/search_provider.py

AutoSearch V5

V5.2 P2.1

Search Provider Interface

用途：

    定義 V5 Search API Provider 的統一介面。

架構：

    Search Provider
        ↓
    SearchResult
        ↓
    V4 SearchAdapter
        ↓
    SearchAdapterManager
        ↓
    Existing V4 Pipeline

支援：

    1. Keyword Search

        search(
            keyword,
            max_results
        )

    2. URL + Keyword Search

        search(
            keyword,
            max_results,
            url
        )

        用於：

            website_search
                ↓
            指定網站 + Keyword
                ↓
            Provider Search

例如：

    search(
        keyword="IC semiconductor",
        max_results=5,
        url="https://www.intel.com/"
    )

GoogleSearchProvider 可以轉換為：

    site:intel.com IC semiconductor


本模組只負責：

    - Provider Interface
    - Provider Name
    - Search Method Contract
    - Result Validation

不負責：

    - Google Search API
    - Google News API
    - SerpApi
    - API Configuration
    - SearchAdapter
    - SearchAdapterManager
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

from models.search_result import (
    SearchResult,
)


# ==================================================
#
# Search Provider
#
# ==================================================

class SearchProvider:
    """
    V5 Search Provider 基礎介面。

    所有 Search Provider
    都應實作：

        search(
            keyword,
            max_results=None,
            url=None
        )

    支援兩種模式：

    1. 一般搜尋

        keyword
            ↓
        Provider
            ↓
        SearchResult[]

    2. 指定網站搜尋

        keyword + url
            ↓
        Provider
            ↓
        SearchResult[]

    例如：

        search(
            "IC semiconductor",
            max_results=5,
            url="https://www.intel.com/"
        )

    Returns:

        list[SearchResult]
    """

    # ==================================================
    #
    # Provider Name
    #
    # ==================================================

    provider_name = ""


    # ==================================================
    #
    # Default Result Limit
    #
    # ==================================================

    max_results = 20


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
        執行 Search Provider。

        Parameters
        ----------
        keyword :
            搜尋關鍵字。

        max_results :
            最大搜尋結果數量。

        url :
            Optional website URL。

            用於：

                URL + Keyword Search

            例如：

                url="https://www.intel.com/"

            Provider 可依自身 API
            實作網站限制。

        Returns
        -------
        list[SearchResult]

        Raises
        ------
        NotImplementedError
            子類別未實作。
        """

        raise NotImplementedError(
            "SearchProvider.search() "
            "must be implemented"
        )


    # ==================================================
    #
    # Validate Results
    #
    # ==================================================

    @classmethod
    def validate_results(
        cls,
        results,
    ):
        """
        驗證 Provider 搜尋結果。

        所有結果必須為：

            list[SearchResult]
        """

        if results is None:

            return False


        if not isinstance(
            results,
            list,
        ):

            return False


        return all(
            isinstance(
                result,
                SearchResult,
            )
            for result in results
        )


# ==================================================
#
# Public API
#
# ==================================================

__all__ = [
    "SearchProvider",
]