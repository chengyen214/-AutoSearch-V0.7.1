"""
models/search_result.py

AutoSearch V4

P4.1 Data Sources

Search Result Model

用途:

1. 統一不同 Search Source 的搜尋結果
2. 保存 Search Source 資訊
3. 保存搜尋排名
4. 保存原始搜尋 URL
5. 支援 Search Adapter
6. 後續轉換成 Article

Pipeline:

Search Source
    ↓
Search Adapter
    ↓
SearchResult
    ↓
Article
    ↓
Crawler
    ↓
Parser
    ↓
Archive


注意:

SearchResult 不負責:

- HTML Download
- Parser
- Article Archive
- AI Analysis
- Database Storage
"""


class SearchResult:
    """
    P4.1 Search Result Model。

    用來表示「搜尋引擎找到的結果」。

    不代表已經完成爬取的 Article。
    """

    def __init__(
        self,
        keyword="",
        title="",
        url="",
        source="",
        published=None,
        search_source="",
        rank=0,
    ):
        # ==========================================
        # Search Query
        # ==========================================

        self.keyword = keyword

        # ==========================================
        # Search Result Basic Data
        # ==========================================

        self.title = title

        self.url = url

        self.source = source

        self.published = published

        # ==========================================
        # P4.1 Search Source
        # ==========================================

        self.search_source = (
            search_source
        )

        # ==========================================
        # Search Ranking
        # ==========================================

        self.rank = rank

    # ==============================================
    # Convert To Dictionary
    # ==============================================

    def to_dict(self):
        """
        將 SearchResult 轉成 dictionary。
        """

        return {
            "keyword": self.keyword,
            "title": self.title,
            "url": self.url,
            "source": self.source,
            "published": self.published,
            "search_source": self.search_source,
            "rank": self.rank,
        }

    # ==============================================
    # Convert To Article
    # ==============================================

    def to_article(self):
        """
        將 SearchResult 轉換成 Article。

        注意:

        SearchResult 只包含搜尋資料。

        Article 後續才會加入:

        - content
        - crawl_time
        - status
        - document_id
        - AI
        - Archive
        """

        from models.article import Article

        return Article(
            keyword=self.keyword,
            title=self.title,
            url=self.url,
            published=self.published,
            source=self.source,
        )

    # ==============================================
    # Representation
    # ==============================================

    def __repr__(self):
        return (
            "SearchResult("
            f"title={self.title}, "
            f"url={self.url}, "
            f"source={self.search_source}, "
            f"rank={self.rank}"
            ")"
        )


__all__ = [
    "SearchResult",
]