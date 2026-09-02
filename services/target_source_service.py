"""
services/target_source_service.py

AutoSearch V5

V5.6.3

Target Source Resolution Service


用途：

    將 Target 轉換成 Pipeline 使用的
    Source Definition。


責任：

    Target
        ↓
    TargetSourceService
        ↓
    Source Definition


支援：

    1.

    URL Target

        url
          ↓
        direct_url


    2.

    URL + Keyword

        url + keyword
          ↓
        generic_search definition
          ↓
        crawler_url


    3.

    Search Target

        keyword + provider
          ↓
        search definition


不負責：

    - Provider Instance
    - SearchAdapter
    - SearchExecution
    - Crawl
    - Parser
    - Article
    - Archive
    - AI


設計原則：

    本 Service 只回答：

        這個 Target 要走哪種 Source。


    不回答：

        Source 如何執行。


    Provider Resolution：

        SourceResolutionBridge


    crawler_url：

        TargetRepository
            ↓
        TargetSourceService
            ↓
        Source Definition
            ↓
        後續 Pipeline
"""


# ==================================================
#
# Imports
#
# ==================================================

from models.target import Target

from database.target_repository import (
    TargetRepository,
)


# ==================================================
#
# Target Source Service
#
# ==================================================

class TargetSourceService:
    """
    Target Source Resolution Service。


    Target
        ↓
    Source Definition


    Source Type：

        direct_url

            直接 Crawl URL


        search

            Search Provider 搜尋


    本 Service 不建立：

        Provider

        Adapter

        Search Result


    crawler_url：

        只負責從 TargetRepository 取得
        並放入 Source Definition。

    不負責：

        crawler_url 的 Database Persistence
    """


    # ==================================================
    #
    # Source Type
    #
    # ==================================================

    SOURCE_TYPE_DIRECT_URL = "direct_url"

    SOURCE_TYPE_SEARCH = "search"


    # ==================================================
    #
    # Default Provider
    #
    # ==================================================

    """
    URL + Keyword 的預設 Search Provider。

    V5.6.3：

        URL + Keyword
            ↓
        generic_search
            ↓
        GenericSearchProvider

    Google News 仍可透過：

        Search Target
            ↓
        search_provider = google_news

    指定。
    """

    DEFAULT_URL_SEARCH_PROVIDER = (
        "generic_search"
    )


    # ==================================================
    #
    # Target Type
    #
    # ==================================================

    TARGET_TYPE_URL = "url"

    TARGET_TYPE_SEARCH = "search"


    # ==================================================
    #
    # Constructor
    #
    # ==================================================

    def __init__(
        self,
        target_repository=None,
    ):
        """
        建立 TargetSourceService。

        TargetRepository 用於：

            URL + Keyword
                ↓
            取得 crawler_url
        """

        if target_repository is None:

            target_repository = (
                TargetRepository()
            )

        self.target_repository = (
            target_repository
        )


    # ==================================================
    #
    # Resolve
    #
    # ==================================================

    def resolve(
        self,
        target,
    ):
        """
        Target
            ↓
        Source Definition
        """

        self._validate_target(
            target
        )

        target_type = (
            self._normalize_string(
                target.target_type
            ).lower()
        )

        if target_type == self.TARGET_TYPE_URL:

            return (
                self.resolve_url_target(
                    target
                )
            )

        if target_type == self.TARGET_TYPE_SEARCH:

            return (
                self.resolve_search_target(
                    target
                )
            )

        raise ValueError(
            f"Unsupported target type: "
            f"{target_type}"
        )


    # ==================================================
    #
    # URL Resolution
    #
    # ==================================================

    def resolve_url_target(
        self,
        target,
    ):
        """
        URL Target Resolution。


        URL + keyword：

            ↓

        generic_search


        URL only：

            ↓

        direct_url


        URL + Keyword：

            TargetRepository
                ↓
            crawler_url
                ↓
            Source Definition
        """

        url = self._normalize_string(
            target.url
        )

        if not url:

            raise ValueError(
                "URL target requires url"
            )


        keyword = (
            self._normalize_string(
                getattr(
                    target,
                    "keyword",
                    None,
                )
            )
        )


        # ==================================================
        #
        # URL + Keyword
        #
        # ==================================================

        if keyword:

            # ----------------------------------------------
            #
            # Get crawler_url
            #
            # ----------------------------------------------

            crawler_url = (
                self.target_repository
                .get_crawler_url_by_url_keyword(
                    url=url,
                    keyword=keyword,
                )
            )


            # ----------------------------------------------
            #
            # Normalize crawler_url
            #
            # ----------------------------------------------

            crawler_url = (
                self._normalize_string(
                    crawler_url
                )
            )


            # ----------------------------------------------
            #
            # Source Definition
            #
            # ----------------------------------------------

            source_definition = {

                "source_type":
                    self.SOURCE_TYPE_SEARCH,

                "target_type":
                    self.TARGET_TYPE_URL,

                "keyword":
                    keyword,

                "provider":
                    self.DEFAULT_URL_SEARCH_PROVIDER,

                "site":
                    url,

                "crawler_url":
                    crawler_url,
            }


            return source_definition


        # ==================================================
        #
        # Direct URL
        #
        # ==================================================

        return {

            "source_type":
                self.SOURCE_TYPE_DIRECT_URL,

            "target_type":
                self.TARGET_TYPE_URL,

            "url":
                url,
        }


    # ==================================================
    #
    # Search Resolution
    #
    # ==================================================

    def resolve_search_target(
        self,
        target,
    ):
        """
        Search Target Resolution。


        keyword + provider

            ↓

        search definition


        Provider：

            generic_search

            google_search

            google_news


        Provider Resolution：

            SourceResolutionBridge
        """

        keyword = self._normalize_string(
            target.keyword
        )

        if not keyword:

            raise ValueError(
                "Search target requires keyword"
            )


        provider = (
            self._normalize_string(
                getattr(
                    target,
                    "search_provider",
                    None,
                )
            )
        )

        if not provider:

            raise ValueError(
                "Search target requires provider"
            )


        return {

            "source_type":
                self.SOURCE_TYPE_SEARCH,

            "target_type":
                self.TARGET_TYPE_SEARCH,

            "keyword":
                keyword,

            "provider":
                provider,
        }


    # ==================================================
    #
    # Helpers
    #
    # ==================================================

    def is_url_target(
        self,
        target,
    ):

        self._validate_target(
            target
        )

        return (
            self._normalize_string(
                target.target_type
            ).lower()
            == self.TARGET_TYPE_URL
        )


    def is_search_target(
        self,
        target,
    ):

        self._validate_target(
            target
        )

        return (
            self._normalize_string(
                target.target_type
            ).lower()
            == self.TARGET_TYPE_SEARCH
        )


    def get_source_type(
        self,
        target,
    ):
        """
        取得 Source Type。
        """

        result = self.resolve(
            target
        )

        return result["source_type"]


    # ==================================================
    #
    # Get Provider
    #
    # ==================================================

    def get_provider(
        self,
        target,
    ):
        """
        取得 Target 對應的 Provider 名稱。

        注意：

            本方法不建立 Provider Instance。

            Provider Instance 由：

                SourceResolutionBridge

            負責。
        """

        result = self.resolve(
            target
        )

        if result.get(
            "source_type"
        ) != self.SOURCE_TYPE_SEARCH:

            return None

        return result.get(
            "provider"
        )


    # ==================================================
    #
    # Get Crawler URL
    #
    # ==================================================

    def get_crawler_url(
        self,
        target,
    ):
        """
        取得 URL + Keyword 對應的 crawler_url。

        Target
            ↓
        TargetSourceService
            ↓
        Source Definition
            ↓
        crawler_url
        """

        result = self.resolve(
            target
        )

        return result.get(
            "crawler_url"
        )


    # ==================================================
    #
    # Internal
    # ==================================================

    @staticmethod
    def _validate_target(
        target,
    ):

        if not isinstance(
            target,
            Target,
        ):

            raise TypeError(
                "target must be Target instance"
            )


    @staticmethod
    def _normalize_string(
        value,
    ):

        if value is None:

            return ""

        return str(
            value
        ).strip()


# ==================================================
#
# Public API
#
# ==================================================

__all__ = [
    "TargetSourceService",
]