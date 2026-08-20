# services/article_service.py
"""
services/article_service.py

AutoSearch V4

P2.4.2 / P3.2 / P4 Compatibility

Article Service

功能:

- Article Collection
- Article Create
- Raw HTML Archive
- Archive Version History
- Article Document Duplicate Detection
- AI Task Creation
- AI Task Batch Trigger
- Article Query
- Article Management

Pipeline:

Keyword
    ↓
Search Adapter
    ↓
Download
    ↓
Raw HTML
    ↓
Parser
    ↓
Article Document Detection
    ↓
Database Duplicate Detection
    ↓
ArticleRepository
    ↓
articles
    ↓
ArchiveService
    ├── MongoDB raw_html
    ├── URL + HTML Hash Duplicate Detection
    ├── MySQL raw_documents
    └── MySQL archive_versions
    ↓
AITaskRepository
    ↓
ai_tasks WAITING
    ↓
AIBatchTriggerService
    ↓
WAITING >= configurable threshold
    ↓
AIScheduler
    ↓
AIWorker
    ↓
Async AI Analysis


Important:

Article 必須先進入 SQL。

AI Analysis 是非同步流程。

因此:

    Article
        ↓
    SQL
        ↓
    ArchiveService
        ↓
    MongoDB Raw HTML
        ↓
    MySQL Archive Metadata
        ↓
    AI Task
        ↓
    AI Worker
        ↓
    AI Analysis


HTML Storage Policy:

原始 HTML 本體:

    MongoDB
        ↓
    raw_html

MySQL:

    raw_documents
    archive_versions

只保存：

    MongoDB Reference
    URL
    Content Hash
    File Size
    MIME Type
    Version Information

不再使用:

    archive/html


Hash Responsibility:

Article document_id
    ↓
generate_hash(title, parsed_content)
    ↓
Article Document Duplicate Detection

Archive HTML
    ↓
ArchiveService
    ↓
generate_content_hash(raw_html)
    ↓
URL + HTML Hash
    ↓
Archive Version Duplicate Detection


Important:

document_id 與 archive file_hash 是兩個不同用途的 Hash。

document_id:
    - Article 文件識別
    - Document duplicate detection
    - 儲存於 articles.document_id
    - 傳遞給 ArchiveService
    - 用於 MongoDB Raw HTML Document Identity
    - 不負責 Archive History

file_hash:
    - 原始 HTML 內容識別
    - Archive Version History
    - Archive Duplicate Detection


Hash Policy:

所有 SHA256 Hash 都集中於:

    utils/hash.py

ArticleService 不自行實作 SHA256。


ArticleService Responsibility:

- Article Collection
- Article Document Duplicate Detection
- Article SQL Persistence
- ArchiveService 呼叫
- AI Task Creation
- AI Batch Trigger
- Article Query
- Article Management


ArticleService 不負責:

- Archive Duplicate Detection
- Archive Hash Calculation
- AI Analysis
- AI Worker
- AI Scheduler
- Knowledge Processing
- Parser Registration
- Parser Selection
- RSS Normalization
- Source Adapter
"""

from config.settings import (
    MAX_RESULTS,
    HEADERS,
)


from database.article_repository import (
    ArticleRepository,
)


from database.ai_task_repository import (
    AITaskRepository,
)


from models.ai_task import (
    AITask,
)


# ======================================
# Search
#
# P4 Search Adapter Compatibility
# ======================================

from search.search_adapter import (
    search,
)


from crawler.crawler import (
    download,
)


from parser.parser import (
    parse,
)


# ======================================
# Article Document Hash
# ======================================

from utils.hash import (
    generate_hash,
)


from utils.logger import (
    logger,
)


# ======================================
# Archive
# ======================================

from services.archive_service import (
    ArchiveService,
)


from archive.archive_integration import (
    ArchiveIntegration,
)


# ======================================
# AI Batch Trigger
#
# P2.4.2
# ======================================

from services.ai_batch_trigger_service import (
    AIBatchTriggerService,
)


