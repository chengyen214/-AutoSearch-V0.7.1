"""
models/website_source.py

AutoSearch V5

V5.3 P3.8

Website Source Model

用途：

    定義 Generic Website Source。

設計：

    Website Source
        ├── name
        ├── base_url
        ├── search_url
        ├── search_method
        ├── keyword_parameter
        ├── max_results
        └── timeout

P3.8 負責：

    - Website Source Definition
    - Configuration Storage
    - Default Configuration
    - Basic Representation

不負責：

    - HTTP Request
    - Search
    - Search Provider
    - SearchAdapter
    - Crawler
    - Parser
    - Article
    - Archive
    - AI
    - Database
    - Scheduler

設計原則：

    WebsiteSource 只是「來源設定」。

    實際如何搜尋與抓取：

        WebsiteSource
            ↓
        Generic Source Handler
            ↓
        Existing V4 Pipeline
"""


class WebsiteSource:
    """
    V5.3 P3.8 Generic Website Source。

    定義一個可配置的 Website Source。

    Example
    -------

    WebsiteSource(
        name="TSMC",
        base_url="https://www.tsmc.com",
        search_url="https://www.tsmc.com/search",
        search_method="query",
        keyword_parameter="q",
    )
    """

    # ==================================================
    # Search Methods
    # ==================================================

    SEARCH_METHOD_QUERY = "query"
    SEARCH_METHOD_PATH = "path"

    ALLOWED_SEARCH_METHODS = {
        SEARCH_METHOD_QUERY,
        SEARCH_METHOD_PATH,
    }

    # ==================================================
    # Defaults
    # ==================================================

    DEFAULT_MAX_RESULTS = 20

    DEFAULT_TIMEOUT = 7

    DEFAULT_SEARCH_METHOD = SEARCH_METHOD_QUERY

    # ==================================================
    # Constructor
    # ==================================================

    def __init__(
        self,
        name="",
        base_url="",
        search_url="",
        search_method=None,
        keyword_parameter="q",
        max_results=None,
        timeout=None,
    ):
        """
        建立 Website Source。

        Parameters
        ----------
        name : str
            Source 名稱。

        base_url : str
            Website Base URL。

        search_url : str
            Website Search URL。

        search_method : str
            Search URL 組合方式。

        keyword_parameter : str
            Keyword 對應的參數名稱。

        max_results : int
            最大搜尋結果數量。

        timeout : int | float
            Request timeout。

        注意：

            本 Model 不執行 HTTP Request。
        """

        if search_method is None:
            search_method = (
                self.DEFAULT_SEARCH_METHOD
            )

        if max_results is None:
            max_results = (
                self.DEFAULT_MAX_RESULTS
            )

        if timeout is None:
            timeout = (
                self.DEFAULT_TIMEOUT
            )

        self.name = name

        self.base_url = base_url

        self.search_url = search_url

        self.search_method = search_method

        self.keyword_parameter = (
            keyword_parameter
        )

        self.max_results = max_results

        self.timeout = timeout

        self.normalize()

    # ==================================================
    # Normalize
    # ==================================================

    def normalize(self):
        """
        Normalize Website Source。

        Returns
        -------

        WebsiteSource
            自己本身。
        """

        self.name = (
            str(self.name).strip()
            if self.name is not None
            else ""
        )

        self.base_url = (
            str(self.base_url).strip()
            if self.base_url is not None
            else ""
        )

        self.search_url = (
            str(self.search_url).strip()
            if self.search_url is not None
            else ""
        )

        self.search_method = (
            str(self.search_method)
            .strip()
            .lower()
            if self.search_method is not None
            else ""
        )

        self.keyword_parameter = (
            str(self.keyword_parameter).strip()
            if self.keyword_parameter is not None
            else ""
        )

        if isinstance(
            self.max_results,
            str,
        ):

            value = self.max_results.strip()

            if value:

                try:

                    self.max_results = int(
                        value
                    )

                except ValueError:

                    pass

        if isinstance(
            self.timeout,
            str,
        ):

            value = self.timeout.strip()

            if value:

                try:

                    self.timeout = float(
                        value
                    )

                except ValueError:

                    pass

        self.validate()

        return self

    # ==================================================
    # Validate
    # ==================================================

    def validate(self):
        """
        驗證 Website Source Configuration。

        Returns
        -------

        bool

        Raises
        ------

        ValueError
            Configuration 無效。
        """

        # ----------------------------------------------
        # Name
        # ----------------------------------------------

        if not self.name:

            raise ValueError(
                "name cannot be empty"
            )

        # ----------------------------------------------
        # Base URL
        # ----------------------------------------------

        if not self.base_url:

            raise ValueError(
                "base_url cannot be empty"
            )

        # ----------------------------------------------
        # Search URL
        # ----------------------------------------------

        if not self.search_url:

            raise ValueError(
                "search_url cannot be empty"
            )

        # ----------------------------------------------
        # Search Method
        # ----------------------------------------------

        if (
            self.search_method
            not in self.ALLOWED_SEARCH_METHODS
        ):

            raise ValueError(
                f"invalid search_method: "
                f"{self.search_method}"
            )

        # ----------------------------------------------
        # Keyword Parameter
        # ----------------------------------------------

        if not self.keyword_parameter:

            raise ValueError(
                "keyword_parameter cannot be empty"
            )

        # ----------------------------------------------
        # Max Results
        # ----------------------------------------------

        if isinstance(
            self.max_results,
            bool,
        ):

            raise ValueError(
                "max_results must be an integer"
            )

        if not isinstance(
            self.max_results,
            int,
        ):

            raise ValueError(
                "max_results must be an integer"
            )

        if self.max_results <= 0:

            raise ValueError(
                "max_results must be greater than 0"
            )

        # ----------------------------------------------
        # Timeout
        # ----------------------------------------------

        if isinstance(
            self.timeout,
            bool,
        ):

            raise ValueError(
                "timeout must be a number"
            )

        if not isinstance(
            self.timeout,
            (int, float),
        ):

            raise ValueError(
                "timeout must be a number"
            )

        if self.timeout <= 0:

            raise ValueError(
                "timeout must be greater than 0"
            )

        return True

    # ==================================================
    # Search Source
    # ==================================================

    @property
    def is_query_search(self):
        """
        判斷是否使用 Query Parameter 搜尋。
        """

        return (
            self.search_method
            == self.SEARCH_METHOD_QUERY
        )

    @property
    def is_path_search(self):
        """
        判斷是否使用 Path 搜尋。
        """

        return (
            self.search_method
            == self.SEARCH_METHOD_PATH
        )

    # ==================================================
    # Dictionary
    # ==================================================

    def to_dict(self):
        """
        將 Website Source 轉成 Dictionary。
        """

        return {
            "name": self.name,
            "base_url": self.base_url,
            "search_url": self.search_url,
            "search_method": self.search_method,
            "keyword_parameter": (
                self.keyword_parameter
            ),
            "max_results": self.max_results,
            "timeout": self.timeout,
        }

    # ==================================================
    # Representation
    # ==================================================

    def __repr__(self):

        return (
            "WebsiteSource("
            f"name={self.name!r}, "
            f"base_url={self.base_url!r}, "
            f"search_url={self.search_url!r}, "
            f"search_method="
            f"{self.search_method!r}, "
            f"keyword_parameter="
            f"{self.keyword_parameter!r}, "
            f"max_results="
            f"{self.max_results!r}, "
            f"timeout={self.timeout!r}"
            ")"
        )


# ==================================================
# Public API
# ==================================================

__all__ = [
    "WebsiteSource",
]
