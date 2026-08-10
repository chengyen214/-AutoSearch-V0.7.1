"""
archive/historical_search.py

AutoSearch V4

P2.3.7 Historical Search

用途:

    搜尋 Archive 歷史版本中的內容。

功能:

    1. 搜尋指定 Article 的所有歷史版本
    2. 搜尋指定 Article 的指定 Version
    3. 搜尋所有歷史版本
    4. 判斷指定版本是否包含關鍵字
    5. 計算搜尋結果數量
    6. 回傳 HistoricalSearchResult
    7. 支援大小寫不敏感搜尋

設計:

    Archive Version
            ↓
    HistoricalSearch
            ↓
    HistoricalSearchResult

注意:

    本模組不直接操作 Database。
"""

from models.historical_search_result import (
    HistoricalSearchResult
)

from database.archive_version_repository import (
    ArchiveVersionRepository
)


class HistoricalSearch:

    """
    Historical Search Engine
    """

    def __init__(
        self,
        version_repository=None
    ):

        self.version_repository = (
            version_repository
            if version_repository is not None
            else ArchiveVersionRepository()
        )

    # ==================================
    # Search Article History
    # ==================================

    def search(
        self,
        article_id,
        keyword
    ):
        """
        搜尋指定 Article 的所有歷史版本。

        Parameters
        ----------
        article_id : int
            Article ID

        keyword : str
            搜尋關鍵字

        Returns
        -------
        list
            HistoricalSearchResult
        """

        if not keyword:

            return []

        versions = (
            self.version_repository
            .get_by_article_id(
                article_id
            )
        )

        results = []

        for version in versions:

            result = self._search_version(
                version,
                keyword
            )

            if result is not None:

                results.append(result)

        return results

    # ==================================
    # Search Specific Version
    # ==================================

    def search_version(
        self,
        article_id,
        version_number,
        keyword
    ):
        """
        搜尋指定 Article 的指定 Version。
        """

        if not keyword:

            return None

        versions = (
            self.version_repository
            .get_by_article_id(
                article_id
            )
        )

        for version in versions:

            if (
                version.version_number
                == version_number
            ):

                return self._search_version(
                    version,
                    keyword
                )

        return None

    # ==================================
    # Search All
    # ==================================

    def search_all(
        self,
        keyword
    ):
        """
        搜尋所有 Article 的歷史版本。

        注意:

            此方法需要 Repository
            提供 get_all()。

        若目前 Repository 尚未提供
        get_all()，則回傳空結果。
        """

        if not keyword:

            return []

        if not hasattr(
            self.version_repository,
            "get_all"
        ):

            return []

        versions = (
            self.version_repository
            .get_all()
        )

        results = []

        for version in versions:

            result = self._search_version(
                version,
                keyword
            )

            if result is not None:

                results.append(result)

        return results

    # ==================================
    # Has Match
    # ==================================

    def has_match(
        self,
        article_id,
        keyword
    ):
        """
        判斷 Article 的歷史版本
        是否曾經出現指定關鍵字。
        """

        results = self.search(
            article_id,
            keyword
        )

        return len(results) > 0

    # ==================================
    # Count
    # ==================================

    def count(
        self,
        article_id,
        keyword
    ):
        """
        計算指定 Article
        有多少歷史版本符合搜尋。
        """

        results = self.search(
            article_id,
            keyword
        )

        return len(results)

    # ==================================
    # Get Results
    # ==================================

    def get_results(
        self,
        article_id,
        keyword
    ):
        """
        取得搜尋結果。

        與 search() 保持一致，
        提供語意較清楚的 API。
        """

        return self.search(
            article_id,
            keyword
        )

    # ==================================
    # Search Version
    # ==================================

    def _search_version(
        self,
        version,
        keyword
    ):
        """
        搜尋單一 Archive Version。

        Version Model 本身可能只保存
        storage_path，因此透過
        _get_content() 取得內容。
        """

        content = self._get_content(
            version
        )

        if content is None:

            return None

        keyword_text = str(
            keyword
        )

        content_text = str(
            content
        )

        if (
            keyword_text.lower()
            not in content_text.lower()
        ):

            return None

        position = (
            content_text.lower()
            .find(
                keyword_text.lower()
            )
        )

        matched_content = (
            self._extract_match(
                content_text,
                position,
                len(keyword_text)
            )
        )

        return HistoricalSearchResult(

            article_id=version.article_id,

            version_id=version.id,

            version_number=(
                version.version_number
            ),

            keyword=keyword_text,

            matched_content=(
                matched_content
            ),

            match_position=position
        )

    # ==================================
    # Get Content
    # ==================================

    def _get_content(
        self,
        version
    ):
        """
        取得 Archive Version Content。

        優先順序:

            1. content
            2. raw_content
            3. 其他可直接取得的內容

        第一階段不直接讀取 Storage，
        避免 Historical Search Engine
        與檔案系統耦合。
        """

        if hasattr(
            version,
            "content"
        ):

            return version.content

        if hasattr(
            version,
            "raw_content"
        ):

            return version.raw_content

        return None

    # ==================================
    # Extract Match
    # ==================================

    @staticmethod
    def _extract_match(
        content,
        position,
        keyword_length,
        context=50
    ):
        """
        擷取關鍵字附近的內容。

        Parameters
        ----------
        content : str
            完整內容

        position : int
            關鍵字位置

        keyword_length : int
            關鍵字長度

        context : int
            前後文長度
        """

        if not content:

            return ""

        if position < 0:

            return ""

        start = max(
            0,
            position - context
        )

        end = min(
            len(content),
            position
            + keyword_length
            + context
        )

        return content[start:end]

    # ==================================
    # Search Text
    # ==================================

    @staticmethod
    def search_text(
        content,
        keyword
    ):
        """
        不依賴 Repository 的純文字搜尋。

        用於單元測試及未來
        Parser / Storage 整合。
        """

        if content is None:

            return None

        if not keyword:

            return None

        content = str(content)

        keyword = str(keyword)

        position = (
            content.lower()
            .find(
                keyword.lower()
            )
        )

        if position == -1:

            return None

        return {
            "keyword": keyword,
            "position": position,
            "matched_content": (
                HistoricalSearch
                ._extract_match(
                    content,
                    position,
                    len(keyword)
                )
            )
        }

    # ==================================
    # Static Match
    # ==================================

    @staticmethod
    def contains(
        content,
        keyword
    ):
        """
        判斷文字是否包含指定關鍵字。
        """

        if content is None:

            return False

        if not keyword:

            return False

        return (
            str(keyword).lower()
            in str(content).lower()
        )

    # ==================================
    # Repr
    # ==================================

    def __repr__(
        self
    ):

        return (
            "HistoricalSearch("
            "version_repository="
            f"{self.version_repository!r}"
            ")"
        )