"""
search/generic_search_provider.py

AutoSearch V5

V5.6.3

Generic Search Provider

用途：

    提供通用 Search Provider。

    從 target URL 的 HTML 中：

        1. 找出包含 keyword 的 <a>
        2. 取得對應 href
        3. 使用 crawler_url 解析 href
        4. 確認解析後 URL 是否屬於 crawler_url
        5. 建立 SearchResult

核心策略：

    keyword
        ↓
    KeywordProcessor
        ↓
    target URL
        ↓
    GET HTML
        ↓
    <a>
        ↓
    Link Text / Context
        ↓
    Keyword Matching
        ↓
    href
        ↓
    crawler_url Resolve
        ↓
    完整 URL
        ↓
    crawler_url Filter
        ↓
    SearchResult[]


重要：

    target_url 與 crawler_url
    可以是不同 domain。

例如：

    target_url:

        https://www.tsmc.com/

    crawler_url:

        https://pr.tsmc.com/chinese/news/

    HTML：

        <a href="/chinese/news/3333">
            Sony與台積公司同意成立合資公司
            支援下一世代影像感測器
        </a>

    href：

        /chinese/news/3333

    必須依照 crawler_url
    的 origin 解析：

        https://pr.tsmc.com
            +
        /chinese/news/3333

    得到：

        https://pr.tsmc.com/chinese/news/3333


不可以：

    https://www.tsmc.com/chinese/news/3333


重要：

    GenericSearchProvider
    只 GET target_url。

    不會 GET：

        https://pr.tsmc.com/chinese/news/3333


Input：

    keyword
    max_results
    url
    crawler_url
    target_language


Output：

    list[SearchResult]


不負責：

    - SearchAdapter
    - SearchAdapterManager
    - Provider Registry
    - Search Execution Control
    - URL Deduplication
    - Crawler
    - Parser
    - Archive
    - AI
"""


# ==================================================
#
# Imports
#
# ==================================================

from urllib.parse import (
    urljoin,
    urlparse,
)

import requests

from bs4 import BeautifulSoup

from models.search_result import (
    SearchResult,
)

from search.search_provider import (
    SearchProvider,
)

from utils.keyword_processor import (
    KeywordProcessor,
)


# ==================================================
#
# Generic Search Provider
#
# ==================================================

