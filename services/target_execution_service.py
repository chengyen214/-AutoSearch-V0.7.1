"""
services/target_execution_service.py

AutoSearch V5

Target Execution Service

用途：

    負責執行 Target。

目前支援：

    1. Direct URL Target

        Target
            ↓
        TargetExecutionService
            ↓
        CrawlService
            ↓
        TargetService.disable()
            ↓
        Target.status = inactive
            ↓
        ParserService
            ↓
        ArticleService
            ↓
        SQL / Archive / AI Task

    2. Search Target

        目前 Search Pipeline
        沿用既有 JobExecutorBridge。

架構：

    Direct URL：

        Target
            ↓
        TargetExecutionService
            ↓
        CrawlService
            ↓
        TargetService.disable()
            ↓
        ParserService
            ↓
        ArticleService
            ↓
        AI Task

    Search：

        Target
            ↓
        TargetExecutionService
            ↓
        JobExecutorBridge
            ↓
        Search
            ↓
        Crawl
            ↓
        Parser
            ↓
        ArticleService

重要：

    TargetExecutionService 不重新實作：

        CrawlService
        ParserService
        ArticleService
        Search
        SearchAdapter

    只負責：

        Target Execution Orchestration

    以及 Direct URL Crawl 成功後：

        Target → inactive

不負責：

    - Crawl implementation
    - Parser implementation
    - Article Persistence implementation
    - AI Analysis implementation
    - AI Task implementation
    - Search implementation
    - SearchAdapter implementation
    - Target Repository
    - Target Business Validation
    - Job 建立

AI Task：

    ArticleService.create()
    內部既有流程負責 AI Task 建立。

Direct URL Status：

    Crawl 成功取得結果後：

        TargetService.disable(target_id)

    由既有 Target Service / Repository
    負責將：

        targets.status

    設為：

        inactive

注意：

    TargetExecutionService 不直接操作：

        TargetRepository

    而是透過：

        TargetService.disable()

    修改 Target Status。

Search Target：

    Search Target 不由本 Service
    自動修改 status。

不修改：

    run.py
    app/main.py
    JobExecutorBridge

只新增 Target-specific Execution Entry。
"""


# ============================================================
#
# Imports
#
# ============================================================

from services.job_executor_bridge import (
    JobExecutorBridge,
)

from services.crawl_service import (
    CrawlService,
)

from services.parser_service import (
    ParserService,
)

from services.article_service import (
    ArticleService,
)

from services.target_service import (
    TargetService,
)

from utils.logger import (
    logger,
)


# ============================================================
#
# Target Execution Service
#
# ============================================================

