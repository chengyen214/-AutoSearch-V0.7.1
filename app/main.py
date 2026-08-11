"""
app/main.py

AutoSearch V4

P2.4 Async AI Scaling Integration

Pipeline:

Keyword
↓
ArticleService
↓
Search
↓
Download HTML
↓
Parser
↓
ArticleRepository
↓
articles
↓
AITaskRepository
↓
ai_tasks WAITING
↓
AIBatchTriggerService
↓
Batch Threshold
↓
AIScheduler
↓
AIWorkerPool
↓
Multiple AIWorker
↓
AI Analysis
↓
Knowledge Archive
↓
Knowledge Intelligence
↓
Search Index


P2.4 Architecture:

AIBatchTriggerService
        ↓
AIScheduler
        ↓
AIWorkerPool
   ┌────┼────┐
   ↓    ↓    ↓
 Worker Worker Worker
   └────┼────┘
        ↓
   AI Analysis


注意:

本 Application 負責：

- 啟動 Article Pipeline
- 建立 AI Task
- Trigger Async AI Pipeline
- 等待本次 AI Worker Pool 完成
- 啟動 Knowledge Intelligence
- Export
- History

本 Application 不負責：

- AI Analysis Logic
- AI Task CRUD
- Batch Threshold 判斷
- Worker Lifecycle
- Worker Pool 管理
- Knowledge Processing Logic
"""

import time

from config.keywords import SEARCH_KEYWORDS

from services.article_service import (
    ArticleService
)

from services.ai_scheduler import (
    AIScheduler
)

from services.ai_batch_trigger_service import (
    AIBatchTriggerService
)

from services.knowledge_intelligence_service import (
    KnowledgeIntelligenceService
)

from exporter.excel import export

from utils.history import save_history

from utils.logger import logger

