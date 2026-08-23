"""
models/search_result.py

AutoSearch V5

P5.6.4 / Search Result Model

用途：

1. 統一不同 Search Provider 的搜尋結果
2. 保存 Search Source 資訊
3. 保存搜尋排名
4. 保存搜尋關鍵字
5. 保存原始搜尋結果 URL
6. 支援 ProviderSearchAdapter
7. 支援 SearchExecutionBridge
8. 後續轉換成 Article

Pipeline：

Search Provider
    ↓
ProviderSearchAdapter
    ↓
SearchExecutionBridge
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


注意：

SearchResult 不負責：

- HTTP Request
- HTML Download
- Parser
- Article Crawl
- Archive
- AI Analysis
- Database Storage
"""


class SearchResult:
    """
    V5 Search Result Model。

    表示：

        「Search Provider 找到的一筆搜尋結果」

    不代表：

        「已完成爬取的 Article」
    """

    # ==================================================
    #
    # Constructor
    #
    # ==================================================

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
        """
        建立 SearchResult。

        Parameters
        ----------
        keyword :
            搜尋關鍵字。

        title :
            搜尋結果標題。

        url :
            搜尋結果 URL。

        source :
            原始內容來源。

        published :
            發布時間。

        search_source :
            搜尋來源，例如：

                google_search
                google_news

        rank :
            搜尋結果排名。
        """

        # ==================================================
        # Search Query
        # ==================================================

        self.keyword = (
            self._normalize_text(
                keyword
            )
        )

        # ==================================================
        # Result Basic Data
        # ==================================================

        self.title = (
            self._normalize_text(
                title
            )
        )

        self.url = (
            self._normalize_text(
                url
            )
        )

        self.source = (
            self._normalize_text(
                source
            )
        )

        self.published = (
            published
        )

        # ==================================================
        # Search Source
        # ==================================================

        self.search_source = (
            self._normalize_text(
                search_source
            )
        )

        # ==================================================
        # Search Ranking
        # ==================================================

        self.rank = (
            self._normalize_rank(
                rank
            )
        )

    # ==================================================
    #
    # Validation
    #
    # ==================================================

    def is_valid(self):
        """
        判斷 SearchResult 是否具有最基本有效資料。

        必須：

            url 存在

        keyword / title / source
        可以為空，因為不同 Provider
        提供的資料完整度可能不同。
        """

        return bool(
            self.url
        )

    # ==================================================
    #
    # To Dictionary
    #
    # ==================================================

    def to_dict(self):
        """
        將 SearchResult 轉成 dictionary。
        """

        return {
            "keyword":
                self.keyword,

            "title":
                self.title,

            "url":
                self.url,

            "source":
                self.source,

            "published":
                self.published,

            "search_source":
                self.search_source,

            "rank":
                self.rank,
        }

    # ==================================================
    #
    # To Article
    #
    # ==================================================

    def to_article(self):
        """
        將 SearchResult 轉換成 Article。

        SearchResult：

            Search Metadata

        Article：

            Crawl / Article Data

        SearchResult 不直接負責：

            content
            crawl_time
            status
            document_id
            AI
            Archive
        """

        from models.article import Article

        return Article(
            keyword=self.keyword,
            title=self.title,
            url=self.url,
            published=self.published,
            source=self.source,
        )

    # ==================================================
    #
    # Representation
    #
    # ==================================================

    def __repr__(self):
        return (
            "SearchResult("
            f"title={self.title!r}, "
            f"url={self.url!r}, "
            f"source={self.search_source!r}, "
            f"rank={self.rank}"
            ")"
        )

    # ==================================================
    #
    # Normalize Text
    #
    # ==================================================

    @staticmethod
    def _normalize_text(
        value,
    ):
        """
        Normalize 基本文字欄位。

        None → ""

        其他型別 → str(value).strip()
        """

        if value is None:

            return ""

        return str(
            value
        ).strip()

    # ==================================================
    #
    # Normalize Rank
    #
    # ==================================================

    @staticmethod
    def _normalize_rank(
        rank,
    ):
        """
        Normalize Search Rank。

        無效值：

            → 0

        Rank 不在 SearchResult
        建立時強制要求 > 0。

        因為：

            SearchExecutionBridge
            ProviderSearchAdapter
            Provider

        都可能在後續重新排序。
        """

        try:

            value = int(
                rank
            )

        except (
            TypeError,
            ValueError,
        ):

            return 0

        if value < 0:

            return 0

        return value


__all__ = [
    "SearchResult",
]