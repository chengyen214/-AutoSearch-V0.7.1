"""
search/generic_website_provider.py

AutoSearch V5

V5.7

Generic Website List Provider

用途：

    提供通用 Website List Provider。

核心設計：

    Source Definition
        ↓
    GenericWebsiteProvider
        ↓
    Website Latest List
        ↓
    HTTP Request
        ↓
    Parse Latest N Items
        ↓
    Keyword Matching
        ↓
    SearchResult[]
        ↓
    ProviderSearchAdapter
        ↓
    SearchExecutionBridge

設計原則：

    GenericWebsiteProvider 不綁定任何特定 Website。

    不寫死：

        - TSMC
        - Intel
        - Renesas
        - NVIDIA
        - AMD
        - 其他特定 Website

    Website 差異全部透過 Configuration 解決。

每個 Website 通常只需要提供：

    - provider_name
    - list_url
    - list_limit
    - result_selector
    - title_selector
    - url_selector
    - published_selector
    - source

如果 Website HTML 結構特殊：

    - optional parser

Pipeline：

    keyword
        ↓
    GenericWebsiteProvider.search()
        ↓
    GET list_url
        ↓
    Parse Website List
        ↓
    Latest N Items
        ↓
    Keyword Matching
        ↓
    Local URL Deduplication
        ↓
    SearchResult[]
        ↓
    max_results

重要：

    list_limit

        = 從 Website 最新列表掃描多少筆

    max_results

        = Keyword Matching 後最多回傳多少筆

例如：

    list_limit = 20
    max_results = 20

代表：

    Website 最新 20 筆
        ↓
    keyword matching
        ↓
    最多回傳 20 筆

本模組不負責：

    - ProviderSearchAdapter
    - SourceResolutionBridge
    - SearchExecutionBridge
    - Global URL Deduplication
    - Crawler
    - Parser
    - Article
    - Archive
    - AI
    - Database
"""


# ==================================================
#
# Standard Library
#
# ==================================================

from urllib.parse import (
    urljoin,
)


# ==================================================
#
# HTTP
#
# ==================================================

import requests


# ==================================================
#
# HTML Parser
#
# ==================================================

from bs4 import (
    BeautifulSoup,
)


# ==================================================
#
# Search Provider Base
#
# ==================================================

from search.search_provider import (
    SearchProvider,
)


# ==================================================
#
# Search Result
#
# ==================================================

from models.search_result import (
    SearchResult,
)


