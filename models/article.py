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

        # P5 Document ID
        self.document_id = document_id

        # 錯誤紀錄
        self.error = error



    def to_dict(self):

        return {

            "keyword":
                self.keyword,

            "title":
                self.title,

            "url":
                self.url,

            "published":
                self.published,

            "source":
                self.source,

            "content":
                self.content,

            "crawl_time":
                self.crawl_time,

            "status":
                self.status,

            "document_id":
                self.document_id,

            "error":
                self.error

        }