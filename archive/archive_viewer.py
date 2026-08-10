"""
archive/archive_viewer.py

AutoSearch V4

P2.3.5 Archive Viewer / Historical Content Retrieval

用途:

    提供 Knowledge Archive 的歷史內容讀取功能。

功能:

    1. 取得指定 Article 的歷史版本
    2. 取得指定 Version
    3. 取得最新 Version
    4. 取得第一個 Version
    5. 取得 Article 歷史 Timeline
    6. 將 Article + Version 組合成 ArchiveView
    7. 取得 Historical Content
    8. 判斷 Article 是否存在歷史版本

設計:

    Article
        ↓
    ArchiveVersionRepository
        ↓
    ArticleHistoryRepository
        ↓
    ArchiveViewer
        ↓
    ArchiveView

注意:

    本模組不直接操作 Database。
"""

from models.archive_view import ArchiveView

from database.article_repository import ArticleRepository
from database.archive_version_repository import ArchiveVersionRepository
from database.article_history_repository import ArticleHistoryRepository


class ArchiveViewer:

    """
    Archive Viewer

    負責 Historical Content Retrieval。
    """

    # ==================================
    # Initialize
    # ==================================

    def __init__(
        self,
        article_repository=None,
        version_repository=None,
        history_repository=None
    ):

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

    # ==================================
    # Get Article
    # ==================================

    def get_article(
        self,
        article_id
    ):

        """
        取得 Article。

        Returns
        -------

        Article / dict / None
        """

        return self.article_repository.get_by_id(
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
        取得指定 Article 的指定 Version。

        Returns
        -------

        ArchiveVersion / None
        """

        return self.history_repository.get_version(
            article_id,
            version_number
        )

    # ==================================
    # Get Version By ID
    # ==================================

    def get_version_by_id(
        self,
        version_id
    ):

        """
        透過 Version ID 取得 ArchiveVersion。
        """

        return self.history_repository.get_version_by_id(
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
        取得 Article 最新版本。

        Returns
        -------

        ArchiveView / None
        """

        version = (
            self.history_repository.get_latest(
                article_id
            )
        )

        if version is None:
            return None

        return self._build_view(
            article_id,
            version
        )

    # ==================================
    # Get First
    # ==================================

    def get_first(
        self,
        article_id
    ):

        """
        取得 Article 第一個版本。

        Returns
        -------

        ArchiveView / None
        """

        version = (
            self.history_repository.get_first(
                article_id
            )
        )

        if version is None:
            return None

        return self._build_view(
            article_id,
            version
        )

    # ==================================
    # Get Specific Version View
    # ==================================

    def get_view(
        self,
        article_id,
        version_number
    ):

        """
        取得指定版本的 ArchiveView。

        Returns
        -------

        ArchiveView / None
        """

        version = self.get_version(
            article_id,
            version_number
        )

        if version is None:
            return None

        return self._build_view(
            article_id,
            version
        )

    # ==================================
    # Get View By Version ID
    # ==================================

    def get_view_by_version_id(
        self,
        version_id
    ):

        """
        透過 Version ID 取得 ArchiveView。
        """

        version = self.get_version_by_id(
            version_id
        )

        if version is None:
            return None

        return self._build_view(
            version.article_id,
            version
        )

    # ==================================
    # Get History
    # ==================================

    def get_history(
        self,
        article_id
    ):

        """
        取得 Article 全部歷史版本。

        Returns
        -------

        list[ArchiveView]
        """

        versions = (
            self.history_repository.get_history(
                article_id
            )
        )

        return [
            self._build_view(
                article_id,
                version
            )
            for version in versions
        ]

    # ==================================
    # Get Timeline
    # ==================================

    def get_timeline(
        self,
        article_id
    ):

        """
        取得 Article History Timeline。

        Returns
        -------

        list
        """

        return self.history_repository.get_timeline(
            article_id
        )

    # ==================================
    # Get Historical Content
    # ==================================

    def get_content(
        self,
        article_id,
        version_number
    ):

        """
        取得指定歷史版本內容。

        Returns
        -------

        str / None
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
        取得最新版本內容。
        """

        view = self.get_latest(
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
        取得第一個版本內容。
        """

        view = self.get_first(
            article_id
        )

        if view is None:
            return None

        return view.content

    # ==================================
    # Has History
    # ==================================

    def has_history(
        self,
        article_id
    ):

        """
        判斷 Article 是否具有歷史版本。
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
        計算 Article 的歷史版本數量。
        """

        return self.history_repository.count_versions(
            article_id
        )

    # ==================================
    # Build Archive View
    # ==================================

    def _build_view(
        self,
        article_id,
        version
    ):

        """
        將 Article + ArchiveVersion
        組合成 ArchiveView。
        """

        article = self.get_article(
            article_id
        )

        if article is None:
            return None

        title = self._get_value(
            article,
            "title",
            ""
        )

        content = self._get_version_content(
            version
        )

        return ArchiveView(

            article_id=article_id,

            version_id=self._get_value(
                version,
                "id"
            ),

            version_number=self._get_value(
                version,
                "version_number"
            ),

            title=title,

            content=content
        )

    # ==================================
    # Get Version Content
    # ==================================

    def _get_version_content(
        self,
        version
    ):

        """
        取得 Version 的 Historical Content。

        ArchiveVersion 主要儲存：

            storage_path
            raw_document_id
            file metadata

        因此這裡先支援：

            content attribute

        如果 Version Model 未提供 content，
        則回傳空字串。

        後續接 Archive Storage 時，
        可以在此處加入真正的檔案讀取。
        """

        content = self._get_value(
            version,
            "content",
            ""
        )

        if content is None:
            return ""

        return content

    # ==================================
    # Get Value
    # ==================================

    @staticmethod
    def _get_value(
        obj,
        key,
        default=None
    ):

        """
        同時支援：

            Object
            Dictionary
        """

        if obj is None:
            return default

        if isinstance(
            obj,
            dict
        ):

            return obj.get(
                key,
                default
            )

        return getattr(
            obj,
            key,
            default
        )

    # ==================================
    # Repr
    # ==================================

    def __repr__(
        self
    ):

        return (
            "ArchiveViewer("
            "article_repository="
            f"{self.article_repository.__class__.__name__}, "
            "version_repository="
            f"{self.version_repository.__class__.__name__}, "
            "history_repository="
            f"{self.history_repository.__class__.__name__}"
            ")"
        )