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


支援:


    1.

    URL Target

        url
          ↓
        direct_url



    2.

    URL + Keyword

        url + keyword
          ↓
        google_search definition



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


    Provider Resolution:

        SourceResolutionBridge

    負責。
"""


from models.target import Target



class TargetSourceService:
    """
    Target Source Resolution Service


    Target
        ↓
    Source Definition


    Source Type:

        direct_url

            直接 Crawl URL



        search

            Search Provider 搜尋


    本 Service 不建立：

        Provider

        Adapter

        Search Result

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

    DEFAULT_URL_SEARCH_PROVIDER = (
        "google_search"
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
    # Resolve
    #
    # ==================================================

    def resolve(
        self,
        target
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
            f"Unsupported target type: {target_type}"
        )



    # ==================================================
    #
    # URL Resolution
    #
    # ==================================================

    def resolve_url_target(
        self,
        target
    ):
        """
        URL Target Resolution


        Rule:


        URL + keyword

            ↓

        Google Search


        URL only

            ↓

        Direct URL Crawl

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
                    None
                )
            )
        )



        # ----------------------------------------------
        #
        # URL + Keyword
        #
        # Google Search
        #
        # ----------------------------------------------

        if keyword:
            
            return {

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

            }


        # ----------------------------------------------
        #
        # Direct URL
        #
        # ----------------------------------------------

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
        target
    ):
        """
        Search Target Resolution


        keyword + provider

            ↓

        search definition


        Provider:

            google_search

            google_news


        Provider Resolution:

            SourceResolutionBridge

        """


        keyword = self._normalize_string(
            target.keyword
        )


        if not keyword:

            raise ValueError(
                "Search target requires keyword"
            )



        provider = self._normalize_string(
            getattr(
                target,
                "search_provider",
                None
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
        target
    ):

        self._validate_target(
            target
        )


        return (

            self._normalize_string(
                target.target_type
            ).lower()

            ==

            self.TARGET_TYPE_URL

        )



    def is_search_target(
        self,
        target
    ):

        self._validate_target(
            target
        )


        return (

            self._normalize_string(
                target.target_type
            ).lower()

            ==

            self.TARGET_TYPE_SEARCH

        )



    def get_source_type(
        self,
        target
    ):
        """
        取得 Source Type
        """

        result = self.resolve(
            target
        )


        return result["source_type"]



    # ==================================================
    #
    # Internal
    #
    # ==================================================

    @staticmethod
    def _validate_target(
        target
    ):

        if not isinstance(
            target,
            Target
        ):

            raise TypeError(
                "target must be Target instance"
            )



    @staticmethod
    def _normalize_string(
        value
    ):

        if value is None:

            return ""


        return str(
            value
        ).strip()



__all__ = [
    "TargetSourceService"
]