"""
services/source_resolution_bridge.py

AutoSearch V5

V5.6.3

Source Resolution Bridge

用途：

    將 V5 TargetSourceService
    產生的 Source Definition
    解析成實際可執行的 Search Provider / Adapter。

責任：

    Source Definition
        ↓
    Provider Resolution
        ↓
    ProviderSearchAdapter

本模組不執行 Search。

URL + Keyword Search：

    TargetSourceService
        ↓
    site
        ↓
    SourceResolutionBridge
        ↓
    url
        ↓
    ProviderSearchAdapter
        ↓
    GoogleSearchProvider


設計原則：

    URL + Keyword：

        site → url

    Search Provider：

        google_search
        google_news

    Google Search：

        keyword + optional url

    Google News：

        keyword

本模組不負責：

    - adapter.search()
    - Google Search API
    - Google News RSS
    - URL Deduplication
    - Crawler
    - Parser
    - Article
    - Archive
    - AI
"""

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
    V5.6.3 Source Resolution Bridge。

    只負責：

        Source Definition
            ↓
        Provider
            ↓
        ProviderSearchAdapter

    並保留：

        site
          ↓
        url

    給後續 Search Execution 使用。

    不負責：

        adapter.search()
    """

    # ==================================================
    # Source Types
    # ==================================================

    SOURCE_TYPE_DIRECT_URL = "direct_url"

    SOURCE_TYPE_SEARCH = "search"

    SUPPORTED_SOURCE_TYPES = {
        SOURCE_TYPE_DIRECT_URL,
        SOURCE_TYPE_SEARCH,
    }

    # ==================================================
    # Providers
    # ==================================================

    PROVIDER_GOOGLE_SEARCH = "google_search"

    PROVIDER_GOOGLE_NEWS = "google_news"

    SUPPORTED_PROVIDERS = {
        PROVIDER_GOOGLE_SEARCH,
        PROVIDER_GOOGLE_NEWS,
    }

    # ==================================================
    # Constructor
    # ==================================================

    def __init__(
        self,
        google_search_provider=None,
        google_news_provider=None,
    ):
        """
        建立 SourceResolutionBridge。

        若未注入 Provider，
        使用預設 Provider。
        """

        if google_search_provider is None:

            google_search_provider = (
                GoogleSearchProvider()
            )

        self._validate_provider_instance(
            google_search_provider
        )

        self.google_search_provider = (
            google_search_provider
        )

        if google_news_provider is None:

            google_news_provider = (
                GoogleNewsProvider()
            )

        self._validate_provider_instance(
            google_news_provider
        )

        self.google_news_provider = (
            google_news_provider
        )

    # ==================================================
    # Resolve
    # ==================================================

    def resolve(
        self,
        source_definition,
    ):
        """
        Source Definition Resolution。
        """

        self._validate_definition(
            source_definition
        )

        source_type = (
            source_definition.get(
                "source_type"
            )
        )

        if source_type == (
            self.SOURCE_TYPE_DIRECT_URL
        ):

            return self.resolve_direct_url(
                source_definition
            )

        if source_type == (
            self.SOURCE_TYPE_SEARCH
        ):

            return self.resolve_search(
                source_definition
            )

        raise ValueError(
            f"Unsupported source type: "
            f"{source_type}"
        )

    # ==================================================
    # Resolve Direct URL
    # ==================================================

    def resolve_direct_url(
        self,
        source_definition,
    ):
        """
        Resolve Direct URL。

        不建立 Provider。
        不建立 Adapter。
        不執行 HTTP。
        """

        self._validate_definition(
            source_definition
        )

        if source_definition.get(
            "source_type"
        ) != self.SOURCE_TYPE_DIRECT_URL:

            raise ValueError(
                "Source definition must be "
                "a direct_url source"
            )

        url = source_definition.get(
            "url"
        )

        if url is None:

            raise ValueError(
                "Direct URL source requires url"
            )

        url = str(
            url
        ).strip()

        if not url:

            raise ValueError(
                "Direct URL source requires url"
            )

        return {
            "source_type":
                self.SOURCE_TYPE_DIRECT_URL,

            "url":
                url,
        }

    # ==================================================
    # Resolve Search
    # ==================================================

    def resolve_search(
        self,
        source_definition,
    ):
        """
        Resolve Search Source。

        Pipeline：

            Source Definition
                    ↓
                Provider
                    ↓
            ProviderSearchAdapter

        URL + Keyword：

            site
              ↓
            url
              ↓
            ProviderSearchAdapter
              ↓
            GoogleSearchProvider

        注意：

            本方法不執行 adapter.search()。

            本方法只負責解析與保存
            Search Execution 所需的參數。
        """

        self._validate_definition(
            source_definition
        )

        if source_definition.get(
            "source_type"
        ) != self.SOURCE_TYPE_SEARCH:

            raise ValueError(
                "Source definition must be "
                "a search source"
            )

        # ==================================================
        # Keyword
        # ==================================================

        keyword = source_definition.get(
            "keyword"
        )

        if keyword is None:

            raise ValueError(
                "Search source requires keyword"
            )

        keyword = str(
            keyword
        ).strip()

        if not keyword:

            raise ValueError(
                "Search source requires keyword"
            )

        # ==================================================
        # Provider
        # ==================================================

        provider_name = source_definition.get(
            "provider"
        )

        if provider_name is None:

            raise ValueError(
                "Search source requires provider"
            )

        provider_name = str(
            provider_name
        ).strip()

        if not provider_name:

            raise ValueError(
                "Search source requires provider"
            )

        if not self.is_supported_provider(
            provider_name
        ):

            raise ValueError(
                f"Unsupported search provider: "
                f"{provider_name}"
            )

        # ==================================================
        # URL / Site
        # ==================================================

        """
        TargetSourceService 對：

            URL + Keyword

        產生：

            site = url

        Provider 層統一使用：

            url

        因此這裡：

            site → url
        """

        site = source_definition.get(
            "site"
        )

        url = None

        if site is not None:

            site = str(
                site
            ).strip()

            if site:

                url = site

        # ==================================================
        # Provider
        # ==================================================

        provider = self.resolve_provider(
            provider_name
        )

        # ==================================================
        # Adapter
        # ==================================================

        adapter = self.create_provider_adapter(
            provider,
            search_source=provider_name,
        )

        # ==================================================
        # Search Source Identity
        # ==================================================

        search_source = getattr(
            adapter,
            "search_source",
            None,
        )

        if not search_source:

            search_source = provider_name

        # ==================================================
        # Result Limit
        # ==================================================

        max_results = getattr(
            adapter,
            "max_results",
            None,
        )

        # ==================================================
        # Resolved Source
        # ==================================================

        resolved_source = {
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

            "search_source":
                search_source,

            "max_results":
                max_results,
        }

        # ==================================================
        # URL Forwarding
        # ==================================================

        """
        只有存在 site 時才加入 url。

        因此：

            Google Search + site

                ↓

            {
                ...
                "url": "https://..."
            }

            Google Search without site

                ↓

            不加入 url

            Google News

                ↓

            通常不會有 url
        """

        if url:

            resolved_source["url"] = url

        return resolved_source

    # ==================================================
    # Resolve Provider
    # ==================================================

    def resolve_provider(
        self,
        provider_name,
    ):
        """
        Provider Name
            ↓
        Provider Instance

        不執行 Search。
        """

        if provider_name is None:

            raise ValueError(
                "provider_name cannot be None"
            )

        provider_name = str(
            provider_name
        ).strip()

        if not provider_name:

            raise ValueError(
                "provider_name cannot be empty"
            )

        if not self.is_supported_provider(
            provider_name
        ):

            raise ValueError(
                f"Unsupported search provider: "
                f"{provider_name}"
            )

        if provider_name == (
            self.PROVIDER_GOOGLE_SEARCH
        ):

            return (
                self.google_search_provider
            )

        if provider_name == (
            self.PROVIDER_GOOGLE_NEWS
        ):

            return (
                self.google_news_provider
            )

        raise ValueError(
            f"Unsupported search provider: "
            f"{provider_name}"
        )

    # ==================================================
    # Create Provider Adapter
    # ==================================================

    @staticmethod
    def create_provider_adapter(
        provider,
        search_source=None,
        max_results=None,
    ):
        """
        Provider
            ↓
        ProviderSearchAdapter

        不執行 Search。
        """

        SourceResolutionBridge._validate_provider_instance(
            provider
        )

        return ProviderSearchAdapter(
            provider=provider,
            search_source=search_source,
            max_results=max_results,
        )

    # ==================================================
    # Get Adapter
    # ==================================================

    @staticmethod
    def get_adapter(
        resolved_source,
    ):
        """
        取得已 Resolution 的 Adapter。

        不建立新的 Adapter。
        """

        if not isinstance(
            resolved_source,
            dict,
        ):

            raise TypeError(
                "resolved_source must be a dict"
            )

        if resolved_source.get(
            "source_type"
        ) != SourceResolutionBridge.SOURCE_TYPE_SEARCH:

            raise ValueError(
                "resolved_source must be "
                "a search source"
            )

        adapter = resolved_source.get(
            "adapter"
        )

        if adapter is None:

            raise ValueError(
                "resolved search source "
                "requires adapter"
            )

        if not callable(
            getattr(
                adapter,
                "search",
                None,
            )
        ):

            raise TypeError(
                "adapter must provide "
                "a search() method"
            )

        return adapter

    # ==================================================
    # Get Provider
    # ==================================================

    @staticmethod
    def get_provider(
        resolved_source,
    ):
        """
        取得 Provider Instance。
        """

        if not isinstance(
            resolved_source,
            dict,
        ):

            raise TypeError(
                "resolved_source must be a dict"
            )

        provider = resolved_source.get(
            "provider_instance"
        )

        if provider is None:

            raise ValueError(
                "resolved search source "
                "requires provider_instance"
            )

        return provider

    # ==================================================
    # Get Provider Name
    # ==================================================

    @staticmethod
    def get_provider_name(
        resolved_source,
    ):
        """
        取得 Provider Identity。
        """

        if not isinstance(
            resolved_source,
            dict,
        ):

            raise TypeError(
                "resolved_source must be a dict"
            )

        provider = resolved_source.get(
            "provider"
        )

        if not provider:

            raise ValueError(
                "resolved search source "
                "requires provider"
            )

        return provider

    # ==================================================
    # Get Search Source
    # ==================================================

    @staticmethod
    def get_search_source(
        resolved_source,
    ):
        """
        取得 Search Source Identity。
        """

        if not isinstance(
            resolved_source,
            dict,
        ):

            raise TypeError(
                "resolved_source must be a dict"
            )

        search_source = resolved_source.get(
            "search_source"
        )

        if search_source:

            return search_source

        provider = resolved_source.get(
            "provider"
        )

        if provider:

            return provider

        raise ValueError(
            "resolved search source "
            "requires search_source"
        )

    # ==================================================
    # Get URL
    # ==================================================

    @staticmethod
    def get_url(
        resolved_source,
    ):
        """
        取得 Search URL。

        URL 來源：

            TargetSourceService
                ↓
            site
                ↓
            SourceResolutionBridge
                ↓
            url
        """

        if not isinstance(
            resolved_source,
            dict,
        ):

            raise TypeError(
                "resolved_source must be a dict"
            )

        url = resolved_source.get(
            "url"
        )

        if url is None:

            return None

        url = str(
            url
        ).strip()

        if not url:

            return None

        return url

    # ==================================================
    # Is Direct URL
    # ==================================================

    def is_direct_url(
        self,
        source_definition,
    ):
        """
        判斷是否為 Direct URL。
        """

        self._validate_definition(
            source_definition
        )

        return (
            source_definition.get(
                "source_type"
            )
            == self.SOURCE_TYPE_DIRECT_URL
        )

    # ==================================================
    # Is Search
    # ==================================================

    def is_search(
        self,
        source_definition,
    ):
        """
        判斷是否為 Search。
        """

        self._validate_definition(
            source_definition
        )

        return (
            source_definition.get(
                "source_type"
            )
            == self.SOURCE_TYPE_SEARCH
        )

    # ==================================================
    # Is Supported Provider
    # ==================================================

    def is_supported_provider(
        self,
        provider_name,
    ):
        """
        判斷 Provider 是否支援。
        """

        if provider_name is None:

            return False

        provider_name = str(
            provider_name
        ).strip()

        if not provider_name:

            return False

        return (
            provider_name
            in self.SUPPORTED_PROVIDERS
        )

    # ==================================================
    # Validation
    # ==================================================

    @classmethod
    def _validate_definition(
        cls,
        source_definition,
    ):
        """
        基本 Source Definition Validation。
        """

        if not isinstance(
            source_definition,
            dict,
        ):

            raise TypeError(
                "source_definition must be a dict"
            )

        source_type = source_definition.get(
            "source_type"
        )

        if not source_type:

            raise ValueError(
                "source_definition requires "
                "source_type"
            )

        if source_type not in (
            cls.SUPPORTED_SOURCE_TYPES
        ):

            raise ValueError(
                f"Unsupported source type: "
                f"{source_type}"
            )

    # ==================================================
    # Provider Validation
    # ==================================================

    @staticmethod
    def _validate_provider_instance(
        provider,
    ):
        """
        驗證 Provider Instance。

        不驗證 API Key。
        不執行 Search。
        """

        if not isinstance(
            provider,
            SearchProvider,
        ):

            raise TypeError(
                "provider must be a SearchProvider"
            )

        if not callable(
            getattr(
                provider,
                "search",
                None,
            )
        ):

            raise TypeError(
                "provider must provide "
                "a search() method"
            )


# ==================================================
# Default Bridge
# ==================================================

default_source_resolution_bridge = (
    SourceResolutionBridge()
)


# ==================================================
# Convenience API
# ==================================================

def resolve_source(
    source_definition,
):
    """
    使用預設 SourceResolutionBridge。
    """

    return (
        default_source_resolution_bridge.resolve(
            source_definition
        )
    )


# ==================================================
# Public API
# ==================================================

__all__ = [
    "SourceResolutionBridge",
    "default_source_resolution_bridge",
    "resolve_source",
]
