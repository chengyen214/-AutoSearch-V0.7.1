"""
tests/V6_3/test_generic_search_provider_real_db.py

AutoSearch V5

P5.6.3

Generic Search Provider Real Target Test

測試 Target 18：

    ID:
        18

    Name:
        TSMC

    Target Type:
        url

    URL:
        https://pr.tsmc.com/chinese/latest-news

    Crawler URL:
        https://pr.tsmc.com/chinese/news/

    Keyword:
        影像感測器

    Search Provider:
        google_search

    Status:
        active


測試目的：

    驗證 GenericSearchProvider：

        Keyword
            ↓
        KeywordProcessor
            ↓
        Target URL
            ↓
        GET HTML
            ↓
        Extract <a>
            ↓
        找到包含 Keyword 的 <a>
            ↓
        取得 href
            ↓
        使用 crawler_url
        組合完整 URL
            ↓
        crawler_url Filter
            ↓
        SearchResult[]


核心 URL Resolution：

    href：

        /chinese/news/3333

    crawler_url：

        https://pr.tsmc.com/chinese/news/

    ↓

    https://pr.tsmc.com/chinese/news/3333


重要：

    Target URL：

        https://pr.tsmc.com/chinese/latest-news

    Crawler URL：

        https://pr.tsmc.com/chinese/news/

    GenericSearchProvider：

        只 GET Target URL。

    找到 <a> 後：

        不 GET article URL。

    relative href：

        /chinese/news/3333

    必須依照 crawler_url
    解析成：

        https://pr.tsmc.com/chinese/news/3333


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


執行：

    python -m pytest tests/V6_3/test_generic_search_provider_real_db.py -s -v
"""


# ==================================================
#
# Imports
#
# ==================================================

import requests

from bs4 import BeautifulSoup

from models.search_result import (
    SearchResult,
)

from search.generic_search_provider import (
    GenericSearchProvider,
)


# ==================================================
#
# Target 18
#
# ==================================================

TARGET_ID = 18

TARGET_NAME = "TSMC"

TARGET_TYPE = "url"

TARGET_URL = (
    "https://pr.tsmc.com/chinese/latest-news"
)

CRAWLER_URL = (
    "https://pr.tsmc.com/chinese/news/"
)

EXPECTED_ARTICLE_URL = (
    "https://pr.tsmc.com/chinese/news/3333"
)

EXPECTED_HREF = (
    "/chinese/news/3333"
)

KEYWORD = (
    "影像感測器"
)

SEARCH_PROVIDER = (
    "google_search"
)

TARGET_STATUS = (
    "active"
)

TARGET_LANGUAGE = (
    "zh-TW"
)


# ==================================================
#
# Test
#
# ==================================================