class GenericSearchProvider(
    SearchProvider
):
    """
    Generic Search Provider。

    搜尋流程：

        keyword
            ↓
        KeywordProcessor
            ↓
        GET target URL
            ↓
        HTML
            ↓
        <a>
            ↓
        Keyword Matching
            ↓
        href
            ↓
        crawler_url Resolve
            ↓
        crawler_url Filter
            ↓
        SearchResult[]
    """


    # ==================================================
    #
    # Provider Name
    #
    # ==================================================

    provider_name = (
        "generic_search"
    )


    # ==================================================
    #
    # Default Result Limit
    #
    # ==================================================

    max_results = 10


    # ==================================================
    #
    # Default Timeout
    #
    # ==================================================

    timeout = 7


    # ==================================================
    #
    # Search
    #
    # ==================================================

    def search(
        self,
        keyword,
        max_results=None,
        url=None,
        crawler_url=None,
        target_language="zh-TW",
    ):
        """
        Generic Search Provider。

        Parameters
        ----------

        keyword:

            Search keyword。

            Type:

                str


        max_results:

            最大搜尋結果數量。

            Type:

                int | None


        url:

            Target website URL。

            此 URL 會被實際 GET。

            Type:

                str | None


        crawler_url:

            Crawler article URL prefix。

            用來：

                1. 解析 relative href
                2. 判斷 article URL
                   是否屬於指定 crawler path

            Type:

                str | None


        target_language:

            KeywordProcessor
            使用的目標語言。

            Type:

                str

            Default:

                zh-TW


        Returns
        -------

        list[SearchResult]

            搜尋結果。

        """


        # ==================================================
        #
        # Normalize Keyword
        #
        # ==================================================

        keyword = (
            self._normalize_keyword(
                keyword
            )
        )

        if not keyword:

            return []


        # ==================================================
        #
        # Normalize Target URL
        #
        # ==================================================

        url = (
            self._normalize_url(
                url
            )
        )

        if not url:

            return []


        # ==================================================
        #
        # Normalize Crawler URL
        #
        # ==================================================

        crawler_url = (
            self._normalize_url_prefix(
                crawler_url
            )
        )

        if not crawler_url:

            return []


        # ==================================================
        #
        # Resolve Result Limit
        #
        # ==================================================

        limit = (
            self._resolve_limit(
                max_results
            )
        )

        if limit <= 0:

            return []


        # ==================================================
        #
        # Keyword Processor
        #
        # ==================================================

        processor = KeywordProcessor()


        keyword_data = (
            processor.process(
                keyword=keyword,
                target_language=target_language,
            )
        )


        if not isinstance(
            keyword_data,
            dict,
        ):

            return []


        # ==================================================
        #
        # Keyword Terms
        #
        # ==================================================

        original_terms = (
            keyword_data.get(
                "original_terms",
                [],
            )
        )

        translated_terms = (
            keyword_data.get(
                "translated_terms",
                [],
            )
        )


        if not isinstance(
            original_terms,
            list,
        ):

            original_terms = []


        if not isinstance(
            translated_terms,
            list,
        ):

            translated_terms = []


        terms = (
            self._build_search_terms(
                original_terms,
                translated_terms,
            )
        )


        # ==================================================
        #
        # Download Target URL
        #
        # ==================================================

        html = (
            self._fetch_html(
                url
            )
        )


        if not html:

            return []


        # ==================================================
        #
        # Parse HTML
        #
        # ==================================================

        soup = BeautifulSoup(
            html,
            "html.parser",
        )


        # ==================================================
        #
        # Extract Keyword Links
        #
        # ==================================================

        links = (
            self._extract_links(
                soup=soup,
                crawler_url=crawler_url,
                terms=terms,
            )
        )


        # ==================================================
        #
        # Build SearchResult
        #
        # ==================================================

        results = []


        for link in links:

            result = SearchResult(

                keyword=keyword,

                title=(
                    link.get(
                        "title",
                        "",
                    )
                ),

                url=(
                    link.get(
                        "url",
                        "",
                    )
                ),

                source=(
                    self._extract_source(
                        link.get(
                            "url",
                            "",
                        )
                    )
                ),

                published=None,

                search_source=(
                    self.provider_name
                ),

                rank=len(results) + 1,
            )


            results.append(
                result
            )


            if len(results) >= limit:

                break


        return results


    # ==================================================
    #
    # Normalize Keyword
    #
    # ==================================================

    @staticmethod
    def _normalize_keyword(
        keyword,
    ):
        """
        Normalize keyword。
        """

        if keyword is None:

            return ""


        return str(
            keyword
        ).strip()


    # ==================================================
    #
    # Normalize URL
    #
    # ==================================================

    @staticmethod
    def _normalize_url(
        url,
    ):
        """
        Normalize URL。
        """

        if url is None:

            return ""


        url = str(
            url
        ).strip()


        if not url:

            return ""


        return url


    # ==================================================
    #
    # Normalize Crawler URL Prefix
    #
    # ==================================================

    @staticmethod
    def _normalize_url_prefix(
        url,
    ):
        """
        Normalize crawler_url。

        例如：

            https://pr.tsmc.com/chinese/news

        →

            https://pr.tsmc.com/chinese/news/
        """

        if url is None:

            return ""


        url = str(
            url
        ).strip()


        if not url:

            return ""


        return (
            url.rstrip("/")
            + "/"
        )


    # ==================================================
    #
    # Resolve Limit
    #
    # ==================================================

    def _resolve_limit(
        self,
        max_results,
    ):
        """
        Resolve result limit。
        """

        if max_results is None:

            return self.max_results


        try:

            value = int(
                max_results
            )

        except (
            TypeError,
            ValueError,
        ):

            return self.max_results


        return min(
            value,
            self.max_results,
        )


    # ==================================================
    #
    # Fetch HTML
    #
    # ==================================================

    def _fetch_html(
        self,
        url,
    ):
        """
        只 GET target URL。

        不會 GET article URL。
        """

        try:

            response = requests.get(

                url,

                timeout=self.timeout,

                headers={
                    "User-Agent":
                        (
                            "Mozilla/5.0 "
                            "(Windows NT 10.0; Win64; x64) "
                            "AppleWebKit/537.36 "
                            "(KHTML, like Gecko) "
                            "Chrome/120 Safari/537.36"
                        )
                },
            )


            response.raise_for_status()


            return response.text


        except Exception as exc:

            print(
                "GenericSearchProvider:"
            )

            print(
                f"  fetch failed: {url}"
            )

            print(
                f"  error: {exc}"
            )

            return ""


    # ==================================================
    #
    # Extract Links
    #
    # ==================================================

    def _extract_links(
        self,
        soup,
        crawler_url,
        terms,
    ):
        """
        從 target HTML 中：

            找 keyword
                ↓
            找對應 <a>
                ↓
            取得 href
                ↓
            使用 crawler_url
            解析完整 URL
                ↓
            crawler_url filter

        不進入 article URL。
        """

        results = []

        existing_urls = set()


        for anchor in soup.find_all(
            "a",
            href=True,
        ):

            # ==================================================
            #
            # href
            #
            # ==================================================

            href = anchor.get(
                "href"
            )


            if not href:

                continue


            href = str(
                href
            ).strip()


            if not href:

                continue


            # ==================================================
            #
            # Ignore Non-Web Links
            #
            # ==================================================

            if href.startswith(
                (
                    "#",
                    "javascript:",
                    "mailto:",
                    "tel:",
                )
            ):

                continue


            # ==================================================
            #
            # Link Text
            #
            # ==================================================

            link_text = (
                anchor.get_text(
                    " ",
                    strip=True,
                )
            )


            # ==================================================
            #
            # HTML title
            #
            # ==================================================

            title = (
                anchor.get(
                    "title",
                    "",
                )
                or ""
            ).strip()


            # ==================================================
            #
            # aria-label
            #
            # ==================================================

            aria_label = (
                anchor.get(
                    "aria-label",
                    "",
                )
                or ""
            ).strip()


            # ==================================================
            #
            # Surrounding Text
            #
            # ==================================================

            surrounding_text = (
                self._extract_surrounding_text(
                    anchor
                )
            )


            # ==================================================
            #
            # Link Context
            #
            # ==================================================

            context_parts = [

                link_text,

                title,

                aria_label,

                surrounding_text,

            ]


            context = " ".join(
                part
                for part in context_parts
                if part
            )


            # ==================================================
            #
            # Keyword Matching
            #
            # ==================================================

            if not self._matches_keyword(
                context=context,
                terms=terms,
            ):

                continue


            # ==================================================
            #
            # Resolve Link URL
            #
            # ==================================================

            article_url = (
                self._resolve_link_url(
                    href=href,
                    crawler_url=crawler_url,
                )
            )


            if not article_url:

                continue


            # ==================================================
            #
            # Crawler URL Filter
            #
            # ==================================================

            if not self._matches_crawler_url(
                article_url=article_url,
                crawler_url=crawler_url,
            ):

                continue


            # ==================================================
            #
            # Duplicate URL
            #
            # ==================================================

            if article_url in existing_urls:

                continue


            existing_urls.add(
                article_url
            )


            # ==================================================
            #
            # Save Link
            #
            # ==================================================

            results.append(
                {
                    "url":
                        article_url,

                    "title":
                        (
                            title
                            or link_text
                        ),

                    "context":
                        context,
                }
            )


        return results


    # ==================================================
    #
    # Resolve Link URL
    #
    # ==================================================

    @staticmethod
    def _resolve_link_url(
        href,
        crawler_url,
    ):
        """
        將 href 解析成完整 URL。

        規則：

        1. Absolute URL

            https://pr.tsmc.com/chinese/news/3333

            →

            原樣保留。


        2. Root-relative URL

            /chinese/news/3333

            crawler_url：

            https://pr.tsmc.com/chinese/news/

            →

            https://pr.tsmc.com/chinese/news/3333


        3. Relative URL

            3333

            →

            https://pr.tsmc.com/chinese/news/3333


        重要：

            crawler_url domain
            優先於 target_url。
        """

        if href is None:

            return ""


        href = str(
            href
        ).strip()


        if not href:

            return ""


        # ==================================================
        #
        # Absolute URL
        #
        # ==================================================

        parsed_href = urlparse(
            href
        )


        if parsed_href.scheme in (
            "http",
            "https",
        ):

            return href


        # ==================================================
        #
        # Crawler URL
        #
        # ==================================================

        crawler_url = (
            str(
                crawler_url
            ).strip()
        )


        if not crawler_url:

            return ""


        parsed_crawler = urlparse(
            crawler_url
        )


        if not parsed_crawler.scheme:

            return ""


        if not parsed_crawler.netloc:

            return ""


        # ==================================================
        #
        # Crawler Origin
        #
        # ==================================================

        crawler_origin = (
            f"{parsed_crawler.scheme}://"
            f"{parsed_crawler.netloc}"
        )


        # ==================================================
        #
        # Root-relative href
        #
        # ==================================================

        if href.startswith("/"):

            return urljoin(
                crawler_origin,
                href,
            )


        # ==================================================
        #
        # Relative href
        #
        # ==================================================

        return urljoin(
            crawler_url,
            href,
        )


    # ==================================================
    #
    # Crawler URL Matching
    #
    # ==================================================

    @staticmethod
    def _matches_crawler_url(
        article_url,
        crawler_url,
    ):
        """
        判斷完整 article URL
        是否屬於 crawler_url。

        Example：

            crawler_url：

                https://pr.tsmc.com/chinese/news/

            article_url：

                https://pr.tsmc.com/chinese/news/3333

            Result：

                True
        """

        if not article_url:

            return False


        if not crawler_url:

            return False


        article_url = str(
            article_url
        ).strip()


        crawler_url = str(
            crawler_url
        ).strip()


        if not article_url:

            return False


        if not crawler_url:

            return False


        return article_url.startswith(
            crawler_url
        )


    # ==================================================
    #
    # Surrounding Text
    #
    # ==================================================

    @staticmethod
    def _extract_surrounding_text(
        anchor,
    ):
        """
        取得 <a> 附近文字。

        優先：

            parent text

        用途：

            取得：

                標題
                日期
                摘要
                類別
                其他列表資訊
        """

        parent = anchor.parent


        if parent is None:

            return ""


        try:

            text = parent.get_text(
                " ",
                strip=True,
            )

        except Exception:

            return ""


        if not text:

            return ""


        return text


    # ==================================================
    #
    # Build Search Terms
    #
    # ==================================================

    @staticmethod
    def _build_search_terms(
        original_terms,
        translated_terms,
    ):
        """
        建立 Keyword Matching Terms。

        original_terms
            +
        translated_terms

        移除：

            None
            empty
            duplicate
        """

        terms = []

        seen = set()


        for term in (
            list(original_terms)
            +
            list(translated_terms)
        ):

            if term is None:

                continue


            term = str(
                term
            ).strip()


            if not term:

                continue


            normalized = (
                term.lower()
            )


            if normalized in seen:

                continue


            seen.add(
                normalized
            )


            terms.append(
                term
            )


        return terms


    # ==================================================
    #
    # Keyword Matching
    #
    # ==================================================

    @staticmethod
    def _matches_keyword(
        context,
        terms,
    ):
        """
        判斷 <a> context
        是否包含 keyword。

        使用：

            case-insensitive
            substring matching
        """

        if not context:

            return False


        if not terms:

            return False


        context = str(
            context
        ).lower()


        for term in terms:

            term = str(
                term
            ).strip().lower()


            if not term:

                continue


            if term in context:

                return True


        return False


    # ==================================================
    #
    # Extract Source
    #
    # ==================================================

    @staticmethod
    def _extract_source(
        url,
    ):
        """
        從 URL 取得 hostname。
        """

        if not url:

            return ""


        try:

            parsed = urlparse(
                url
            )


            return (
                parsed.netloc
                or ""
            )


        except Exception:

            return ""


# ==================================================
#
# Public API
#
# ==================================================

__all__ = [
    "GenericSearchProvider",
]