"""
services/article_service.py

AutoSearch V4

P2.3 Run Flow Archive History Integration

功能:

- Article Collection
- Article Create
- Raw HTML Archive
- Archive Version History
- History Detection
- Article Query
- AI Task Trigger

Pipeline:

Keyword
↓
Search
↓
Download
↓
Parser
↓
Article History Detection
↓
ArticleRepository
↓
articles
↓
ArchiveIntegration
↓
ArchiveService
├── raw_documents
└── archive_versions
↓
AITaskRepository
↓
ai_tasks WAITING

Archive History:

New URL
↓
Article
↓
Version 1

Same URL + Same HTML
↓
Existing Article
↓
No New Version

Same URL + Changed HTML
↓
Existing Article
↓
Version 2
↓
Version 3
↓
...
"""

import hashlib

from config.settings import (
    MAX_RESULTS,
    HEADERS
)

from database.article_repository import (
    ArticleRepository
)

from database.ai_task_repository import (
    AITaskRepository
)

from models.ai_task import (
    AITask
)

from search.search_engine import (
    search
)

from crawler.crawler import (
    download
)

from parser.parser import (
    parse
)

from utils.hash import (
    generate_hash
)

from utils.duplicate import (
    is_duplicate,
    save_document
)

from utils.logger import logger

# ======================================
#
# Archive
#
# ======================================

from services.archive_service import (
    ArchiveService
)

from archive.archive_integration import (
    ArchiveIntegration
)


