"""
services/archive_management_service.py

AutoSearch V4

P3.3

Archive Management Service

功能：

    1. Article Metadata Management
    2. Archive Version Management
    3. Archive Article Management
    4. Archive Protection
    5. Archive Statistics
    6. Search Index Management Foundation

架構：

    API
        ↓
    ArchiveManagementService
        ↓
    Repository
        ↓
    Database

設計原則：

    API Layer
        不直接操作 Database

    Service Layer
        負責 Management Business Logic

    Repository Layer
        負責 Database CRUD


P3.3 不負責：

    AI Analysis
    Knowledge Intelligence
    Search Ranking
    Crawler
"""


from database.article_metadata_repository import (
    ArticleMetadataRepository
)

from database.archive_version_repository import (
    ArchiveVersionRepository
)

from database.archive_browser_repository import (
    ArchiveBrowserRepository
)


class ArchiveManagementService:
    """
    AutoSearch V4

    P3.3 Archive Management Service。

    負責：

        Article Metadata
        Archive Version
        Archive Article
        Archive Protection
        Archive Statistics
    """

    # ==================================================
    # INIT
    # ==================================================

    def __init__(
        self,
        metadata_repository=None,
        version_repository=None,
        archive_repository=None
    ):
        """
        建立 Archive Management Service。

        Repository 可以透過 Dependency Injection
        傳入，方便：

            Unit Test
            Mock
            Integration Test
        """

        # ----------------------------------------------
        # Article Metadata Repository
        # ----------------------------------------------

        if metadata_repository is None:

            metadata_repository = (
                ArticleMetadataRepository()
            )

        self.metadata_repository = (
            metadata_repository
        )

        # ----------------------------------------------
        # Archive Version Repository
        # ----------------------------------------------

        if version_repository is None:

            version_repository = (
                ArchiveVersionRepository()
            )

        self.version_repository = (
            version_repository
        )

        # ----------------------------------------------
        # Archive Repository
        # ----------------------------------------------

        if archive_repository is None:

            archive_repository = (
                ArchiveBrowserRepository()
            )

        self.archive_repository = (
            archive_repository
        )

    # ==================================================
    # ARTICLE METADATA
    # ==================================================

    def get_metadata(
        self,
        article_id
    ):
        """
        取得 Article Metadata。
        """

        if article_id is None:
            return None

        if article_id <= 0:
            return None

        return (
            self.metadata_repository
            .get_by_article_id(
                article_id
            )
        )

    # ==================================================

    def metadata_exists(
        self,
        article_id
    ):
        """
        檢查 Article Metadata 是否存在。
        """

        if article_id is None:
            return False

        if article_id <= 0:
            return False

        return (
            self.metadata_repository
            .exists(
                article_id
            )
        )

    # ==================================================

    def create_metadata(
        self,
        metadata
    ):
        """
        建立 Article Metadata。

        若 Metadata 已存在，
        拒絕重複建立。
        """

        if metadata is None:
            return None

        article_id = (
            metadata.article_id
        )

        if article_id is None:
            return None

        if article_id <= 0:
            return None

        # ----------------------------------------------
        # Duplicate Protection
        # ----------------------------------------------

        if self.metadata_exists(
            article_id
        ):

            raise ValueError(
                "Article metadata already exists"
            )

        return (
            self.metadata_repository
            .insert(
                metadata
            )
        )

    # ==================================================

    def update_metadata(
        self,
        article_id,
        metadata
    ):
        """
        更新 Article Metadata。
        """

        if article_id is None:
            return False

        if article_id <= 0:
            return False

        if metadata is None:
            return False

        if not self.metadata_exists(
            article_id
        ):

            return False

        result = (
            self.metadata_repository
            .update(
                article_id,
                metadata
            )
        )

        return result

    # ==================================================
    # ARCHIVE VERSION
    # ==================================================

    def get_version(
        self,
        article_id,
        version_number
    ):
        """
        取得指定 Archive Version。
        """

        if article_id is None:
            return None

        if article_id <= 0:
            return None

        if version_number is None:
            return None

        if version_number <= 0:
            return None

        return (
            self.version_repository
            .get_version(
                article_id,
                version_number
            )
        )

    # ==================================================

    def get_version_by_id(
        self,
        version_id
    ):
        """
        依 Version ID 取得 Archive Version。
        """

        if version_id is None:
            return None

        if version_id <= 0:
            return None

        return (
            self.version_repository
            .get_by_id(
                version_id
            )
        )

    # ==================================================

    def get_versions(
        self,
        article_id
    ):
        """
        取得 Article 所有 Archive Versions。
        """

        if article_id is None:
            return []

        if article_id <= 0:
            return []

        return (
            self.version_repository
            .get_by_article_id(
                article_id
            )
        )

    # ==================================================

    def get_latest_version(
        self,
        article_id
    ):
        """
        取得最新 Archive Version。
        """

        if article_id is None:
            return None

        if article_id <= 0:
            return None

        return (
            self.version_repository
            .get_latest_version(
                article_id
            )
        )

    # ==================================================

    def get_latest_version_number(
        self,
        article_id
    ):
        """
        取得最新 Version Number。

        無 Version 時：

            0
        """

        if article_id is None:
            return 0

        if article_id <= 0:
            return 0

        return (
            self.version_repository
            .get_latest_version_number(
                article_id
            )
        )

    # ==================================================

    def get_next_version_number(
        self,
        article_id
    ):
        """
        取得下一個 Version Number。
        """

        if article_id is None:
            return 1

        if article_id <= 0:
            return 1

        return (
            self.version_repository
            .get_next_version_number(
                article_id
            )
        )

    # ==================================================

    def version_exists(
        self,
        article_id,
        version_number
    ):
        """
        檢查 Version 是否存在。
        """

        if article_id is None:
            return False

        if article_id <= 0:
            return False

        if version_number is None:
            return False

        if version_number <= 0:
            return False

        return (
            self.version_repository
            .exists(
                article_id,
                version_number
            )
        )

    # ==================================================

    def count_versions(
        self,
        article_id
    ):
        """
        計算 Article Archive Version 數量。
        """

        if article_id is None:
            return 0

        if article_id <= 0:
            return 0

        return (
            self.version_repository
            .count_by_article_id(
                article_id
            )
        )

    # ==================================================
    # ARCHIVE VERSION DELETE
    # ==================================================

    def delete_version(
        self,
        version_id
    ):
        """
        刪除指定 Archive Version。

        P3.3：

            Version Management

        注意：

            Version Delete 必須經過
            Service Layer。

        API 不直接呼叫 Repository。
        """

        if version_id is None:
            return False

        if version_id <= 0:
            return False

        version = (
            self.version_repository
            .get_by_id(
                version_id
            )
        )

        if version is None:
            return False

        # ----------------------------------------------
        # Archive Protection
        # ----------------------------------------------

        if self._is_version_protected(
            version
        ):

            raise ValueError(
                "Archive version is protected"
            )

        return (
            self.version_repository
            .delete_by_id(
                version_id
            )
        )

    # ==================================================
    # ARCHIVE PROTECTION
    # ==================================================

    def _is_version_protected(
        self,
        version
    ):
        """
        判斷 Archive Version 是否受到保護。

        P3.3 Foundation：

            Version 本身存在 Archive 關聯時，
            預設視為 Protected。

        後續可依：

            Knowledge Archive
            Raw Document
            Search Index

        擴充更完整的 Protection Rule。
        """

        if version is None:
            return False

        # ----------------------------------------------
        # raw_document_id
        # ----------------------------------------------

        raw_document_id = getattr(
            version,
            "raw_document_id",
            None
        )

        if raw_document_id is not None:
            return True

        return False

    # ==================================================
    # ARCHIVE ARTICLE
    # ==================================================

    def get_article(
        self,
        article_id
    ):
        """
        取得 Archive Article。
        """

        if article_id is None:
            return None

        if article_id <= 0:
            return None

        if hasattr(
            self.archive_repository,
            "get_article"
        ):

            return (
                self.archive_repository
                .get_article(
                    article_id
                )
            )

        if hasattr(
            self.archive_repository,
            "get_by_id"
        ):

            return (
                self.archive_repository
                .get_by_id(
                    article_id
                )
            )

        return None

    # ==================================================

    def get_articles(
        self,
        limit=None
    ):
        """
        取得 Archive Articles。
        """

        if hasattr(
            self.archive_repository,
            "get_articles"
        ):

            if limit is None:

                return (
                    self.archive_repository
                    .get_articles()
                )

            return (
                self.archive_repository
                .get_articles(
                    limit=limit
                )
            )

        return []

    # ==================================================
    # STATISTICS
    # ==================================================

    def get_statistics(self):
        """
        取得 Archive Management Statistics。
        """

        if hasattr(
            self.archive_repository,
            "get_statistics"
        ):

            return (
                self.archive_repository
                .get_statistics()
            )

        statistics = {

            "articles":
                self._safe_count_articles(),

            "archive_versions":
                0

        }

        return statistics

    # ==================================================

    def _safe_count_articles(self):
        """
        安全取得 Article Count。
        """

        if hasattr(
            self.archive_repository,
            "count_articles"
        ):

            return (
                self.archive_repository
                .count_articles()
            )

        if hasattr(
            self.archive_repository,
            "count"
        ):

            return (
                self.archive_repository
                .count()
            )

        return 0

    # ==================================================
    # SEARCH INDEX MANAGEMENT
    # ==================================================

    def get_index_status(self):
        """
        取得 Search Index Management Status。

        P3.3 Foundation。

        目前先提供狀態資訊，
        實際 Refresh / Rebuild
        由 Search Index Service 處理。
        """

        return {

            "status":
                "available",

            "service":
                "archive-search-index",

            "operations": [

                "status",

                "refresh",

                "rebuild"

            ]

        }

    # ==================================================

    def refresh_index(self):
        """
        Refresh Search Index。

        P3.3 Foundation：

            尚未直接執行 Index Refresh。

        保留 Service API，
        後續接 SearchIndexService。
        """

        return {

            "status":
                "not_implemented",

            "operation":
                "refresh"

        }

    # ==================================================

    def rebuild_index(self):
        """
        Rebuild Search Index。

        P3.3 Foundation：

            尚未直接執行 Index Rebuild。

        後續接 SearchIndexService。
        """

        return {

            "status":
                "not_implemented",

            "operation":
                "rebuild"

        }

    # ==================================================
    # HEALTH
    # ==================================================

    def health_check(self):
        """
        Archive Management Service Health Check。
        """

        return {

            "status":
                "ok",

            "service":
                "archive-management-service",

            "version":
                "P3.3"

        }

    # ==================================================
    # REPR
    # ==================================================

    def __repr__(self):
        return (
            "ArchiveManagementService("
            f"metadata_repository="
            f"{self.metadata_repository!r}, "
            f"version_repository="
            f"{self.version_repository!r}, "
            f"archive_repository="
            f"{self.archive_repository!r}"
            ")"
        )
