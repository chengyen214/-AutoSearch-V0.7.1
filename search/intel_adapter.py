"""
search/intel_adapter.py

AutoSearch V4

P4.4 Website Search Source #2

Intel Newsroom

功能:

1. Intel Newsroom 最新新聞搜尋來源
2. 取得 Intel 官方新聞列表
3. Keyword Matching
4. URL 去重
5. Result Limit
6. 統一回傳 SearchResult

Pipeline:

Keyword
    ↓
IntelNewsAdapter
    ↓
Intel Newsroom
    ↓
Keyword Matching
    ↓
SearchResult
    ↓
SearchAdapterManager


注意:

IntelNewsAdapter 不負責:

- HTML Download
- Parser
- Article Archive
- AI Analysis
- AI Worker
- Database Storage
"""


from urllib.parse import urljoin


import requests


from bs4 import BeautifulSoup


from config.settings import (
    INTEL_RESULTS,
    HEADERS,
    TIMEOUT,
)


from models.search_result import (
    SearchResult,
)


# ==================================================
#
# Search Adapter Base
#
# ==================================================
#
# 注意:
#
# 不從 search.search_adapter import SearchAdapter
#
# 避免:
#
# search_adapter.py
#       ↓
# intel_adapter.py
#       ↓
# search_adapter.py
#
# 循環 import。
#
# ==================================================

from search.search_adapter_base import (
    SearchAdapter,
)


# ==================================================
#
# Intel Newsroom
#
# ==================================================


INTEL_NEWS_URL = (
    "https://newsroom.intel.com/news"
)


# ==================================================
#
# Intel News Adapter
#
# ==================================================


class IntelNewsAdapter(SearchAdapter):
    """
    Intel Newsroom Adapter。

    P4.4

    搜尋來源:

        Intel Newsroom
        News

    Source:

        intel

    Result Limit:

        INTEL_RESULTS
    """

    # ==================================================
    #
    # Result Limit
    #
    # ==================================================

    max_results = INTEL_RESULTS

    # ==================================================
    #
    # Search Source
    #
    # ==================================================

    search_source = "intel"

    # ==================================================
    #
    # Website
    #
    # ==================================================

    base_url = INTEL_NEWS_URL

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
        搜尋 Intel Newsroom。

        Pipeline:

            Intel Newsroom
                    ↓
              HTML Download
                    ↓
              HTML Parsing
                    ↓
               News Links
                    ↓
             Keyword Matching
                    ↓
              SearchResult

        Returns
        -------

        list[SearchResult]
        """

        # ==================================================
        #
        # Validate Keyword
        #
        # ==================================================

        if keyword is None:

            keyword = ""

        if not isinstance(
            keyword,
            str,
        ):

            keyword = str(
                keyword
            )

        keyword = keyword.strip()

        if not keyword:

            return []

        # ==================================================
        #
        # Validate Result Limit
        #
        # ==================================================

        if max_results is None:

            max_results = (
                self.max_results
            )

        try:

            max_results = int(
                max_results
            )

        except (
            TypeError,
            ValueError,
        ):

            max_results = (
                self.max_results
            )

        if max_results <= 0:

            return []

        # ==================================================
        #
        # Keyword Parts
        #
        # ==================================================

        keyword_parts = [

            part.strip().lower()

            for part in keyword.split()

            if part.strip()

        ]

        if not keyword_parts:

            return []

        # ==================================================
        #
        # Download Intel Newsroom
        #
        # ==================================================

        try:

            response = requests.get(

                self.base_url,

                headers=HEADERS,

                timeout=TIMEOUT,

            )

            response.raise_for_status()

        except Exception as e:

            print(
                "Intel Newsroom request failed:",
                e,
            )

            return []

        # ==================================================
        #
        # Parse HTML
        #
        # ==================================================

        try:

            soup = BeautifulSoup(

                response.text,

                "html.parser",

            )

        except Exception as e:

            print(
                "Intel Newsroom parse failed:",
                e,
            )

            return []

        # ==================================================
        #
        # Results
        #
        # ==================================================

        results = []

        # ==================================================
        #
        # URL Deduplication
        #
        # ==================================================

        url_set = set()

        # ==================================================
        #
        # Find News Links
        #
        # ==================================================

        for link in soup.find_all("a"):

            # ----------------------------------------------
            # Result Limit
            # ----------------------------------------------

            if len(results) >= max_results:

                break

            # ----------------------------------------------
            # Title
            # ----------------------------------------------

            title = link.get_text(
                " ",
                strip=True,
            )

            # ----------------------------------------------
            # HREF
            # ----------------------------------------------

            href = link.get(
                "href",
                "",
            )

            if not title or not href:

                continue

            # ==================================================
            #
            # Build Absolute URL
            #
            # ==================================================

            url = urljoin(
                self.base_url,
                href,
            )

            # ==================================================
            #
            # Validate Intel URL
            #
            # ==================================================

            if not url.startswith(
                "https://newsroom.intel.com/"
            ):

                continue

            # ==================================================
            #
            # Ignore News Listing
            #
            # ==================================================

            if url.rstrip("/") == (
                self.base_url.rstrip("/")
            ):

                continue

            # ==================================================
            #
            # Ignore Non-Article Pages
            #
            # ==================================================

            ignored_paths = (

                "/category/",

                "/author/",

                "/tag/",

                "/page/",

                "/search",

                "/subscribe",

                "/press-hub",

                "/press-kits",

            )

            if any(
                path in url.lower()
                for path in ignored_paths
            ):

                continue

            # ==================================================
            #
            # URL Deduplication
            #
            # ==================================================

            if url in url_set:

                continue

            # ==================================================
            #
            # Keyword Matching
            #
            # ==================================================
            #
            # Intel Newsroom 的標題通常包含：
            #
            # Intel
            # Foundry
            # Semiconductor
            # AI
            # Manufacturing
            # Processor
            #
            # 目前採用與 TSMC 相同的
            # OR keyword matching。
            #
            # ==================================================

            text = title.lower()

            matched = any(

                part in text

                for part in keyword_parts

            )

            if not matched:

                continue

            # ==================================================
            #
            # Save URL
            #
            # ==================================================

            url_set.add(
                url
            )

            # ==================================================
            #
            # Create SearchResult
            #
            # ==================================================

            result = SearchResult(

                keyword=keyword,

                title=title,

                url=url,

                source="Intel",

                published=None,

                search_source=(
                    self.search_source
                ),

                rank=len(results) + 1,

            )

            results.append(
                result
            )

        # ==================================================
        #
        # Rebuild Source Rank
        #
        # ==================================================

        for rank, result in enumerate(

            results,

            start=1,

        ):

            result.rank = rank

        # ==================================================
        #
        # Log
        #
        # ==================================================

        print()

        print(
            f"Intel Newsroom 搜尋完成：{keyword}"
        )

        print(
            f"Intel Newsroom 取得文章：{len(results)}"
        )

        return results


# ==================================================
#
# Export
#
# ==================================================


__all__ = [

    "IntelNewsAdapter",

    "INTEL_NEWS_URL",

]