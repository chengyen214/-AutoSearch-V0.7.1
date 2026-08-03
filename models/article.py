"""
Article 資料模型

用途：
統一整個專案的文章資料格式。

所有模組(Parser、Cleaner、Exporter、
Database、未來的 V3 AI)
都使用這個 Article。
"""


class Article:

    def __init__(
        self,
        keyword="",
        title="",
        url="",
        published=None,
        source="",
        content="",
        crawl_time=None,
        status="Success",
        document_id="",
        error=""
    ):

        self.keyword = keyword

        self.title = title

        self.url = url

        self.published = published

        self.source = source

        self.content = content

        self.crawl_time = crawl_time

        self.status = status

        self.document_id = document_id

        self.error = error

    def to_dict(self):
        """轉成 Dictionary"""

        return {
            "keyword": self.keyword,
            "title": self.title,
            "url": self.url,
            "published": self.published,
            "source": self.source,
            "content": self.content,
            "crawl_time": self.crawl_time,
            "status": self.status,
            "document_id": self.document_id,
            "error": self.error,
        }

    def __repr__(self):
        return (
            f"Article("
            f"title='{self.title}', "
            f"source='{self.source}', "
            f"status='{self.status}')"
        )