class TargetExecutionService:

    """
    Target Execution Service。

    Direct URL：

        Target
            ↓
        CrawlService
            ↓
        TargetService.disable()
            ↓
        ParserService
            ↓
        ArticleService

    Search：

        Target
            ↓
        JobExecutorBridge
            ↓
        Existing Search Pipeline
    """

    # ========================================================
    #
    # Initialization
    #
    # ========================================================

    def __init__(
        self,
        job_executor_bridge=None,
        crawl_service=None,
        parser_service=None,
        article_service=None,
        target_service=None,
    ):
        """
        建立 TargetExecutionService。

        Parameters
        ----------
        job_executor_bridge :
            Search Target 使用的既有 JobExecutorBridge。

        crawl_service :
            Direct URL 使用的 CrawlService。

        parser_service :
            Direct URL 使用的 ParserService。

        article_service :
            Direct URL 使用的 ArticleService。

        target_service :
            Target Status 管理使用的 TargetService。

        所有 Service 都支援 Dependency Injection。

        方便：

            Unit Test
            Integration Test
            Mock
            未來擴充
        """

        if job_executor_bridge is None:

            job_executor_bridge = (
                JobExecutorBridge()
            )

        self.job_executor_bridge = (
            job_executor_bridge
        )

        if crawl_service is None:

            crawl_service = (
                CrawlService()
            )

        self.crawl_service = (
            crawl_service
        )

        if parser_service is None:

            parser_service = (
                ParserService()
            )

        self.parser_service = (
            parser_service
        )

        if article_service is None:

            article_service = (
                ArticleService()
            )

        self.article_service = (
            article_service
        )

        if target_service is None:

            target_service = (
                TargetService()
            )

        self.target_service = (
            target_service
        )

        logger.info(
            "TargetExecutionService initialized: "
            "Direct URL -> Crawl -> "
            "Target inactive -> Parser -> "
            "ArticleService"
        )

    # ========================================================
    #
    # Execute Target
    #
    # ========================================================

    def execute(
        self,
        target,
    ):
        """
        執行 Target。

        Direct URL：

            Target
                ↓
            CrawlService
                ↓
            TargetService.disable()
                ↓
            ParserService
                ↓
            ArticleService

        Search：

            不在 execute() 中重新實作。

            使用：

                execute_search()

            或：

                execute_search_and_crawl()

        Returns
        -------

        dict
            Execution Result

        Raises
        ------

        ValueError
            Target 不存在
            或 Target 類型不支援。
        """

        self._validate_target(
            target
        )

        # ====================================================
        #
        # Direct URL Target
        #
        # ====================================================

        if self.is_direct_url(
            target
        ):

            return (
                self.execute_direct_url(
                    target
                )
            )

        # ====================================================
        #
        # Search Target
        #
        # ====================================================

        if self.is_search(
            target
        ):

            raise ValueError(
                "Search Target execution is not "
                "implemented in TargetExecutionService.execute(). "
                "Use execute_search() or "
                "execute_search_and_crawl()."
            )

        # ====================================================
        #
        # Unsupported
        #
        # ====================================================

        raise ValueError(
            "Unsupported Target type."
        )

    # ========================================================
    #
    # Execute Direct URL
    #
    # ========================================================

    def execute_direct_url(
        self,
        target,
    ):
        """
        執行 Direct URL Target。

        Pipeline：

            Target
              ↓
            CrawlService
              ↓
            TargetService.disable()
              ↓
            ParserService
              ↓
            ArticleService
              ↓
            SQL / Archive / AI Task

        Status：

            Crawl 成功後：

                TargetService.disable(target_id)
                    ↓
                targets.status = inactive

        注意：

            不直接操作 TargetRepository。

            使用：

                TargetService.disable()
        """

        self._validate_target(
            target
        )

        if not self.is_direct_url(
            target
        ):

            raise ValueError(
                "Target is not a Direct URL Target."
            )

        target_id = (
            self._get_target_id(
                target
            )
        )

        logger.info(
            "Executing Direct URL Target: "
            f"target_id={target_id}"
        )

        # ====================================================
        #
        # Crawl
        #
        # ====================================================

        try:

            crawl_result = (
                self.crawl_service
                .crawl_target(
                    target
                )
            )

        except Exception as e:

            logger.exception(
                "Direct URL crawl failed: "
                f"target_id={target_id} | "
                f"{e}"
            )

            return {
                "crawl_result": None,

                "parser_result": None,

                "article_result": {
                    "article": None,
                    "article_id": None,
                    "status": "crawl_failed",
                    "archive_version": None,
                    "ai_task": None,
                    "error": str(e),
                },

                "target_status": (
                    self._get_target_status(
                        target
                    )
                ),
            }

        # ====================================================
        #
        # Crawl Failed
        #
        # ====================================================

        if crawl_result is None:

            logger.warning(
                "Direct URL crawl returned None: "
                f"target_id={target_id}"
            )

            return {
                "crawl_result": None,

                "parser_result": None,

                "article_result": {
                    "article": None,
                    "article_id": None,
                    "status": "crawl_failed",
                    "archive_version": None,
                    "ai_task": None,
                },

                "target_status": (
                    self._get_target_status(
                        target
                    )
                ),
            }

        # ====================================================
        #
        # Crawl Successful
        #
        # ====================================================

        """
        Crawl 已成功取得結果。

        此時才停用 Direct URL Target。

        執行：

            TargetExecutionService
                ↓
            TargetService.disable(target_id)
                ↓
            TargetRepository
                ↓
            targets.status = inactive
        """

        target_status = (
            self._deactivate_target(
                target_id
            )
        )

        # ====================================================
        #
        # Parser
        #
        # ====================================================

        keyword = (
            self._get_keyword(
                target
            )
        )

        try:

            parser_result = (
                self.parser_service
                .parse_crawl_result(
                    crawl_result,
                    keyword,
                )
            )

        except Exception as e:

            logger.exception(
                "Direct URL parser failed: "
                f"target_id={target_id} | "
                f"{e}"
            )

            return {
                "crawl_result":
                    crawl_result,

                "parser_result":
                    None,

                "article_result": {
                    "article": None,
                    "article_id": None,
                    "status": "parser_failed",
                    "archive_version": None,
                    "ai_task": None,
                    "error": str(e),
                },

                "target_status":
                    target_status,
            }

        # ====================================================
        #
        # Parser Failed
        #
        # ====================================================

        if parser_result is None:

            logger.warning(
                "Direct URL parser returned None: "
                f"target_id={target_id}"
            )

            return {
                "crawl_result":
                    crawl_result,

                "parser_result":
                    None,

                "article_result": {
                    "article": None,
                    "article_id": None,
                    "status": "parser_failed",
                    "archive_version": None,
                    "ai_task": None,
                },

                "target_status":
                    target_status,
            }

        # ====================================================
        #
        # Article
        #
        # ====================================================

        article = (
            self._extract_article(
                parser_result
            )
        )

        if article is None:

            logger.warning(
                "Parser result does not contain "
                "an Article object: "
                f"target_id={target_id}"
            )

            return {
                "crawl_result":
                    crawl_result,

                "parser_result":
                    parser_result,

                "article_result": {
                    "article": None,
                    "article_id": None,
                    "status": "parser_result_invalid",
                    "archive_version": None,
                    "ai_task": None,
                },

                "target_status":
                    target_status,
            }

        # ====================================================
        #
        # HTML
        #
        # ====================================================

        html = (
            self._extract_html(
                crawl_result
            )
        )

        if html is None:

            logger.warning(
                "Crawl result does not contain "
                "raw HTML: "
                f"target_id={target_id}"
            )

            return {
                "crawl_result":
                    crawl_result,

                "parser_result":
                    parser_result,

                "article_result": {
                    "article":
                        article,

                    "article_id":
                        None,

                    "status":
                        "html_missing",

                    "archive_version":
                        None,

                    "ai_task":
                        None,
                },

                "target_status":
                    target_status,
            }

        # ====================================================
        #
        # ArticleService
        #
        # ====================================================

        try:

            article_result = (
                self.article_service
                .create(
                    article=article,
                    html=html,
                )
            )

        except Exception as e:

            logger.exception(
                "ArticleService failed: "
                f"target_id={target_id} | "
                f"{e}"
            )

            article_result = {
                "article":
                    article,

                "article_id":
                    None,

                "status":
                    "article_service_failed",

                "archive_version":
                    None,

                "ai_task":
                    None,

                "error":
                    str(e),
            }

        # ====================================================
        #
        # Completed
        #
        # ====================================================

        logger.info(
            "Direct URL Target execution completed: "
            f"target_id={target_id} | "
            f"target_status={target_status} | "
            f"status="
            f"{self._get_result_status(article_result)}"
        )

        return {
            "crawl_result":
                crawl_result,

            "parser_result":
                parser_result,

            "article_result":
                article_result,

            "target_status":
                target_status,
        }

    # ========================================================
    #
    # Deactivate Target
    #
    # ========================================================

    def _deactivate_target(
        self,
        target_id,
    ):
        """
        將 Direct URL Target 設為 inactive。

        執行位置：

            Crawl 成功
                ↓
            _deactivate_target()
                ↓
            TargetService.disable()
                ↓
            TargetRepository
                ↓
            targets.status = inactive

        不直接操作：

            TargetRepository

        而是透過：

            TargetService.disable()

        Returns
        -------

        str
            "inactive"

        None
            Target ID 不存在，或 disable() 回傳 False。

        Raises
        ------

        Exception
            TargetService.disable()
            發生例外時向上拋出。
        """

        if target_id is None:

            logger.warning(
                "Cannot deactivate Target: "
                "target_id is None"
            )

            return None

        logger.info(
            "Deactivating Direct URL Target: "
            f"target_id={target_id}"
        )

        try:

            disabled = (
                self.target_service
                .disable(
                    target_id
                )
            )

        except Exception as e:

            logger.exception(
                "Failed to deactivate Target: "
                f"target_id={target_id} | "
                f"{e}"
            )

            raise

        if not disabled:

            logger.warning(
                "TargetService.disable() returned "
                "False: "
                f"target_id={target_id}"
            )

            return None

        logger.info(
            "Direct URL Target deactivated: "
            f"target_id={target_id} | "
            "status=inactive"
        )

        return "inactive"

    # ========================================================
    #
    # Execute Crawl
    #
    # ========================================================

    def execute_crawl(
        self,
        target,
    ):
        """
        Direct URL Execution Alias。

        Target API / UI 可以直接使用：

            execute_crawl()

        實際流程：

            CrawlService
                ↓
            TargetService.disable()
                ↓
            ParserService
                ↓
            ArticleService
        """

        return (
            self.execute_direct_url(
                target
            )
        )

    # ========================================================
    #
    # Is Direct URL
    #
    # ========================================================

    def is_direct_url(
        self,
        target,
    ):
        """
        判斷 Target 是否為 Direct URL。

        Target Type 判斷仍沿用
        JobExecutorBridge 的既有邏輯。
        """

        self._validate_target(
            target
        )

        return (
            self.job_executor_bridge
            .is_direct_url(
                target
            )
        )

    # ========================================================
    #
    # Is Search
    #
    # ========================================================

    def is_search(
        self,
        target,
    ):
        """
        判斷 Target 是否為 Search Target。

        Target Type 判斷沿用既有
        JobExecutorBridge。
        """

        self._validate_target(
            target
        )

        return (
            self.job_executor_bridge
            .is_search(
                target
            )
        )

    # ========================================================
    #
    # Resolve Source
    #
    # ========================================================

    def resolve_source(
        self,
        target,
    ):
        """
        取得 Target Source Definition。
        """

        self._validate_target(
            target
        )

        return (
            self.job_executor_bridge
            .resolve_source(
                target
            )
        )

    # ========================================================
    #
    # Resolve Resolved Source
    #
    # ========================================================

    def resolve_resolved_source(
        self,
        target,
    ):
        """
        取得 Resolution 後的 Source。
        """

        self._validate_target(
            target
        )

        return (
            self.job_executor_bridge
            .resolve_resolved_source(
                target
            )
        )

    # ========================================================
    #
    # Execute Search
    #
    # ========================================================

    def execute_search(
        self,
        target,
        max_results=None,
    ):
        """
        執行 Search Target。

        Search Pipeline 仍由：

            JobExecutorBridge

        負責。

        本 Service 不重新實作 Search。
        """

        self._validate_target(
            target
        )

        if not self.is_search(
            target
        ):

            raise ValueError(
                "Target is not a Search Target."
            )

        return (
            self.job_executor_bridge
            .execute_search(
                target,
                max_results=max_results,
            )
        )

    # ========================================================
    #
    # Execute Search And Crawl
    #
    # ========================================================

    def execute_search_and_crawl(
        self,
        target,
        max_results=None,
    ):
        """
        執行完整 Search Target Pipeline。

        Search Pipeline：

            Target
              ↓
            JobExecutorBridge
              ↓
            Search
              ↓
            Crawl
              ↓
            Parser
              ↓
            ArticleService
              ↓
            SQL / Archive / AI Task

        注意：

            Search Target Status
            不由此方法自動修改。

            Search Target 仍沿用
            既有 Job Pipeline。
        """

        self._validate_target(
            target
        )

        if not self.is_search(
            target
        ):

            raise ValueError(
                "Target is not a Search Target."
            )

        logger.info(
            "Executing Search Target Pipeline: "
            f"target_id={self._get_target_id(target)}"
        )

        return (
            self.job_executor_bridge
            .execute_search_and_crawl(
                target,
                max_results=max_results,
            )
        )

    # ========================================================
    #
    # Provider
    #
    # ========================================================

    def get_provider(
        self,
        target,
    ):
        """
        取得 Target Provider。
        """

        self._validate_target(
            target
        )

        return (
            self.job_executor_bridge
            .get_provider(
                target
            )
        )

    # ========================================================
    #
    # Resolved Provider
    #
    # ========================================================

    def get_resolved_provider(
        self,
        target,
    ):
        """
        取得 Resolution 後的 Provider。
        """

        self._validate_target(
            target
        )

        return (
            self.job_executor_bridge
            .get_resolved_provider(
                target
            )
        )

    # ========================================================
    #
    # Resolved Adapter
    #
    # ========================================================

    def get_resolved_adapter(
        self,
        target,
    ):
        """
        取得 Resolution 後的 Search Adapter。
        """

        self._validate_target(
            target
        )

        return (
            self.job_executor_bridge
            .get_resolved_adapter(
                target
            )
        )

    # ========================================================
    #
    # Resolved Search Source
    #
    # ========================================================

    def get_resolved_search_source(
        self,
        target,
    ):
        """
        取得 Resolution 後的 Search Source。
        """

        self._validate_target(
            target
        )

        return (
            self.job_executor_bridge
            .get_resolved_search_source(
                target
            )
        )

    # ========================================================
    #
    # Supported Provider
    #
    # ========================================================

    def is_supported_provider(
        self,
        provider,
    ):
        """
        判斷 Provider 是否支援。
        """

        return (
            self.job_executor_bridge
            .is_supported_provider(
                provider
            )
        )

    # ========================================================
    #
    # Extract Article
    #
    # ========================================================

    @staticmethod
    def _extract_article(
        parser_result,
    ):
        """
        從 Parser Result 取得 Article。

        支援：

            dict["article"]
            dict["parsed_article"]
            dict["result"]
            document_id dict
            object.article
            object.parsed_article
            object.result
            object.document_id
        """

        if parser_result is None:
            return None

        if isinstance(
            parser_result,
            dict,
        ):

            for key in (
                "article",
                "parsed_article",
                "result",
            ):

                value = (
                    parser_result.get(
                        key
                    )
                )

                if value is not None:
                    return value

            if (
                "document_id"
                in parser_result
            ):

                return parser_result

            return None

        for attribute in (
            "article",
            "parsed_article",
            "result",
        ):

            if hasattr(
                parser_result,
                attribute,
            ):

                value = getattr(
                    parser_result,
                    attribute,
                    None,
                )

                if value is not None:
                    return value

        if hasattr(
            parser_result,
            "document_id",
        ):

            return parser_result

        return None

    # ========================================================
    #
    # Extract HTML
    #
    # ========================================================

    @staticmethod
    def _extract_html(
        crawl_result,
    ):
        """
        從 Crawl Result 取得 Raw HTML。

        支援：

            html
            raw_html
            content
        """

        if crawl_result is None:
            return None

        if isinstance(
            crawl_result,
            dict,
        ):

            for key in (
                "html",
                "raw_html",
                "content",
            ):

                value = (
                    crawl_result.get(
                        key
                    )
                )

                if value is not None:
                    return value

            return None

        for attribute in (
            "html",
            "raw_html",
            "content",
        ):

            if hasattr(
                crawl_result,
                attribute,
            ):

                value = getattr(
                    crawl_result,
                    attribute,
                    None,
                )

                if value is not None:
                    return value

        return None

    # ========================================================
    #
    # Get Keyword
    #
    # ========================================================

    @staticmethod
    def _get_keyword(target):
        """
        取得 Target Keyword。

        Direct URL Target：
            如果沒有 keyword，
            暫時使用固定 keyword：

                IC semiconductor
        """

        if target is None:
            return "IC semiconductor"

        if isinstance(target, dict):
            keyword = target.get("keyword")
        else:
            keyword = getattr(
                target,
                "keyword",
                None,
            )

        keyword = (
            str(keyword).strip()
            if keyword is not None
            else ""
        )

        if not keyword:
            return "IC semiconductor"

        return keyword
    # ========================================================
    #
    # Get Result Status
    #
    # ========================================================

    @staticmethod
    def _get_result_status(
        result,
    ):
        """
        取得 ArticleService Result Status。
        """

        if not isinstance(
            result,
            dict,
        ):

            return "unknown"

        status = result.get(
            "status"
        )

        if status is None:
            return "unknown"

        return str(
            status
        ).strip()

    # ========================================================
    #
    # Get Target Status
    #
    # ========================================================

    @staticmethod
    def _get_target_status(
        target,
    ):
        """
        取得 Target Status。

        支援：

            Target Model
            dict
        """

        if target is None:
            return None

        if isinstance(
            target,
            dict,
        ):

            return target.get(
                "status"
            )

        return getattr(
            target,
            "status",
            None,
        )

    # ========================================================
    #
    # Target ID
    #
    # ========================================================

    @staticmethod
    def _get_target_id(
        target,
    ):
        """
        取得 Target ID。

        支援：

            Target Model
            dict
        """

        if target is None:
            return None

        if isinstance(
            target,
            dict,
        ):

            return target.get(
                "id"
            )

        return getattr(
            target,
            "id",
            None,
        )

    # ========================================================
    #
    # Validation
    #
    # ========================================================

    @staticmethod
    def _validate_target(
        target,
    ):
        """
        基本 Target Validation。

        不負責：

            TargetValidator
            Business Validation
            Duplicate Check

        只確認 Target 存在。
        """

        if target is None:

            raise ValueError(
                "target cannot be None"
            )

        return True


# ============================================================
#
# Default Service
#
# ============================================================

default_target_execution_service = (
    TargetExecutionService()
)


# ============================================================
#
# Convenience Function
#
# ============================================================

def execute_target(
    target,
):
    """
    Convenience Function。

    執行 Target。
    """

    return (
        default_target_execution_service
        .execute(
            target
        )
    )


# ============================================================
#
# Public API
#
# ============================================================

__all__ = [
    "TargetExecutionService",
    "default_target_execution_service",
    "execute_target",
]
