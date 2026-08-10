"""
archive/archive_browser.py

AutoSearch V4

P2.3.6 Archive Browser

用途:

    提供 Knowledge Archive 歷史版本瀏覽功能。

功能:

    1. 取得 Article
    2. 取得 Article 所有 Version
    3. 取得指定 Version
    4. 依 Version ID 取得 Version
    5. 取得最新 Version
    6. 取得第一個 Version
    7. 取得 Version Timeline
    8. 取得上一個 Version
    9. 取得下一個 Version
    10. 取得 Archive Summary
    11. 判斷 Article 是否有 History
    12. 建立完整 Browser View

設計:

    Article
        ↓
    ArchiveVersionRepository
        ↓
    ArticleHistoryRepository
        ↓
    ArchiveViewer
        ↓
    ArchiveBrowser

注意:

    本模組不直接操作 Database。
"""

from database.article_repository import ArticleRepository

from database.archive_version_repository import (
    ArchiveVersionRepository
)

from database.article_history_repository import (
    ArticleHistoryRepository
)

from archive.archive_viewer import ArchiveViewer


class ArchiveBrowser:
    """
    Knowledge Archive Browser

    負責整合 Article History、
    Archive Version 與 Archive Viewer。
    """

    # ==================================
    # Initialize
    # ==================================

    def __init__(
        self,
        article_repository=None,
        version_repository=None,
        history_repository=None,
        viewer=None
    ):
        """
        初始化 Archive Browser。

        Parameters
        ----------
        article_repository :
            Article Repository

        version_repository :
            Archive Version Repository

        history_repository :
            Article History Repository

        viewer :
            Archive Viewer
        """

        self.article_repository = (
            article_repository
            if article_repository is not None
            else ArticleRepository()
        )

        self.version_repository = (
            version_repository
            if version_repository is not None
            else ArchiveVersionRepository()
        )

        self.history_repository = (
            history_repository
            if history_repository is not None
            else ArticleHistoryRepository()
        )

        self.viewer = (
            viewer
            if viewer is not None
            else ArchiveViewer(
                article_repository=self.article_repository,
                version_repository=self.version_repository,
                history_repository=self.history_repository
            )
        )

    # ==================================
    # Get Article
    # ==================================

    def get_article(
        self,
        article_id
    ):
        """
        取得 Article。
        """

        return self.article_repository.get_by_id(
            article_id
        )

    # ==================================
    # Get Versions
    # ==================================

    def get_versions(
        self,
        article_id
    ):
        """
        取得 Article 所有 Archive Versions。
        """

        return self.version_repository.get_by_article_id(
            article_id
        )

    # ==================================
    # Get Version
    # ==================================

    def get_version(
        self,
        article_id,
        version_number
    ):
        """
        取得指定 Version。
        """

        versions = self.get_versions(
            article_id
        )

        for version in versions:

            if (
                version.version_number
                == version_number
            ):
                return version

        return None

    # ==================================
    # Get Version By ID
    # ==================================

    def get_version_by_id(
        self,
        version_id
    ):
        """
        依 Version ID 取得 Version。
        """

        return self.version_repository.get_by_id(
            version_id
        )

    # ==================================
    # Get Latest
    # ==================================

    def get_latest(
        self,
        article_id
    ):
        """
        取得最新 Version。
        """

        return self.version_repository.get_latest_version(
            article_id
        )

    # ==================================
    # Get First
    # ==================================

    def get_first(
        self,
        article_id
    ):
        """
        取得第一個 Version。
        """

        versions = self.get_versions(
            article_id
        )

        if not versions:
            return None

        return versions[0]

    # ==================================
    # Get Timeline
    # ==================================

    def get_timeline(
        self,
        article_id
    ):
        """
        取得 Article Version Timeline。
        """

        return self.history_repository.get_timeline(
            article_id
        )

    # ==================================
    # Get Previous Version
    # ==================================

    def get_previous_version(
        self,
        article_id,
        version_number
    ):
        """
        取得指定 Version 的上一個 Version。
        """

        versions = self.get_versions(
            article_id
        )

        previous = None

        for version in versions:

            if (
                version.version_number
                >= version_number
            ):
                break

            previous = version

        return previous

    # ==================================
    # Get Next Version
    # ==================================

    def get_next_version(
        self,
        article_id,
        version_number
    ):
        """
        取得指定 Version 的下一個 Version。
        """

        versions = self.get_versions(
            article_id
        )

        for version in versions:

            if (
                version.version_number
                > version_number
            ):
                return version

        return None

    # ==================================
    # Has History
    # ==================================

    def has_history(
        self,
        article_id
    ):
        """
        判斷 Article 是否存在歷史版本。
        """

        return self.history_repository.has_history(
            article_id
        )

    # ==================================
    # Count Versions
    # ==================================

    def count_versions(
        self,
        article_id
    ):
        """
        計算 Article Version 數量。
        """

        return self.history_repository.count_versions(
            article_id
        )

    # ==================================
    # Get Summary
    # ==================================

    def get_summary(
        self,
        article_id
    ):
        """
        取得 Article History Summary。
        """

        return self.history_repository.get_summary(
            article_id
        )

    # ==================================
    # Get View
    # ==================================

    def get_view(
        self,
        article_id,
        version_number
    ):
        """
        取得指定 Version 的 Archive View。
        """

        return self.viewer.get_view(
            article_id,
            version_number
        )

    # ==================================
    # Get View By Version ID
    # ==================================

    def get_view_by_version_id(
        self,
        version_id
    ):
        """
        依 Version ID 取得 Archive View。
        """

        return self.viewer.get_view_by_version_id(
            version_id
        )

    # ==================================
    # Get Content
    # ==================================

    def get_content(
        self,
        article_id,
        version_number
    ):
        """
        取得指定 Version 的歷史內容。
        """

        view = self.get_view(
            article_id,
            version_number
        )

        if view is None:
            return None

        return view.content

    # ==================================
    # Get Latest Content
    # ==================================

    def get_latest_content(
        self,
        article_id
    ):
        """
        取得最新 Version 的內容。
        """

        view = self.viewer.get_latest(
            article_id
        )

        if view is None:
            return None

        return view.content

    # ==================================
    # Get First Content
    # ==================================

    def get_first_content(
        self,
        article_id
    ):
        """
        取得第一個 Version 的內容。
        """

        view = self.viewer.get_first(
            article_id
        )

        if view is None:
            return None

        return view.content

    # ==================================
    # Browse
    # ==================================

    def browse(
        self,
        article_id
    ):
        """
        建立完整 Archive Browser View。

        Returns
        -------

        dict
            {
                "article": ...,
                "versions": ...,
                "latest": ...,
                "first": ...,
                "timeline": ...,
                "summary": ...,
                "has_history": ...,
                "count": ...
            }
        """

        article = self.get_article(
            article_id
        )

        if article is None:
            return None

        versions = self.get_versions(
            article_id
        )

        latest = self.get_latest(
            article_id
        )

        first = self.get_first(
            article_id
        )

        timeline = self.get_timeline(
            article_id
        )

        summary = self.get_summary(
            article_id
        )

        has_history = self.has_history(
            article_id
        )

        count = self.count_versions(
            article_id
        )

        return {
            "article": article,
            "versions": versions,
            "latest": latest,
            "first": first,
            "timeline": timeline,
            "summary": summary,
            "has_history": has_history,
            "count": count
        }

    # ==================================
    # Dictionary Browse
    # ==================================

    def browse_dict(
        self,
        article_id
    ):
        """
        建立適合 API / JSON 使用的 Browser 結果。
        """

        result = self.browse(
            article_id
        )

        if result is None:
            return None

        article = result["article"]

        versions = result["versions"]

        latest = result["latest"]

        first = result["first"]

        return {
            "article": self._to_dict(
                article
            ),

            "versions": [
                self._to_dict(version)
                for version in versions
            ],

            "latest": self._to_dict(
                latest
            ),

            "first": self._to_dict(
                first
            ),

            "timeline": result["timeline"],

            "summary": result["summary"],

            "has_history": result["has_history"],

            "count": result["count"]
        }

    # ==================================
    # Convert Object
    # ==================================

    @staticmethod
    def _to_dict(
        value
    ):
        """
        將 Model 轉成 Dictionary。
        """

        if value is None:
            return None

        if isinstance(
            value,
            dict
        ):
            return value

        if hasattr(
            value,
            "to_dict"
        ):
            return value.to_dict()

        if hasattr(
            value,
            "__dict__"
        ):
            return dict(
                value.__dict__
            )

        return value

    # ==================================
    # Representation
    # ==================================

    def __repr__(
        self
    ):
        return (
            "ArchiveBrowser("
            "article_repository="
            f"{self.article_repository.__class__.__name__}, "
            "version_repository="
            f"{self.version_repository.__class__.__name__}, "
            "history_repository="
            f"{self.history_repository.__class__.__name__}"
            ")"
        )