"""
services/article_service.py

AutoSearch V5

Article Service

用途：

    負責：

        Article SQL Persistence
        Archive Persistence
        AI Task Creation
        AI Batch Trigger
        Article Query
        Article Management

Pipeline：

    Parsed Article
        ↓
    ArticleService
        ↓
    ArticleRepository
        ↓
    SQL articles
        ↓
    ArchiveService
        ↓
    MongoDB raw_html
        ↓
    MySQL raw_documents
        ↓
    MySQL archive_versions
        ↓
    AITaskRepository
        ↓
    ai_tasks WAITING
        ↓
    AIBatchTriggerService
        ↓
    AI Scheduler
        ↓
    AI Worker


重要：

    ArticleService 不負責：

        Crawler
        Parser
        Search
        Download
        Search Source
        Search Execution
        AI Analysis
        AI Worker
        AI Scheduler


ArticleService 只負責：

    Article
        ↓
    SQL
        ↓
    Archive
        ↓
    AI Task


Hash Responsibility：

    Article document_id
        ↓
    Article Document Identity

    Archive file_hash
        ↓
    Archive Version Duplicate Detection

所有 SHA256 Hash：

    utils/hash.py

ArticleService 不自行計算 SHA256。
"""

from database.article_repository import (
    ArticleRepository,
)

from database.ai_task_repository import (
    AITaskRepository,
)

from models.ai_task import (
    AITask,
)

from services.archive_service import (
    ArchiveService,
)

from archive.archive_integration import (
    ArchiveIntegration,
)

from services.ai_batch_trigger_service import (
    AIBatchTriggerService,
)

from utils.logger import (
    logger,
)


