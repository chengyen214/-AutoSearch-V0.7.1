"""
services/source_resolution_bridge.py

AutoSearch V5

V5.6.2

Source Resolution Bridge


用途：

    將 TargetSourceService
    產生的 Source Definition

    解析成 Pipeline 使用的
    Resolved Source。


Pipeline:

    Target

        ↓

    TargetSourceService

        ↓

    Source Definition

        ↓

    SourceResolutionBridge

        ↓

    Resolved Source


負責：

    - Source Definition Resolution
    - Source Type Resolution
    - Search Provider Resolution
    - Provider Registry
    - Provider Adapter Binding


不負責：

    - Target CRUD
    - Target Validation
    - Search Execution
    - adapter.search()
    - SearchResult Processing
    - URL Deduplication
    - Crawl
    - Parser
    - Article
    - Archive
    - AI
    - Job
    - Scheduler


設計原則：

    P5.6.2：

        「這個 Source Definition
         要由哪個 Provider / Adapter 執行？」


    P5.6.3：

        「Search 實際如何執行。」


Search Execution:

    SourceResolutionBridge

            ↓

    ProviderSearchAdapter

            ↓

    SearchExecutionBridge

            ↓

    adapter.search()
"""


# ==================================================
#
# Imports
#
# ==================================================

from search.search_provider import (
    SearchProvider,
)


from search.google_search_provider import (
    GoogleSearchProvider,
)


from search.google_news_provider import (
    GoogleNewsProvider,
)


from search.provider_adapter import (
    ProviderSearchAdapter,
)



