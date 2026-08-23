"""
services/generic_source_handler.py

AutoSearch V5

V5.3 P3.9

Generic Source Handler

用途：

    將 WebsiteSource Configuration
    轉換成統一的 Search Request Definition。

架構：

    Target
        ↓
    TargetSourceService
        ↓
    WebsiteSource
        ↓
    GenericSourceHandler
        ↓
    Search Request Definition
        ↓
    Existing V4 Pipeline

P3.9 負責：

    - Generic Website Source Handling
    - Source Validation
    - Keyword Normalization
    - Query URL Construction
    - Path URL Construction
    - Request Definition 建立
    - Max Results Configuration
    - Timeout Configuration

P3.9 不負責：

    - HTTP Request
    - requests
    - Search Provider
    - SearchAdapter
    - Crawler
    - Parser
    - Article
    - Archive
    - AI
    - Database
    - Job
    - Scheduler

設計原則：

    不為每個網站建立獨立 Adapter。

    不應該出現：

        tsmc_adapter.py
        intel_adapter.py
        nvidia_adapter.py
        amd_adapter.py

    而應該：

        WebsiteSource
            ↓
        GenericSourceHandler
            ↓
        Request Definition

    所有 Generic Website Source
    使用同一個 Handler。
"""


from urllib.parse import (
    quote_plus,
    urlencode,
    urlparse,
)


from models.website_source import (
    WebsiteSource,
)


