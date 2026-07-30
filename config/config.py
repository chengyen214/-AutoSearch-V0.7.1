"""
search/search_engine.py

功能：
    根據使用者輸入的關鍵字，
    搜尋網路上的相關文章網址。

作者：
    Andy

版本：
    V2
"""

import urllib.parse
import feedparser


def search(keyword, max_results=10):
    """
    根據關鍵字搜尋文章

    Parameters
    ----------
    keyword : str
        搜尋關鍵字

    max_results : int
        最多取得幾筆搜尋結果

    Returns
    -------
    list
        搜尋結果清單

        [
            {
                "title": "...",
                "url": "...",
                "published": "..."
            }
        ]
    """

    # -------------------------
    # 將中文關鍵字轉成URL格式
    # 例如：
    # IC 設計
    # ↓
    # IC%20%E8%A8%AD%E8%A8%88
    # -------------------------

    query = urllib.parse.quote(keyword)

    # -------------------------
    # 建立 Google News RSS 搜尋網址
    # -------------------------

    rss_url = (
        "https://news.google.com/rss/search"
        f"?q={query}"
        "&hl=zh-TW"
        "&gl=TW"
        "&ceid=TW:zh-Hant"
    )

    # -------------------------
    # 讀取RSS資料
    # -------------------------

    feed = feedparser.parse(rss_url)

    results = []

    # -------------------------
    # 將RSS內容整理成Python List
    # -------------------------

    for item in feed.entries[:max_results]:

        article = {

            "title": item.title,

            "url": item.link,

            "published": item.get("published", "")

        }

        results.append(article)

    # -------------------------
    # 回傳搜尋結果
    # -------------------------

    return results