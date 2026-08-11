"""
services/ai_scheduler.py

AutoSearch V4

P2.4.8.1

Async AI Scheduler

功能:

1. Background AI Worker Runner
2. Periodic AI Task Processing
3. Single Run Mode
4. Worker Lock Protection
5. Scheduler Lifecycle Management
6. Async Background Execution
7. 避免 Scheduler 重複啟動
8. AI Worker Pool Integration
9. Multi-Worker Scaling
10. Worker Monitoring

Flow:

AIBatchTriggerService
        |
        v
AIScheduler
        |
        v
AIWorkerPool
    |    |    |
    v    v    v
 Worker Worker Worker
    |    |    |
    +----+----+
         |
         v
     AI Analysis Pipeline

P2.4.8.1:

Scheduler
    ↓
AIWorkerPool
    ↓
Worker Monitoring
    ↓
completed_workers
failed_workers

注意:

本 Scheduler 不負責:

- AI Analysis Logic
- AI Task CRUD
- Database
- Knowledge Processing
- Batch Threshold 判斷

Batch Threshold 由:

    AIBatchTriggerService

負責。

Worker Lifecycle 由:

    AIWorkerPool

負責。
"""

import time
import threading

from ai.worker import AIWorker

from services.ai_worker_pool import (
    AIWorkerPool
)

from utils.logger import logger