class ArticleService:
    """
    Article Service

    P2.4.2 + P3.2 + P4 Compatibility

    核心原則:

        Article 資料先進 SQL。

        原始 HTML 由 ArchiveService
        儲存到 MongoDB。

        AI Analysis 後續非同步處理。

    Pipeline:

        Search
            ↓
        Download
            ↓
        Raw HTML
            ↓
        Parse
            ↓
        Article
            ↓
        Article SQL
            ↓
        ArchiveService
            ↓
        MongoDB Raw HTML
            ↓
        MySQL Archive Metadata
            ↓
        AI Task WAITING
            ↓
        Batch Trigger
            ↓
        Scheduler / Worker
            ↓
        AI Analysis

    負責:

        Article Collection
        Article Document Detection
        Article SQL Persistence
        Archive Integration
        AI Task Creation
        AI Batch Trigger
        Article Query
        Article Management
    """

    # ==================================================
    #
    # Initialize
    #
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

        Dependency Injection:

        - ArticleRepository
        - AITaskRepository
        - ArchiveService
        - ArchiveIntegration
        - AIBatchTriggerService
        """

        if repo is None:
            repo = ArticleRepository()

        self.repo = repo

        if task_repo is None:
            task_repo = AITaskRepository()

        self.task_repo = task_repo

        if archive_service is None:
            archive_service = ArchiveService()

        self.archive_service = archive_service

        if archive_integration is None:
            archive_integration = ArchiveIntegration(
                archive_repository=(
                    self.archive_service.version_repo
                )
            )

        self.archive_integration = archive_integration

        if batch_trigger is None:
            batch_trigger = AIBatchTriggerService(
                task_repository=self.task_repo
            )

        self.batch_trigger = batch_trigger

    # ==================================================
    #
    # Find Existing Article By URL
    #
    # ==================================================

    def _find_existing_article_by_url(
        self,
        url,
    ):
        """
        依 URL 找出既有 Article。

        此方法只負責 Article Entity Lookup。

        不負責 Archive Duplicate Detection。
        """

        try:

            if not url:
                return None

            url = str(url).strip()

            if not url:
                return None

            if hasattr(
                self.repo,
                "find_by_url",
            ):
                return self.repo.find_by_url(url)

            if hasattr(
                self.repo,
                "find_all",
            ):

                articles = self.repo.find_all()

                for item in articles:

                    item_url = self._get_value(
                        item,
                        "url",
                        None,
                    )

                    if item_url is None:
                        continue

                    if str(
                        item_url
                    ).strip() == url:

                        return item

        except Exception as e:

            logger.exception(
                "Find existing article error: "
                f"{e}"
            )

        return None

    # ==================================================
    #
    # Find Existing Article By Document ID
    #
    # ==================================================

    def _find_existing_article_by_document_id(
        self,
        document_id,
    ):
        """
        依 document_id 查詢既有 Article。

        document_id 只負責:

            Article Document Duplicate Detection

        不參與:

            Archive Version Duplicate Detection
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

            if hasattr(
                self.repo,
                "get_by_document_id",
            ):
                return self.repo.get_by_document_id(
                    document_id
                )

            if hasattr(
                self.repo,
                "find_all",
            ):

                articles = self.repo.find_all()

                for item in articles:

                    existing_document_id = (
                        self._get_value(
                            item,
                            "document_id",
                            None,
                        )
                    )

                    if existing_document_id is None:
                        continue

                    if str(
                        existing_document_id
                    ).strip() == document_id:

                        return item

        except Exception as e:

            logger.exception(
                "Find existing article by document_id "
                "error: "
                f"{e}"
            )

        return None

    # ==================================================
    #
    # Get Article ID
    #
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
    #
    # Get Object / Dict Value
    #
    # ==================================================

    @staticmethod
    def _get_value(
        obj,
        key,
        default=None,
    ):
        """
        同時支援:

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
    #
    # Generate Article Document Hash
    #
    # ==================================================

    @staticmethod
    def _get_document_hash(
        title,
        content,
    ):
        """
        產生 Article Document Hash。

        用途:

            Article Document Duplicate Detection

        Hash Source:

            title + parsed content
        """

        return generate_hash(
            title,
            content,
        )

    # ==================================================
    #
    # Get Latest Archive Version
    #
    # ==================================================

    def _get_latest_archive_version(
        self,
        article_id,
    ):
        """
        取得指定 Article 最新 Archive Version。

        此方法只用於 Version History
        與 Version Information。

        不負責 Archive Duplicate Detection。
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
    #
    # Determine Archive Version Created
    #
    # ==================================================

    def _is_new_archive_version(
        self,
        previous_version,
        saved_version,
    ):
        """
        判斷 ArchiveService.save_html()
        是否真的建立新的 Archive Version。
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

            logger.warning(
                "Unable to determine archive version "
                "creation status: "
                f"previous={previous_number}, "
                f"saved={saved_number}"
            )

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
    #
    # Persist Existing Article Snapshot
    #
    # ==================================================

    def _update_existing_article_snapshot(
        self,
        article_id,
        article,
    ):
        """
        更新既有 Article 的目前 SQL Snapshot。

        Archive History:

            ArchiveService

        Article Current Snapshot:

            ArticleRepository
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
                "ArticleRepository.update_content_snapshot "
                "not implemented"
            )

            return False

        try:

            success = (
                self.repo.update_content_snapshot(
                    article_id=article_id,
                    document_id=getattr(
                        article,
                        "document_id",
                        "",
                    ),
                    content=getattr(
                        article,
                        "content",
                        "",
                    ),
                    crawl_time=getattr(
                        article,
                        "crawl_time",
                        None,
                    ),
                    status=getattr(
                        article,
                        "status",
                        "Success",
                    ),
                )
            )

            if not success:

                logger.error(
                    "Article SQL snapshot update failed: "
                    f"article={article_id}"
                )

                return False

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
                f"article={article_id}, "
                f"document_id="
                f"{getattr(article, 'document_id', '')}"
            )

            return True

        except Exception as e:

            logger.exception(
                "Update existing article snapshot error: "
                f"{e}"
            )

            return False

    # ==================================================
    #
    # Trigger AI Batch
    #
    # ==================================================

    def _trigger_ai_batch(
        self,
    ):
        """
        檢查 WAITING AI Task 數量。

        注意:

            這裡只負責通知 Batch Trigger。

            不直接啟動:

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
    #
    # Search Results
    #
    # P4 Compatibility Boundary
    #
    # ==================================================

    @staticmethod
    def _search(
        keyword,
    ):
        """
        ArticleService Search Boundary。

        ArticleService 不管理 Source Adapter。

        Search Adapter 負責:

            Source Registry
            Source Adapter
            Google News
            Website Search
            RSS
            Search Result Deduplication
            Per-Source Result Limit
        """

        return search(
            keyword
        )

    # ==================================================
    #
    # Create AI Task
    #
    # ==================================================

    def create_ai_task(
        self,
        article_id,
    ):
        """
        建立 AI Analysis Task。

        Article 必須已經存在 SQL。

        流程:

            articles
                ↓
            ai_tasks
                ↓
            WAITING
                ↓
            Batch Trigger
        """

        try:

            if article_id is None:

                logger.warning(
                    "Cannot create AI Task without "
                    "article_id"
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
    #
    # Collect Articles
    #
    # ==================================================

    def create(
        self,
        keyword,
    ):
        """
        搜尋並建立 Articles。

        Pipeline:

            Keyword
                ↓
            Search Adapter
                ↓
            Download
                ↓
            Raw HTML
                ↓
            Parser
                ↓
            document_id
                ↓
            Article Duplicate Detection
                ↓
            ArticleRepository
                ↓
            articles
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
            AIScheduler / AIWorker

        核心原則:

            Article SQL persistence
                不依賴
            Archive

            Archive HTML
                優先使用
            Article.document_id

            Raw HTML 本體
                只儲存於 MongoDB

            Archive failure
                不刪除
            Article SQL

            AI Worker
                不在此 Service 中直接執行
        """

        articles = []

        total = 0
        new = 0
        duplicate = 0
        failed = 0

        try:

            if keyword is None:

                logger.warning(
                    "Article create skipped: "
                    "keyword is None"
                )

                return {
                    "articles": [],
                    "total": 0,
                    "new": 0,
                    "duplicate": 0,
                    "failed": 0,
                }

            keyword = str(
                keyword
            ).strip()

            if not keyword:

                logger.warning(
                    "Article create skipped: "
                    "keyword is empty"
                )

                return {
                    "articles": [],
                    "total": 0,
                    "new": 0,
                    "duplicate": 0,
                    "failed": 0,
                }

            # ==================================
            #
            # P4
            # Search Adapter
            #
            # ==================================

            results = self._search(
                keyword
            )

            if results is None:
                results = []

            try:

                max_results = int(
                    MAX_RESULTS
                )

            except (
                TypeError,
                ValueError,
            ):

                max_results = None

            if (
                max_results is not None
                and max_results > 0
            ):

                results = results[
                    :max_results
                ]

            total = len(
                results
            )

            # ==================================
            #
            # Process Search Results
            #
            # ==================================

            for item in results:

                try:

                    item_url = self._get_value(
                        item,
                        "url",
                        "",
                    )

                    item_title = self._get_value(
                        item,
                        "title",
                        "",
                    )

                    item_source = self._get_value(
                        item,
                        "source",
                        "",
                    )

                    item_published = (
                        self._get_value(
                            item,
                            "published",
                            None,
                        )
                    )

                    logger.info(
                        f"Processing {item_title}"
                    )

                    # ==================================
                    #
                    # Validate URL
                    #
                    # ==================================

                    if not item_url:

                        failed += 1

                        logger.warning(
                            "Search result URL is empty"
                        )

                        continue

                    # ==================================
                    #
                    # Download
                    #
                    # ==================================

                    html = download(
                        item_url,
                        HEADERS,
                    )

                    if html is None:

                        failed += 1

                        logger.warning(
                            "Download failed: "
                            f"{item_url}"
                        )

                        continue

                    logger.info(
                        "Raw HTML downloaded: "
                        f"url={item_url}, "
                        f"size={len(html.encode('utf-8')) if isinstance(html, str) else len(html)}"
                    )

                    # ==================================
                    #
                    # Parse
                    #
                    # ==================================

                    article = parse(
                        html,
                        keyword,
                    )

                    if article is None:

                        failed += 1

                        logger.warning(
                            "Parse failed: "
                            f"{item_url}"
                        )

                        continue

                    # ==================================
                    #
                    # Article Metadata
                    #
                    # ==================================

                    article.keyword = keyword
                    article.title = item_title
                    article.url = item_url
                    article.source = item_source
                    article.published = item_published
                    article.status = "Success"

                    # ==================================
                    #
                    # Article Document Hash
                    #
                    # ==================================

                    article.document_id = (
                        self._get_document_hash(
                            article.title,
                            article.content,
                        )
                    )

                    # ==================================================
                    #
                    # STEP 1
                    #
                    # Article Document Duplicate Detection
                    #
                    # ==================================================

                    existing_document = (
                        self
                        ._find_existing_article_by_document_id(
                            article.document_id
                        )
                    )

                    if existing_document is not None:

                        existing_document_id = (
                            self._get_article_id(
                                existing_document
                            )
                        )

                        duplicate += 1

                        logger.info(
                            "Duplicate article document: "
                            f"document_id="
                            f"{article.document_id}, "
                            f"existing_article="
                            f"{existing_document_id}, "
                            f"url={item_url}"
                        )

                        continue

                    # ==================================================
                    #
                    # STEP 2
                    #
                    # Existing Article By URL
                    #
                    # ==================================================

                    existing_article = (
                        self
                        ._find_existing_article_by_url(
                            item_url
                        )
                    )

                    existing_article_id = (
                        self._get_article_id(
                            existing_article
                        )
                    )

                    # ==================================================
                    #
                    # NEW ARTICLE
                    #
                    # ==================================================

                    if existing_article_id is None:

                        logger.info(
                            "New article detected: "
                            f"url={item_url}"
                        )

                        # ==========================================
                        #
                        # 1. SQL FIRST
                        #
                        # ==========================================

                        saved = self.repo.insert(
                            article
                        )

                        if saved is None:

                            failed += 1

                            logger.error(
                                "Failed to save article to SQL: "
                                f"url={item_url}"
                            )

                            continue

                        saved_id = self._get_article_id(
                            saved
                        )

                        if saved_id is None:

                            failed += 1

                            logger.error(
                                "Article SQL insert succeeded "
                                "but article ID is missing: "
                                f"url={item_url}"
                            )

                            continue

                        # ------------------------------------------
                        #
                        # Use persisted Article document_id
                        #
                        # 正式 Archive Identity
                        #
                        # ------------------------------------------

                        saved_document_id = (
                            self._get_value(
                                saved,
                                "document_id",
                                None,
                            )
                        )

                        if not saved_document_id:

                            saved_document_id = (
                                getattr(
                                    article,
                                    "document_id",
                                    None,
                                )
                            )

                        logger.info(
                            "Article persisted to SQL: "
                            f"article={saved_id}, "
                            f"document_id="
                            f"{saved_document_id}, "
                            f"url={item_url}"
                        )

                        articles.append(
                            saved
                        )

                        new += 1

                        # ==========================================
                        #
                        # 2. ARCHIVE
                        #
                        # ==========================================
                        #
                        # IMPORTANT:
                        #
                        # raw HTML:
                        #
                        #     html
                        #
                        # document identity:
                        #
                        #     saved_document_id
                        #
                        # ArchiveService:
                        #
                        #     MongoDB raw_html
                        #         +
                        #     MySQL raw_documents
                        #         +
                        #     MySQL archive_versions
                        #
                        # ==========================================

                        previous_version = (
                            self
                            ._get_latest_archive_version(
                                saved_id
                            )
                        )

                        archive_version = (
                            self.archive_service.save_html(
                                article_id=saved_id,
                                document_id=saved_document_id,
                                url=item_url,
                                html=html,
                            )
                        )

                        if archive_version is None:

                            logger.error(
                                "Archive failed after "
                                "Article SQL persistence: "
                                f"article={saved_id}, "
                                f"url={item_url}"
                            )

                            # ======================================
                            #
                            # IMPORTANT
                            #
                            # Article remains in SQL.
                            #
                            # Archive failure does NOT remove
                            # the Article.
                            #
                            # ======================================

                        else:

                            is_new_version = (
                                self._is_new_archive_version(
                                    previous_version,
                                    archive_version,
                                )
                            )

                            archive_version_number = (
                                self._get_value(
                                    archive_version,
                                    "version_number",
                                    None,
                                )
                            )

                            archive_file_hash = (
                                self._get_value(
                                    archive_version,
                                    "file_hash",
                                    None,
                                )
                            )

                            if is_new_version:

                                logger.info(
                                    "Archive completed: "
                                    f"article={saved_id}, "
                                    f"document_id="
                                    f"{saved_document_id}, "
                                    f"version="
                                    f"{archive_version_number}, "
                                    f"file_hash="
                                    f"{archive_file_hash}, "
                                    "storage=mongodb/raw_html"
                                )

                            else:

                                logger.warning(
                                    "Archive returned no new "
                                    "version for new Article: "
                                    f"article={saved_id}, "
                                    f"version="
                                    f"{archive_version_number}"
                                )

                        # ==========================================
                        #
                        # 3. AI TASK
                        #
                        # IMPORTANT:
                        #
                        # Article SQL already exists.
                        #
                        # AI Task creation must not depend on
                        # Archive success.
                        #
                        # ==========================================

                        task = self.create_ai_task(
                            saved_id
                        )

                        if task is None:

                            logger.warning(
                                "AI Task creation failed: "
                                f"article={saved_id}"
                            )

                        else:

                            self._trigger_ai_batch()

                        continue

                    # ==================================================
                    #
                    # EXISTING URL
                    #
                    # document_id 不同
                    #
                    # = Changed Article Content
                    #
                    # ==================================================

                    logger.info(
                        "Existing URL with changed "
                        "Article document detected: "
                        f"article={existing_article_id}, "
                        f"url={item_url}"
                    )

                    # ==========================================
                    #
                    # Existing Article Document ID
                    #
                    # ==========================================

                    existing_document_id = (
                        self._get_value(
                            existing_article,
                            "document_id",
                            None,
                        )
                    )

                    # ==========================================
                    #
                    # Previous Archive Version
                    #
                    # ==========================================

                    previous_version = (
                        self
                        ._get_latest_archive_version(
                            existing_article_id
                        )
                    )

                    previous_version_number = (
                        self._get_value(
                            previous_version,
                            "version_number",
                            None,
                        )
                    )

                    # ==========================================
                    #
                    # ArchiveService
                    #
                    # Archive Duplicate Authority
                    #
                    # IMPORTANT:
                    #
                    # MongoDB Raw HTML identity:
                    #
                    #     document_id
                    #
                    # Duplicate Detection:
                    #
                    #     URL + HTML Hash
                    #
                    # document_id 不參與
                    # Archive Duplicate Detection。
                    #
                    # ==========================================

                    archive_version = (
                        self.archive_service.save_html(
                            article_id=existing_article_id,
                            document_id=article.document_id,
                            url=item_url,
                            html=html,
                        )
                    )

                    if archive_version is None:

                        failed += 1

                        logger.error(
                            "Archive failed for "
                            f"existing article="
                            f"{existing_article_id}"
                        )

                        continue

                    archive_version_number = (
                        self._get_value(
                            archive_version,
                            "version_number",
                            None,
                        )
                    )

                    archive_file_hash = (
                        self._get_value(
                            archive_version,
                            "file_hash",
                            None,
                        )
                    )

                    is_new_version = (
                        self._is_new_archive_version(
                            previous_version,
                            archive_version,
                        )
                    )

                    # ==========================================
                    #
                    # Same URL + Same HTML
                    #
                    # ==========================================

                    if not is_new_version:

                        duplicate += 1

                        logger.info(
                            "Archive duplicate: "
                            f"article="
                            f"{existing_article_id}, "
                            f"version="
                            f"{archive_version_number}, "
                            f"previous_version="
                            f"{previous_version_number}, "
                            f"url={item_url}"
                        )

                        continue

                    # ==========================================
                    #
                    # New Archive Version
                    #
                    # Update current Article SQL Snapshot
                    #
                    # ==========================================

                    snapshot_updated = (
                        self._update_existing_article_snapshot(
                            existing_article_id,
                            article,
                        )
                    )

                    if not snapshot_updated:

                        failed += 1

                        logger.error(
                            "Article SQL snapshot update failed "
                            "after new Archive Version: "
                            f"article="
                            f"{existing_article_id}, "
                            f"url={item_url}"
                        )

                        continue

                    logger.info(
                        "New archive version created and "
                        "Article SQL snapshot updated: "
                        f"article="
                        f"{existing_article_id}, "
                        f"previous_version="
                        f"{previous_version_number}, "
                        f"new_version="
                        f"{archive_version_number}, "
                        f"file_hash="
                        f"{archive_file_hash}, "
                        f"document_id="
                        f"{article.document_id}, "
                        "storage=mongodb/raw_html"
                    )

                    # ==========================================
                    #
                    # AI Task
                    #
                    # New SQL Snapshot
                    #     ↓
                    # AI WAITING
                    #
                    # ==========================================

                    task = self.create_ai_task(
                        existing_article_id
                    )

                    if task is None:

                        logger.warning(
                            "AI Task creation failed: "
                            f"article="
                            f"{existing_article_id}"
                        )

                    else:

                        self._trigger_ai_batch()

                    articles.append(
                        article
                    )

                    new += 1

                except Exception as e:

                    failed += 1

                    logger.exception(
                        "Article processing error: "
                        f"{e}"
                    )

            return {
                "articles": articles,
                "total": total,
                "new": new,
                "duplicate": duplicate,
                "failed": failed,
            }

        except Exception as e:

            logger.exception(
                "Article create error: "
                f"{e}"
            )

            return {
                "articles": [],
                "total": total,
                "new": new,
                "duplicate": duplicate,
                "failed": failed,
            }

    # ==================================================
    #
    # P3.2
    # Article Query
    #
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
    #
    # P3.2
    # AI Query
    #
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
    #
    # P3.2
    # Update Article
    #
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

        不負責:

            AI Analysis
            Archive Version
            AI Task
            Batch Trigger
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

            result = self.repo.update(
                article_id=article_id,
                keyword=keyword,
                title=title,
                url=url,
                source=source,
                published=published,
                status=status,
            )

            if not result:

                logger.warning(
                    "Article update failed: "
                    f"id={article_id}"
                )

                return None

            logger.info(
                "Article updated successfully: "
                f"id={article_id}"
            )

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
    #
    # P3.2
    # Delete Article
    #
    # ==================================================

    def delete_article(
        self,
        article_id,
    ):
        """
        刪除 Article。

        Repository 負責:

            Article existence
            Archive Protection
            Raw Document Protection
            AI Task Protection
            Knowledge Archive Protection
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

            success = self.repo.delete(
                article_id
            )

            if not success:

                logger.warning(
                    "Article delete blocked or failed: "
                    f"article={article_id}"
                )

                return False

            logger.info(
                "Article deleted: "
                f"article={article_id}"
            )

            return True

        except Exception as e:

            logger.exception(
                "Delete article error: "
                f"{e}"
            )

            return False

    # ==================================================
    #
    # P3.2
    # Count
    #
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
    #
    # Close
    #
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
