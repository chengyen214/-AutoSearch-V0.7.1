"""
tests/test_ai_worker_pool_reliability.py

AutoSearch V4

P2.4.7.1

AI Worker Pool Reliability Tests

測試:

1. 單一 Worker 失敗
2. Worker Exception Isolation
3. 其他 Worker 繼續執行
4. Pool 不因 Worker Exception 崩潰
5. Worker Failure 不影響 Pool Status
6. 多 Worker Failure Isolation
7. Worker 正常執行與失敗 Worker 並存
8. Pool Stop 後狀態正確
"""

import time

from services.ai_worker_pool import (
    AIWorkerPool
)


# ==================================================
# Mock Workers
# ==================================================


class SuccessfulWorker:
    """
    正常 Worker。
    """

    execution_count = 0

    def run_once(self):

        type(self).execution_count += 1

        return 1


class FailingWorker:
    """
    永遠發生 Exception 的 Worker。
    """

    execution_count = 0

    def run_once(self):

        type(self).execution_count += 1

        raise RuntimeError(
            "Mock worker failure"
        )


class MixedWorker:
    """
    混合 Worker。

    第一個 Worker 失敗，
    第二個 Worker 正常執行。
    """

    created_count = 0

    def __init__(self):

        type(self).created_count += 1

        self.worker_id = (
            type(self).created_count
        )

    def run_once(self):

        if self.worker_id == 1:

            raise RuntimeError(
                "First worker failed"
            )

        return 1


# ==================================================
# Fixtures / Helpers
# ==================================================


def reset_worker_state():

    SuccessfulWorker.execution_count = 0

    FailingWorker.execution_count = 0

    MixedWorker.created_count = 0


# ==================================================
# Worker Failure Isolation
# ==================================================


def test_worker_failure_does_not_crash_pool():

    reset_worker_state()

    pool = AIWorkerPool(
        worker_count=1,
        worker_class=FailingWorker
    )

    result = pool.start()

    assert result is True

    # ----------------------------------------------
    # Worker Thread 執行後應該自行結束
    # ----------------------------------------------

    pool.join(
        timeout=1
    )

    # ----------------------------------------------
    # Pool 本身仍然存在
    # ----------------------------------------------

    assert pool.workers

    pool.stop()


# ==================================================
# Multiple Worker Failure Isolation
# ==================================================


def test_multiple_worker_failure_isolation():

    reset_worker_state()

    pool = AIWorkerPool(
        worker_count=3,
        worker_class=FailingWorker
    )

    result = pool.start()

    assert result is True

    pool.join(
        timeout=1
    )

    assert (
        FailingWorker.execution_count
        == 3
    )

    pool.stop()


# ==================================================
# Mixed Worker
# ==================================================


def test_failed_worker_does_not_affect_other_workers():

    reset_worker_state()

    pool = AIWorkerPool(
        worker_count=2,
        worker_class=MixedWorker
    )

    result = pool.start()

    assert result is True

    pool.join(
        timeout=1
    )

    # ----------------------------------------------
    # 兩個 Worker 都應該被執行
    # ----------------------------------------------

    assert (
        MixedWorker.created_count
        == 2
    )

    pool.stop()


# ==================================================
# Pool Status After Worker Failure
# ==================================================


def test_pool_status_after_worker_failure():

    reset_worker_state()

    pool = AIWorkerPool(
        worker_count=1,
        worker_class=FailingWorker
    )

    pool.start()

    pool.join(
        timeout=1
    )

    status = (
        pool.get_status()
    )

    assert (
        status["worker_count"]
        == 1
    )

    assert (
        status["active_workers"]
        == 0
    )

    pool.stop()


# ==================================================
# Successful Worker
# ==================================================


def test_successful_worker_still_executes():

    reset_worker_state()

    pool = AIWorkerPool(
        worker_count=2,
        worker_class=SuccessfulWorker
    )

    result = pool.start()

    assert result is True

    pool.join(
        timeout=1
    )

    assert (
        SuccessfulWorker.execution_count
        == 2
    )

    pool.stop()


# ==================================================
# Failed And Successful Worker Isolation
# ==================================================


def test_failed_worker_does_not_stop_successful_worker():

    reset_worker_state()

    class WorkerA:

        execution_count = 0

        def run_once(self):

            type(self).execution_count += 1

            raise RuntimeError(
                "Worker A failed"
            )

    class WorkerB:

        execution_count = 0

        def run_once(self):

            type(self).execution_count += 1

            return 1

    class WorkerFactory:

        created_count = 0

        def __new__(cls):

            cls.created_count += 1

            if cls.created_count == 1:

                return WorkerA()

            return WorkerB()

    pool = AIWorkerPool(
        worker_count=2,
        worker_class=WorkerFactory
    )

    result = pool.start()

    assert result is True

    pool.join(
        timeout=1
    )

    assert (
        WorkerA.execution_count
        == 1
    )

    assert (
        WorkerB.execution_count
        == 1
    )

    pool.stop()


# ==================================================
# Pool Can Stop After Worker Failure
# ==================================================


def test_pool_can_stop_after_worker_failure():

    reset_worker_state()

    pool = AIWorkerPool(
        worker_count=2,
        worker_class=FailingWorker
    )

    pool.start()

    pool.join(
        timeout=1
    )

    result = pool.stop()

    assert result is True

    status = (
        pool.get_status()
    )

    assert (
        status["running"]
        is False
    )


# ==================================================
# Pool Restart After Failure
# ==================================================


def test_pool_can_start_again_after_worker_failure():

    reset_worker_state()

    pool = AIWorkerPool(
        worker_count=1,
        worker_class=FailingWorker
    )

    result = pool.start()

    assert result is True

    pool.join(
        timeout=1
    )

    pool.stop()

    # ----------------------------------------------
    # 再次啟動
    # ----------------------------------------------

    result = pool.start()

    assert result is True

    pool.join(
        timeout=1
    )

    pool.stop()


# ==================================================
# Worker Exception Must Not Escape
# ==================================================


def test_worker_exception_isolated_from_start():

    reset_worker_state()

    pool = AIWorkerPool(
        worker_count=1,
        worker_class=FailingWorker
    )

    # ----------------------------------------------
    # start() 不應因 Worker Exception 直接拋出
    # ----------------------------------------------

    result = pool.start()

    assert result is True

    pool.join(
        timeout=1
    )

    pool.stop()


# ==================================================
# Worker Count Remains Stable
# ==================================================


def test_worker_count_remains_stable_after_failure():

    reset_worker_state()

    pool = AIWorkerPool(
        worker_count=3,
        worker_class=FailingWorker
    )

    pool.start()

    pool.join(
        timeout=1
    )

    assert (
        pool.get_worker_count()
        == 3
    )

    pool.stop()