class SourceResolutionBridge:
    """
    Source Resolution Bridge。


    Source Definition:

        {
            "source_type":
                "search",

            "keyword":
                "AI",

            "provider":
                "google_search",

            "site":
                "https://example.com"
        }


    Resolution:

        Source Definition

                ↓

        Provider

                ↓

        ProviderSearchAdapter


    本類別不執行 Search。
    """



    # ==================================================
    #
    # Source Types
    #
    # ==================================================

    SOURCE_TYPE_DIRECT_URL = (
        "direct_url"
    )


    SOURCE_TYPE_SEARCH = (
        "search"
    )


    SUPPORTED_SOURCE_TYPES = {

        SOURCE_TYPE_DIRECT_URL,

        SOURCE_TYPE_SEARCH,

    }



    # ==================================================
    #
    # Provider Names
    #
    # ==================================================

    PROVIDER_GOOGLE_SEARCH = (
        "google_search"
    )


    PROVIDER_GOOGLE_NEWS = (
        "google_news"
    )



    SUPPORTED_PROVIDERS = {

        PROVIDER_GOOGLE_SEARCH,

        PROVIDER_GOOGLE_NEWS,

    }



    # ==================================================
    #
    # Constructor
    #
    # ==================================================

    def __init__(
        self,
        providers=None,
    ):
        """
        建立 SourceResolutionBridge。


        providers:

            Provider Registry


        Example:


        {
            "google_search":
                GoogleSearchProvider(),

            "google_news":
                GoogleNewsProvider(),
        }


        若沒有提供：

            使用 Default Registry。
        """



        if providers is None:

            providers = (

                self._create_default_registry()

            )



        if not isinstance(
            providers,
            dict,
        ):

            raise TypeError(
                "providers must be dict"
            )



        self.providers = (

            self._normalize_provider_registry(
                providers
            )

        )



    # ==================================================
    #
    # Default Provider Registry
    #
    # ==================================================

    @staticmethod
    def _create_default_registry():
        """
        建立預設 Provider Registry。


        P5.6.2 支援：


            google_search

            google_news
        """


        return {

            "google_search":

                GoogleSearchProvider(),


            "google_news":

                GoogleNewsProvider(),

        }



    # ==================================================
    #
    # Resolve
    #
    # ==================================================

    def resolve(
        self,
        source_definition,
    ):
        """
        Source Definition

                ↓

        Resolved Source
        """



        self._validate_definition(
            source_definition
        )



        source_type = (

            self._normalize_string(
                source_definition.get(
                    "source_type"
                )
            )
            .lower()

        )



        if source_type == (

            self.SOURCE_TYPE_DIRECT_URL

        ):

            return (

                self.resolve_direct_url(
                    source_definition
                )

            )



        if source_type == (

            self.SOURCE_TYPE_SEARCH

        ):

            return (

                self.resolve_search(
                    source_definition
                )

            )



        raise ValueError(
            f"Unsupported source type: "
            f"{source_type}"
        )



    # ==================================================
    #
    # Direct URL Resolution
    #
    # ==================================================

    def resolve_direct_url(
        self,
        source_definition,
    ):
        """
        Direct URL Resolution。


        只保留 URL。


        不：

            Crawl

            HTTP Request

            Parser
        """



        url = (

            self._normalize_string(
                source_definition.get(
                    "url"
                )
            )

        )



        if not url:

            raise ValueError(
                "direct_url requires url"
            )



        resolved = {

            "source_type":

                self.SOURCE_TYPE_DIRECT_URL,


            "url":

                url,

        }



        target_type = (

            self._normalize_string(
                source_definition.get(
                    "target_type"
                )
            )
            .lower()

        )



        if target_type:

            resolved[
                "target_type"
            ] = target_type



        return resolved



    # ==================================================
    #
    # Search Resolution
    #
    # ==================================================

    def resolve_search(
        self,
        source_definition,
    ):
        """
        Search Resolution。


        Input:


        {
            source_type:
                "search",

            keyword:
                "AI",

            provider:
                "google_search",

            site:
                "https://example.com"
        }


        Output:

        {
            provider_instance:

            adapter:
        }


        不執行：

            adapter.search()
        """



        keyword = (

            self._normalize_string(
                source_definition.get(
                    "keyword"
                )
            )

        )



        if not keyword:

            raise ValueError(
                "search requires keyword"
            )



        provider_name = (

            self._normalize_string(
                source_definition.get(
                    "provider"
                )
            )
            .lower()

        )



        if not provider_name:

            raise ValueError(
                "search requires provider"
            )



        provider = (

            self.resolve_provider(
                provider_name
            )

        )



        site = (

            self._normalize_string(
                source_definition.get(
                    "site"
                )
            )

        )


        adapter = (

            self.create_adapter(
                provider,
                provider_name,
            )

        )



        resolved = {


            "source_type":

                self.SOURCE_TYPE_SEARCH,


            "keyword":

                keyword,


            "provider":

                provider_name,


            "provider_instance":

                provider,


            "adapter":

                adapter,

        }



        if site:

            resolved[
                "site"
            ] = site



        target_type = (

            self._normalize_string(
                source_definition.get(
                    "target_type"
                )
            )
            .lower()

        )



        if target_type:

            resolved[
                "target_type"
            ] = target_type



        return resolved
    # ==================================================
    #
    # Resolve Provider
    #
    # ==================================================

    def resolve_provider(
        self,
        provider_name,
    ):
        """
        Provider Name

                ↓

        Provider Instance


        不執行：

            provider.search()
        """

        provider_name = (
            self._normalize_string(
                provider_name
            )
            .lower()
        )


        if not provider_name:

            raise ValueError(
                "provider_name required"
            )


        provider = (
            self.providers.get(
                provider_name
            )
        )


        if provider is None:

            raise ValueError(
                f"Unsupported provider: "
                f"{provider_name}"
            )


        self._validate_provider_instance(
            provider
        )


        return provider



    # ==================================================
    #
    # Create Adapter
    #
    # ==================================================

    @staticmethod
    def create_adapter(
        provider,
        search_source=None,
    ):
        """
        Provider

            ↓

        ProviderSearchAdapter


        P5.6.2：

            建立 Adapter


        P5.6.3：

            執行 adapter.search()
        """


        SourceResolutionBridge._validate_provider_instance(
            provider
        )


        if search_source is not None:

            search_source = (
                str(
                    search_source
                )
                .strip()
            )


            if not search_source:

                search_source = None



        return ProviderSearchAdapter(
            provider=provider,
            search_source=search_source,
        )



    # ==================================================
    #
    # Provider Registry
    #
    # ==================================================

    def register_provider(
        self,
        name,
        provider,
    ):
        """
        Register Provider。
        """


        name = (
            self._normalize_string(
                name
            )
            .lower()
        )


        if not name:

            raise ValueError(
                "provider name required"
            )


        self._validate_provider_instance(
            provider
        )


        self.providers[
            name
        ] = provider



    def unregister_provider(
        self,
        name,
    ):
        """
        Remove Provider。
        """


        name = (
            self._normalize_string(
                name
            )
            .lower()
        )


        if name in self.providers:

            del self.providers[
                name
            ]



    def has_provider(
        self,
        provider_name,
    ):
        """
        Provider existence check。
        """


        provider_name = (
            self._normalize_string(
                provider_name
            )
            .lower()
        )


        return (
            provider_name
            in self.providers
        )



    def list_providers(
        self,
    ):
        """
        List Provider Names。
        """


        return list(
            self.providers.keys()
        )


    # ==================================================
    #
    # Source Type Checker
    #
    # ==================================================

    @staticmethod
    def is_direct_url(
        resolved_source,
    ):
        """
        判斷是否 Direct URL Source。
        """

        if not isinstance(
            resolved_source,
            dict,
        ):
            raise TypeError(
                "resolved_source must be dict"
            )


        return (
            resolved_source.get(
                "source_type"
            )
            ==
            SourceResolutionBridge.SOURCE_TYPE_DIRECT_URL
        )



    @staticmethod
    def is_search(
        resolved_source,
    ):
        """
        判斷是否 Search Source。
        """

        if not isinstance(
            resolved_source,
            dict,
        ):
            raise TypeError(
                "resolved_source must be dict"
            )


        return (
            resolved_source.get(
                "source_type"
            )
            ==
            SourceResolutionBridge.SOURCE_TYPE_SEARCH
        )


    # ==================================================
    #
    # Getter
    #
    # ==================================================

    @staticmethod
    def get_provider(
        resolved_source,
    ):
        """
        取得 Resolved Source Provider。
        """


        if not isinstance(
            resolved_source,
            dict,
        ):

            raise TypeError(
                "resolved_source must be dict"
            )


        provider = (
            resolved_source.get(
                "provider_instance"
            )
        )


        if provider is None:

            raise ValueError(
                "resolved source requires "
                "provider_instance"
            )


        SourceResolutionBridge._validate_provider_instance(
            provider
        )


        return provider



    @staticmethod
    def get_adapter(
        resolved_source,
    ):
        """
        取得 Resolved Source Adapter。


        P5.6.3 使用。
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
                "resolved source requires adapter"
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



    @staticmethod
    def get_site(
        resolved_source,
    ):
        """
        取得 Site。


        URL + Keyword Google Search 使用。
        """


        if not isinstance(
            resolved_source,
            dict,
        ):

            raise TypeError(
                "resolved_source must be dict"
            )


        return (
            SourceResolutionBridge
            ._normalize_string(
                resolved_source.get(
                    "site"
                )
            )
        )



    # ==================================================
    #
    # Validation
    #
    # ==================================================

    @classmethod
    def _validate_definition(
        cls,
        source_definition,
    ):
        """
        Source Definition Validation。


        只確認：

            dict

            source_type
        """


        if not isinstance(
            source_definition,
            dict,
        ):

            raise TypeError(
                "source_definition must be dict"
            )


        source_type = (
            cls._normalize_string(
                source_definition.get(
                    "source_type"
                )
            )
            .lower()
        )


        if not source_type:

            raise ValueError(
                "source_type required"
            )


        if source_type not in (
            cls.SUPPORTED_SOURCE_TYPES
        ):

            raise ValueError(
                f"Unsupported source type: "
                f"{source_type}"
            )



    @staticmethod
    def _validate_provider_instance(
        provider,
    ):
        """
        Provider Instance Validation。


        不驗證：

            API Key

            Network

            Search Result
        """


        if not isinstance(
            provider,
            SearchProvider,
        ):

            raise TypeError(
                "provider must be SearchProvider"
            )


        if not callable(
            getattr(
                provider,
                "search",
                None,
            )
        ):

            raise TypeError(
                "provider requires search()"
            )


        provider_name = (
            SourceResolutionBridge
            ._normalize_string(
                getattr(
                    provider,
                    "provider_name",
                    "",
                )
            )
        )


        if not provider_name:

            raise ValueError(
                "provider_name required"
            )



    @staticmethod
    def _normalize_provider_registry(
        providers,
    ):
        """
        Normalize Provider Registry。
        """


        result = {}


        for name, provider in providers.items():


            name = (
                SourceResolutionBridge
                ._normalize_string(
                    name
                )
                .lower()
            )


            if not name:

                raise ValueError(
                    "provider name required"
                )


            SourceResolutionBridge._validate_provider_instance(
                provider
            )


            result[
                name
            ] = provider



        return result



    # ==================================================
    #
    # Utility
    #
    # ==================================================

    @staticmethod
    def _normalize_string(
        value,
    ):
        """
        Normalize String。
        """


        if value is None:

            return ""


        return str(
            value
        ).strip()



# ==================================================
#
# Default Bridge
#
# ==================================================

default_source_resolution_bridge = (
    SourceResolutionBridge()
)



# ==================================================
#
# Convenience API
#
# ==================================================

def resolve_source(
    source_definition,
):
    """
    Convenience Resolver。


    Pipeline:


        TargetSourceService

                ↓

        SourceResolutionBridge

                ↓

        ProviderSearchAdapter

    """


    return (
        default_source_resolution_bridge.resolve(
            source_definition
        )
    )



# ==================================================
#
# Public API
#
# ==================================================

__all__ = [

    "SourceResolutionBridge",

    "default_source_resolution_bridge",

    "resolve_source",

]