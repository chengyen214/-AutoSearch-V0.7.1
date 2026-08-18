"""
search/tsmc_adapter.py

AutoSearch V4

P4.3 Website Search Source #1

TSMC Press Center - Latest News

功能:

1. TSMC Latest News 網頁搜尋來源
2. 取得 TSMC 官方新聞列表
3. Keyword Matching
4. URL 去重
5. Result Limit
6. 統一回傳 SearchResult

Pipeline:

Keyword
    ↓
TSMCNewsAdapter
    ↓
TSMC Latest News
    ↓
Keyword Matching
    ↓
SearchResult
    ↓
SearchAdapterManager


注意:

TSMCNewsAdapter 不負責:

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
    TSMC_RESULTS,
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
# tsmc_adapter.py
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
# TSMC Latest News
#
# ==================================================


TSMC_LATEST_NEWS_URL = (
    "https://pr.tsmc.com/english/latest-news"
)


# ==================================================
#
# TSMC News Adapter
#
# ==================================================


class TSMCNewsAdapter(SearchAdapter):
    """
    TSMC Press Center Latest News Adapter。

    P4.3

    搜尋來源:

        TSMC Press Center
        Latest News

    Source:

        tsmc

    Result Limit:

        TSMC_RESULTS
    """

    # ==================================================
    #
    # Result Limit
    #
    # ==================================================

    max_results = TSMC_RESULTS

    # ==================================================
    #
    # Search Source
    #
    # ==================================================

    search_source = "tsmc"

    # ==================================================
    #
    # Website
    #
    # ==================================================

    base_url = TSMC_LATEST_NEWS_URL

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
        搜尋 TSMC Latest News。

        Pipeline:

            TSMC Latest News
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
        # Download TSMC Latest News
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
                "TSMC Latest News request failed:",
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
                "TSMC Latest News parse failed:",
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
            # Validate TSMC URL
            #
            # ==================================================

            if not url.startswith(
                "https://pr.tsmc.com/"
            ):

                continue

            # ==================================================
            #
            # Ignore Latest News Listing
            #
            # ==================================================

            if url.rstrip("/") == (
                self.base_url.rstrip("/")
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

                source="TSMC",

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
            f"TSMC 搜尋完成：{keyword}"
        )

        print(
            f"TSMC 取得文章：{len(results)}"
        )

        return results


# ==================================================
#
# Export
#
# ==================================================


__all__ = [

    "TSMCNewsAdapter",

    "TSMC_LATEST_NEWS_URL",

]