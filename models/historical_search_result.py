"""
models/historical_search_result.py

AutoSearch V4

P2.3.7 Historical Search

用途:

    儲存 Historical Search 的單筆搜尋結果。

功能:

    1. 儲存 Article ID
    2. 儲存 Version ID
    3. 儲存 Version Number
    4. 儲存搜尋關鍵字
    5. 儲存匹配內容
    6. 儲存匹配位置
    7. 儲存搜尋時間
    8. 提供結果摘要
    9. 提供 Dictionary 轉換

設計:

    Historical Search
            ↓
    HistoricalSearchResult
            ↓
    Archive Version
"""

from datetime import datetime


class HistoricalSearchResult:

    """
    Historical Search Result Model
    """

    # ==================================
    # Init
    # ==================================

    def __init__(
        self,
        article_id=None,
        version_id=None,
        version_number=None,
        keyword="",
        matched_content="",
        match_position=None,
        created_time=None
    ):

        self.article_id = article_id

        self.version_id = version_id

        self.version_number = version_number

        self.keyword = keyword

        self.matched_content = (
            matched_content
            if matched_content is not None
            else ""
        )

        self.match_position = match_position

        self.created_time = (
            created_time
            if created_time is not None
            else datetime.now()
        )

    # ==================================
    # Has Match
    # ==================================

    def has_match(
        self
    ):
        """
        判斷是否有搜尋匹配內容。
        """

        return bool(
            self.matched_content
        )

    # ==================================
    # Content Length
    # ==================================

    def content_length(
        self
    ):
        """
        取得匹配內容長度。
        """

        return len(
            self.matched_content
        )

    # ==================================
    # Version Info
    # ==================================

    def version_info(
        self
    ):
        """
        取得 Version 資訊。
        """

        return {
            "version_id": self.version_id,
            "version_number": self.version_number
        }

    # ==================================
    # Summary
    # ==================================

    def summary(
        self
    ):
        """
        產生搜尋結果摘要。
        """

        return {
            "article_id": self.article_id,
            "version_id": self.version_id,
            "version_number": self.version_number,
            "keyword": self.keyword,
            "matched_content": self.matched_content,
            "match_position": self.match_position
        }

    # ==================================
    # To Dict
    # ==================================

    def to_dict(
        self
    ):
        """
        Model → Dictionary
        """

        return {
            "article_id": self.article_id,
            "version_id": self.version_id,
            "version_number": self.version_number,
            "keyword": self.keyword,
            "matched_content": self.matched_content,
            "match_position": self.match_position,
            "created_time": self.created_time
        }

    # ==================================
    # Repr
    # ==================================

    def __repr__(
        self
    ):

        return (
            "HistoricalSearchResult("
            f"article_id={self.article_id!r}, "
            f"version_id={self.version_id!r}, "
            f"version_number={self.version_number!r}, "
            f"keyword={self.keyword!r}"
            ")"
        )