class ArticleService:
    """
    AutoSearch V5 Article Service。

    核心 Pipeline：

        Article
          ↓
        SQL
          ↓
        Archive
          ↓
        AI Task

    不負責：

        Crawler
        Parser
        Search
        Download
        Search Adapter
        Search Execution
        AI Analysis
        AI Worker
        AI Scheduler
        Knowledge Processing
    """

    # ==================================================
    # Initialize
    # ==================================================

    def __init__(
        self,
        repo=None,
        task_repo=None,
        archive_service=None,
        archive_integration=None,
        batch_trigger=None,
    ):
        """
        建立 Article Service。

        Dependency Injection：

            ArticleRepository
            AITaskRepository
            ArchiveService
            ArchiveIntegration
            AIBatchTriggerService
        """

        # ==========================================
        # Article Repository
        # ==========================================

        if repo is None:
            repo = ArticleRepository()

        self.repo = repo

        # ==========================================
        # AI Task Repository
        # ==========================================

        if task_repo is None:
            task_repo = AITaskRepository()

        self.task_repo = task_repo

        # ==========================================
        # Archive Service
        # ==========================================

        if archive_service is None:
            archive_service = ArchiveService()

        self.archive_service = archive_service

        # ==========================================
        # Archive Integration
        # ==========================================

        if archive_integration is None:

            archive_integration = ArchiveIntegration(
                archive_repository=(
                    self.archive_service.version_repo
                )
            )

        self.archive_integration = archive_integration

        # ==========================================
        # AI Batch Trigger
        # ==========================================

        if batch_trigger is None:

            batch_trigger = AIBatchTriggerService(
                task_repository=self.task_repo
            )

        self.batch_trigger = batch_trigger

        logger.info(
            "ArticleService initialized: "
            "SQL -> Archive -> AI Task"
        )

    # ==================================================
    # Utility
    # ==================================================

    @staticmethod
    def _get_value(
        obj,
        key,
        default=None,
    ):
        """
        同時支援：

            object
            dict
        """

        if obj is None:
            return default

        if isinstance(
            obj,
            dict,
        ):
            return obj.get(
                key,
                default,
            )

        return getattr(
            obj,
            key,
            default,
        )

    # ==================================================
    # Get Article ID
    # ==================================================

    @staticmethod
    def _get_article_id(
        article,
    ):
        """
        從 Article object / dict 取得 ID。
        """

        if article is None:
            return None

        if isinstance(
            article,
            dict,
        ):
            return article.get("id")

        return getattr(
            article,
            "id",
            None,
        )

    # ==================================================
    # Find Existing Article By URL
    # ==================================================

    def _find_existing_article_by_url(
        self,
        url,
    ):
        """
        依 URL 找出既有 Article。

        只負責 Article Entity Lookup。
        """

        if not url:
            return None

        try:

            url = str(
                url
            ).strip()

            if not url:
                return None

            if hasattr(
                self.repo,
                "find_by_url",
            ):
                return self.repo.find_by_url(
                    url
                )

        except Exception as e:

            logger.exception(
                "Find existing article by URL error: "
                f"{e}"
            )

        return None

    # ==================================================
    # Find Existing Article By Document ID
    # ==================================================

    def _find_existing_article_by_document_id(
        self,
        document_id,
    ):
        """
        依 document_id 查詢既有 Article。

        只負責：

            Article Document Duplicate Detection
        """

        if not document_id:
            return None

        try:

            document_id = str(
                document_id
            ).strip()

            if not document_id:
                return None

            if hasattr(
                self.repo,
                "find_by_document_id",
            ):
                return self.repo.find_by_document_id(
                    document_id
                )

        except Exception as e:

            logger.exception(
                "Find existing article by "
                "document_id error: "
                f"{e}"
            )

        return None

    # ==================================================
    # Get Latest Archive Version
    # ==================================================

    def _get_latest_archive_version(
        self,
        article_id,
    ):
        """
        取得指定 Article 最新 Archive Version。

        只負責 Version Information。

        不負責 Archive Hash。
        """

        try:

            repository = (
                self.archive_integration
                ._get_archive_repository()
            )

            if repository is None:
                return None

            if hasattr(
                repository,
                "get_latest_version",
            ):
                return repository.get_latest_version(
                    article_id
                )

            if hasattr(
                repository,
                "get_latest",
            ):
                return repository.get_latest(
                    article_id
                )

        except Exception as e:

            logger.exception(
                "Get latest archive version error: "
                f"{e}"
            )

        return None

    # ==================================================
    # Determine Archive Version Created
    # ==================================================

    def _is_new_archive_version(
        self,
        previous_version,
        saved_version,
    ):
        """
        判斷 ArchiveService.save_html()
        是否建立新的 Archive Version。
        """

        if saved_version is None:
            return False

        if previous_version is None:
            return True

        previous_number = self._get_value(
            previous_version,
            "version_number",
            None,
        )

        saved_number = self._get_value(
            saved_version,
            "version_number",
            None,
        )

        if (
            previous_number is None
            or saved_number is None
        ):

            return False

        try:

            return int(
                saved_number
            ) > int(
                previous_number
            )

        except (
            TypeError,
            ValueError,
        ):

            return False

    # ==================================================
    # Update Existing Article Snapshot
    # ==================================================

    def _update_existing_article_snapshot(
        self,
        article_id,
        article,
    ):
        """
        更新既有 Article Current SQL Snapshot。

        只負責：

            articles

        Archive History：

            ArchiveService
        """

        if article_id is None:
            return False

        if article is None:
            return False

        if not hasattr(
            self.repo,
            "update_content_snapshot",
        ):

            logger.error(
                "ArticleRepository."
                "update_content_snapshot "
                "not implemented"
            )

            return False

        try:

            success = (
                self.repo.update_content_snapshot(
                    article_id=article_id,

                    document_id=self._get_value(
                        article,
                        "document_id",
                        "",
                    ),

                    content=self._get_value(
                        article,
                        "content",
                        "",
                    ),

                    crawl_time=self._get_value(
                        article,
                        "crawl_time",
                        None,
                    ),

                    status=self._get_value(
                        article,
                        "status",
                        "Success",
                    ),
                )
            )

            if not success:

                logger.error(
                    "Article SQL snapshot "
                    "update failed: "
                    f"article={article_id}"
                )

                return False

            # ==========================================
            # Existing Article Content Changed
            # ==========================================
            #
            # 新版本需要重新進入 AI Pipeline。
            #
            # ==========================================

            if hasattr(
                self.repo,
                "update_ai_status",
            ):

                self.repo.update_ai_status(
                    article_id,
                    "pending",
                )

            logger.info(
                "Article SQL snapshot updated: "
                f"article={article_id}"
            )

            return True

        except Exception as e:

            logger.exception(
                "Update existing article snapshot error: "
                f"{e}"
            )

            return False

    # ==================================================
    # Create AI Task
    # ==================================================

    def create_ai_task(
        self,
        article_id,
    ):
        """
        建立 AI Analysis Task。

        前提：

            Article 已經存在 SQL。

        Pipeline：

            articles
                ↓
            ai_tasks
                ↓
            WAITING
        """

        try:

            if article_id is None:

                logger.warning(
                    "Cannot create AI Task "
                    "without article_id"
                )

                return None

            task = AITask(
                article_id=article_id,
                task_type="analysis",
                status="WAITING",
                priority=0,
                retry_count=0,
            )

            result = self.task_repo.insert(
                task
            )

            if result is None:

                logger.warning(
                    "AI Task insert returned None: "
                    f"article={article_id}"
                )

                return None

            logger.info(
                "AI Task created: "
                f"article={article_id}, "
                "status=WAITING"
            )

            return result

        except Exception as e:

            logger.exception(
                "Create AI Task error: "
                f"{e}"
            )

            return None

    # ==================================================
    # Trigger AI Batch
    # ==================================================

    def _trigger_ai_batch(
        self,
    ):
        """
        通知 Batch Trigger 檢查 WAITING Tasks。

        不直接啟動：

            Scheduler
            Worker
            AI Analyzer
        """

        try:

            result = (
                self.batch_trigger
                .check_and_trigger()
            )

            logger.info(
                "AI Batch Trigger checked: "
                f"triggered={result}"
            )

            return result

        except Exception as e:

            logger.exception(
                "AI Batch Trigger error: "
                f"{e}"
            )

            return False

    # ==================================================
    # Persist Article
    # ==================================================

    def create(
        self,
        article,
        html=None,
    ):
        """
        儲存一篇已經完成 Parser 的 Article。

        注意：

            ArticleService 不再：

                Search
                Download
                Parse

        呼叫端必須提供：

            article
            html

        Pipeline：

            Article
                ↓
            ArticleRepository
                ↓
            SQL
                ↓
            ArchiveService
                ↓
            AI Task

        Args：

            article:
                已完成 Parser 的 Article Model

            html:
                原始 HTML

        Returns：

            dict
        """

        result = {
            "article": None,
            "article_id": None,
            "status": None,
            "archive_version": None,
            "ai_task": None,
        }

        # ==================================================
        # Validate Article
        # ==================================================

        if article is None:

            logger.error(
                "Article create failed: "
                "article is None"
            )

            result["status"] = "failed"

            return result

        # ==================================================
        # Validate HTML
        # ==================================================

        if html is None:

            logger.error(
                "Article create failed: "
                "html is None"
            )

            result["status"] = "failed"

            return result

        # ==================================================
        # Article Identity
        # ==================================================

        document_id = self._get_value(
            article,
            "document_id",
            None,
        )

        url = self._get_value(
            article,
            "url",
            None,
        )

        if not document_id:

            logger.error(
                "Article create failed: "
                "document_id is empty"
            )

            result["status"] = "failed"

            return result

        if not url:

            logger.error(
                "Article create failed: "
                "url is empty"
            )

            result["status"] = "failed"

            return result

        try:

            # ==================================================
            # STEP 1
            # Article Document Duplicate
            # ==================================================

            existing_document = (
                self._find_existing_article_by_document_id(
                    document_id
                )
            )

            if existing_document is not None:

                existing_id = self._get_article_id(
                    existing_document
                )

                logger.info(
                    "Article document duplicate: "
                    f"document_id={document_id}, "
                    f"article={existing_id}"
                )

                result["article"] = existing_document
                result["article_id"] = existing_id
                result["status"] = "duplicate"

                return result

            # ==================================================
            # STEP 2
            # Existing Article By URL
            # ==================================================

            existing_article = (
                self._find_existing_article_by_url(
                    url
                )
            )

            existing_article_id = (
                self._get_article_id(
                    existing_article
                )
            )

            # ==================================================
            # NEW ARTICLE
            # ==================================================

            if existing_article_id is None:

                logger.info(
                    "New Article: "
                    f"url={url}"
                )

                # ==========================================
                # SQL FIRST
                # ==========================================

                saved = self.repo.insert(
                    article
                )

                if saved is None:

                    logger.error(
                        "Article SQL insert failed: "
                        f"url={url}"
                    )

                    result["status"] = "failed"

                    return result

                saved_id = self._get_article_id(
                    saved
                )

                if saved_id is None:

                    logger.error(
                        "Article SQL insert succeeded "
                        "but ID is missing: "
                        f"url={url}"
                    )

                    result["status"] = "failed"

                    return result

                # ==========================================
                # ARCHIVE
                # ==========================================

                archive_version = (
                    self.archive_service.save_html(
                        article_id=saved_id,
                        document_id=document_id,
                        url=url,
                        html=html,
                    )
                )

                if archive_version is None:

                    logger.error(
                        "Archive failed after SQL "
                        f"persistence: article={saved_id}"
                    )

                    result["status"] = "archive_failed"
                    result["article"] = saved
                    result["article_id"] = saved_id

                    return result

                # ==========================================
                # AI TASK
                # ==========================================

                task = self.create_ai_task(
                    saved_id
                )

                if task is not None:

                    self._trigger_ai_batch()

                else:

                    logger.warning(
                        "AI Task creation failed: "
                        f"article={saved_id}"
                    )

                result["article"] = saved
                result["article_id"] = saved_id
                result["archive_version"] = (
                    archive_version
                )
                result["ai_task"] = task
                result["status"] = "created"

                logger.info(
                    "Article pipeline completed: "
                    "SQL -> Archive -> AI Task, "
                    f"article={saved_id}"
                )

                return result

            # ==================================================
            # EXISTING URL
            # ==================================================

            logger.info(
                "Existing Article URL detected: "
                f"article={existing_article_id}, "
                f"url={url}"
            )

            # ==========================================
            # Previous Archive Version
            # ==========================================

            previous_version = (
                self._get_latest_archive_version(
                    existing_article_id
                )
            )

            # ==========================================
            # Archive
            # ==========================================

            archive_version = (
                self.archive_service.save_html(
                    article_id=existing_article_id,
                    document_id=document_id,
                    url=url,
                    html=html,
                )
            )

            if archive_version is None:

                logger.error(
                    "Archive failed for existing "
                    f"article={existing_article_id}"
                )

                result["status"] = "archive_failed"
                result["article"] = existing_article
                result["article_id"] = existing_article_id

                return result

            # ==========================================
            # Determine New Version
            # ==========================================

            is_new_version = (
                self._is_new_archive_version(
                    previous_version,
                    archive_version,
                )
            )

            if not is_new_version:

                logger.info(
                    "Archive duplicate: "
                    f"article={existing_article_id}, "
                    f"url={url}"
                )

                result["article"] = existing_article
                result["article_id"] = existing_article_id
                result["archive_version"] = (
                    archive_version
                )
                result["status"] = "duplicate"

                return result

            # ==========================================
            # Update Current SQL Snapshot
            # ==========================================

            snapshot_updated = (
                self._update_existing_article_snapshot(
                    existing_article_id,
                    article,
                )
            )

            if not snapshot_updated:

                logger.error(
                    "Article SQL snapshot update failed: "
                    f"article={existing_article_id}"
                )

                result["status"] = "failed"
                result["article"] = existing_article
                result["article_id"] = existing_article_id
                result["archive_version"] = (
                    archive_version
                )

                return result

            # ==========================================
            # AI TASK
            # ==========================================

            task = self.create_ai_task(
                existing_article_id
            )

            if task is not None:

                self._trigger_ai_batch()

            else:

                logger.warning(
                    "AI Task creation failed: "
                    f"article={existing_article_id}"
                )

            result["article"] = article
            result["article_id"] = existing_article_id
            result["archive_version"] = (
                archive_version
            )
            result["ai_task"] = task
            result["status"] = "updated"

            logger.info(
                "Article pipeline completed: "
                "SQL -> Archive -> AI Task, "
                f"article={existing_article_id}"
            )

            return result

        except Exception as e:

            logger.exception(
                "Article persistence pipeline failed: "
                f"{e}"
            )

            result["status"] = "failed"

            return result

    # ==================================================
    # Query
    # ==================================================

    def get_all(
        self,
        limit=None,
    ):
        """
        取得 Article 列表。
        """

        try:

            return self.repo.find_all(
                limit
            )

        except Exception as e:

            logger.exception(
                "Get all articles error: "
                f"{e}"
            )

            return []

    # ==================================================

    def get_by_id(
        self,
        article_id,
    ):
        """
        依 ID 取得 Article。
        """

        try:

            return self.repo.find_by_id(
                article_id
            )

        except Exception as e:

            logger.exception(
                "Get article by id error: "
                f"{e}"
            )

            return None

    # ==================================================

    def get_by_keyword(
        self,
        keyword,
    ):
        """
        依 Keyword 取得 Article。
        """

        try:

            return self.repo.find_by_keyword(
                keyword
            )

        except Exception as e:

            logger.exception(
                "Get by keyword error: "
                f"{e}"
            )

            return []

    # ==================================================

    def get_by_source(
        self,
        source,
    ):
        """
        依 Source 取得 Article。
        """

        try:

            return self.repo.find_by_source(
                source
            )

        except Exception as e:

            logger.exception(
                "Get by source error: "
                f"{e}"
            )

            return []

    # ==================================================
    # AI Query
    # ==================================================

    def get_by_importance(
        self,
        level,
    ):
        """
        取得 AI Importance >= level。
        """

        try:

            return self.repo.find_by_importance(
                level
            )

        except Exception as e:

            logger.exception(
                "Get AI importance error: "
                f"{e}"
            )

            return []

    # ==================================================

    def get_by_category(
        self,
        category,
    ):
        """
        依 AI Category 搜尋。
        """

        try:

            return self.repo.find_by_category(
                category
            )

        except Exception as e:

            logger.exception(
                "Get AI category error: "
                f"{e}"
            )

            return []

    # ==================================================

    def get_by_ai_keyword(
        self,
        keyword,
    ):
        """
        依 AI Keyword 搜尋。
        """

        try:

            return self.repo.find_by_ai_keyword(
                keyword
            )

        except Exception as e:

            logger.exception(
                "Get AI keyword error: "
                f"{e}"
            )

            return []

    # ==================================================

    def get_ai_top(
        self,
        limit=10,
    ):
        """
        AI Importance Ranking。
        """

        try:

            if hasattr(
                self.repo,
                "get_top_ai_articles",
            ):

                return self.repo.get_top_ai_articles(
                    limit
                )

            articles = self.repo.find_all()

            def importance_value(
                item,
            ):

                value = self._get_value(
                    item,
                    "ai_importance",
                    0,
                )

                if value is None:
                    return 0

                try:
                    return float(
                        value
                    )

                except (
                    TypeError,
                    ValueError,
                ):
                    return 0

            articles.sort(
                key=importance_value,
                reverse=True,
            )

            return articles[:limit]

        except Exception as e:

            logger.exception(
                "Get AI top error: "
                f"{e}"
            )

            return []

    # ==================================================
    # Update Article
    # ==================================================

    def update_article(
        self,
        article_id,
        keyword=None,
        title=None,
        url=None,
        source=None,
        published=None,
        status=None,
    ):
        """
        更新 Article Metadata。

        不處理：

            Archive
            AI Analysis
            AI Task
        """

        try:

            existing = self.repo.find_by_id(
                article_id
            )

            if existing is None:

                logger.warning(
                    "Article update failed: "
                    f"id={article_id} not found"
                )

                return None

            if not hasattr(
                self.repo,
                "update",
            ):

                logger.error(
                    "ArticleRepository.update "
                    "not implemented"
                )

                return None

            success = self.repo.update(
                article_id=article_id,
                keyword=keyword,
                title=title,
                url=url,
                source=source,
                published=published,
                status=status,
            )

            if not success:
                return None

            return self.repo.find_by_id(
                article_id
            )

        except Exception as e:

            logger.exception(
                "Update article error: "
                f"{e}"
            )

            return None

    # ==================================================
    # Delete Article
    # ==================================================

    def delete_article(
        self,
        article_id,
    ):
        """
        刪除 Article。

        實際 Protection / Dependency
        由 Repository 處理。
        """

        try:

            existing = self.repo.find_by_id(
                article_id
            )

            if existing is None:

                logger.warning(
                    "Delete article failed: "
                    f"article={article_id} not found"
                )

                return False

            if not hasattr(
                self.repo,
                "delete",
            ):

                logger.error(
                    "ArticleRepository.delete "
                    "not implemented"
                )

                return False

            return bool(
                self.repo.delete(
                    article_id
                )
            )

        except Exception as e:

            logger.exception(
                "Delete article error: "
                f"{e}"
            )

            return False

    # ==================================================
    # Count
    # ==================================================

    def count(
        self,
    ):
        """
        Article Count。
        """

        try:

            return self.repo.count()

        except Exception as e:

            logger.exception(
                "Article count error: "
                f"{e}"
            )

            return 0

    # ==================================================
    # Close
    # ==================================================

    def close(
        self,
    ):
        """
        關閉 Repository Database Connection。
        """

        try:

            self.repo.close()

        except Exception as e:

            logger.exception(
                "Article service close error: "
                f"{e}"
            )


# ======================================
#
# Public API
#
# ======================================

__all__ = [
    "ArticleService",
]