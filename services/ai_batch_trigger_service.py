"""
services/ai_batch_trigger_service.py

AutoSearch V4

P2.4.8

AI Batch Trigger Service

功能:

1. 檢查 WAITING AI Task 數量
2. Batch Threshold 判斷
3. 啟動 AIScheduler
4. AIScheduler → AIWorkerPool Integration
5. 避免重複啟動 Scheduler
6. Force Trigger
7. Scheduler Lifecycle
8. Batch Status Monitoring
9. Worker Pool Status Monitoring

Flow:

Crawler
    |
    v
ArticleService
    |
    v
AITaskRepository
    |
    v
ai_tasks
    |
    v
AIBatchTriggerService
    |
    | WAITING >= AI_THRESHOLD
    v
AIScheduler
    |
    v
AIWorkerPool
    |       |       |
    v       v       v
 Worker   Worker  Worker
    |       |       |
    +-------+-------+
            |
            v
       AI Analysis


P2.4.8 Integration:

AIBatchTriggerService
        ↓
AIScheduler
        ↓
AIWorkerPool
        ↓
Multiple AIWorker


注意:

本 Service 不負責:

- AI Analysis Logic
- AI Worker Lifecycle
- Worker Recovery
- Task CRUD
- Database CRUD
- Knowledge Processing
- Search Ranking
- Batch Processing Logic


Configuration:

AI_THRESHOLD

由:

config/settings.py

統一管理。

例如:

AI_THRESHOLD = 40

因此本 Service 不應再寫死:

threshold=50
"""

from database.ai_task_repository import (
    AITaskRepository
)

from services.ai_scheduler import (
    AIScheduler
)

from config.settings import (
    AI_THRESHOLD
)

from utils.logger import (
    logger
)


