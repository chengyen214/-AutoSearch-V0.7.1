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
    - result normalization


不負責:

    - Provider Resolution
    - Provider Registry
    - Search Execution Control
    - URL Deduplication
    - Crawl
    - Parser
    - Archive
    - AI
"""


from models.search_result import (
    SearchResult,
)


from search.search_adapter_base import (
    SearchAdapter,
)


from search.search_provider import (
    SearchProvider,
)



class ProviderSearchAdapter(
    SearchAdapter
):
    """
    SearchProvider Adapter。


    將：

        SearchProvider

    包裝成：

        SearchAdapter


    Example:


        GoogleSearchProvider

                ↓

        ProviderSearchAdapter

                ↓

        adapter.search()

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


        支援：

            keyword

            site/url


        Example:


            adapter.search(
                "AI",
                site="https://www.tsmc.com"
            )


        """



        keyword = self._normalize_keyword(
            keyword
        )


        if not keyword:

            return []



        limit = (
            self._resolve_limit(
                max_results
            )
        )



        # ----------------------------------
        #
        # Provider Execute
        #
        # ----------------------------------

        results = (
            self.provider.search(
                keyword,
                max_results=limit,
                **kwargs,
            )
        )



        return (
            self._normalize_results(
                results,
                keyword,
            )
        )



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



    @staticmethod
    def _normalize_limit(
        value,
    ):

        try:

            value = int(value)

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
    ):

        if results is None:

            return []


        if not isinstance(
            results,
            list,
        ):

            return []



        normalized = []



        for result in results:


            if not isinstance(
                result,
                SearchResult,
            ):

                continue



            if not result.url:

                continue



            result.keyword = keyword


            result.search_source = (
                self.search_source
            )


            result.rank = (
                len(normalized)+1
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




__all__ = [
    "ProviderSearchAdapter",
]