"""
search_engine.py

RSS搜尋模組

功能:
1. Google News RSS搜尋
2. Google News URL解碼
3. URL去重
4. 數量限制
5. 回傳 Article 資料模型
"""


import feedparser

from urllib.parse import quote

from googlenewsdecoder import gnewsdecoder

from models.article import Article





def resolve_google_news_url(url):
    """
    Google News URL解碼

    將:

    https://news.google.com/rss/articles/xxxxx

    轉成:

    真正新聞網址
    """

    try:

        result = gnewsdecoder(
            url
        )


        if result.get("status"):

            return result["decoded_url"]


        return url


    except Exception as e:

        print(
            "Google News解碼失敗:",
            e
        )

        return url





def search(keyword, max_results=10):

    """
    搜尋新聞

    input:

        keyword:
            搜尋關鍵字


        max_results:
            最大文章數


    output:

        list[Article]

    """



    print()

    print("=" * 50)

    print(
        f"開始搜尋：{keyword}"
    )

    print("=" * 50)





    # URL encode

    keyword_encode = quote(

        keyword

    )





    rss_url = (

        "https://news.google.com/rss/search?"

        f"q={keyword_encode}"

        "&hl=zh-TW"

        "&gl=TW"

        "&ceid=TW:zh-Hant"

    )





    feed = feedparser.parse(

        rss_url

    )





    results = []



    # 本次搜尋去重

    url_set = set()





    for item in feed.entries:





        if len(results) >= max_results:

            break





        title = item.get(

            "title",

            ""

        )





        url = item.get(

            "link",

            ""

        )





        published = item.get(

            "published",

            ""

        )





        source = ""





        if hasattr(

            item,

            "source"

        ):

            source = item.source.get(

                "title",

                ""

            )







        # =========================
        # Google News URL解碼
        # =========================


        url = resolve_google_news_url(

            url

        )





        print(

            "URL:",

            url

        )







        # URL去重


        if url in url_set:

            continue





        url_set.add(

            url

        )







        # =========================
        # P5
        # RSS資料轉 Article
        # =========================


        article = Article(

            keyword=keyword,

            title=title,

            url=url,

            published=published,

            source=source

        )







        results.append(

            article

        )







    print()

    print(
        f"搜尋完成：{keyword}"
    )



    print(
        f"取得文章：{len(results)}"
    )





    return results