"""
services/ai_worker_pool.py

AutoSearch V4

P2.4.9

AI Worker Pool
Reliability + Monitoring + Queue Drain

功能:

1. 建立多個 AI Worker
2. 管理 Worker 數量
3. 啟動 Worker Pool
4. 停止 Worker Pool
5. 管理 Worker Lifecycle
6. 等待 Worker 結束
7. 提供 Pool Status
8. Worker Failure Isolation
9. Worker Monitoring
10. Pool Lifecycle Completion Detection
11. Queue Drain
12. Continuous AI Task Processing

Architecture:

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
AI Analysis

P2.4.9 Queue Drain:

WAITING
   |
   v
Worker.run_once()
   |
   +----> claim batch
   |          |
   |          v
   |      process batch
   |          |
   |          v
   |      claim next batch
   |
   +----> no WAITING task
              |
              v
        Worker.run_once()
        returns
              |
              v
        Worker finished

注意:

Queue Drain 的實際邏輯由:

    AIWorker.run_once()

負責。

AIWorkerPool 不再重複執行
run_once() Queue Drain。

因此:

    AIWorker.run_once()
        |
        +--> claim_waiting_tasks()
        +--> process_task()
        +--> repeat
        +--> no tasks
        +--> return total_success

AIWorkerPool 只負責:

    Worker Thread Lifecycle
    Worker Monitoring
    Worker Failure Isolation

Threshold 只負責「是否啟動」。

一旦 Pool 啟動，
不再因為 WAITING < Threshold
而提前停止。

Pool Worker 會呼叫:

    AIWorker.run_once()

由 Worker 自己持續處理
WAITING Queue。

P2.4.9 Reliability:

- 單一 Worker 失敗不得 Crash Pool
- Worker failure 不影響其他 Worker
- Worker failure 不自動建立 replacement Worker
- Pool 可以正常 stop()
- Pool lifecycle 完成後可以再次 start()
- Worker count 保持穩定
- Scheduler 可以偵測 Pool 已完成
- Worker 持續 Drain WAITING Queue

AIWorkerPool 不負責:

- AI Analysis Logic
- Task CRUD
- Batch Threshold
- Scheduler
- Database
- Knowledge Processing
- Worker Auto Recovery
- Queue Drain Logic

AIWorkerPool 負責:

- Worker 建立
- Worker 數量
- Worker Lifecycle
- Worker 啟動 / 停止
- Worker Failure Isolation
- Worker Monitoring
- Worker Thread 管理
"""


import threading

from ai.worker import AIWorker

from utils.logger import logger