class ArticleService:

    # ==================================
    # Initialize
    # ==================================

    def __init__(self):

        # ==================================
        # Repository
        # ==================================

        self.repo = ArticleRepository()

        self.task_repo = AITaskRepository()

        # ==================================
        # Archive Service
        #
        # 負責：
        #
        # 1. HTML Snapshot
        # 2. RawDocument
        # 3. ArchiveVersion
        # 4. Version Number
        # ==================================

        self.archive_service = (
            ArchiveService()
        )

        # ==================================
        # Archive Integration
        #
        # P2.3
        #
        # 負責：
        #
        # 1. History Detection
        # 2. Timeline
        # 3. Version Query
        # 4. Diff
        # 5. Knowledge History
        #
        # 注意：
        #
        # archive_versions 目前由
        # ArchiveVersionRepository 管理。
        # ==================================

        self.archive_integration = (
            ArchiveIntegration(
                archive_repository=(
                    self.archive_service.version_repo
                )
            )
        )

    # ==================================================
    #
    # Find Existing Article By URL
    #
    # ==================================================

    def _find_existing_article_by_url(
        self,
        url
    ):
        """
        依 URL 找出既有 Article。

        優先使用 Repository 的：

            find_by_url()

        若目前 Repository 尚未提供，
        則 fallback 到 find_all()。

        Returns
        -------

        Article / dict / None
        """

        try:

            # ==================================
            # Preferred Repository API
            # ==================================

            if hasattr(
                self.repo,
                "find_by_url"
            ):

                return self.repo.find_by_url(
                    url
                )

            # ==================================
            # Fallback
            # ==================================

            if hasattr(
                self.repo,
                "find_all"
            ):

                articles = (
                    self.repo.find_all()
                )

                for item in articles:

                    if isinstance(
                        item,
                        dict
                    ):

                        item_url = item.get(
                            "url"
                        )

                    else:

                        item_url = getattr(
                            item,
                            "url",
                            None
                        )

                    if item_url == url:

                        return item

        except Exception as e:

            logger.exception(
                f"Find existing article error: {e}"
            )

        return None

    # ==================================================
    #
    # Get Article ID
    #
    # ==================================================

    @staticmethod
    def _get_article_id(
        article
    ):
        """
        從 Article object / dict 取得 ID。
        """

        if article is None:

            return None

        if isinstance(
            article,
            dict
        ):

            return article.get(
                "id"
            )

        return getattr(
            article,
            "id",
            None
        )

    # ==================================================
    #
    # Generate Archive File Hash
    #
    # ==================================================

    @staticmethod
    def _get_html_hash(
        html
    ):
        """
        計算與 ArchiveService 完全一致的
        HTML File Hash。

        ArchiveService.save_html():

            open(..., "w", encoding="utf-8")
            f.write(html)

        因此實際落盤內容為：

            html.encode("utf-8")

        這裡直接使用相同方式計算 SHA256。

        用途：

            Run Flow History Detection
        """

        if html is None:

            html = ""

        if not isinstance(
            html,
            str
        ):

            html = str(html)

        return hashlib.sha256(
            html.encode("utf-8")
        ).hexdigest()

    # ==================================================
    #
    # Get Latest Archive Version
    #
    # ==================================================

    def _get_latest_archive_version(
        self,
        article_id
    ):
        """
        透過 ArchiveIntegration 取得最新
        Archive Version。

        ArchiveIntegration 的 Repository
        使用 ArchiveVersionRepository。
        """

        try:

            repository = (
                self.archive_integration
                ._get_archive_repository()
            )

            if repository is None:

                return None

            # ==================================
            # ArchiveVersionRepository API
            # ==================================

            if hasattr(
                repository,
                "get_latest_version"
            ):

                return repository.get_latest_version(
                    article_id
                )

            # ==================================
            # Compatibility
            # ==================================

            if hasattr(
                repository,
                "get_latest"
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
    # Check Archive History
    #
    # ==================================================

    def _check_archive_history(
        self,
        article_id,
        html
    ):
        """
        判斷 Article 是否需要建立新的
        Archive Version。

        使用：

            HTML SHA256
            ↓
            latest archive_versions.file_hash
            ↓
            比較

        Returns
        -------

        dict

        {
            "exists": True / False,
            "changed": True / False,
            "latest_version": ...,
            "latest_version_number": ...,
            "file_hash": ...
        }
        """

        # ==================================
        # Calculate Current HTML Hash
        # ==================================

        file_hash = (
            self._get_html_hash(
                html
            )
        )

        # ==================================
        # Get Latest Version
        #
        # 透過 ArchiveIntegration
        # ==================================

        latest = (
            self._get_latest_archive_version(
                article_id
            )
        )

        # ==================================
        # No History
        # ==================================

        if latest is None:

            return {

                "exists": False,

                "changed": True,

                "latest_version": None,

                "latest_version_number": None,

                "file_hash": file_hash

            }

        # ==================================
        # Existing History
        # ==================================

        old_hash = getattr(
            latest,
            "file_hash",
            None
        )

        changed = (
            old_hash != file_hash
        )

        latest_version_number = getattr(
            latest,
            "version_number",
            None
        )

        return {

            "exists": True,

            "changed": changed,

            "latest_version": latest,

            "latest_version_number": (
                latest_version_number
            ),

            "file_hash": file_hash

        }

    # ==================================================
    #
    # Collect Articles
    #
    # ==================================================

    def create(
        self,
        keyword
    ):

        articles = []

        total = 0
        new = 0
        duplicate = 0
        failed = 0

        try:

            # ==================================
            # Search
            # ==================================

            results = search(
                keyword,
                MAX_RESULTS
            )

            total = len(results)

            # ==================================
            # Process Results
            # ==================================

            for item in results:

                try:

                    logger.info(
                        f"Processing {item.title}"
                    )

                    # ==================================
                    # Download
                    # ==================================

                    html = download(
                        item.url,
                        HEADERS
                    )

                    if html is None:

                        failed += 1

                        logger.warning(
                            f"Download failed: {item.url}"
                        )

                        continue

                    # ==================================
                    # Parser
                    # ==================================

                    article = parse(
                        html,
                        keyword
                    )

                    if article is None:

                        failed += 1

                        logger.warning(
                            f"Parse failed: {item.url}"
                        )

                        continue

                    # ==================================
                    # Article Metadata
                    # ==================================

                    article.keyword = keyword

                    article.title = item.title

                    article.url = item.url

                    article.source = item.source

                    article.published = item.published

                    article.status = "Success"

                    # ==================================
                    # Document ID
                    # ==================================

                    article.document_id = (
                        generate_hash(
                            article.title,
                            article.content
                        )
                    )

                    # ==================================
                    #
                    # Find Existing Article By URL
                    #
                    # History Detection 必須優先於
                    # Document Duplicate Detection。
                    #
                    # 原因：
                    #
                    # 同 URL + Changed Content
                    # document_id 一定會不同。
                    #
                    # ==================================

                    existing_article = (
                        self._find_existing_article_by_url(
                            item.url
                        )
                    )

                    existing_article_id = (
                        self._get_article_id(
                            existing_article
                        )
                    )

                    # ==================================
                    #
                    # Existing Article
                    #
                    # ==================================

                    if existing_article_id is not None:

                        logger.info(
                            "Existing article found: "
                            f"article={existing_article_id}, "
                            f"url={item.url}"
                        )

                        # ==================================
                        # History Detection
                        # ==================================

                        history_result = (
                            self._check_archive_history(
                                existing_article_id,
                                html
                            )
                        )

                        # ==================================
                        #
                        # Same Content
                        #
                        # ==================================

                        if not history_result[
                            "changed"
                        ]:

                            duplicate += 1

                            logger.info(
                                "Archive unchanged: "
                                f"article="
                                f"{existing_article_id}, "
                                f"version="
                                f"{history_result['latest_version_number']}, "
                                f"url={item.url}"
                            )

                            # 不建立：
                            #
                            # Article
                            # Version
                            # AI Task
                            #
                            continue

                        # ==================================
                        #
                        # Content Changed
                        #
                        # ==================================

                        logger.info(
                            "Archive content changed: "
                            f"article="
                            f"{existing_article_id}, "
                            f"old_version="
                            f"{history_result['latest_version_number']}"
                        )

                        # ==================================
                        #
                        # Save New Document Hash
                        #
                        # Changed content 是新的 Document
                        #
                        # ==================================

                        if not is_duplicate(
                            article.document_id
                        ):

                            save_document(
                                article.document_id
                            )

                        # ==================================
                        #
                        # Save New Archive Version
                        #
                        # 使用原 Article ID
                        #
                        # ArchiveService 會：
                        #
                        # 1. 儲存 HTML
                        # 2. 建立 RawDocument
                        # 3. 取得 Next Version Number
                        # 4. 建立 ArchiveVersion
                        #
                        # ==================================

                        archive_version = (
                            self.archive_service.save_html(

                                article_id=(
                                    existing_article_id
                                ),

                                url=item.url,

                                html=html

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

                        # ==================================
                        #
                        # Archive Success
                        #
                        # ==================================

                        logger.info(
                            "Archive history updated: "
                            f"article="
                            f"{existing_article_id}, "
                            f"version="
                            f"{archive_version.version_number}"
                        )

                        # ==================================
                        #
                        # Create AI Task
                        #
                        # Content Changed
                        # → 重新分析
                        #
                        # ==================================

                        task = self.create_ai_task(
                            existing_article_id
                        )

                        if task is None:

                            logger.warning(
                                "AI Task creation failed: "
                                f"article="
                                f"{existing_article_id}"
                            )

                        # ==================================
                        #
                        # Result
                        #
                        # 使用既有 Article
                        #
                        # ==================================

                        articles.append(
                            existing_article
                        )

                        new += 1

                        continue

                    # ==================================
                    #
                    # New Article
                    #
                    # URL 從未存在
                    #
                    # ==================================

                    logger.info(
                        "New article detected: "
                        f"url={item.url}"
                    )

                    # ==================================
                    # Document Duplicate Check
                    #
                    # 只有 URL 不存在時才判斷
                    # 是否為完全相同的 Document。
                    #
                    # ==================================

                    if is_duplicate(
                        article.document_id
                    ):

                        duplicate += 1

                        logger.info(
                            "Duplicate document: "
                            f"{article.document_id}"
                        )

                        continue

                    # ==================================
                    # Save Document Hash
                    # ==================================

                    save_document(
                        article.document_id
                    )

                    # ==================================
                    #
                    # Save Article First
                    #
                    # 必須先取得 Article ID
                    #
                    # ==================================

                    saved = self.repo.insert(
                        article
                    )

                    if saved is None:

                        failed += 1

                        logger.error(
                            "Failed to save article"
                        )

                        continue

                    # ==================================
                    #
                    # Archive Version 1
                    #
                    # ==================================

                    archive_version = (
                        self.archive_service.save_html(

                            article_id=saved.id,

                            url=item.url,

                            html=html

                        )
                    )

                    # ==================================
                    #
                    # Archive 必須成功
                    #
                    # 才建立 AI Task
                    #
                    # ==================================

                    if archive_version is None:

                        failed += 1

                        logger.error(

                            "Archive failed, "
                            f"article={saved.id}. "
                            "AI Task will not be created."

                        )

                        continue

                    # ==================================
                    #
                    # Archive Success
                    #
                    # ==================================

                    logger.info(

                        "Archive completed: "

                        f"article={saved.id}, "

                        f"version="
                        f"{archive_version.version_number}"

                    )

                    # ==================================
                    #
                    # Create AI Task
                    #
                    # ==================================

                    task = self.create_ai_task(
                        saved.id
                    )

                    if task is None:

                        logger.warning(

                            "AI Task creation failed: "
                            f"article={saved.id}"

                        )

                    # ==================================
                    # Result
                    # ==================================

                    articles.append(
                        saved
                    )

                    new += 1

                except Exception as e:

                    failed += 1

                    logger.exception(
                        f"Article processing error: {e}"
                    )

            # ==================================
            # Return
            # ==================================

            return {

                "articles": articles,

                "total": total,

                "new": new,

                "duplicate": duplicate,

                "failed": failed

            }

        except Exception as e:

            logger.exception(
                f"Article create error: {e}"
            )

            return {

                "articles": [],

                "total": total,

                "new": new,

                "duplicate": duplicate,

                "failed": failed

            }

    # ==================================================
    #
    # Create AI Task
    #
    # ==================================================

    def create_ai_task(
        self,
        article_id
    ):

        try:

            task = AITask(

                article_id=article_id,

                task_type="analysis",

                status="WAITING",

                priority=0,

                retry_count=0

            )

            result = self.task_repo.insert(
                task
            )

            logger.info(
                f"AI Task created "
                f"article={article_id}"
            )

            return result

        except Exception as e:

            logger.exception(
                f"Create AI Task error: {e}"
            )

            return None

    # ==================================================
    #
    # Query
    #
    # ==================================================

    def get_all(
        self,
        limit=None
    ):

        try:

            return self.repo.find_all(
                limit
            )

        except Exception as e:

            logger.error(e)

            return []

    # ==================================================

    def get_by_id(
        self,
        article_id
    ):

        try:

            return self.repo.find_by_id(
                article_id
            )

        except Exception as e:

            logger.error(e)

            return None

    # ==================================================

    def get_by_keyword(
        self,
        keyword
    ):

        try:

            return self.repo.find_by_keyword(
                keyword
            )

        except Exception as e:

            logger.error(e)

            return []

    # ==================================================

    def get_by_source(
        self,
        source
    ):

        try:

            return self.repo.find_by_source(
                source
            )

        except Exception as e:

            logger.error(e)

            return []

    # ==================================================
    #
    # AI Query
    #
    # ==================================================

    def get_by_importance(
        self,
        level
    ):

        return self.repo.find_by_importance(
            level
        )

    # ==================================================

    def get_by_category(
        self,
        category
    ):

        return self.repo.find_by_category(
            category
        )

    # ==================================================

    def get_by_ai_keyword(
        self,
        keyword
    ):

        return self.repo.find_by_ai_keyword(
            keyword
        )

    # ==================================================

    def get_ai_top(
        self,
        limit=10
    ):

        try:

            articles = self.repo.find_all()

            articles.sort(

                key=lambda x:
                x.get(
                    "ai_importance",
                    0
                ),

                reverse=True

            )

            return articles[:limit]

        except Exception as e:

            logger.error(e)

            return []

    # ==================================================
    #
    # Count
    #
    # ==================================================

    def count(self):

        try:

            return self.repo.count()

        except Exception as e:

            logger.error(e)

            return 0

    # ==================================================
    #
    # Close
    #
    # ==================================================

    def close(self):

        try:

            self.repo.close()

        except Exception as e:

            logger.error(e)