class AIScheduler:

    """
    Async AI Scheduler

    P2.4.8.1

    負責:

    - Background Worker
    - Periodic Task Processing
    - Scheduler Lifecycle
    - Worker Lock
    - Async Execution
    - Worker Pool Integration
    - Multi-Worker Scaling
    - Worker Monitoring

    不負責:

    - AI Analysis
    - Database
    - Task CRUD
    - Batch Threshold
    - Knowledge Processing
    """

    # ==================================================
    # Initialize
    # ==================================================

    def __init__(
        self,
        interval=30,
        worker=None,
        worker_pool=None
    ):
        """
        初始化 Scheduler。

        Parameters
        ----------
        interval:
            Worker 執行間隔，單位秒。

        worker:
            單一 AIWorker。

            保留 P2.4.4
            Legacy / Test 相容性。

        worker_pool:
            AIWorkerPool。

            P2.4.6.2
            Multi-Worker Scaling。
        """

        # ----------------------------------------------
        # Interval
        # ----------------------------------------------

        if interval is None or interval < 1:

            interval = 30

        self.interval = interval

        # ----------------------------------------------
        # Worker
        # ----------------------------------------------

        if worker is None:

            worker = AIWorker()

        self.worker = worker

        # ----------------------------------------------
        # Worker Pool
        # ----------------------------------------------

        if worker_pool is None:

            worker_pool = AIWorkerPool(
                worker_count=1,
                worker_class=type(
                    worker
                )
            )

        self.worker_pool = (
            worker_pool
        )

        # ----------------------------------------------
        # Scheduler State
        # ----------------------------------------------

        self.running = False

        self.thread = None

        # ----------------------------------------------
        # Worker Lock
        # ----------------------------------------------

        self.lock = threading.Lock()

    # ==================================================
    # Run Once
    # ==================================================

    def run_once(
        self
    ):
        """
        執行一次 AI Worker。

        P2.4.4 Legacy Mode。

        注意:

        此方法維持 Legacy 行為，
        不直接取代 Worker Pool。

        Returns
        -------

        int
            AI Worker 處理數量。
        """

        # ----------------------------------------------
        # Worker Lock
        # ----------------------------------------------

        if not self.lock.acquire(
            blocking=False
        ):

            logger.warning(
                "AI Scheduler worker "
                "already running"
            )

            return 0

        try:

            logger.info(
                "AI Scheduler executing worker"
            )

            result = (
                self.worker.run_once()
            )

            # ------------------------------------------
            # Normalize Result
            # ------------------------------------------

            if result is None:

                result = 0

            logger.info(
                "AI Scheduler completed "
                f"count={result}"
            )

            return result

        except Exception as e:

            logger.exception(
                f"AI Scheduler worker failed: {e}"
            )

            return 0

        finally:

            self.lock.release()

    # ==================================================
    # Run Worker Pool
    # ==================================================

    def _run_worker_pool(
        self
    ):
        """
        執行 Worker Pool。

        Worker Pool 負責:

        - 建立 Workers
        - 啟動 Workers
        - Worker Lifecycle

        Scheduler 只負責:

        - Pool 啟動
        - Pool 狀態控制
        """

        if self.worker_pool is None:

            return 0

        # ----------------------------------------------
        # Already Running
        # ----------------------------------------------

        pool_running = getattr(
            self.worker_pool,
            "running",
            False
        )

        if pool_running is True:

            logger.info(
                "AI Scheduler worker pool "
                "already running"
            )

            return 1

        # ----------------------------------------------
        # Start Worker Pool
        # ----------------------------------------------

        result = (
            self.worker_pool.start()
        )

        if result is False:

            logger.warning(
                "AI Scheduler worker pool "
                "failed to start"
            )

            return 0

        logger.info(
            "AI Scheduler worker pool "
            "started successfully"
        )

        return 1

    # ==================================================
    # Start Worker Pool
    # ==================================================

    def _start_worker_pool(
        self
    ):
        """
        同步啟動 Worker Pool。
        """

        if self.worker_pool is None:

            return True

        # ----------------------------------------------
        # Already Running
        # ----------------------------------------------

        pool_running = getattr(
            self.worker_pool,
            "running",
            False
        )

        if pool_running is True:

            logger.info(
                "AI Scheduler worker pool "
                "already running"
            )

            return True

        # ----------------------------------------------
        # Start Worker Pool
        # ----------------------------------------------

        result = (
            self.worker_pool.start()
        )

        if result is False:

            logger.warning(
                "AI Scheduler worker pool "
                "failed to start"
            )

            return False

        logger.info(
            "AI Scheduler worker pool "
            "started successfully"
        )

        return True

    # ==================================================
    # Background Loop
    # ==================================================

    def _loop(
        self
    ):
        """
        Scheduler Background Loop。

        Scheduler
            ↓
        Worker Pool
            ↓
        Multiple Workers
        """

        logger.info(
            "AI Scheduler background loop started"
        )

        while self.running:

            try:

                # --------------------------------------
                # Worker Pool
                # --------------------------------------

                self._run_worker_pool()

            except Exception as e:

                logger.exception(
                    f"AI Scheduler loop error: {e}"
                )

            # ------------------------------------------
            # Interruptible Wait
            # ------------------------------------------

            end_time = (
                time.time()
                + self.interval
            )

            while self.running:

                remaining = (
                    end_time
                    - time.time()
                )

                if remaining <= 0:

                    break

                time.sleep(
                    min(
                        remaining,
                        0.1
                    )
                )

        logger.info(
            "AI Scheduler background loop stopped"
        )

    # ==================================================
    # Start
    # ==================================================

    def start(
        self
    ):
        """
        啟動 Background Scheduler。

        1. 啟動 Worker Pool
        2. 建立 Scheduler Thread
        3. 啟動 Background Loop
        """

        # ----------------------------------------------
        # Already Running
        # ----------------------------------------------

        if self.running:

            logger.warning(
                "AI Scheduler already started"
            )

            return True

        try:

            # ------------------------------------------
            # Start Worker Pool First
            # ------------------------------------------

            pool_started = (
                self._start_worker_pool()
            )

            if pool_started is False:

                logger.warning(
                    "AI Scheduler failed "
                    "because Worker Pool "
                    "could not start"
                )

                return False

            # ------------------------------------------
            # Set State
            # ------------------------------------------

            self.running = True

            # ------------------------------------------
            # Create Background Thread
            # ------------------------------------------

            self.thread = threading.Thread(

                target=self._loop,

                name="AI-Scheduler",

                daemon=True

            )

            # ------------------------------------------
            # Start Thread
            # ------------------------------------------

            self.thread.start()

            logger.info(
                "AI Scheduler thread started "
                f"with worker pool="
                f"{self.worker_pool!r}"
            )

            return True

        except Exception as e:

            self.running = False

            self.thread = None

            logger.exception(
                f"AI Scheduler start failed: {e}"
            )

            return False

    # ==================================================
    # Stop
    # ==================================================

    def stop(
        self
    ):
        """
        停止 Background Scheduler。

        1. 停止 Scheduler Loop
        2. 等待 Scheduler Thread
        3. 停止 Worker Pool
        """

        # ----------------------------------------------
        # Already Stopped
        # ----------------------------------------------

        if not self.running:

            return True

        logger.info(
            "Stopping AI Scheduler"
        )

        # ----------------------------------------------
        # Stop Loop
        # ----------------------------------------------

        self.running = False

        # ----------------------------------------------
        # Wait Scheduler Thread
        # ----------------------------------------------

        thread = self.thread

        if (
            thread is not None
            and thread.is_alive()
            and thread is not threading.current_thread()
        ):

            thread.join(
                timeout=5
            )

        self.thread = None

        # ----------------------------------------------
        # Stop Worker Pool
        # ----------------------------------------------

        if self.worker_pool is not None:

            pool_result = (
                self.worker_pool.stop()
            )

            if pool_result is False:

                logger.warning(
                    "AI Scheduler worker pool "
                    "failed to stop"
                )

                return False

        logger.info(
            "AI Scheduler stopped"
        )

        return True

    # ==================================================
    # Is Running
    # ==================================================

    def is_running(
        self
    ):
        """
        取得 Scheduler 是否正在執行。
        """

        return self.running

    # ==================================================
    # Worker Pool Running
    # ==================================================

    def is_worker_pool_running(
        self
    ):
        """
        取得 Worker Pool 是否正在執行。
        """

        if self.worker_pool is None:

            return False

        return (
            getattr(
                self.worker_pool,
                "running",
                False
            )
            is True
        )

    # ==================================================
    # Worker Count
    # ==================================================

    def get_worker_count(
        self
    ):
        """
        取得 Worker Pool Worker 數量。
        """

        if self.worker_pool is None:

            return 0

        getter = getattr(
            self.worker_pool,
            "get_worker_count",
            None
        )

        if callable(getter):

            return getter()

        return getattr(
            self.worker_pool,
            "worker_count",
            0
        )

    # ==================================================
    # Active Worker Count
    # ==================================================

    def get_active_worker_count(
        self
    ):
        """
        取得目前 Active Worker 數量。
        """

        if self.worker_pool is None:

            return 0

        getter = getattr(
            self.worker_pool,
            "get_active_worker_count",
            None
        )

        if callable(getter):

            return getter()

        return 0

    # ==================================================
    # Completed Worker Count
    # ==================================================

    def get_completed_worker_count(
        self
    ):
        """
        取得已完成 Worker 數量。

        P2.4.8.1

        優先使用 AIWorkerPool
        的正式 API。

        如果 Pool 沒有提供正式 API，
        則從 Pool Status 取得。

        Compatibility fallback 可避免
        舊版 WorkerPool 造成 Scheduler Crash。
        """

        if self.worker_pool is None:

            return 0

        # ----------------------------------------------
        # Preferred API
        # ----------------------------------------------

        getter = getattr(
            self.worker_pool,
            "get_completed_worker_count",
            None
        )

        if callable(getter):

            try:

                return getter()

            except Exception as e:

                logger.exception(
                    "AI Scheduler failed to "
                    "get completed worker count: "
                    f"{e}"
                )

        # ----------------------------------------------
        # Status Fallback
        # ----------------------------------------------

        status_getter = getattr(
            self.worker_pool,
            "get_status",
            None
        )

        if callable(status_getter):

            try:

                status = status_getter()

                return status.get(
                    "completed_workers",
                    0
                )

            except Exception as e:

                logger.exception(
                    "AI Scheduler failed to "
                    "read completed worker "
                    f"status: {e}"
                )

        return 0

    # ==================================================
    # Failed Worker Count
    # ==================================================

    def get_failed_worker_count(
        self
    ):
        """
        取得失敗 Worker 數量。

        P2.4.8.1

        Worker Failure Isolation
        不會因為 Worker failure
        讓 Scheduler Crash。
        """

        if self.worker_pool is None:

            return 0

        # ----------------------------------------------
        # Preferred API
        # ----------------------------------------------

        getter = getattr(
            self.worker_pool,
            "get_failed_worker_count",
            None
        )

        if callable(getter):

            try:

                return getter()

            except Exception as e:

                logger.exception(
                    "AI Scheduler failed to "
                    "get failed worker count: "
                    f"{e}"
                )

        # ----------------------------------------------
        # Status Fallback
        # ----------------------------------------------

        status_getter = getattr(
            self.worker_pool,
            "get_status",
            None
        )

        if callable(status_getter):

            try:

                status = status_getter()

                return status.get(
                    "failed_workers",
                    0
                )

            except Exception as e:

                logger.exception(
                    "AI Scheduler failed to "
                    "read failed worker "
                    f"status: {e}"
                )

        return 0

    # ==================================================
    # Worker Pool Status
    # ==================================================

    def get_worker_pool_status(
        self
    ):
        """
        取得完整 Worker Pool Status。

        P2.4.8.1

        Returns
        -------

        dict

        {
            "running": True,
            "worker_count": 3,
            "active_workers": 1,
            "completed_workers": 2,
            "failed_workers": 0
        }
        """

        if self.worker_pool is None:

            return None

        # ----------------------------------------------
        # Preferred API
        # ----------------------------------------------

        getter = getattr(
            self.worker_pool,
            "get_status",
            None
        )

        if callable(getter):

            try:

                status = getter()

                if isinstance(
                    status,
                    dict
                ):

                    return status

            except Exception as e:

                logger.exception(
                    "AI Scheduler failed to "
                    f"get worker pool status: {e}"
                )

        # ----------------------------------------------
        # Compatibility Fallback
        # ----------------------------------------------

        return {

            "running": (
                self.is_worker_pool_running()
            ),

            "worker_count": (
                self.get_worker_count()
            ),

            "active_workers": (
                self.get_active_worker_count()
            ),

            "completed_workers": (
                self.get_completed_worker_count()
            ),

            "failed_workers": (
                self.get_failed_worker_count()
            )

        }

    # ==================================================
    # Status
    # ==================================================

    def get_status(
        self
    ):
        """
        取得完整 Scheduler Status。

        P2.4.8.1

        Returns
        -------

        dict

        {
            "running": True,
            "thread_alive": True,
            "interval": 30,
            "worker_pool": <AIWorkerPool>,
            "worker_count": 3,
            "active_workers": 1,
            "completed_workers": 2,
            "failed_workers": 0,
            "worker_pool_running": True
        }
        """

        thread_alive = False

        if self.thread is not None:

            thread_alive = (
                self.thread.is_alive()
            )

        # ----------------------------------------------
        # Worker Pool Running
        # ----------------------------------------------

        pool_running = (
            self.is_worker_pool_running()
        )

        # ----------------------------------------------
        # Worker Monitoring
        # ----------------------------------------------

        completed_workers = (
            self.get_completed_worker_count()
        )

        failed_workers = (
            self.get_failed_worker_count()
        )

        return {

            "running": (
                self.running
            ),

            "thread_alive": (
                thread_alive
            ),

            "interval": (
                self.interval
            ),

            "worker_pool": (
                self.worker_pool
            ),

            "worker_count": (
                self.get_worker_count()
            ),

            "active_workers": (
                self.get_active_worker_count()
            ),

            "completed_workers": (
                completed_workers
            ),

            "failed_workers": (
                failed_workers
            ),

            "worker_pool_running": (
                pool_running
            )

        }

    # ==================================================
    # Repr
    # ==================================================

    def __repr__(
        self
    ):

        return (
            "AIScheduler("
            f"interval={self.interval}, "
            f"running={self.running}, "
            f"worker_count="
            f"{self.get_worker_count()}, "
            f"worker_pool="
            f"{self.worker_pool!r}"
            ")"
        )


# ==================================================
# Standalone Runner
# ==================================================

if __name__ == "__main__":

    scheduler = AIScheduler(
        interval=30
    )

    try:

        scheduler.start()

        while scheduler.is_running():

            time.sleep(1)

    except KeyboardInterrupt:

        logger.info(
            "KeyboardInterrupt received"
        )

        scheduler.stop()
