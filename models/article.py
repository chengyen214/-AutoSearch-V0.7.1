"""
Article 資料模型

用途：

統一整個專案的文章資料格式。

所有模組(Parser、Cleaner、Exporter、
未來的 MySQL、LangChain)
都使用這個 Article。
"""


class Article:

    def __init__(
        self,
        keyword="",
        title="",
        url="",
        published="",
        source="",
        content="",
        crawl_time="",
        status="Success"
    ):

        # 搜尋關鍵字
        self.keyword = keyword

        # 文章標題
        self.title = title

        # 文章網址
        self.url = url

        # 發布日期
        self.published = published

        # 網站來源
        self.source = source

        # 文章內容
        self.content = content

        # 抓取時間
        self.crawl_time = crawl_time

        # 抓取狀態
        self.status = status

    def to_dict(self):
        """
        轉成 Dictionary

        Excel、MySQL
        都可以直接使用。
        """

        return {
            "keyword": self.keyword,
            "title": self.title,
            "url": self.url,
            "published": self.published,
            "source": self.source,
            "content": self.content,
            "crawl_time": self.crawl_time,
            "status": self.status
        }