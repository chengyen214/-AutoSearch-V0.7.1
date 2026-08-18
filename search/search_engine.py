"""
search/search_engine.py

AutoSearch V4

P4.2 Google News Search

功能:

1. Google News RSS 搜尋
2. Google News URL 解碼
3. URL 去重
4. Google News 搜尋數量限制
5. RSS 資料解析
6. 統一回傳 SearchResult

P4.2 架構:

    Google News RSS
            ↓
    search_engine.search()
            ↓
        SearchResult
            ↓
    GoogleNewsAdapter
            ↓
    SearchAdapterManager
            ↓
    SearchResult → Article


注意:

search_engine.py 不負責:

- Article 建立
- HTML Download
- Parser
- Archive
- AI Analysis
- AI Worker
- Database Storage

Article 建立由:

    SearchResult.to_article()

負責。

Search Adapter 負責:

    SearchResult → Multi-Source Search

"""


from urllib.parse import quote


import feedparser


from googlenewsdecoder import (
    gnewsdecoder,
)


from models.search_result import (
    SearchResult,
)


# ==================================================
#
# Google News URL Decode
#
# ==================================================


def resolve_google_news_url(
    url,
):
    """
    Google News URL 解碼。

    將:

        https://news.google.com/rss/articles/xxxxx

    嘗試轉換成:

        真正新聞網址

    如果解碼失敗:

        回傳原始 URL

    Parameters
    ----------
    url:
        Google News URL

    Returns
    -------
    str
        解碼後 URL
    """

    # ----------------------------------------------
    # Empty URL
    # ----------------------------------------------

    if not url:

        return url

    try:

        result = gnewsdecoder(
            url
        )

        # ------------------------------------------
        # Decoder Success
        # ------------------------------------------

        if (
            isinstance(
                result,
                dict,
            )
            and result.get("status")
        ):

            decoded_url = result.get(
                "decoded_url"
            )

            if decoded_url:

                return decoded_url

        # ------------------------------------------
        # Decoder Failed
        # ------------------------------------------

        return url

    except Exception as e:

        print(
            "Google News URL 解碼失敗:",
            e,
        )

        return url


# ==================================================
#
# Google News RSS Search
#
# ==================================================


def search(
    keyword,
    max_results=10,
):
    """
    Google News RSS 搜尋。

    Parameters
    ----------
    keyword:
        搜尋關鍵字

    max_results:
        最大搜尋結果數量

    Returns
    -------
    list[SearchResult]

    P4.2:

        Google News RSS
                ↓
            SearchResult
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

    try:

        max_results = int(
            max_results
        )

    except (
        TypeError,
        ValueError,
    ):

        max_results = 10

    if max_results <= 0:

        return []

    # ==================================================
    #
    # Search Log
    #
    # ==================================================

    print()

    print(
        "=" * 50
    )

    print(
        f"開始搜尋：{keyword}"
    )

    print(
        "=" * 50
    )

    # ==================================================
    #
    # URL Encode
    #
    # ==================================================

    keyword_encode = quote(
        keyword
    )

    # ==================================================
    #
    # Google News RSS URL
    #
    # ==================================================

    rss_url = (

        "https://news.google.com/rss/search?"

        f"q={keyword_encode}"

        "&hl=zh-TW"

        "&gl=TW"

        "&ceid=TW:zh-Hant"

    )

    # ==================================================
    #
    # RSS Request
    #
    # ==================================================

    try:

        feed = feedparser.parse(
            rss_url
        )

    except Exception as e:

        print(
            "Google News RSS 搜尋失敗:",
            e,
        )

        return []

    # ==================================================
    #
    # RSS Parse Error
    #
    # ==================================================

    if getattr(
        feed,
        "bozo",
        False,
    ):

        exception = getattr(
            feed,
            "bozo_exception",
            None,
        )

        if exception:

            print(
                "Google News RSS 解析警告:",
                exception,
            )

    # ==================================================
    #
    # Result
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
    # RSS Entries
    #
    # ==================================================

    for item in feed.entries:

        # ------------------------------------------
        # Result Limit
        # ------------------------------------------

        if len(results) >= max_results:

            break

        # ==================================================
        #
        # Title
        #
        # ==================================================

        title = item.get(
            "title",
            "",
        )

        # ==================================================
        #
        # URL
        #
        # ==================================================

        url = item.get(
            "link",
            "",
        )

        if not url:

            continue

        # ==================================================
        #
        # Published
        #
        # ==================================================

        published = item.get(
            "published",
            None,
        )

        # ==================================================
        #
        # Source
        #
        # ==================================================

        source = ""

        item_source = getattr(
            item,
            "source",
            None,
        )

        if item_source:

            try:

                source = item_source.get(
                    "title",
                    "",
                )

            except (
                AttributeError,
                TypeError,
            ):

                source = ""

        # ==================================================
        #
        # Google News URL Decode
        #
        # ==================================================

        url = resolve_google_news_url(
            url
        )

        print(
            "URL:",
            url,
        )

        # ==================================================
        #
        # URL Deduplication
        #
        # ==================================================

        if url in url_set:

            continue

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

            source=source,

            published=published,

            search_source="google_news",

            rank=len(results) + 1,

        )

        results.append(
            result
        )

    # ==================================================
    #
    # Search Complete
    #
    # ==================================================

    print()

    print(
        f"搜尋完成：{keyword}"
    )

    print(
        f"取得文章：{len(results)}"
    )

    return results


# ==================================================
#
# Export
#
# ==================================================


__all__ = [

    "resolve_google_news_url",

    "search",

]