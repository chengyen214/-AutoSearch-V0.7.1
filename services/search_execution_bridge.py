"""
services/search_execution_bridge.py

AutoSearch V5

V5.6.3

Search Execution Bridge


用途：

    將 P5.6.2 SourceResolutionBridge
    解析完成的 Resolved Search Source

    交給已建立完成的 Search Adapter

    執行 Search。


Pipeline：

    Target
        ↓
    TargetSourceService
        ↓
    Source Definition
        ↓
    SourceResolutionBridge
        ↓
    Resolved Source
        ↓
    SearchExecutionBridge
        ↓
    Existing Adapter
        ↓
    adapter.search()
        ↓
    SearchResult[]


P5.6.3 負責：

    - Resolved Source Validation
    - Adapter Resolution
    - Keyword Resolution
    - URL / Site Resolution
    - Search Execution
    - Result Limit Resolution
    - Search Result Normalization


P5.6.3 不負責：

    - Target CRUD
    - Target Validation
    - Source Definition 建立
    - Provider Registry
    - Provider Resolution
    - Provider Implementation
    - SearchProvider Implementation
    - Adapter 建立
    - Crawler
    - Parser
    - Article
    - Archive
    - AI
    - Job
    - Scheduler


設計原則：

P5.6.2 SourceResolutionBridge：

    Source Definition
        ↓
    Provider Instance
        ↓
    Search Adapter
        ↓
    site → Resolved Source


回答：

    「誰負責 Search？」


P5.6.3 SearchExecutionBridge：

    Resolved Adapter
        ↓
    keyword
    optional site/url
        ↓
    adapter.search()


回答：

    「如何執行 Search？」


URL + Keyword：

    TargetSourceService
        ↓
    site
        ↓
    SourceResolutionBridge
        ↓
    site
        ↓
    SearchExecutionBridge
        ↓
    url
        ↓
    ProviderSearchAdapter
        ↓
    GoogleSearchProvider


Google Search：

    keyword + site/url
        ↓
    site:domain keyword
        ↓
    Google Search


Google News：

    keyword
        ↓
    SearchExecutionBridge
        ↓
    ProviderSearchAdapter
        ↓
    GoogleNewsProvider


本模組不執行：

    - Provider Resolution
    - Adapter Creation
    - Provider API / RSS Implementation
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
# Search Execution Bridge
#
# ==================================================

class SearchExecutionBridge:
    """
    Search Execution Bridge。


    使用 SourceResolutionBridge
    已解析完成的 Adapter。


    不負責：

        Provider 建立
        Adapter 建立
        Provider Resolution


    只負責：

        Keyword Resolution
        Site / URL Resolution
        Search Execution
        Result Normalization


    URL / Site 規則：

        URL + Keyword

            resolved_source["site"]
                    ↓
            resolved_source["url"]
                    ↓
            adapter.search(
                keyword,
                url=url,
            )


        若 resolved_source 已經提供：

            resolved_source["url"]

        則直接使用。


        Google News：

            沒有 site/url

                    ↓

            adapter.search(
                keyword,
            )
    """


    # ==================================================
    #
    # Source Type
    #
    # ==================================================

    SOURCE_TYPE_SEARCH = (
        "search"
    )


    # ==================================================
    #
    # Constructor
    #
    # ==================================================

    def __init__(
        self,
        default_max_results=None,
    ):
        """
        建立 SearchExecutionBridge。


        Parameters
        ----------

        default_max_results:

            Bridge 預設搜尋結果數量。


            None：

                使用 Adapter 自己設定。
        """

        if default_max_results is not None:

            default_max_results = (
                self._normalize_max_results(
                    default_max_results
                )
            )


        self.default_max_results = (
            default_max_results
        )


    # ==================================================
    #
    # Execute
    #
    # ==================================================

    def execute(
        self,
        resolved_source,
        max_results=None,
    ):
        """
        執行 Resolved Search Source。


        Input：

        {
            "source_type":
                "search",

            "keyword":
                "AI",

            "provider":
                "google_search",

            "provider_instance":
                Provider(),

            "adapter":
                ProviderSearchAdapter(),

            "site":
                "https://example.com"
        }


        URL + Keyword：

            keyword + site
                ↓
            adapter.search(
                keyword,
                url=site,
            )


        Google News：

            keyword only
                ↓
            adapter.search(
                keyword,
            )


        Output：

            list[SearchResult]
        """

        # ----------------------------------------------
        #
        # Validate
        #
        # ----------------------------------------------

        self._validate_resolved_source(
            resolved_source
        )


        # ----------------------------------------------
        #
        # Keyword
        #
        # ----------------------------------------------

        keyword = (
            self.get_keyword(
                resolved_source
            )
        )


        # ----------------------------------------------
        #
        # URL / Site
        #
        # ----------------------------------------------

        url = (
            self.get_url(
                resolved_source
            )
        )


        # ----------------------------------------------
        #
        # Existing Adapter
        #
        # ----------------------------------------------

        adapter = (
            self.get_adapter(
                resolved_source
            )
        )


        # ----------------------------------------------
        #
        # Result Limit
        #
        # ----------------------------------------------

        result_limit = (
            self._resolve_max_results(
                adapter,
                max_results,
            )
        )


        # ----------------------------------------------
        #
        # Search Arguments
        #
        # ----------------------------------------------

        search_kwargs = {}


        if url:

            search_kwargs["url"] = url


        # ----------------------------------------------
        #
        # Search Execution Debug Information
        #
        # ----------------------------------------------

        print(
            "SearchExecution:"
        )

        print(
            f"  keyword = {keyword}"
        )

        print(
            f"  url     = {url}"
        )

        print(
            f"  provider = "
            f"{resolved_source.get('provider')}"
        )


        # ----------------------------------------------
        #
        # Execute Search
        #
        # ----------------------------------------------

        results = (
            adapter.search(
                keyword,
                max_results=result_limit,
                **search_kwargs,
            )
        )


        # ----------------------------------------------
        #
        # Normalize
        #
        # ----------------------------------------------

        return (
            self._normalize_results(
                results,
                keyword,
            )
        )


    # ==================================================
    #
    # Alias
    #
    # ==================================================

    def run(
        self,
        resolved_source,
        max_results=None,
    ):
        """
        execute alias。
        """

        return self.execute(
            resolved_source,
            max_results=max_results,
        )


    def execute_search(
        self,
        resolved_source,
        max_results=None,
    ):
        """
        execute_search alias。
        """

        return self.execute(
            resolved_source,
            max_results=max_results,
        )


    # ==================================================
    #
    # Adapter Resolution
    #
    # ==================================================

    @staticmethod
    def get_adapter(
        resolved_source,
    ):
        """
        取得 SourceResolutionBridge
        已建立完成的 Adapter。


        不重新建立 Adapter。


        Expected：

            resolved_source["adapter"]
        """

        if not isinstance(
            resolved_source,
            dict,
        ):

            raise TypeError(
                "resolved_source must be dict"
            )


        adapter = (
            resolved_source.get(
                "adapter"
            )
        )


        if adapter is None:

            raise ValueError(
                "resolved_source requires adapter"
            )


        if not callable(
            getattr(
                adapter,
                "search",
                None,
            )
        ):

            raise TypeError(
                "adapter requires search()"
            )


        return adapter


    # ==================================================
    #
    # Get Keyword
    #
    # ==================================================

    @staticmethod
    def get_keyword(
        resolved_source,
    ):
        """
        取得 Search Keyword。
        """

        keyword = (
            resolved_source.get(
                "keyword"
            )
        )


        if keyword is None:

            raise ValueError(
                "search source requires keyword"
            )


        keyword = str(
            keyword
        ).strip()


        if not keyword:

            raise ValueError(
                "search source requires keyword"
            )


        return keyword


    # ==================================================
    #
    # Get URL / Site
    #
    # ==================================================

    @staticmethod
    def get_url(
        resolved_source,
    ):
        """
        取得 Search URL。


        V5.6.3 Source Definition 使用：

            site
                ↓
            SourceResolutionBridge
                ↓
            site


        SearchExecutionBridge 必須將：

            site
                ↓
            url


        再傳給：

            adapter.search(
                keyword,
                url=url,
            )


        同時保留對舊格式的相容：


            resolved_source["url"]


        Priority：

            1.
            url

            2.
            site


        Google News：

            沒有 url / site

                ↓

            return None
        """

        if not isinstance(
            resolved_source,
            dict,
        ):

            raise TypeError(
                "resolved_source must be dict"
            )


        # ----------------------------------------------
        #
        # 1. Existing URL
        #
        # ----------------------------------------------

        url = (
            resolved_source.get(
                "url"
            )
        )


        if url is not None:

            url = str(
                url
            ).strip()


            if url:

                return url


        # ----------------------------------------------
        #
        # 2. Current Source Definition Site
        #
        # ----------------------------------------------

        site = (
            resolved_source.get(
                "site"
            )
        )


        if site is not None:

            site = str(
                site
            ).strip()


            if site:

                return site


        # ----------------------------------------------
        #
        # 3. No URL / Site
        #
        # ----------------------------------------------

        return None


    # ==================================================
    #
    # Resolve Max Results
    #
    # ==================================================

    def _resolve_max_results(
        self,
        adapter,
        max_results,
    ):
        """
        決定 Search Result Limit。


        Priority：

            1.
            execute(max_results)

            2.
            Bridge default_max_results

            3.
            Adapter max_results

            4.
            None
        """

        if max_results is not None:

            return (
                self._normalize_max_results(
                    max_results
                )
            )


        if self.default_max_results is not None:

            return (
                self._normalize_max_results(
                    self.default_max_results
                )
            )


        adapter_limit = getattr(
            adapter,
            "max_results",
            None,
        )


        if adapter_limit is None:

            return None


        return (
            self._normalize_max_results(
                adapter_limit
            )
        )


    # ==================================================
    #
    # Normalize Max Results
    #
    # ==================================================

    @staticmethod
    def _normalize_max_results(
        max_results,
    ):
        """
        Normalize Result Limit。
        """

        try:

            value = int(
                max_results
            )

        except (
            TypeError,
            ValueError,
        ):

            raise ValueError(
                "max_results must be positive integer"
            )


        if value <= 0:

            raise ValueError(
                "max_results must be greater than zero"
            )


        return value


    # ==================================================
    #
    # Normalize Search Results
    #
    # ==================================================

    @staticmethod
    def _normalize_results(
        results,
        keyword,
    ):
        """
        Normalize Adapter Search Results。


        處理：

            - None
            - list validation
            - SearchResult validation
            - URL validation
            - keyword normalization
            - rank normalization


        不重新建立 SearchResult。
        """

        if results is None:

            return []


        if not isinstance(
            results,
            list,
        ):

            raise TypeError(
                "adapter.search() must return list"
            )


        normalized = []


        for result in results:

            if not isinstance(
                result,
                SearchResult,
            ):

                continue


            url = getattr(
                result,
                "url",
                None,
            )


            if not url:

                continue


            # ----------------------------------
            #
            # Keyword
            #
            # ----------------------------------

            try:

                result.keyword = keyword

            except AttributeError:

                pass


            # ----------------------------------
            #
            # Rank
            #
            # ----------------------------------

            try:

                result.rank = (
                    len(normalized) + 1
                )

            except AttributeError:

                pass


            normalized.append(
                result
            )


        return normalized


    # ==================================================
    #
    # Validation
    #
    # ==================================================

    @classmethod
    def _validate_resolved_source(
        cls,
        resolved_source,
    ):
        """
        Validate Resolved Source。


        確認：

            dict
            source_type
            adapter


        不重新執行：

            Provider Resolution
            Adapter Creation
        """

        if not isinstance(
            resolved_source,
            dict,
        ):

            raise TypeError(
                "resolved_source must be dict"
            )


        source_type = (
            resolved_source.get(
                "source_type"
            )
        )


        if not source_type:

            raise ValueError(
                "resolved_source requires source_type"
            )


        if source_type != (
            cls.SOURCE_TYPE_SEARCH
        ):

            raise ValueError(
                "resolved_source must be search source"
            )


        if (
            "adapter"
            not in resolved_source
        ):

            raise ValueError(
                "resolved_source requires adapter"
            )


    # ==================================================
    #
    # Default Bridge
    #
    # ==================================================

default_search_execution_bridge = (
    SearchExecutionBridge()
)


# ==================================================
#
# Convenience API
#
# ==================================================

def execute_search(
    resolved_source,
    max_results=None,
):
    """
    使用 Default Bridge 執行 Search。


    Pipeline：

        Source Definition
            ↓
        SourceResolutionBridge
            ↓
        SearchExecutionBridge
            ↓
        Existing Adapter
            ↓
        SearchResult[]
    """

    return (
        default_search_execution_bridge.execute(
            resolved_source,
            max_results=max_results,
        )
    )


# ==================================================
#
# Public API
#
# ==================================================

__all__ = [
    "SearchExecutionBridge",
    "default_search_execution_bridge",
    "execute_search",
]
