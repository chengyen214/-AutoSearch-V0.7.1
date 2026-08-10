"""
archive/archive_integration.py

AutoSearch V4

P2.3 Archive Integration

用途:

    整合 Knowledge Archive 相關功能。

功能:

    1. 處理新 Article
    2. 判斷 Article 是否已存在
    3. 判斷內容是否變更
    4. 建立新的 Archive Version
    5. 取得 Article History
    6. 取得 Version Timeline
    7. 產生 Version Diff
    8. 取得 Knowledge History

設計:

    Article
        ↓
    ArchiveIntegration
        ↓
    ArchiveService
        ↓
    RawDocumentRepository
        ↓
    ArchiveVersionRepository
        ↓
    Version / History
        ↓
    Archive Viewer / Browser / Diff
        ↓
    Knowledge History

注意:

    本模組不直接操作 Database。

    Repository / Service 必須透過
    dependency injection 或 _get_xxx()
    取得。
"""


class ArchiveIntegration:
    """
    Archive Integration Service

    P2.3

    負責統一：

        Article
            ↓
        Archive
            ↓
        Version
            ↓
        History
            ↓
        Knowledge History
    """

    # ==================================
    # Init
    # ==================================

    def __init__(
        self,
        archive_service=None,
        archive_repository=None,
        article_history_repository=None,
        knowledge_history_engine=None,
        repository=None
    ):
        """
        初始化 Archive Integration。

        repository 為 backward compatible
        參數，支援舊測試與 Fake Repository。
        """

        # ==================================
        # Archive Service
        # ==================================

        self.archive_service = (
            archive_service
        )

        # ==================================
        # Repository
        # ==================================

        if archive_repository is None:
            archive_repository = repository

        self.archive_repository = (
            archive_repository
        )

        # ==================================
        # Article History Repository
        # ==================================

        self.article_history_repository = (
            article_history_repository
        )

        # ==================================
        # Knowledge History
        # ==================================

        self.knowledge_history_engine = (
            knowledge_history_engine
        )

    # ==================================
    # Archive Service
    # ==================================

    def _get_archive_service(self):
        """
        取得 ArchiveService。
        """

        if self.archive_service is None:

            try:

                from services.archive_service import (
                    ArchiveService
                )

                self.archive_service = (
                    ArchiveService()
                )

            except ImportError:

                return None

        return self.archive_service

    # ==================================
    # Archive Repository
    # ==================================

    def _get_archive_repository(self):
        """
        取得 Archive Repository。
        """

        if self.archive_repository is None:

            try:

                from database.archive_repository import (
                    ArchiveRepository
                )

                self.archive_repository = (
                    ArchiveRepository()
                )

            except ImportError:

                return None

        return self.archive_repository

    # ==================================
    # Article History Repository
    # ==================================

    def _get_article_history_repository(self):
        """
        取得 Article History Repository。
        """

        if (
            self.article_history_repository
            is None
        ):

            try:

                from database.article_history_repository import (
                    ArticleHistoryRepository
                )

                self.article_history_repository = (
                    ArticleHistoryRepository()
                )

            except ImportError:

                return None

        return self.article_history_repository

    # ==================================
    # Knowledge History
    # ==================================

    def _get_knowledge_history_engine(self):
        """
        取得 Knowledge History Engine。
        """

        if (
            self.knowledge_history_engine
            is None
        ):

            try:

                from archive.knowledge_history import (
                    KnowledgeHistoryEngine
                )

                self.knowledge_history_engine = (
                    KnowledgeHistoryEngine()
                )

            except ImportError:

                return None

        return self.knowledge_history_engine

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

        repository = (
            self._get_archive_repository()
        )

        if repository is None:
            return None

        if hasattr(
            repository,
            "get_article"
        ):

            return repository.get_article(
                article_id
            )

        if hasattr(
            repository,
            "get_by_id"
        ):

            return repository.get_by_id(
                article_id
            )

        return None

    # ==================================
    # Get Latest Version
    # ==================================

    def get_latest_version(
        self,
        article_id
    ):
        """
        取得最新 Archive Version。
        """

        repository = (
            self._get_archive_repository()
        )

        if repository is not None:

            if hasattr(
                repository,
                "get_latest_version"
            ):

                return repository.get_latest_version(
                    article_id
                )

            if hasattr(
                repository,
                "get_latest"
            ):

                return repository.get_latest(
                    article_id
                )

        history_repository = (
            self._get_article_history_repository()
        )

        if history_repository is not None:

            if hasattr(
                history_repository,
                "get_latest"
            ):

                return history_repository.get_latest(
                    article_id
                )

            if hasattr(
                history_repository,
                "get_latest_version"
            ):

                return history_repository.get_latest_version(
                    article_id
                )

        archive_service = (
            self._get_archive_service()
        )

        if archive_service is not None:

            if hasattr(
                archive_service,
                "get_latest_version"
            ):

                return archive_service.get_latest_version(
                    article_id
                )

        return None

    # ==================================
    # Get History
    # ==================================

    def get_history(
        self,
        article_id
    ):
        """
        取得 Article History。
        """

        repository = (
            self._get_article_history_repository()
        )

        if repository is not None:

            if hasattr(
                repository,
                "get_history"
            ):

                return repository.get_history(
                    article_id
                )

            if hasattr(
                repository,
                "get_by_article_id"
            ):

                return repository.get_by_article_id(
                    article_id
                )

        repository = (
            self._get_archive_repository()
        )

        if repository is not None:

            if hasattr(
                repository,
                "get_by_article_id"
            ):

                return repository.get_by_article_id(
                    article_id
                )

            if hasattr(
                repository,
                "get_history"
            ):

                return repository.get_history(
                    article_id
                )

        archive_service = (
            self._get_archive_service()
        )

        if archive_service is not None:

            if hasattr(
                archive_service,
                "get_versions"
            ):

                return archive_service.get_versions(
                    article_id
                )

        return []

    # ==================================
    # Get Timeline
    # ==================================

    def get_timeline(
        self,
        article_id
    ):
        """
        取得 Version Timeline。
        """

        history = self.get_history(
            article_id
        )

        return sorted(
            history,
            key=lambda item: (
                getattr(
                    item,
                    "version_number",
                    0
                )
                if getattr(
                    item,
                    "version_number",
                    None
                ) is not None
                else 0
            )
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

        repository = (
            self._get_archive_repository()
        )

        if repository is not None:

            if hasattr(
                repository,
                "get_version"
            ):

                return repository.get_version(
                    article_id,
                    version_number
                )

        timeline = self.get_timeline(
            article_id
        )

        for version in timeline:

            if (
                getattr(
                    version,
                    "version_number",
                    None
                )
                == version_number
            ):

                return version

        return None

    # ==================================
    # Compare Content
    # ==================================

    @staticmethod
    def content_changed(
        old_content,
        new_content
    ):
        """
        判斷內容是否變更。
        """

        old_content = (
            old_content
            if old_content is not None
            else ""
        )

        new_content = (
            new_content
            if new_content is not None
            else ""
        )

        return old_content != new_content

    # ==================================
    # Content Hash
    # ==================================

    @staticmethod
    def content_hash(
        content
    ):
        """
        計算 SHA256。
        """

        import hashlib

        if content is None:
            content = ""

        if not isinstance(
            content,
            bytes
        ):

            content = content.encode(
                "utf-8"
            )

        return hashlib.sha256(
            content
        ).hexdigest()

    # ==================================
    # Version Hash
    # ==================================

    @staticmethod
    def _get_version_hash(
        version
    ):
        """
        取得 Version file_hash。
        """

        if version is None:
            return None

        return getattr(
            version,
            "file_hash",
            None
        )

    # ==================================
    # Create Version
    # ==================================

    def create_version(
        self,
        article_id,
        article,
        version_number=None,
        html=None,
        url=None
    ):
        """
        建立新的 Archive Version。

        Production:

            ArchiveService.save_html()

        Test / Legacy:

            Repository.create_version()

            Repository.save_version()
        """

        # ==================================
        # Archive Service
        # ==================================

        archive_service = (
            self._get_archive_service()
        )

        if archive_service is not None:

            if hasattr(
                archive_service,
                "save_html"
            ):

                if html is None:

                    html = getattr(
                        article,
                        "html",
                        None
                    )

                if html is not None:

                    if url is None:

                        url = getattr(
                            article,
                            "url",
                            ""
                        )

                    return archive_service.save_html(
                        article_id=article_id,
                        url=url,
                        html=html
                    )

        # ==================================
        # Repository
        # ==================================

        repository = (
            self._get_archive_repository()
        )

        if repository is None:
            return None

        if hasattr(
            repository,
            "create_version"
        ):

            return repository.create_version(
                article_id,
                article,
                version_number
            )

        if hasattr(
            repository,
            "save_version"
        ):

            return repository.save_version(
                article_id,
                article,
                version_number
            )

        return None

    # ==================================
    # Process Article
    # ==================================

    def process_article(
        self,
        article_id,
        article,
        content=None,
        html=None,
        url=None,
        content_hash=None
    ):
        """
        處理 Article Archive History。

        Flow:

            Article
                ↓
            Latest Version
                ↓
            History Detection
                ↓
            Content Compare
                ↓
            ┌──────────────────────┐
            │                      │
          unchanged             changed
            │                      │
            ↓                      ↓
        no new version        Version N+1
        """

        # ==================================
        # Content
        # ==================================

        if content is None:

            content = getattr(
                article,
                "content",
                ""
            )

        # ==================================
        # HTML
        # ==================================

        if html is None:

            html = getattr(
                article,
                "html",
                None
            )

        # ==================================
        # URL
        # ==================================

        if url is None:

            url = getattr(
                article,
                "url",
                ""
            )

        # ==================================
        # Latest Version
        # ==================================

        latest = self.get_latest_version(
            article_id
        )

        # ==================================
        # First Run
        # ==================================

        if latest is None:

            version = self.create_version(
                article_id,
                article,
                version_number=1,
                html=html,
                url=url
            )

            return {

                "article_id": article_id,

                "created": (
                    version is not None
                ),

                "changed": True,

                "version": version,

                "version_number": (
                    getattr(
                        version,
                        "version_number",
                        1
                    )
                    if version is not None
                    else None
                ),

                "reason": "new_article"

            }

        # ==================================
        # Determine Change
        # ==================================

        changed = None

        # ==================================
        # Explicit Hash
        # ==================================

        if content_hash is not None:

            old_hash = (
                self._get_version_hash(
                    latest
                )
            )

            changed = (
                old_hash != content_hash
            )

        # ==================================
        # HTML Hash
        # ==================================

        elif html is not None:

            new_hash = (
                self.content_hash(
                    html
                )
            )

            old_hash = (
                self._get_version_hash(
                    latest
                )
            )

            changed = (
                old_hash != new_hash
            )

        # ==================================
        # Content Compare
        # ==================================

        else:

            old_content = getattr(
                latest,
                "content",
                ""
            )

            changed = self.content_changed(
                old_content,
                content
            )

        # ==================================
        # Unchanged
        # ==================================

        if not changed:

            return {

                "article_id": article_id,

                "created": False,

                "changed": False,

                "version": latest,

                "version_number": (
                    getattr(
                        latest,
                        "version_number",
                        None
                    )
                ),

                "reason": "unchanged"

            }

        # ==================================
        # New Version Number
        # ==================================

        old_version_number = getattr(
            latest,
            "version_number",
            0
        )

        if old_version_number is None:
            old_version_number = 0

        new_version_number = (
            old_version_number + 1
        )

        # ==================================
        # Create Version
        # ==================================

        version = self.create_version(
            article_id,
            article,
            version_number=new_version_number,
            html=html,
            url=url
        )

        return {

            "article_id": article_id,

            "created": (
                version is not None
            ),

            "changed": True,

            "version": version,

            "version_number": (
                getattr(
                    version,
                    "version_number",
                    new_version_number
                )
                if version is not None
                else None
            ),

            "reason": "content_changed"

        }

    # ==================================
    # Diff
    # ==================================

    def get_diff(
        self,
        old_content,
        new_content,
        article_id=None,
        from_version=None,
        to_version=None
    ):
        """
        取得 Version Diff。
        """

        from archive.version_diff import (
            VersionDiff
        )

        return VersionDiff.compare(
            old_content,
            new_content,
            article_id=article_id,
            from_version=from_version,
            to_version=to_version
        )

    # ==================================
    # Knowledge History
    # ==================================

    def get_knowledge_history(
        self,
        article_id
    ):
        """
        取得 Knowledge History。
        """

        engine = (
            self._get_knowledge_history_engine()
        )

        if engine is None:
            return []

        return engine.get_history(
            article_id
        )

    # ==================================
    # Knowledge Evolution
    # ==================================

    def get_knowledge_evolution(
        self,
        article_id
    ):
        """
        取得完整 Knowledge Evolution。
        """

        engine = (
            self._get_knowledge_history_engine()
        )

        if engine is None:
            return []

        return engine.get_knowledge_evolution(
            article_id
        )

    # ==================================
    # Archive Status
    # ==================================

    def get_status(
        self,
        article_id
    ):
        """
        取得 Article Archive 狀態。
        """

        history = self.get_history(
            article_id
        )

        latest = self.get_latest_version(
            article_id
        )

        knowledge_history = (
            self.get_knowledge_history(
                article_id
            )
        )

        return {

            "article_id": article_id,

            "has_history": (
                len(history) > 0
            ),

            "version_count": (
                len(history)
            ),

            "latest_version": (
                getattr(
                    latest,
                    "version_number",
                    None
                )
                if latest is not None
                else None
            ),

            "knowledge_history_count": (
                len(knowledge_history)
            )
        }

    # ==================================
    # Repr
    # ==================================

    def __repr__(self):

        return (
            "ArchiveIntegration("
            f"archive_service="
            f"{self.archive_service!r}, "
            f"archive_repository="
            f"{self.archive_repository!r}, "
            f"article_history_repository="
            f"{self.article_history_repository!r}, "
            f"knowledge_history_engine="
            f"{self.knowledge_history_engine!r}"
            ")"
        )