from config.settings import (
    AI_THRESHOLD
)
class AutoSearchApplication:

    """
    AutoSearch V4 Application

    P2.4 Async AI Scaling Integration

    負責將：

        Article Pipeline
            ↓
        Batch Trigger
            ↓
        Scheduler
            ↓
        Worker Pool
            ↓
        Knowledge Intelligence

    整合成完整 Application Pipeline。
    """

    # ==================================================
    # Initialize
    # ==================================================

    def __init__(
        self,
        ai_threshold=AI_THRESHOLD,
        ai_wait_interval=0.1
    ):
        """
        Parameters
        ----------

        ai_threshold:
            WAITING AI Task 啟動門檻。

            Default:
                50

        ai_wait_interval:
            等待 AI Worker Pool 完成時的
            Polling 間隔，單位秒。

            Default:
                0.1
        """

        # ----------------------------------------------
        # Article Pipeline
        # ----------------------------------------------

        self.article_service = (
            ArticleService()
        )

        # ----------------------------------------------
        # AI Scheduler
        # ----------------------------------------------

        self.ai_scheduler = (
            AIScheduler()
        )

        # ----------------------------------------------
        # AI Batch Trigger
        # ----------------------------------------------

        self.ai_batch_trigger = (
            AIBatchTriggerService(

                scheduler=(
                    self.ai_scheduler
                ),

                threshold=(
                    ai_threshold
                )

            )
        )

        # ----------------------------------------------
        # AI Wait Interval
        # ----------------------------------------------

        if (
            ai_wait_interval is None
            or ai_wait_interval <= 0
        ):

            ai_wait_interval = 0.1

        self.ai_wait_interval = (
            ai_wait_interval
        )

        # ----------------------------------------------
        # Knowledge Layer
        # ----------------------------------------------

        self.knowledge_service = (
            KnowledgeIntelligenceService()
        )

    # ==================================================
    # Collect Articles
    # ==================================================

    def _collect_articles(
        self
    ):
        """
        執行 Article Collection Pipeline。

        Flow:

            Keyword
                ↓
            ArticleService
                ↓
            Article
                ↓
            AI Task

        Returns
        -------

        list

            本次收集到的 Articles。
        """

        articles = []

        for keyword in SEARCH_KEYWORDS:

            logger.info(
                f"開始搜尋：{keyword}"
            )

            result = (
                self.article_service.create(
                    keyword
                )
            )

            # ------------------------------------------
            # Invalid Result
            # ------------------------------------------

            if not result:

                logger.warning(
                    "ArticleService returned "
                    f"empty result for keyword={keyword}"
                )

                continue

            # ------------------------------------------
            # Articles
            # ------------------------------------------

            keyword_articles = (
                result.get(
                    "articles",
                    []
                )
            )

            if keyword_articles:

                articles.extend(
                    keyword_articles
                )

            # ------------------------------------------
            # History
            # ------------------------------------------

            save_history(

                keyword,

                result.get(
                    "total",
                    0
                ),

                result.get(
                    "new",
                    0
                ),

                result.get(
                    "duplicate",
                    0
                ),

                result.get(
                    "failed",
                    0
                )

            )

        logger.info(
            "Articles collected="
            f"{len(articles)}"
        )

        return articles

    # ==================================================
    # Start Async AI
    # ==================================================

    def _start_async_ai(
        self
    ):
        """
        啟動 P2.4 Async AI Scaling。

        Flow:

            WAITING AI Tasks
                    ↓
            AIBatchTriggerService
                    ↓
              Threshold Check
                    ↓
                AIScheduler
                    ↓
               AIWorkerPool
                    ↓
              Multiple Workers

        Returns
        -------

        bool

            True:
                Scheduler 已啟動或已經執行

            False:
                Threshold 尚未達成
                或啟動失敗
        """

        logger.info(
            "Checking AI Batch Trigger"
        )

        result = (
            self.ai_batch_trigger
            .check_and_trigger()
        )

        if result:

            logger.info(
                "Async AI Scaling triggered"
            )

        else:

            logger.info(
                "Async AI Scaling not triggered"
            )

        return result

    # ==================================================
    # Wait AI Completion
    # ==================================================

    def _wait_for_ai_completion(
        self
    ):
        """
        等待本次 AI Worker Pool 完成。

        目的：

        避免：

            AI Worker
                ↓
            Background Thread
                ↓
            Application 提前結束

        導致：

            Knowledge Intelligence
                ↓
            在 AI Analysis 尚未完成時執行。

        注意：

        本方法不負責 Worker Lifecycle。

        Worker Lifecycle 仍由：

            AIWorkerPool

        負責。

        Returns
        -------

        bool

            True:
                AI Pool 已完成

            False:
                Scheduler / Pool 尚未啟動
                或等待發生錯誤
        """

        scheduler = (
            self.ai_scheduler
        )

        pool = getattr(
            scheduler,
            "worker_pool",
            None
        )

        if pool is None:

            logger.warning(
                "AI Worker Pool is unavailable"
            )

            return False

        logger.info(
            "Waiting for AI Worker Pool "
            "to complete"
        )

        while True:

            try:

                status = (
                    scheduler
                    .get_status()
                )

                # --------------------------------------
                # Pool Running
                # --------------------------------------

                pool_running = (
                    status.get(
                        "worker_pool_running",
                        False
                    )
                )

                # --------------------------------------
                # Active Workers
                # --------------------------------------

                active_workers = (
                    status.get(
                        "active_workers",
                        0
                    )
                )

                # --------------------------------------
                # Worker Count
                # --------------------------------------

                worker_count = (
                    status.get(
                        "worker_count",
                        0
                    )
                )

                # --------------------------------------
                # Not Started
                # --------------------------------------

                if (
                    not pool_running
                    and worker_count == 0
                ):

                    logger.info(
                        "AI Worker Pool "
                        "was not started"
                    )

                    return False

                # --------------------------------------
                # Completed
                # --------------------------------------

                if active_workers == 0:

                    logger.info(
                        "AI Worker Pool "
                        "completed: "
                        f"workers={worker_count}"
                    )

                    return True

                # --------------------------------------
                # Waiting
                # --------------------------------------

                time.sleep(
                    self.ai_wait_interval
                )

            except KeyboardInterrupt:

                logger.warning(
                    "KeyboardInterrupt received "
                    "while waiting for AI"
                )

                return False

            except Exception as e:

                logger.exception(
                    "AI Worker Pool wait failed: "
                    f"{e}"
                )

                return False

    # ==================================================
    # Stop Async AI
    # ==================================================

    def _stop_async_ai(
        self
    ):
        """
        停止本次 Application 啟動的
        Async AI Scheduler。

        Returns
        -------

        bool
        """

        try:

            if (
                self.ai_scheduler
                .is_running()
            ):

                logger.info(
                    "Stopping Async AI Scheduler"
                )

                result = (
                    self.ai_scheduler
                    .stop()
                )

                if result is False:

                    logger.warning(
                        "Async AI Scheduler "
                        "failed to stop"
                    )

                    return False

            return True

        except Exception as e:

            logger.exception(
                "Stop Async AI failed: "
                f"{e}"
            )

            return False

    # ==================================================
    # Main Pipeline
    # ==================================================

    def run(
        self
    ):
        """
        執行完整 AutoSearch V4 Pipeline。

        Flow:

            1. Article Collection
            2. AI Task Creation
            3. Batch Trigger
            4. Async AI Scaling
            5. AI Worker Pool
            6. Knowledge Intelligence
            7. Export

        Returns
        -------

        list

            本次收集到的 Articles。
        """

        logger.info(
            "========== "
            "AutoSearch V4 Start "
            "=========="
        )

        articles = []

        ai_triggered = False

        try:

            # ==========================================
            #
            # Step 1
            #
            # Article Collection
            #
            # ==========================================

            articles = (
                self._collect_articles()
            )

            # ==========================================
            #
            # Step 2
            #
            # Async AI Scaling
            #
            # ==========================================

            logger.info(
                "Start Async AI Scaling"
            )

            ai_triggered = (
                self._start_async_ai()
            )

            # ------------------------------------------
            # Wait For AI
            # ------------------------------------------

            if ai_triggered:

                ai_completed = (
                    self._wait_for_ai_completion()
                )

                if ai_completed:

                    logger.info(
                        "Async AI Pipeline "
                        "completed"
                    )

                else:

                    logger.warning(
                        "Async AI Pipeline "
                        "did not complete normally"
                    )

            else:

                logger.info(
                    "AI Batch Threshold "
                    "not reached; "
                    "AI Scheduler not started"
                )

            # ==========================================
            #
            # Step 3
            #
            # Knowledge Intelligence
            #
            # ==========================================

            logger.info(
                "Start Knowledge Intelligence"
            )

            self.knowledge_service.run()

            logger.info(
                "Knowledge Intelligence finished"
            )

        except KeyboardInterrupt:

            logger.warning(
                "KeyboardInterrupt received"
            )

        except Exception as e:

            logger.exception(
                f"AutoSearch V4 pipeline failed: {e}"
            )

        finally:

            # ------------------------------------------
            # AI Scheduler Cleanup
            # ------------------------------------------

            if ai_triggered:

                self._stop_async_ai()

            logger.info(
                "========== "
                "AutoSearch V4 Finish "
                "=========="
            )

        # ==========================================
        #
        # Step 4
        #
        # Export
        #
        # ==========================================

        if articles:

            try:

                export(
                    articles
                )

                logger.info(
                    "Article export completed"
                )

            except Exception as e:

                logger.exception(
                    f"Article export failed: {e}"
                )

        return articles


# ======================================
#
# Backward Compatible Entry
#
# ======================================

def main():
    """
    Backward compatible Application entry.
    """

    app = (
        AutoSearchApplication()
    )

    app.run()


if __name__ == "__main__":

    main()