class AIBatchTriggerService:

    """
    AI Batch Trigger Service

    P2.4.8

    負責將:

        WAITING Task
            ↓
        Threshold
            ↓
        Scheduler
            ↓
        Worker Pool

    串接起來。

    Threshold 預設由:

        config.settings.AI_THRESHOLD

    提供。
    """

    # ==================================================
    # Initialize
    # ==================================================

    def __init__(
        self,
        task_repository=None,
        scheduler=None,
        threshold=None
    ):
        """
        初始化 Batch Trigger Service。

        Parameters
        ----------
        task_repository:
            AITaskRepository。

        scheduler:
            AIScheduler。

        threshold:
            WAITING Task 啟動門檻。

            如果未指定:

                使用 config.settings.AI_THRESHOLD
        """

        # ----------------------------------------------
        # Task Repository
        # ----------------------------------------------

        if task_repository is None:

            task_repository = (
                AITaskRepository()
            )

        self.task_repository = (
            task_repository
        )

        # ----------------------------------------------
        # Scheduler
        # ----------------------------------------------

        if scheduler is None:

            scheduler = (
                AIScheduler()
            )

        self.scheduler = scheduler

        # ----------------------------------------------
        # Threshold
        #
        # Central Configuration
        #
        # 優先使用外部傳入值。
        #
        # 未指定時使用:
        #
        # config.settings.AI_THRESHOLD
        # ----------------------------------------------

        if (
            threshold is None
            or threshold < 1
        ):

            threshold = AI_THRESHOLD

        self.threshold = threshold

    # ==================================================
    # Count Waiting Tasks
    # ==================================================

    def count_waiting_tasks(
        self
    ):
        """
        取得目前 WAITING AI Task 數量。

        P2.4 Async AI Scaling

        不能使用:

            get_waiting_tasks()

        再透過 len() 計算。

        因為 get_waiting_tasks()
        本身可能具有 LIMIT。

        例如:

            get_waiting_tasks(limit=10)

        即使資料庫實際有:

            WAITING = 52

        也可能只回傳:

            10

        導致:

            52 >= 40

        被錯誤判斷成:

            10 >= 40

        因此 Batch Threshold
        必須優先使用 Repository:

            count_waiting_tasks()

        Returns
        -------

        int

            WAITING AI Task 數量
        """

        try:

            # ------------------------------------------
            # Preferred Repository API
            #
            # 使用 SQL COUNT
            #
            # SELECT COUNT(*)
            # FROM ai_tasks
            # WHERE status='WAITING'
            # ------------------------------------------

            count_method = getattr(
                self.task_repository,
                "count_waiting_tasks",
                None
            )

            if callable(
                count_method
            ):

                count = (
                    count_method()
                )

                if count is None:

                    return 0

                return int(
                    count
                )

            # ------------------------------------------
            # Compatibility Fallback
            #
            # 舊版 Repository
            # 尚未提供 count_waiting_tasks()
            #
            # 才退回 get_waiting_tasks()
            # ------------------------------------------

            get_method = getattr(
                self.task_repository,
                "get_waiting_tasks",
                None
            )

            if callable(
                get_method
            ):

                tasks = (
                    get_method(
                        limit=None
                    )
                )

                if tasks is None:

                    return 0

                return len(
                    tasks
                )

            return 0

        except Exception as e:

            logger.exception(
                "Count waiting AI tasks failed: "
                f"{e}"
            )

            return 0

    # ==================================================
    # Should Trigger
    # ==================================================

    def should_trigger(
        self
    ):
        """
        判斷是否達到 Batch Threshold。

        條件:

            WAITING >= threshold
        """

        waiting_count = (
            self.count_waiting_tasks()
        )

        result = (
            waiting_count >= self.threshold
        )

        logger.info(
            "AI Batch Trigger check: "
            f"waiting={waiting_count}, "
            f"threshold={self.threshold}, "
            f"trigger={result}"
        )

        return result

    # ==================================================
    # Trigger
    # ==================================================

    def trigger(
        self
    ):
        """
        執行 Batch Trigger。

        Flow:

            WAITING Task
                ↓
            Threshold
                ↓
            AIScheduler
                ↓
            AIWorkerPool

        Returns
        -------

        bool

            True:
                Scheduler 已啟動
                或 Scheduler 已經執行。

            False:
                Threshold 未達到
                或 Scheduler 啟動失敗。
        """

        try:

            waiting_count = (
                self.count_waiting_tasks()
            )

            # ------------------------------------------
            # Threshold Not Reached
            # ------------------------------------------

            if waiting_count < self.threshold:

                logger.info(
                    "AI Batch Trigger skipped: "
                    f"waiting={waiting_count}, "
                    f"threshold={self.threshold}"
                )

                return False

            # ------------------------------------------
            # Scheduler Already Running
            # ------------------------------------------

            if getattr(
                self.scheduler,
                "running",
                False
            ):

                logger.info(
                    "AI Scheduler already running"
                )

                return True

            # ------------------------------------------
            # Trigger Scheduler
            # ------------------------------------------

            logger.info(
                "AI Batch Trigger reached: "
                f"waiting={waiting_count}, "
                f"threshold={self.threshold}"
            )

            result = (
                self.scheduler.start()
            )

            # ------------------------------------------
            # Scheduler Start Failed
            # ------------------------------------------

            if result is False:

                logger.warning(
                    "AI Batch Trigger failed: "
                    "Scheduler could not start"
                )

                return False

            logger.info(
                "AI Scheduler started by "
                "Batch Trigger"
            )

            return True

        except Exception as e:

            logger.exception(
                f"AI Batch Trigger failed: {e}"
            )

            return False

    # ==================================================
    # Check And Trigger
    # ==================================================

    def check_and_trigger(
        self
    ):
        """
        檢查 WAITING AI Task
        並觸發 Scheduler。

        這是 ArticleService /
        Pending Task Monitor
        建議使用的入口。
        """

        return self.trigger()

    # ==================================================
    # Force Trigger
    # ==================================================

    def force_trigger(
        self
    ):
        """
        強制啟動 Scheduler。

        不檢查 Threshold。

        用途:

        - 手動測試
        - Debug
        - Queue 不足 Threshold
          但仍希望立即處理
        """

        try:

            # ------------------------------------------
            # Already Running
            # ------------------------------------------

            if getattr(
                self.scheduler,
                "running",
                False
            ):

                logger.info(
                    "AI Scheduler already running"
                )

                return True

            # ------------------------------------------
            # Start
            # ------------------------------------------

            logger.info(
                "AI Scheduler force trigger"
            )

            result = (
                self.scheduler.start()
            )

            # ------------------------------------------
            # Start Failed
            # ------------------------------------------

            if result is False:

                logger.warning(
                    "AI Scheduler force start failed"
                )

                return False

            logger.info(
                "AI Scheduler force started"
            )

            return True

        except Exception as e:

            logger.exception(
                f"Force AI Scheduler failed: {e}"
            )

            return False

    # ==================================================
    # Stop
    # ==================================================

    def stop(
        self
    ):
        """
        停止 Scheduler。

        Scheduler 會負責進一步停止
        Worker Pool。
        """

        try:

            if not getattr(
                self.scheduler,
                "running",
                False
            ):

                return True

            result = (
                self.scheduler.stop()
            )

            if result is False:

                logger.warning(
                    "AI Scheduler stop failed"
                )

                return False

            logger.info(
                "AI Scheduler stopped "
                "by Batch Trigger Service"
            )

            return True

        except Exception as e:

            logger.exception(
                f"Stop AI Scheduler failed: {e}"
            )

            return False

    # ==================================================
    # Scheduler Status
    # ==================================================

    def get_scheduler_status(
        self
    ):
        """
        取得 Scheduler Status。

        優先使用:

            AIScheduler.get_status()

        如果 Scheduler 尚未提供
        get_status()，則 fallback
        到 running。
        """

        if self.scheduler is None:

            return None

        getter = getattr(
            self.scheduler,
            "get_status",
            None
        )

        if callable(
            getter
        ):

            return getter()

        return {
            "running": (
                getattr(
                    self.scheduler,
                    "running",
                    False
                )
            )
        }

    # ==================================================
    # Worker Pool Status
    # ==================================================

    def get_worker_pool_status(
        self
    ):
        """
        取得 Worker Pool Status。

        Flow:

            Batch Trigger
                ↓
            Scheduler
                ↓
            Worker Pool
        """

        if self.scheduler is None:

            return None

        # ----------------------------------------------
        # Preferred Scheduler API
        # ----------------------------------------------

        getter = getattr(
            self.scheduler,
            "get_worker_pool_status",
            None
        )

        if callable(
            getter
        ):

            return getter()

        # ----------------------------------------------
        # Fallback
        # ----------------------------------------------

        worker_pool = getattr(
            self.scheduler,
            "worker_pool",
            None
        )

        if worker_pool is None:

            return None

        pool_getter = getattr(
            worker_pool,
            "get_status",
            None
        )

        if callable(
            pool_getter
        ):

            return pool_getter()

        return None

    # ==================================================
    # Status
    # ==================================================

    def get_status(
        self
    ):
        """
        取得完整 Batch Trigger Status。

        Returns:

        {
            "waiting": 40,
            "threshold": 40,
            "trigger": True,
            "scheduler_running": True,
            "scheduler": {...},
            "worker_pool": {...}
        }
        """

        waiting_count = (
            self.count_waiting_tasks()
        )

        scheduler_status = (
            self.get_scheduler_status()
        )

        worker_pool_status = (
            self.get_worker_pool_status()
        )

        return {

            # ------------------------------------------
            # Batch
            # ------------------------------------------

            "waiting": (
                waiting_count
            ),

            "threshold": (
                self.threshold
            ),

            "trigger": (
                waiting_count
                >= self.threshold
            ),

            # ------------------------------------------
            # Scheduler
            # ------------------------------------------

            "scheduler_running": (
                getattr(
                    self.scheduler,
                    "running",
                    False
                )
            ),

            "scheduler": (
                scheduler_status
            ),

            # ------------------------------------------
            # Worker Pool
            # ------------------------------------------

            "worker_pool": (
                worker_pool_status
            )

        }

    # ==================================================
    # Repr
    # ==================================================

    def __repr__(
        self
    ):

        return (
            "AIBatchTriggerService("
            f"threshold={self.threshold}, "
            f"scheduler="
            f"{self.scheduler!r}"
            ")"
        )
