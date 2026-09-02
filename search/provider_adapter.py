"""
search/provider_adapter.py

AutoSearch V5

V5.6.3

Provider Search Adapter

用途：

    將 SearchProvider
    包裝成 V4 SearchAdapter。

Pipeline:

    SearchProvider
            ↓
    ProviderSearchAdapter
            ↓
    SearchExecutionBridge
            ↓
    SearchResult[]


責任:

    - Adapter Interface
    - Provider 呼叫轉接
    - keyword forwarding
    - site/url forwarding
    - crawler_url forwarding
    - result normalization


不負責:

    - Provider Registry
    - Search Execution Control
    - URL Deduplication
    - Crawl
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


from search.search_adapter_base import (
    SearchAdapter,
)


from search.search_provider import (
    SearchProvider,
)


# ==================================================
#
# Provider Search Adapter
#
# ==================================================

class ProviderSearchAdapter(
    SearchAdapter
):
    """
    SearchProvider Adapter。

    將：

        SearchProvider

    包裝成：

        SearchAdapter。


    Keyword-only：

        keyword
            ↓
        Provider


    Keyword + URL：

        keyword
        url
            ↓
        Provider


    GenericSearchProvider：

        keyword
        max_results
        url
        crawler_url
            ↓
        GenericSearchProvider


    GoogleNewsProvider：

        keyword
        max_results
            ↓
        GoogleNewsProvider
    """


    # ==================================================
    #
    # Constructor
    #
    # ==================================================

    def __init__(
        self,
        provider,
        search_source=None,
        max_results=None,
    ):

        if not isinstance(
            provider,
            SearchProvider,
        ):

            raise TypeError(
                "provider must be SearchProvider"
            )


        self.provider = provider


        if search_source is None:

            search_source = getattr(
                provider,
                "provider_name",
                "",
            )


        self.search_source = (
            str(
                search_source
            ).strip()
        )


        if max_results is None:

            max_results = getattr(
                provider,
                "max_results",
                None,
            )


        self.max_results = (
            max_results
        )


    # ==================================================
    #
    # Search
    #
    # ==================================================

    def search(
        self,
        keyword,
        max_results=None,
        **kwargs,
    ):
        """
        Adapter Search。

        將 Search Execution 所需參數
        forwarding 到 Provider。

        支援：

            Keyword only

                keyword
                    ↓
                Provider


            Generic Search

                keyword
                max_results
                url
                crawler_url
                    ↓
                GenericSearchProvider


            Google News

                keyword
                max_results
                    ↓
                GoogleNewsProvider


        本 Adapter：

            不執行 Search Logic
            不執行 URL Deduplication
            不執行 Crawl
        """


        # ==================================================
        #
        # Keyword
        #
        # ==================================================

        keyword = self._normalize_keyword(
            keyword
        )


        if not keyword:

            return []


        # ==================================================
        #
        # Result Limit
        #
        # ==================================================

        limit = (
            self._resolve_limit(
                max_results
            )
        )


        # ==================================================
        #
        # Provider
        #
        # ==================================================

        provider = (
            self.provider
        )


        provider_name = getattr(
            provider,
            "provider_name",
            "",
        )


        # ==================================================
        #
        # URL
        #
        # ==================================================

        url = kwargs.get(
            "url"
        )


        if self._has_url(
            url
        ):

            url = str(
                url
            ).strip()


        else:

            url = None


        # ==================================================
        #
        # Crawler URL
        #
        # ==================================================

        crawler_url = kwargs.get(
            "crawler_url"
        )


        if self._has_url(
            crawler_url
        ):

            crawler_url = str(
                crawler_url
            ).strip()


        else:

            crawler_url = None


        # ==================================================
        #
        # Provider Execute
        #
        # ==================================================

        # --------------------------------------------------
        #
        # GenericSearchProvider
        #
        # --------------------------------------------------

        if provider_name == "generic_search":

            results = (
                provider.search(
                    keyword=keyword,
                    max_results=limit,
                    url=url,
                    crawler_url=crawler_url,
                )
            )


        # --------------------------------------------------
        #
        # Other Providers
        #
        # --------------------------------------------------

        else:

            provider_kwargs = {}


            if limit is not None:

                provider_kwargs[
                    "max_results"
                ] = limit


            if url is not None:

                provider_kwargs[
                    "url"
                ] = url


            if crawler_url is not None:

                provider_kwargs[
                    "crawler_url"
                ] = crawler_url


            results = (
                provider.search(
                    keyword,
                    **provider_kwargs,
                )
            )


        # ==================================================
        #
        # Result Normalize
        #
        # ==================================================

        return (
            self._normalize_results(
                results,
                keyword,
                provider,
            )
        )


    # ==================================================
    #
    # URL Validation
    #
    # ==================================================

    @staticmethod
    def _has_url(
        url,
    ):
        """
        判斷 URL 是否存在。
        """

        if url is None:

            return False


        url = str(
            url
        ).strip()


        if not url:

            return False


        return True


    # ==================================================
    #
    # Keyword
    #
    # ==================================================

    @staticmethod
    def _normalize_keyword(
        keyword,
    ):

        if keyword is None:

            return ""


        return str(
            keyword
        ).strip()


    # ==================================================
    #
    # Max Results
    #
    # ==================================================

    def _resolve_limit(
        self,
        max_results,
    ):

        if max_results is not None:

            return self._normalize_limit(
                max_results
            )


        if self.max_results is not None:

            return self._normalize_limit(
                self.max_results
            )


        return None


    # ==================================================
    #
    # Normalize Limit
    #
    # ==================================================

    @staticmethod
    def _normalize_limit(
        value,
    ):

        try:

            value = int(
                value
            )

        except Exception:

            return 20


        if value <= 0:

            return 20


        return value


    # ==================================================
    #
    # Result Normalize
    #
    # ==================================================

    def _normalize_results(
        self,
        results,
        keyword,
        provider=None,
    ):

        if results is None:

            return []


        if not isinstance(
            results,
            list,
        ):

            return []


        normalized = []


        # ----------------------------------------------
        #
        # Provider
        #
        # ----------------------------------------------

        if provider is None:

            provider = (
                self.provider
            )


        provider_source = getattr(
            provider,
            "provider_name",
            self.search_source,
        )


        # ----------------------------------------------
        #
        # Normalize
        #
        # ----------------------------------------------

        for result in results:

            if not isinstance(
                result,
                SearchResult,
            ):

                continue


            if not result.url:

                continue


            result.keyword = (
                keyword
            )


            result.search_source = (
                provider_source
            )


            result.rank = (
                len(normalized) + 1
            )


            normalized.append(
                result
            )


        return normalized


    # ==================================================
    #
    # Identity
    #
    # ==================================================

    def get_source_name(
        self,
    ):

        return self.search_source


# ==================================================
#
# Public API
#
# ==================================================

__all__ = [
    "ProviderSearchAdapter",
]