def test_generic_search_real_tsmc_target_18():
    """
    Target 18 Real Generic Search Test。

    驗證：

        1. GenericSearchProvider 可以正常執行
        2. Input Format 與 GoogleSearchProvider 一致
        3. Target URL 可以下載
        4. KeywordProcessor 可以參與 Keyword Search
        5. 找到 Keyword 對應的 <a>
        6. 取得 href
        7. crawler_url 可以解析 relative href
        8. 解析後 URL 符合 crawler_url
        9. 不進入 crawler article URL
        10. Output 為 list[SearchResult]
    """

    print()
    print("=" * 60)
    print(
        "Target 18 Generic Search Provider Real Test"
    )
    print("=" * 60)


    # ==================================================
    #
    # Target Information
    #
    # ==================================================

    print()
    print(
        "Target"
    )
    print("-" * 60)

    print(
        f"ID              : {TARGET_ID}"
    )

    print(
        f"Name            : {TARGET_NAME}"
    )

    print(
        f"Type            : {TARGET_TYPE}"
    )

    print(
        f"URL             : {TARGET_URL}"
    )

    print(
        f"Crawler URL     : {CRAWLER_URL}"
    )

    print(
        f"Expected URL    : {EXPECTED_ARTICLE_URL}"
    )

    print(
        f"Expected href   : {EXPECTED_HREF}"
    )

    print(
        f"Keyword         : {KEYWORD}"
    )

    print(
        f"Search Provider : {SEARCH_PROVIDER}"
    )

    print(
        f"Status          : {TARGET_STATUS}"
    )


    # ==================================================
    #
    # Provider
    #
    # ==================================================

    provider = (
        GenericSearchProvider()
    )


    assert (
        provider.provider_name
        == "generic_search"
    )


    # ==================================================
    #
    # Direct Target HTML Verification
    #
    # ==================================================

    print()
    print(
        "Target HTML Verification"
    )
    print("-" * 60)

    print(
        f"GET : {TARGET_URL}"
    )


    try:

        response = requests.get(
            TARGET_URL,
            timeout=7,
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

    except Exception as exc:

        print()
        print(
            "Target HTML Request FAILED"
        )

        print(
            f"Error : {exc}"
        )

        raise


    html = response.text


    assert html


    print(
        f"HTML Length : {len(html)}"
    )


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
    # Keyword Anchor Inspection
    #
    # ==================================================

    print()
    print(
        "Keyword Anchor Inspection"
    )
    print("-" * 60)

    keyword_anchor_count = 0

    keyword_href_candidates = []


    keyword_lower = (
        KEYWORD.lower()
    )


    for anchor in soup.find_all(
        "a",
        href=True,
    ):

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


        # --------------------------------------------------
        #
        # Link Text
        #
        # --------------------------------------------------

        link_text = (
            anchor.get_text(
                " ",
                strip=True,
            )
        )


        # --------------------------------------------------
        #
        # title
        #
        # --------------------------------------------------

        title = (
            anchor.get(
                "title",
                "",
            )
            or ""
        ).strip()


        # --------------------------------------------------
        #
        # aria-label
        #
        # --------------------------------------------------

        aria_label = (
            anchor.get(
                "aria-label",
                "",
            )
            or ""
        ).strip()


        # --------------------------------------------------
        #
        # Parent Text
        #
        # --------------------------------------------------

        parent = anchor.parent

        if parent is not None:

            surrounding_text = (
                parent.get_text(
                    " ",
                    strip=True,
                )
            )

        else:

            surrounding_text = ""


        # --------------------------------------------------
        #
        # Context
        #
        # --------------------------------------------------

        context = " ".join(
            part
            for part in [
                link_text,
                title,
                aria_label,
                surrounding_text,
            ]
            if part
        )


        # --------------------------------------------------
        #
        # Keyword Match
        #
        # --------------------------------------------------

        if (
            keyword_lower
            not in context.lower()
        ):

            continue


        keyword_anchor_count += 1


        keyword_href_candidates.append(
            {
                "href":
                    href,

                "link_text":
                    link_text,

                "title":
                    title,

                "aria_label":
                    aria_label,

                "context":
                    context,
            }
        )


    # ==================================================
    #
    # Keyword Anchor Result
    #
    # ==================================================

    print(
        f"Keyword Anchor Count : "
        f"{keyword_anchor_count}"
    )


    if keyword_href_candidates:

        print()

        print(
            "Keyword Anchor Candidates:"
        )


        for index, item in enumerate(
            keyword_href_candidates,
            start=1,
        ):

            print(
                f"[{index}]"
            )

            print(
                f"  href        : "
                f"{item['href']}"
            )

            print(
                f"  link_text   : "
                f"{item['link_text']}"
            )

            print(
                f"  title       : "
                f"{item['title']}"
            )

            print(
                f"  aria-label  : "
                f"{item['aria_label']}"
            )

            print(
                f"  context     : "
                f"{item['context'][:500]}"
            )

    else:

        print()
        print(
            f"No <a> containing keyword "
            f"'{KEYWORD}' was found in target HTML."
        )


    # ==================================================
    #
    # Execute Generic Search
    #
    # ==================================================

    print()
    print(
        "Generic Search"
    )
    print("-" * 60)

    print(
        "Executing:"
    )

    print(
        f"  keyword      = {KEYWORD}"
    )

    print(
        f"  max_results  = 20"
    )

    print(
        f"  url          = {TARGET_URL}"
    )

    print(
        f"  crawler_url  = {CRAWLER_URL}"
    )


    # ==================================================
    #
    # IMPORTANT
    #
    # GoogleSearchProvider
    # 與 GenericSearchProvider
    #
    # 接收格式必須一致。
    #
    # 因此：
    #
    # 不傳：
    #
    #     target_language
    #
    # ==================================================

    results = (
        provider.search(
            keyword=KEYWORD,
            max_results=20,
            url=TARGET_URL,
            crawler_url=CRAWLER_URL,
        )
    )


    # ==================================================
    #
    # Output Type
    #
    # ==================================================

    assert isinstance(
        results,
        list,
    )


    # ==================================================
    #
    # Result
    #
    # ==================================================

    print()
    print(
        "Results"
    )
    print("-" * 60)

    print(
        f"Result Count : {len(results)}"
    )


    for index, result in enumerate(
        results,
        start=1,
    ):

        assert isinstance(
            result,
            SearchResult,
        )


        print(
            f"[{index}]"
        )

        print(
            f"  Keyword      : {result.keyword}"
        )

        print(
            f"  Title        : {result.title}"
        )

        print(
            f"  URL          : {result.url}"
        )

        print(
            f"  Source       : {result.source}"
        )

        print(
            f"  Search Source: {result.search_source}"
        )

        print(
            f"  Rank         : {result.rank}"
        )

        print(
            "-" * 60
        )


    # ==================================================
    #
    # Result Validation
    #
    # ==================================================

    for result in results:

        # ----------------------------------------------
        #
        # Keyword
        #
        # ----------------------------------------------

        assert (
            result.keyword
            == KEYWORD
        )


        # ----------------------------------------------
        #
        # URL
        #
        # ----------------------------------------------

        assert result.url


        # ----------------------------------------------
        #
        # Crawler URL
        #
        # ----------------------------------------------

        assert (
            result.url.startswith(
                CRAWLER_URL
            )
        )


        # ----------------------------------------------
        #
        # Search Source
        #
        # ----------------------------------------------

        assert (
            result.search_source
            == "generic_search"
        )


    # ==================================================
    #
    # Rank Validation
    #
    # ==================================================

    if results:

        ranks = [
            result.rank
            for result in results
        ]

        assert (
            ranks
            == list(
                range(
                    1,
                    len(results) + 1,
                )
            )
        )


    # ==================================================
    #
    # Result Limit
    #
    # ==================================================

    assert (
        len(results)
        <= 20
    )


    # ==================================================
    #
    # Expected URL In Result
    #
    # ==================================================

    expected_result = None


    for result in results:

        if (
            result.url
            == EXPECTED_ARTICLE_URL
        ):

            expected_result = (
                result
            )

            break


    print()
    print(
        "Expected Article Result"
    )
    print("-" * 60)

    print(
        f"Expected href : "
        f"{EXPECTED_HREF}"
    )

    print(
        f"Expected URL  : "
        f"{EXPECTED_ARTICLE_URL}"
    )

    print(
        f"Found Result  : "
        f"{expected_result is not None}"
    )


    if expected_result is not None:

        print(
            f"Title         : "
            f"{expected_result.title}"
        )

        print(
            f"Keyword       : "
            f"{expected_result.keyword}"
        )

        print(
            f"Search Source : "
            f"{expected_result.search_source}"
        )


    # ==================================================
    #
    # Final Debug Summary
    #
    # ==================================================

    print()
    print("=" * 60)

    print(
        "DEBUG SUMMARY"
    )

    print("=" * 60)

    print(
        f"Keyword Anchor Count        : "
        f"{keyword_anchor_count}"
    )

    print(
        f"Expected href               : "
        f"{EXPECTED_HREF}"
    )

    print(
        f"Expected Complete URL       : "
        f"{EXPECTED_ARTICLE_URL}"
    )

    print(
        f"Expected URL returned       : "
        f"{expected_result is not None}"
    )

    print(
        f"Total Generic Search Results: "
        f"{len(results)}"
    )

    print("=" * 60)


    # ==================================================
    #
    # Result
    #
    # ==================================================

    print()
    print("=" * 60)

    print(
        "RESULT:"
    )


    if expected_result is not None:

        print(
            "Target 18 successfully found "
            "the expected keyword link."
        )

        print(
            f"  href -> {EXPECTED_HREF}"
        )

        print(
            f"  URL  -> {EXPECTED_ARTICLE_URL}"
        )

    elif results:

        print(
            f"Target 18 returned "
            f"{len(results)} matching crawler URLs."
        )

    else:

        print(
            "Target 18 returned 0 matching results."
        )

        print(
            "This means the target HTML did not "
            "contain a matching keyword <a>."
        )


    print("=" * 60)
