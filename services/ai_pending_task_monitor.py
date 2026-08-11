"""
services/ai_pending_task_monitor.py

AutoSearch V4

P2.4.3

AI Pending Task Monitor

功能:

1. 監控 WAITING AI Task
2. 計算 Pending Task 數量
3. Threshold 判斷
4. 提供 Pending Task Status
5. 提供 Queue Monitor API
6. Repository Error 保護
7. Threshold 可配置

Flow:

AITaskRepository
        |
        v
ai_tasks
        |
        v
AIPendingTaskMonitor
        |
        +---- count_waiting_tasks()
        |
        +---- is_threshold_reached()
        |
        +---- check()
        |
        +---- get_status()
        |
        v
AI Batch Trigger / Scheduler


P2.4.3 Default:

WAITING Task >= 50
        |
        v
Threshold Reached


注意:

本 Monitor 不負責：

- AI Analysis
- AI Worker
- Scheduler 啟動
- Task CRUD
- Knowledge Processing

Scheduler / Batch Trigger
由其他 Service 負責。
"""

from database.ai_task_repository import (
    AITaskRepository
)

from utils.logger import logger


class AIPendingTaskMonitor:

    """
    AI Pending Task Monitor

    P2.4.3

    負責監控目前 AI Task Queue
    中的 WAITING Task 數量。

    主要提供：

        count_waiting_tasks()
        is_threshold_reached()
        has_pending_tasks()
        check()
        get_status()

    Threshold 預設為 50，
    且可以由外部設定。
    """

    # ==================================================
    # Initialize
    # ==================================================

    def __init__(
        self,
        task_repository=None,
        threshold=50
    ):
        """
        Parameters
        ----------
        task_repository:
            AITaskRepository

        threshold:
            Pending AI Task Threshold

        Default:
            50
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
        # Threshold
        # ----------------------------------------------

        if threshold is None or threshold < 1:

            threshold = 50

        self.threshold = threshold

    # ==================================================
    # Count Waiting Tasks
    # ==================================================

    def count_waiting_tasks(
        self
    ):
        """
        取得目前 WAITING AI Task 數量。

        Repository:

            get_waiting_tasks(
                limit=None
            )

        Returns
        -------

        int

            WAITING Task 數量
        """

        try:

            tasks = (
                self.task_repository
                .get_waiting_tasks(
                    limit=None
                )
            )

            if tasks is None:

                return 0

            return len(tasks)

        except Exception as e:

            logger.exception(
                "Count waiting AI tasks failed: "
                f"{e}"
            )

            return 0

    # ==================================================
    # Has Pending Tasks
    # ==================================================

    def has_pending_tasks(
        self
    ):
        """
        判斷目前是否存在 WAITING Task。

        Returns
        -------

        bool
        """

        waiting_count = (
            self.count_waiting_tasks()
        )

        result = (
            waiting_count > 0
        )

        logger.info(
            "AI Pending Task check: "
            f"waiting={waiting_count}, "
            f"pending={result}"
        )

        return result

    # ==================================================
    # Threshold Reached
    # ==================================================

    def is_threshold_reached(
        self
    ):
        """
        判斷 WAITING Task 是否達到 Threshold。

        條件：

            waiting >= threshold

        Returns
        -------

        bool
        """

        waiting_count = (
            self.count_waiting_tasks()
        )

        result = (
            waiting_count >= self.threshold
        )

        logger.info(
            "AI Pending Task threshold check: "
            f"waiting={waiting_count}, "
            f"threshold={self.threshold}, "
            f"reached={result}"
        )

        return result

    # ==================================================
    # Check
    # ==================================================

    def check(
        self
    ):
        """
        執行 Pending Task Monitor。

        Returns
        -------

        bool

            True:
                WAITING >= threshold

            False:
                WAITING < threshold
        """

        return self.is_threshold_reached()

    # ==================================================
    # Get Status
    # ==================================================

    def get_status(
        self
    ):
        """
        取得目前 Pending Task 狀態。

        Returns
        -------

        dict

        {
            "waiting": 50,
            "threshold": 50,
            "pending": True,
            "threshold_reached": True
        }
        """

        waiting_count = (
            self.count_waiting_tasks()
        )

        return {

            "waiting": waiting_count,

            "threshold": self.threshold,

            "pending": (
                waiting_count > 0
            ),

            "threshold_reached": (
                waiting_count >= self.threshold
            )

        }

    # ==================================================
    # Get Waiting Tasks
    # ==================================================

    def get_waiting_tasks(
        self,
        limit=None
    ):
        """
        取得目前 WAITING Tasks。

        這裡只負責監控層的查詢，
        不修改 Task。

        Parameters
        ----------

        limit:
            最大 Task 數量。

        Returns
        -------

        list
        """

        try:

            return (
                self.task_repository
                .get_waiting_tasks(
                    limit=limit
                )
            )

        except Exception as e:

            logger.exception(
                "Get waiting AI tasks failed: "
                f"{e}"
            )

            return []

    # ==================================================
    # Remaining Capacity
    # ==================================================

    def get_remaining_threshold(
        self
    ):
        """
        取得距離 Threshold 還剩多少 Task。

        Example:

            waiting=30
            threshold=50

            return 20

        如果已經達到 Threshold：

            return 0
        """

        waiting_count = (
            self.count_waiting_tasks()
        )

        remaining = (
            self.threshold
            - waiting_count
        )

        if remaining < 0:

            remaining = 0

        return remaining

    # ==================================================
    # Threshold Progress
    # ==================================================

    def get_progress(
        self
    ):
        """
        取得 Threshold 進度。

        Returns
        -------

        float

            0.0 ~ 1.0

        Example:

            waiting=25
            threshold=50

            0.5
        """

        waiting_count = (
            self.count_waiting_tasks()
        )

        progress = (
            waiting_count
            / self.threshold
        )

        if progress > 1:

            progress = 1.0

        return progress

    # ==================================================
    # Repr
    # ==================================================

    def __repr__(
        self
    ):

        return (
            "AIPendingTaskMonitor("
            f"threshold={self.threshold}, "
            f"task_repository="
            f"{self.task_repository!r}"
            ")"
        )