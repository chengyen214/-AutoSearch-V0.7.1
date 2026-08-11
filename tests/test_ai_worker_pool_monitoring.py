"""
tests/test_ai_worker_pool_monitoring.py

AutoSearch V4

P2.4.8

AI Worker Pool Monitoring Tests

測試:

1. Pool Monitoring Status
2. Worker Count
3. Active Worker Count
4. Completed Worker Count
5. Failed Worker Count
6. Running Status
7. Worker Failure 不影響 Pool Monitoring
8. Worker Success 不影響 Pool Monitoring
9. Monitoring 不觸發 Worker Restart
10. Monitoring Status 結構穩定
"""

import time

from services.ai_worker_pool import (
    AIWorkerPool
)


# ==================================================
# Mock Workers
# ==================================================


class SuccessfulWorker:

    execution_count = 0

    def run_once(self):

        type(self).execution_count += 1

        return 1


class FailingWorker:

    execution_count = 0

    def run_once(self):

        type(self).execution_count += 1

        raise RuntimeError(
            "Mock worker failure"
        )


class SlowWorker:

    execution_count = 0

    def run_once(self):

        type(self).execution_count += 1

        time.sleep(
            0.2
        )

        return 1


# ==================================================
# Helpers
# ==================================================


def reset_worker_state():

    SuccessfulWorker.execution_count = 0

    FailingWorker.execution_count = 0

    SlowWorker.execution_count = 0


# ==================================================
# Basic Monitoring
# ==================================================


def test_monitoring_status_before_start():

    reset_worker_state()

    pool = AIWorkerPool(
        worker_count=3,
        worker_class=SuccessfulWorker
    )

    status = (
        pool.get_status()
    )

    assert status["running"] is False

    assert (
        status["worker_count"]
        == 0
    )

    assert (
        status["active_workers"]
        == 0
    )


# ==================================================
# Worker Count
# ==================================================


def test_monitoring_worker_count():

    reset_worker_state()

    pool = AIWorkerPool(
        worker_count=3,
        worker_class=SuccessfulWorker
    )

    pool.create_workers()

    status = (
        pool.get_status()
    )

    assert (
        status["worker_count"]
        == 3
    )


# ==================================================
# Active Worker Count
# ==================================================


def test_monitoring_active_worker_count():

    reset_worker_state()

    pool = AIWorkerPool(
        worker_count=3,
        worker_class=SlowWorker
    )

    pool.start()

    time.sleep(
        0.05
    )

    status = (
        pool.get_status()
    )

    assert (
        status["active_workers"]
        == 3
    )

    pool.join(
        timeout=1
    )


# ==================================================
# Completed Workers
# ==================================================


def test_monitoring_completed_worker_count():

    reset_worker_state()

    pool = AIWorkerPool(
        worker_count=3,
        worker_class=SuccessfulWorker
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
        == 3
    )

    assert (
        status["active_workers"]
        == 0
    )

    assert (
        status["completed_workers"]
        == 3
    )


# ==================================================
# Failed Workers
# ==================================================


def test_monitoring_failed_worker_count():

    reset_worker_state()

    pool = AIWorkerPool(
        worker_count=2,
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
        == 2
    )

    assert (
        status["active_workers"]
        == 0
    )

    assert (
        status["failed_workers"]
        == 2
    )


# ==================================================
# Mixed Worker
# ==================================================


def test_monitoring_mixed_worker_pool():

    reset_worker_state()

    class WorkerA:

        def run_once(self):

            raise RuntimeError(
                "Worker A failed"
            )

    class WorkerB:

        def run_once(self):

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

    pool.start()

    pool.join(
        timeout=1
    )

    status = (
        pool.get_status()
    )

    assert (
        status["worker_count"]
        == 2
    )

    assert (
        status["active_workers"]
        == 0
    )

    assert (
        status["completed_workers"]
        == 2
    )


# ==================================================
# Pool Running Status
# ==================================================


def test_monitoring_running_status():

    reset_worker_state()

    pool = AIWorkerPool(
        worker_count=2,
        worker_class=SlowWorker
    )

    pool.start()

    time.sleep(
        0.05
    )

    status = (
        pool.get_status()
    )

    assert (
        status["running"]
        is True
    )

    pool.stop()

    status = (
        pool.get_status()
    )

    assert (
        status["running"]
        is False
    )


# ==================================================
# Failure Does Not Crash Monitoring
# ==================================================


def test_monitoring_survives_worker_failure():

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

    status = (
        pool.get_status()
    )

    assert (
        status is not None
    )

    assert (
        status["worker_count"]
        == 3
    )

    assert (
        status["active_workers"]
        == 0
    )


# ==================================================
# Monitoring Does Not Restart Worker
# ==================================================


def test_monitoring_does_not_restart_worker():

    reset_worker_state()

    pool = AIWorkerPool(
        worker_count=2,
        worker_class=FailingWorker
    )

    pool.start()

    pool.join(
        timeout=1
    )

    first_count = (
        FailingWorker.execution_count
    )

    status = (
        pool.get_status()
    )

    assert (
        status["active_workers"]
        == 0
    )

    # ----------------------------------------------
    # Monitoring 不應該觸發任何 Worker Restart
    # ----------------------------------------------

    status = (
        pool.get_status()
    )

    second_count = (
        FailingWorker.execution_count
    )

    assert (
        second_count
        == first_count
    )


# ==================================================
# Status Structure
# ==================================================


def test_monitoring_status_structure():

    reset_worker_state()

    pool = AIWorkerPool(
        worker_count=2,
        worker_class=SuccessfulWorker
    )

    pool.start()

    pool.join(
        timeout=1
    )

    status = (
        pool.get_status()
    )

    required_keys = {

        "running",

        "worker_count",

        "active_workers",

        "completed_workers",

        "failed_workers"

    }

    assert (
        required_keys
        .issubset(
            status.keys()
        )
    )


# ==================================================
# Worker Count Stability
# ==================================================


def test_monitoring_worker_count_stability():

    reset_worker_state()

    pool = AIWorkerPool(
        worker_count=3,
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
        == 3
    )

    # ----------------------------------------------
    # Monitoring 不應該建立新的 Worker
    # ----------------------------------------------

    status = (
        pool.get_status()
    )

    assert (
        status["worker_count"]
        == 3
    )

    assert (
        len(pool.workers)
        == 3
    )