class GenericSourceHandler:
    """
    V5.3 P3.9 Generic Source Handler。

    將 WebsiteSource Configuration
    轉換成統一的 Request Definition。

    注意：

        本 Handler 不執行 HTTP Request。

        只負責：

            Configuration
                ↓
            Request Definition
    """

    # ==================================================
    # Constructor
    # ==================================================

    def __init__(self):
        """
        建立 GenericSourceHandler。
        """

        pass

    # ==================================================
    # Handle
    # ==================================================

    def handle(
        self,
        source,
        keyword,
    ):
        """
        處理 Generic Website Source。

        Parameters
        ----------
        source : WebsiteSource
            Website Source Configuration。

        keyword : str
            User Search Keyword。

        Returns
        -------
        dict
            統一 Request Definition。

        Raises
        ------
        TypeError
            source 不是 WebsiteSource。

        ValueError
            Source 或 Keyword 無效。
        """

        self.validate_source(
            source
        )

        keyword = self.normalize_keyword(
            keyword
        )

        if not keyword:

            raise ValueError(
                "keyword cannot be empty"
            )

        if source.is_query_search:

            return self.build_query_request(
                source,
                keyword,
            )

        if source.is_path_search:

            return self.build_path_request(
                source,
                keyword,
            )

        raise ValueError(
            f"Unsupported search method: "
            f"{source.search_method}"
        )

    # ==================================================
    # Build Request
    # ==================================================

    def build_request(
        self,
        source,
        keyword,
    ):
        """
        建立 Generic Source Request Definition。

        此方法為統一入口。

        等同：

            handle()
        """

        return self.handle(
            source,
            keyword,
        )

    # ==================================================
    # Query Request
    # ==================================================

    def build_query_request(
        self,
        source,
        keyword,
    ):
        """
        建立 Query Parameter Search Request。

        Example：

            search_url =
                https://example.com/search

            keyword_parameter =
                q

            keyword =
                semiconductor

        Result URL：

            https://example.com/search?q=semiconductor
        """

        self.validate_source(
            source
        )

        keyword = self.normalize_keyword(
            keyword
        )

        if not keyword:

            raise ValueError(
                "keyword cannot be empty"
            )

        params = {
            source.keyword_parameter: keyword
        }

        url = self._append_query_parameters(
            source.search_url,
            params,
        )

        return self._build_request_definition(
            source=source,
            keyword=keyword,
            url=url,
            search_method=(
                WebsiteSource.SEARCH_METHOD_QUERY
            ),
        )

    # ==================================================
    # Path Request
    # ==================================================

    def build_path_request(
        self,
        source,
        keyword,
    ):
        """
        建立 Path Search Request。

        Example：

            search_url =
                https://example.com/search

            keyword =
                semiconductor

        Result URL：

            https://example.com/search/semiconductor

        Keyword 會進行 URL encoding。
        """

        self.validate_source(
            source
        )

        keyword = self.normalize_keyword(
            keyword
        )

        if not keyword:

            raise ValueError(
                "keyword cannot be empty"
            )

        encoded_keyword = quote_plus(
            keyword
        )

        base_url = (
            source.search_url.rstrip("/")
        )

        url = (
            f"{base_url}/"
            f"{encoded_keyword}"
        )

        return self._build_request_definition(
            source=source,
            keyword=keyword,
            url=url,
            search_method=(
                WebsiteSource.SEARCH_METHOD_PATH
            ),
        )

    # ==================================================
    # Normalize Keyword
    # ==================================================

    @staticmethod
    def normalize_keyword(
        keyword,
    ):
        """
        Normalize Search Keyword。

        處理：

            None
            非字串
            前後空白
            多餘空白

        Example：

            "  IC   semiconductor  "

        →

            "IC semiconductor"
        """

        if keyword is None:

            return ""

        if not isinstance(
            keyword,
            str,
        ):

            keyword = str(
                keyword
            )

        return " ".join(
            keyword.strip().split()
        )

    # ==================================================
    # Validate Source
    # ==================================================

    @staticmethod
    def validate_source(
        source,
    ):
        """
        驗證 WebsiteSource。

        GenericSourceHandler 不重新實作
        WebsiteSource 的完整 Validation。

        WebsiteSource 本身已負責：

            normalize()
            validate()

        Handler 只確認：

            1. 型別正確
            2. Source Configuration 合法
        """

        if not isinstance(
            source,
            WebsiteSource,
        ):

            raise TypeError(
                "source must be an instance "
                "of WebsiteSource"
            )

        source.validate()

        return True

    # ==================================================
    # Request Definition
    # ==================================================

    @staticmethod
    def _build_request_definition(
        source,
        keyword,
        url,
        search_method,
    ):
        """
        建立統一 Request Definition。

        注意：

            這不是 HTTP Request。

            只是描述：

                「之後應該如何發出 Request」
        """

        return {

            "source_name":
                source.name,

            "base_url":
                source.base_url,

            "search_url":
                source.search_url,

            "url":
                url,

            "keyword":
                keyword,

            "search_method":
                search_method,

            "keyword_parameter":
                source.keyword_parameter,

            "max_results":
                source.max_results,

            "timeout":
                source.timeout,

        }

    # ==================================================
    # Append Query Parameters
    # ==================================================

    @staticmethod
    def _append_query_parameters(
        url,
        parameters,
    ):
        """
        將 Query Parameters 加入 URL。

        支援原本已存在 Query String 的 URL。

        Example：

            https://example.com/search?page=1

        +

            q=AI

        →

            https://example.com/search?page=1&q=AI
        """

        parsed = urlparse(
            url
        )

        existing_query = parsed.query

        new_query = urlencode(
            parameters
        )

        if existing_query:

            query = (
                f"{existing_query}"
                f"&{new_query}"
            )

        else:

            query = new_query

        return (
            f"{parsed.scheme}://"
            f"{parsed.netloc}"
            f"{parsed.path}"
            f"?{query}"
        )


# ======================================================
# Default Handler
# ======================================================

default_generic_source_handler = (
    GenericSourceHandler()
)


# ======================================================
# Convenience Function
# ======================================================

def build_source_request(
    source,
    keyword,
):
    """
    建立 Generic Source Request Definition。

    Example：

        build_source_request(
            source,
            "semiconductor",
        )
    """

    return default_generic_source_handler.handle(
        source,
        keyword,
    )


# ======================================================
# Public API
# ======================================================

__all__ = [
    "GenericSourceHandler",
    "default_generic_source_handler",
    "build_source_request",
]
