"""
app/main.py

AutoSearch V4

P2.4 Async AI Scaling Integration
P2.4 Startup Queue Recovery
P2.4 Persistent AI Queue Resume

Pipeline:

Application Start
↓
Startup Queue Recovery
↓
RUNNING -> WAITING
↓
Existing WAITING Queue Detection
↓
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
Batch Threshold / Existing Queue Resume
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

Startup
        |
        v
Queue Recovery
        |
        v
RUNNING -> WAITING
        |
        v
Existing Queue Detection
        |
        +----------------------+
        |                      |
        v                      v
Existing Queue > 0        No Existing Queue
        |                      |
        v                      v
Force Trigger          AI_THRESHOLD Trigger
        |                      |
        +----------+-----------+
                   |
                   v
              AIScheduler
                   |
                   v
              AIWorkerPool
             /      |      \
            v       v       v
         Worker   Worker   Worker
            \       |       /
             +------+------+
                    |
                    v
               AI Analysis
                    |
                    v
              Queue Drain
                    |
                    v
              WAITING = 0


P2.4 Startup Queue Recovery:

Previous Process
        |
        v
RUNNING Tasks
        |
        | process interrupted
        v
Application Restart
        |
        v
recover_running_tasks()
        |
        v
RUNNING -> WAITING
        |
        v
Resume Queue


P2.4 Existing Queue Rule:

如果 Application 啟動前
資料庫已經存在 WAITING Task，

即使:

    WAITING < AI_THRESHOLD

也必須 Resume。

因此:

    Existing Queue
        ↓
    Force Trigger

而不是:

    Existing Queue
        ↓
    Threshold Check


AI_THRESHOLD 只負責：

    本次啟動後新產生的 Queue
    是否達到自動啟動門檻。


注意:

本 Application 負責：

- Startup Queue Recovery
- Existing AI Queue Resume
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


from config.settings import (
    AI_THRESHOLD
)


from database.ai_task_repository import (
    AITaskRepository
)


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


class AutoSearchApplication:

    """
    AutoSearch V4 Application

    P2.4 Async AI Scaling Integration
    P2.4 Startup Queue Recovery

    負責將：

        Startup Recovery
            ↓
        Existing Queue Resume
            ↓
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
            WAITING AI Task
            新 Queue 自動啟動門檻。

        ai_wait_interval:
            等待 AI Worker Pool 完成時的
            Polling 間隔，單位秒。
        """

        # ----------------------------------------------
        # AI Task Repository
        # ----------------------------------------------
        #
        # P2.4 Startup Queue Recovery
        #

        self.ai_task_repository = (
            AITaskRepository()
        )

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
    # Recover Startup AI Queue
    # ==================================================

    def _recover_startup_ai_queue(
        self
    ):
        """
        P2.4 Startup Queue Recovery。

        Application 啟動時：

            RUNNING
                |
                v
            WAITING

        用途：

        如果前一次程序因為：

            Ctrl+C
            Process Crash
            Terminal 關閉
            Machine Restart

        導致 AI Task 卡在：

            RUNNING

        本次啟動時自動恢復。

        同時記錄：

            Application 啟動前
            是否已經存在 WAITING Task。

        這樣可以區分：

            舊 Queue Resume

        與：

            本次新產生 Queue
        """

        try:

            # ==========================================
            # Step 1
            # Count RUNNING
            # ==========================================

            running_before = (
                self.ai_task_repository
                .count_running_tasks()
            )

            logger.info(
                "Startup AI Queue Recovery: "
                f"running={running_before}"
            )

            # ==========================================
            # Step 2
            # Recover RUNNING
            # ==========================================

            recovered = 0

            if running_before > 0:

                recovered = (
                    self.ai_task_repository
                    .recover_running_tasks()
                )

                logger.info(
                    "Startup AI Queue Recovery completed: "
                    f"recovered={recovered}"
                )

            else:

                logger.info(
                    "Startup AI Queue Recovery: "
                    "no RUNNING tasks"
                )

            # ==========================================
            # Step 3
            # Count Existing WAITING
            # ==========================================

            waiting_after_recovery = (
                self.ai_task_repository
                .count_waiting_tasks()
            )

            logger.info(
                "Startup AI Queue state: "
                f"waiting={waiting_after_recovery}, "
                f"recovered={recovered}"
            )

            return {
                "running_before": (
                    running_before
                ),

                "recovered": (
                    recovered
                ),

                "waiting": (
                    waiting_after_recovery
                )

            }

        except Exception as e:

            logger.exception(
                "Startup AI Queue Recovery failed: "
                f"{e}"
            )

            return {

                "running_before": 0,

                "recovered": 0,

                "waiting": 0,

                "error": True

            }

    # ==================================================
    # Check Existing AI Queue
    # ==================================================

    def _has_existing_ai_queue(
        self
    ):
        """
        判斷 Application 啟動時
        是否已經存在 WAITING AI Queue。

        注意：

        這個判斷代表：

            本次 run.py 啟動之前
            Queue 就已經存在。

        一旦成立：

            不受 AI_THRESHOLD 限制。

        直接 Resume。
        """

        try:

            waiting = (
                self.ai_task_repository
                .count_waiting_tasks()
            )

            result = (
                waiting > 0
            )

            logger.info(
                "Existing AI Queue check: "
                f"waiting={waiting}, "
                f"existing={result}"
            )

            return result

        except Exception as e:

            logger.exception(
                "Existing AI Queue check failed: "
                f"{e}"
            )

            return False

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
    # Start Async AI - Threshold Mode
    # ==================================================

    def _start_async_ai(
        self
    ):
        """
        啟動 P2.4 Async AI Scaling。

        此方法只處理：

            本次新 Queue

        使用：

            AIBatchTriggerService
            + AI_THRESHOLD

        Returns
        -------

        bool
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
    # Resume Existing Async AI
    # ==================================================

    def _resume_existing_async_ai(
        self
    ):
        """
        P2.4 Existing Queue Resume。

        與一般 Threshold Trigger
        不同。

        Existing Queue：

            WAITING > 0
                |
                v
            Force Trigger
                |
                v
            AIScheduler
                |
                v
            AIWorkerPool

        不受 AI_THRESHOLD 限制。

        Returns
        -------

        bool
        """

        try:

            waiting = (
                self.ai_task_repository
                .count_waiting_tasks()
            )

            if waiting <= 0:

                logger.info(
                    "No existing AI Queue "
                    "to resume"
                )

                return False

            logger.info(
                "Resuming existing AI Queue: "
                f"waiting={waiting}"
            )

            result = (
                self.ai_batch_trigger
                .force_trigger()
            )

            if result:

                logger.info(
                    "Existing AI Queue "
                    "resume triggered"
                )

            else:

                logger.warning(
                    "Existing AI Queue "
                    "resume failed"
                )

            return result

        except Exception as e:

            logger.exception(
                "Resume existing AI Queue failed: "
                f"{e}"
            )

            return False

    # ==================================================
    # Wait AI Completion
    # ==================================================

    def _wait_for_ai_completion(
        self
    ):
        """
        等待 AI Worker Pool 完成。

        Worker Lifecycle
        仍由 AIWorkerPool 負責。

        Returns
        -------

        bool
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
                # Lifecycle Completed
                # --------------------------------------

                lifecycle_completed = (
                    status.get(
                        "lifecycle_completed",
                        False
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

                if (
                    active_workers == 0
                    and (
                        lifecycle_completed
                        or not pool_running
                    )
                ):

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

            1. Startup Queue Recovery
            2. Existing Queue Detection
            3. Article Collection
            4. Existing Queue Resume
            5. New Queue Threshold Trigger
            6. AI Worker Pool
            7. Knowledge Intelligence
            8. Export

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

        # ==============================================
        #
        # Startup Queue State
        #
        # ==============================================

        startup_queue = {
            "running_before": 0,
            "recovered": 0,
            "waiting": 0
        }

        existing_queue = False

        try:

            # ==========================================
            #
            # Step 0
            #
            # Startup Queue Recovery
            #
            # ==========================================

            logger.info(
                "Starting AI Queue Recovery"
            )

            startup_queue = (
                self._recover_startup_ai_queue()
            )

            # ------------------------------------------
            # Existing Queue
            # ------------------------------------------

            existing_queue = (
                startup_queue.get(
                    "waiting",
                    0
                ) > 0
            )

            if existing_queue:

                logger.info(
                    "Existing AI Queue detected: "
                    f"waiting="
                    f"{startup_queue['waiting']}"
                )

            else:

                logger.info(
                    "No existing AI Queue detected"
                )

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
            # Async AI
            #
            # ==========================================

            logger.info(
                "Start Async AI Scaling"
            )

            # ------------------------------------------
            # Existing Queue Resume
            # ------------------------------------------

            if existing_queue:

                ai_triggered = (
                    self._resume_existing_async_ai()
                )

                if ai_triggered:

                    logger.info(
                        "Existing AI Queue "
                        "successfully resumed"
                    )

                else:

                    logger.warning(
                        "Existing AI Queue "
                        "could not be resumed"
                    )

            # ------------------------------------------
            # New Queue Threshold
            # ------------------------------------------
            #
            # 只有沒有既有 Queue 時，
            # 才進入一般 Threshold Trigger。
            #

            else:

                ai_triggered = (
                    self._start_async_ai()
                )

                if ai_triggered:

                    logger.info(
                        "Async AI Scaling triggered"
                    )

                else:

                    logger.info(
                        "Async AI Scaling not triggered"
                    )

            # ==========================================
            #
            # Step 3
            #
            # Wait For AI
            #
            # ==========================================

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

                if existing_queue:

                    logger.warning(
                        "Existing AI Queue "
                        "was not started"
                    )

                else:

                    logger.info(
                        "AI Batch Threshold "
                        "not reached; "
                        "AI Scheduler not started"
                    )

            # ==========================================
            #
            # Step 4
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
        # Step 5
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
    Backward compatible Application entry。
    """

    app = (
        AutoSearchApplication()
    )

    app.run()


if __name__ == "__main__":

    main()