class AIWorkerPool:

    """
    AI Worker Pool

    P2.4.9

    管理多個 AIWorker。

    一次 Pool lifecycle:

        start()
            |
            v
        Worker Threads
            |
            v
        AIWorker.run_once()
            |
            v
        Worker 自己 Drain Queue
            |
            v
        Queue Empty
            |
            v
        run_once() return
            |
            v
        Worker Thread 結束
            |
            v
        Pool lifecycle completed

    Queue Drain 原則:

        Queue Drain 完整責任
        由 AIWorker.run_once()
        負責。

        AIWorkerPool 不再重複
        呼叫 run_once()。

    Worker failure:

        Worker A failure
              |
              v
        Worker A Thread 結束
              |
              +------> Worker B 繼續
              |
              +------> Pool 保持可用

    不自動建立 replacement Worker。
    """

    # ==================================================
    # Initialize
    # ==================================================

    def __init__(
        self,
        worker_count=1,
        worker_class=None
    ):
        """
        初始化 Worker Pool。
        """

        # ----------------------------------------------
        # Worker Class
        # ----------------------------------------------

        if worker_class is None:

            worker_class = AIWorker

        self.worker_class = (
            worker_class
        )

        # ----------------------------------------------
        # Worker Count
        # ----------------------------------------------

        if (
            worker_count is None
            or worker_count < 1
        ):

            worker_count = 1

        self.worker_count = (
            worker_count
        )

        # ----------------------------------------------
        # Workers
        # ----------------------------------------------

        self.workers = []

        # ----------------------------------------------
        # Threads
        # ----------------------------------------------

        self.threads = []

        # ----------------------------------------------
        # Monitoring
        # ----------------------------------------------

        self.completed_workers = 0

        self.failed_workers = 0

        # ----------------------------------------------
        # Lifecycle
        # ----------------------------------------------

        self.running = False

        self.lifecycle_completed = False

        # ----------------------------------------------
        # Lock
        # ----------------------------------------------

        self.lock = threading.RLock()

    # ==================================================
    # Create Workers
    # ==================================================

    def create_workers(
        self
    ):
        """
        建立 Worker。

        Worker Object 可以重複使用。

        注意:

        Worker Thread 不重複使用。
        """

        with self.lock:

            # ------------------------------------------
            # Already Created
            # ------------------------------------------

            if self.workers:

                return self.workers

            # ------------------------------------------
            # Create Workers
            # ------------------------------------------

            for _ in range(
                self.worker_count
            ):

                worker = (
                    self.worker_class()
                )

                self.workers.append(
                    worker
                )

        logger.info(
            "AI Worker Pool created: "
            f"workers={len(self.workers)}"
        )

        return self.workers

    # ==================================================
    # Normalize Worker Result
    # ==================================================

    def _normalize_worker_result(
        self,
        result
    ):
        """
        統一 Worker.run_once() 回傳值。

        AIWorker.run_once()
        正常回傳:

            int

        例如:

            10
            5
            0

        Legacy Worker:

            None

        None 視為 0。

        注意:

        不允許負數。

        負數代表 Worker 回傳異常資料，
        為避免錯誤監控資料，
        一律視為 0。
        """

        if result is None:

            return 0

        try:

            result = int(
                result
            )

        except (
            TypeError,
            ValueError
        ):

            logger.warning(
                "AI Worker Pool received "
                "invalid worker result: "
                f"{result!r}"
            )

            return 0

        if result < 0:

            return 0

        return result

    # ==================================================
    # Run Worker
    # ==================================================

    def _run_worker(
        self,
        worker
    ):
        """
        執行單一 Worker Thread。

        P2.4.9:

        Queue Drain 已由:

            AIWorker.run_once()

        負責。

        Pool 不再執行:

            while True:
                worker.run_once()

        避免：

            Pool Queue Drain
                +
            Worker Queue Drain

        造成雙重 Queue Drain。

        正確流程:

            Worker Thread
                |
                v
            worker.run_once()
                |
                v
            AIWorker 自己持續：
                |
                +--> claim batch
                +--> process batch
                +--> claim next batch
                +--> process
                +--> ...
                +--> no WAITING task
                |
                v
            return total_success
                |
                v
            Worker completed

        Worker failure:

            failed_workers += 1

        不會:

            - Crash Pool
            - Stop other Workers
            - Restart Worker
            - Create replacement Worker
        """

        try:

            logger.info(
                "AI Worker Pool worker started"
            )

            # ------------------------------------------
            # Execute Worker Lifecycle
            # ------------------------------------------

            result = (
                worker.run_once()
            )

            processed = (
                self._normalize_worker_result(
                    result
                )
            )

            logger.info(
                "AI Worker Pool worker "
                f"completed processed={processed}"
            )

            # ------------------------------------------
            # Successful Worker Completion
            # ------------------------------------------

            with self.lock:

                self.completed_workers += 1

        except Exception as e:

            # ------------------------------------------
            # Worker Failure
            # ------------------------------------------

            with self.lock:

                self.failed_workers += 1

            logger.exception(
                "AI Worker Pool worker failed: "
                f"{e}"
            )

        finally:

            logger.info(
                "AI Worker Pool worker stopped"
            )

            # ------------------------------------------
            # Check Lifecycle
            # ------------------------------------------

            self._check_lifecycle_completion()

    # ==================================================
    # Check Lifecycle Completion
    # ==================================================

    def _check_lifecycle_completion(
        self
    ):
        """
        判斷目前 Pool Lifecycle
        是否已經全部完成。

        重要：

        此方法可能由 Worker Thread 自己呼叫。

        因此不能單純：

            thread.is_alive()

        因為目前 Worker Thread
        在執行 finally 時本身仍然是 alive。

        正確判斷：

            排除 current_thread()

        流程:

            Worker A 完成
                |
                v
            current_thread = A
                |
                v
            A 不計入 alive
                |
                v
            Worker B / C 若仍 alive
                |
                v
            Pool 繼續 running

        最後一個 Worker:

            Worker A 完成
                |
                v
            A 不計入 alive
                |
                v
            沒有其他 Worker
                |
                v
            running = False
            lifecycle_completed = True
        """

        with self.lock:

            if not self.threads:

                return

            current_thread = (
                threading.current_thread()
            )

            # ------------------------------------------
            # Check Other Worker Threads
            #
            # 關鍵修正：
            #
            # 排除目前正在執行
            # _check_lifecycle_completion()
            # 的 Worker Thread。
            # ------------------------------------------

            alive = any(

                thread is not current_thread

                and thread.is_alive()

                for thread in self.threads

            )

            if alive:

                return

            # ------------------------------------------
            # All Other Workers Finished
            # ------------------------------------------

            self.running = False

            self.lifecycle_completed = True

        logger.info(
            "AI Worker Pool lifecycle completed: "
            f"completed={self.completed_workers}, "
            f"failed={self.failed_workers}"
        )

    # ==================================================
    # Start
    # ==================================================

    def start(
        self
    ):
        """
        啟動 Worker Pool。

        每次 start():

            Worker Threads
                |
                v
            AIWorker.run_once()
                |
                v
            Worker 自己 Drain Queue
                |
                v
            Worker 完成
                |
                v
            lifecycle completed

        Returns
        -------

        bool
        """

        try:

            with self.lock:

                # --------------------------------------
                # Already Running
                # --------------------------------------

                if self.running:

                    logger.info(
                        "AI Worker Pool already running"
                    )

                    return True

                # --------------------------------------
                # Create Workers
                # --------------------------------------

                self.create_workers()

                # --------------------------------------
                # Remove Old Thread References
                # --------------------------------------

                self.threads = []

                # --------------------------------------
                # Reset Monitoring
                # --------------------------------------

                self.completed_workers = 0

                self.failed_workers = 0

                self.lifecycle_completed = False

                # --------------------------------------
                # Set Running
                # --------------------------------------

                self.running = True

                # --------------------------------------
                # Start Workers
                # --------------------------------------

                for worker in self.workers:

                    thread = threading.Thread(

                        target=self._run_worker,

                        args=(worker,),

                        name="AI-Worker",

                        daemon=True

                    )

                    self.threads.append(
                        thread
                    )

                    thread.start()

            logger.info(
                "AI Worker Pool started: "
                f"workers={len(self.workers)}"
            )

            return True

        except Exception as e:

            with self.lock:

                self.running = False

                self.lifecycle_completed = True

            logger.exception(
                "AI Worker Pool start failed: "
                f"{e}"
            )

            return False

    # ==================================================
    # Stop
    # ==================================================

    def stop(
        self
    ):
        """
        停止 Worker Pool。

        不強制 terminate Worker。

        Worker 收到 stop request 後，
        會在目前 AIWorker.run_once()
        完成後結束。

        注意:

        AIWorker.run_once()
        本身負責 Queue Drain。

        如果 Worker 正在執行 AI Analysis，
        stop() 不會中斷該分析。

        同樣地，
        stop() 不會強制中斷
        AIWorker.run_once()。
        """

        try:

            with self.lock:

                # --------------------------------------
                # Already Stopped
                # --------------------------------------

                if not self.running:

                    return True

                # --------------------------------------
                # Stop Request
                # --------------------------------------

                self.running = False

                threads = list(
                    self.threads
                )

            # ------------------------------------------
            # Wait Threads
            # ------------------------------------------

            for thread in threads:

                if thread.is_alive():

                    thread.join(
                        timeout=5
                    )

            self._check_lifecycle_completion()

            logger.info(
                "AI Worker Pool stopped"
            )

            return True

        except Exception as e:

            logger.exception(
                "AI Worker Pool stop failed: "
                f"{e}"
            )

            return False

    # ==================================================
    # Join
    # ==================================================

    def join(
        self,
        timeout=None
    ):
        """
        等待所有 Worker Thread 結束。

        不會建立新的 Worker。

        不會 Restart Worker。
        """

        threads = list(
            self.threads
        )

        for thread in threads:

            if thread.is_alive():

                thread.join(
                    timeout=timeout
                )

        self._check_lifecycle_completion()

    # ==================================================
    # Is Running
    # ==================================================

    def is_running(
        self
    ):
        """
        取得 Pool 是否正在執行。
        """

        with self.lock:

            return self.running

    # ==================================================
    # Is Completed
    # ==================================================

    def is_completed(
        self
    ):
        """
        取得目前 Pool Lifecycle
        是否已完成。
        """

        with self.lock:

            return (
                self.lifecycle_completed
            )

    # ==================================================
    # Worker Count
    # ==================================================

    def get_worker_count(
        self
    ):
        """
        取得 Worker Object 數量。
        """

        with self.lock:

            return len(
                self.workers
            )

    # ==================================================
    # Active Worker Count
    # ==================================================

    def get_active_worker_count(
        self
    ):
        """
        取得目前仍在執行的
        Worker Thread 數量。
        """

        with self.lock:

            threads = list(
                self.threads
            )

        return sum(

            1

            for thread in threads

            if thread.is_alive()

        )

    # ==================================================
    # Completed Worker Count
    # ==================================================

    def get_completed_worker_count(
        self
    ):
        """
        取得成功完成 Worker 數量。

        注意:

        一個 Worker 即使處理：

            10 + 10 + 5

        仍然只算：

            completed_workers = 1

        因為 Queue Drain
        已經由同一個
        AIWorker.run_once()
        完成。
        """

        with self.lock:

            return (
                self.completed_workers
            )

    # ==================================================
    # Failed Worker Count
    # ==================================================

    def get_failed_worker_count(
        self
    ):
        """
        取得失敗 Worker 數量。
        """

        with self.lock:

            return (
                self.failed_workers
            )

    # ==================================================
    # Lifecycle Completed
    # ==================================================

    def is_lifecycle_completed(
        self
    ):
        """
        P2.4.9

        取得目前 Pool Lifecycle
        是否已完成。

        與 is_completed()
        相同用途。

        提供額外 API，
        方便 Scheduler / Service
        使用。
        """

        return self.is_completed()

    # ==================================================
    # Status
    # ==================================================

    def get_status(
        self
    ):
        """
        取得完整 Worker Pool Status。

        Returns
        -------

        dict

        {
            "running": True,
            "lifecycle_completed": False,
            "worker_count": 3,
            "active_workers": 3,
            "completed_workers": 0,
            "failed_workers": 0
        }
        """

        return {

            "running": (
                self.is_running()
            ),

            "lifecycle_completed": (
                self.is_completed()
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
    # Repr
    # ==================================================

    def __repr__(
        self
    ):

        return (
            "AIWorkerPool("
            f"worker_count="
            f"{self.worker_count}, "
            f"running="
            f"{self.running}, "
            f"lifecycle_completed="
            f"{self.lifecycle_completed}"
            ")"
        )