class GenericWebsiteProvider(SearchProvider):
    """
    通用 Website List Provider。

    不依賴 Website Search API。

    每次 Search：

        Website Latest List
                ↓
        最新 N 筆
                ↓
        Keyword Matching
                ↓
        SearchResult[]

    Website 的差異：

        由 Constructor Configuration 決定。

    例如：

        provider = GenericWebsiteProvider(
            provider_name="intel",
            list_url="https://example.com/news",
            list_limit=20,
            result_selector=".news-item",
            title_selector=".title",
            url_selector="a",
            published_selector=".date",
            source="Intel",
        )

        results = provider.search("IC")
    """

    # ==================================================
    #
    # Provider Identity
    #
    # ==================================================

    provider_name = "generic_website"

    # ==================================================
    #
    # Default List Limit
    #
    # ==================================================

    list_limit = 20

    # ==================================================
    #
    # Default Result Limit
    #
    # ==================================================

    max_results = 20

    # ==================================================
    #
    # Default Timeout
    #
    # ==================================================

    timeout = 7

    # ==================================================
    #
    # Constructor
    #
    # ==================================================

    def __init__(
        self,
        provider_name=None,
        list_url=None,
        list_limit=None,
        max_results=None,
        timeout=None,
        headers=None,
        result_selector=None,
        title_selector=None,
        url_selector=None,
        published_selector=None,
        source=None,
        parser=None,
    ):
        """
        建立 Generic Website List Provider。

        Parameters
        ----------

        provider_name :
            Provider Identity。

        list_url :
            Website 最新消息列表 URL。

        list_limit :
            每次最多掃描多少筆 Website List Item。

            預設：

                20

        max_results :
            Keyword Matching 後最多回傳多少筆。

            預設：

                20

        timeout :
            HTTP Timeout。

        headers :
            HTTP Request Headers。

        result_selector :
            一筆列表項目的 Container Selector。

            例如：

                article
                .news-item
                li.news-item

        title_selector :
            標題 Selector。

            例如：

                h2
                .title
                a.title

        url_selector :
            URL Selector。

            例如：

                a

        published_selector :
            Optional Published Date Selector。

        source :
            Article Source Identity。

        parser :
            Optional Custom Parser。

            Signature：

                parser(
                    html,
                    keyword,
                    provider
                )

            必須回傳：

                list[SearchResult]

            Custom Parser 的結果：

                仍然會經過：

                    list_limit
                    keyword matching
                    URL dedup
                    normalization
                    max_results
        """

        # ==================================================
        #
        # Provider Name
        #
        # ==================================================

        if provider_name is None:

            provider_name = (
                self.provider_name
            )

        provider_name = (
            self._normalize_text(
                provider_name
            )
        )

        if not provider_name:

            raise ValueError(
                "provider_name cannot be empty"
            )

        self.provider_name = (
            provider_name
        )

        # ==================================================
        #
        # List URL
        #
        # ==================================================

        if list_url is None:

            list_url = ""

        self.list_url = (
            self._normalize_text(
                list_url
            )
        )

        # ==================================================
        #
        # List Limit
        #
        # ==================================================

        if list_limit is None:

            list_limit = (
                self.list_limit
            )

        self.list_limit = (
            self._normalize_positive_int(
                list_limit,
                "list_limit",
            )
        )

        # ==================================================
        #
        # Result Limit
        #
        # ==================================================

        if max_results is None:

            max_results = (
                self.max_results
            )

        self.max_results = (
            self._normalize_positive_int(
                max_results,
                "max_results",
            )
        )

        # ==================================================
        #
        # Timeout
        #
        # ==================================================

        if timeout is None:

            timeout = (
                self.timeout
            )

        self.timeout = (
            self._normalize_positive_int(
                timeout,
                "timeout",
            )
        )

        # ==================================================
        #
        # Headers
        #
        # ==================================================

        if headers is None:

            headers = {
                "User-Agent": (
                    "Mozilla/5.0 "
                    "(Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 "
                    "(KHTML, like Gecko) "
                    "Chrome/151.0 Safari/537.36"
                )
            }

        if not isinstance(
            headers,
            dict,
        ):

            raise TypeError(
                "headers must be a dict"
            )

        self.headers = dict(
            headers
        )

        # ==================================================
        #
        # HTML Selectors
        #
        # ==================================================

        self.result_selector = (
            self._normalize_optional_text(
                result_selector
            )
        )

        self.title_selector = (
            self._normalize_optional_text(
                title_selector
            )
        )

        self.url_selector = (
            self._normalize_optional_text(
                url_selector
            )
        )

        self.published_selector = (
            self._normalize_optional_text(
                published_selector
            )
        )

        # ==================================================
        #
        # Source
        #
        # ==================================================

        self.source = (
            self._normalize_optional_text(
                source
            )
        )

        # ==================================================
        #
        # Custom Parser
        #
        # ==================================================

        if (
            parser is not None
            and not callable(parser)
        ):

            raise TypeError(
                "parser must be callable"
            )

        self.parser = parser

    # ==================================================
    #
    # Search
    #
    # ==================================================

    def search(
        self,
        keyword,
        max_results=None,
    ):
        """
        執行 Website List Search。

        Pipeline：

            keyword
                ↓
            GET list_url
                ↓
            Parse Latest List
                ↓
            Keyword Matching
                ↓
            Normalize
                ↓
            SearchResult[]
        """

        # ==================================================
        #
        # Keyword
        #
        # ==================================================

        keyword = (
            self._normalize_text(
                keyword
            )
        )

        if not keyword:

            return []

        # ==================================================
        #
        # Result Limit
        #
        # ==================================================

        if max_results is None:

            max_results = (
                self.max_results
            )

        max_results = (
            self._normalize_positive_int(
                max_results,
                "max_results",
            )
        )

        # ==================================================
        #
        # Validate List URL
        #
        # ==================================================

        if not self.list_url:

            raise ValueError(
                "list_url is required"
            )

        # ==================================================
        #
        # HTTP Request
        #
        # ==================================================

        try:

            response = requests.get(
                self.list_url,
                headers=self.headers,
                timeout=self.timeout,
            )

            response.raise_for_status()

        except requests.RequestException as e:

            print(
                "Generic Website Provider failed:",
                self.provider_name,
                e,
            )

            return []

        # ==================================================
        #
        # Parse
        #
        # ==================================================

        if self.parser is not None:

            results = self.parser(
                response.text,
                keyword,
                self,
            )

        else:

            results = (
                self.parse_results(
                    response.text,
                    keyword,
                )
            )

        # ==================================================
        #
        # Normalize
        #
        # ==================================================

        return self._normalize_results(
            results,
            keyword,
            max_results,
        )

    # ==================================================
    #
    # Parse Results
    #
    # ==================================================

    def parse_results(
        self,
        html,
        keyword,
    ):
        """
        解析 Website 最新列表。

        注意：

            這裡只解析 List。

            不負責：

                Article Crawl
                Article Parser
                Archive
                AI
        """

        if not html:

            return []

        soup = BeautifulSoup(
            html,
            "html.parser",
        )

        # ==================================================
        #
        # Result Containers
        #
        # ==================================================

        if self.result_selector:

            containers = soup.select(
                self.result_selector
            )

        else:

            containers = soup.select(
                "a[href]"
            )

        # ==================================================
        #
        # Parse List
        #
        # ==================================================

        results = []

        for container in containers:

            # --------------------------------------------------
            # URL
            # --------------------------------------------------

            url = (
                self._extract_url(
                    container
                )
            )

            if not url:

                continue

            # --------------------------------------------------
            # Title
            # --------------------------------------------------

            title = (
                self._extract_title(
                    container
                )
            )

            if not title:

                continue

            # --------------------------------------------------
            # Published
            # --------------------------------------------------

            published = (
                self._extract_published(
                    container
                )
            )

            # --------------------------------------------------
            # SearchResult
            # --------------------------------------------------

            result = SearchResult(

                keyword=keyword,

                title=title,

                url=url,

                source=(
                    self.source
                    or self.provider_name
                ),

                published=published,

                search_source=(
                    self.provider_name
                ),

                rank=len(results) + 1,
            )

            results.append(
                result
            )

            # --------------------------------------------------
            # List Limit
            # --------------------------------------------------

            if len(results) >= self.list_limit:

                break

        return results

    # ==================================================
    #
    # Extract URL
    #
    # ==================================================

    def _extract_url(
        self,
        container,
    ):
        """
        從 List Container 取得 URL。
        """

        element = container

        # ==================================================
        #
        # URL Selector
        #
        # ==================================================

        if self.url_selector:

            selected = container.select_one(
                self.url_selector
            )

            if selected is None:

                return ""

            element = selected

        # ==================================================
        #
        # Href
        #
        # ==================================================

        url = element.get(
            "href"
        )

        if not url:

            return ""

        url = (
            self._normalize_text(
                url
            )
        )

        if not url:

            return ""

        # ==================================================
        #
        # Invalid URL
        #
        # ==================================================

        if url.startswith(
            (
                "#",
                "javascript:",
                "mailto:",
                "tel:",
            )
        ):

            return ""

        # ==================================================
        #
        # Relative URL
        #
        # ==================================================

        url = urljoin(
            self.list_url,
            url,
        )

        # ==================================================
        #
        # HTTP Validation
        #
        # ==================================================

        if not url.startswith(
            (
                "http://",
                "https://",
            )
        ):

            return ""

        return url

    # ==================================================
    #
    # Extract Title
    #
    # ==================================================

    def _extract_title(
        self,
        container,
    ):
        """
        取得 List Item Title。
        """

        # ==================================================
        #
        # Explicit Selector
        #
        # ==================================================

        if self.title_selector:

            selected = container.select_one(
                self.title_selector
            )

            if selected is None:

                return ""

            return self._normalize_text(
                selected.get_text(
                    " ",
                    strip=True,
                )
            )

        # ==================================================
        #
        # Anchor
        #
        # ==================================================

        if container.name == "a":

            title = (
                container.get_text(
                    " ",
                    strip=True,
                )
            )

            if title:

                return self._normalize_text(
                    title
                )

        # ==================================================
        #
        # Nested Anchor
        #
        # ==================================================

        anchor = container.select_one(
            "a[href]"
        )

        if anchor is not None:

            title = (
                anchor.get_text(
                    " ",
                    strip=True,
                )
            )

            if title:

                return self._normalize_text(
                    title
                )

        # ==================================================
        #
        # Container Text
        #
        # ==================================================

        return self._normalize_text(
            container.get_text(
                " ",
                strip=True,
            )
        )

    # ==================================================
    #
    # Extract Published
    #
    # ==================================================

    def _extract_published(
        self,
        container,
    ):
        """
        取得 Website 原始 Published Date。

        Generic Provider 不負責：

            Date Parsing
            Date Normalization
            Timezone Conversion

        只保留 Website 原始文字。
        """

        if not self.published_selector:

            return None

        selected = container.select_one(
            self.published_selector
        )

        if selected is None:

            return None

        value = (
            selected.get_text(
                " ",
                strip=True,
            )
        )

        value = (
            self._normalize_text(
                value
            )
        )

        return value or None

    # ==================================================
    #
    # Keyword Matching
    #
    # ==================================================

    def matches_keyword(
        self,
        result,
        keyword,
    ):
        """
        判斷 List Item 是否符合 Keyword。

        第一版使用：

            case-insensitive substring matching

        Matching 欄位：

            - title

        例如：

            keyword = "IC"

            title =
                "Intel Announces New IC..."

            → True

        不負責：

            - NLP
            - Semantic Search
            - AI Matching
            - Synonym Expansion
            - Stemming
        """

        if not isinstance(
            result,
            SearchResult,
        ):

            return False

        keyword = (
            self._normalize_text(
                keyword
            ).casefold()
        )

        if not keyword:

            return False

        title = (
            self._normalize_text(
                getattr(
                    result,
                    "title",
                    "",
                )
            ).casefold()
        )

        if not title:

            return False

        return keyword in title

    # ==================================================
    #
    # Normalize Results
    #
    # ==================================================

    def _normalize_results(
        self,
        results,
        keyword,
        max_results,
    ):
        """
        Normalize / Validate / Filter Results。

        Pipeline：

            Parsed List
                ↓
            SearchResult Validation
                ↓
            URL Validation
                ↓
            Keyword Matching
                ↓
            Local URL Deduplication
                ↓
            Rank Rebuild
                ↓
            max_results
        """

        if results is None:

            return []

        if not isinstance(
            results,
            list,
        ):

            raise TypeError(
                "Website parser "
                "must return a list"
            )

        normalized = []

        seen_urls = set()

        for result in results:

            # ==================================================
            #
            # SearchResult Validation
            #
            # ==================================================

            if not isinstance(
                result,
                SearchResult,
            ):

                continue

            # ==================================================
            #
            # URL
            #
            # ==================================================

            url = self._normalize_text(
                getattr(
                    result,
                    "url",
                    "",
                )
            )

            if not url:

                continue

            # ==================================================
            #
            # Local URL Deduplication
            #
            # ==================================================

            if url in seen_urls:

                continue

            seen_urls.add(
                url
            )

            # ==================================================
            #
            # Keyword Matching
            #
            # ==================================================

            if not self.matches_keyword(
                result,
                keyword,
            ):

                continue

            # ==================================================
            #
            # Keyword
            #
            # ==================================================

            result.keyword = (
                keyword
            )

            # ==================================================
            #
            # Search Source
            #
            # ==================================================

            result.search_source = (
                self.provider_name
            )

            # ==================================================
            #
            # Source
            #
            # ==================================================

            if not result.source:

                result.source = (
                    self.source
                    or self.provider_name
                )

            # ==================================================
            #
            # Rank
            #
            # ==================================================

            result.rank = (
                len(normalized) + 1
            )

            normalized.append(
                result
            )

            # ==================================================
            #
            # Result Limit
            #
            # ==================================================

            if len(normalized) >= max_results:

                break

        return normalized

    # ==================================================
    #
    # Validate Results
    #
    # ==================================================

    def validate_results(
        self,
        results,
    ):
        """
        驗證 Provider Search Results。
        """

        if not isinstance(
            results,
            list,
        ):

            return False

        for result in results:

            if not isinstance(
                result,
                SearchResult,
            ):

                return False

            url = self._normalize_text(
                getattr(
                    result,
                    "url",
                    "",
                )
            )

            if not url:

                return False

            if not url.startswith(
                (
                    "http://",
                    "https://",
                )
            ):

                return False

        return True

    # ==================================================
    #
    # Normalize Text
    #
    # ==================================================

    @staticmethod
    def _normalize_text(
        value,
    ):
        """
        Normalize Text。
        """

        if value is None:

            return ""

        return str(
            value
        ).strip()

    # ==================================================
    #
    # Normalize Optional Text
    #
    # ==================================================

    @classmethod
    def _normalize_optional_text(
        cls,
        value,
    ):
        """
        Optional String。

        None / Empty：

            None
        """

        value = cls._normalize_text(
            value
        )

        return value or None

    # ==================================================
    #
    # Normalize Positive Integer
    #
    # ==================================================

    @staticmethod
    def _normalize_positive_int(
        value,
        field_name,
    ):
        """
        Normalize Positive Integer。
        """

        try:

            value = int(
                value
            )

        except (
            TypeError,
            ValueError,
        ):

            raise ValueError(
                f"{field_name} must be "
                "a positive integer"
            )

        if value <= 0:

            raise ValueError(
                f"{field_name} must be "
                "greater than zero"
            )

        return value


# ==================================================
#
# Public API
#
# ==================================================

__all__ = [
    "GenericWebsiteProvider",
]