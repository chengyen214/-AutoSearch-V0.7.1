"""
search/search_result.py

AutoSearch V4

P4.1 Search Adapter Foundation

Search Result Data Model

用途:
    統一不同 Search Source 的搜尋結果格式。

支援來源:

    - Google News
    - Website Search Source #1
    - Website Search Source #2
    - 未來其他 Search Adapter

Pipeline:

    Keyword
        ↓
    SearchAdapter
        ↓
    SearchResult
        ↓
    SearchManager
        ↓
    Crawler
        ↓
    Parser
        ↓
    Article


注意:

SearchResult 不負責:

    - HTML Download
    - HTML Parsing
    - Article 建立
    - Database
    - Archive
    - AI Analysis
    - Knowledge Processing
"""


# ==================================================
#
# P4.1 Search Result
#
# ==================================================


class SearchResult:
    """
    P4.1 統一搜尋結果模型。

    Search Adapter 必須將不同網站的搜尋結果
    轉換成 SearchResult。

    例如:

        Google News
            ↓
        SearchResult

        TSMC Search
            ↓
        SearchResult

        Other Website
            ↓
        SearchResult
    """

    def __init__(
        self,
        keyword="",
        title="",
        url="",
        published=None,
        source="",
        rank=None,
        source_type="",
    ):
        """
        Parameters
        ----------

        keyword:
            本次搜尋使用的 Keyword。

        title:
            搜尋結果標題。

        url:
            搜尋結果 URL。

        published:
            發布時間。

        source:
            文章來源名稱。

        rank:
            該結果在該 Search Source 中的排名。

        source_type:
            搜尋來源類型。

            例如:

                google_news
                website
                rss
                api
        """

        # ==========================================
        #
        # Search Keyword
        #
        # ==========================================

        self.keyword = keyword

        # ==========================================
        #
        # Result Basic Data
        #
        # ==========================================

        self.title = title

        self.url = url

        self.published = published

        self.source = source

        # ==========================================
        #
        # Search Ranking
        #
        # P4.1
        #
        # ==========================================

        self.rank = rank

        # ==========================================
        #
        # Search Source Type
        #
        # P4.1
        #
        # ==========================================

        self.source_type = source_type

    # ==================================================
    #
    # Dictionary
    #
    # ==================================================

    def to_dict(self):
        """
        將 SearchResult 轉換成 Dictionary。
        """

        return {

            "keyword": self.keyword,

            "title": self.title,

            "url": self.url,

            "published": self.published,

            "source": self.source,

            "rank": self.rank,

            "source_type": self.source_type,

        }

    # ==================================================
    #
    # Representation
    #
    # =================================================