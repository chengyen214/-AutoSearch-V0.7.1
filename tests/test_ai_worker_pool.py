"""
tests/test_ai_worker_pool.py

AutoSearch V4

P2.4.6.1

Test:

AI Worker Pool
"""

from unittest.mock import MagicMock

from services.ai_worker_pool import (
    AIWorkerPool
)


# ==================================================
# Mock Worker
# ==================================================

class MockWorker:

    instances = []

    def __init__(self):

        self.run_once_called = False

        MockWorker.instances.append(
            self
        )

    def run_once(self):

        self.run_once_called = True

        return 1


class FailingWorker:

    def run_once(self):

        raise Exception(
            "Worker failed"
        )


# ==================================================
# Helpers
# ==================================================

def reset_mock_workers():

    MockWorker.instances = []


# ==================================================
# Test Create Workers
# ==================================================

def test_create_workers():

    reset_mock_workers()

    pool = AIWorkerPool(
        worker_count=3,
        worker_class=MockWorker
    )

    workers = pool.create_workers()

    assert len(workers) == 3

    assert pool.get_worker_count() == 3


# ==================================================
# Test Create Workers Only Once
# ==================================================

def test_create_workers_only_once():

    reset_mock_workers()

    pool = AIWorkerPool(
        worker_count=3,
        worker_class=MockWorker
    )

    first = pool.create_workers()

    second = pool.create_workers()

    assert first is second

    assert len(first) == 3

    assert len(MockWorker.instances) == 3


# ==================================================
# Test Worker Count
# ==================================================

def test_worker_count():

    reset_mock_workers()

    pool = AIWorkerPool(
        worker_count=5,
        worker_class=MockWorker
    )

    pool.create_workers()

    assert pool.get_worker_count() == 5


# ==================================================
# Test Default Worker Count
# ==================================================

def test_default_worker_count():

    pool = AIWorkerPool(
        worker_class=MockWorker
    )

    assert pool.worker_count == 1


# ==================================================
# Test Invalid Worker Count
# ==================================================

def test_invalid_worker_count():

    pool = AIWorkerPool(
        worker_count=0,
        worker_class=MockWorker
    )

    assert pool.worker_count == 1


# ==================================================
# Test Start
# ==================================================

def test_start():

    reset_mock_workers()

    pool = AIWorkerPool(
        worker_count=3,
        worker_class=MockWorker
    )

    result = pool.start()

    assert result is True

    assert pool.running is True

    assert pool.get_worker_count() == 3

    pool.join()


# ==================================================
# Test Start Worker Execution
# ==================================================

def test_start_workers_execute():

    reset_mock_workers()

    pool = AIWorkerPool(
        worker_count=3,
        worker_class=MockWorker
    )

    pool.start()

    pool.join()

    assert len(
        MockWorker.instances
    ) == 3

    for worker in MockWorker.instances:

        assert worker.run_once_called is True


# ==================================================
# Test Start Already Running
# ==================================================

def test_start_already_running():

    reset_mock_workers()

    pool = AIWorkerPool(
        worker_count=2,
        worker_class=MockWorker
    )

    first = pool.start()

    second = pool.start()

    assert first is True

    assert second is True

    assert pool.running is True

    pool.join()


# ==================================================
# Test Stop
# ==================================================

def test_stop():

    reset_mock_workers()

    pool = AIWorkerPool(
        worker_count=2,
        worker_class=MockWorker
    )

    pool.start()

    pool.join()

    result = pool.stop()

    assert result is True

    assert pool.running is False


# ==================================================
# Test Stop Already Stopped
# ==================================================

def test_stop_already_stopped():

    pool = AIWorkerPool(
        worker_count=2,
        worker_class=MockWorker
    )

    result = pool.stop()

    assert result is True

    assert pool.running is False


# ==================================================
# Test Join
# ==================================================

def test_join():

    reset_mock_workers()

    pool = AIWorkerPool(
        worker_count=3,
        worker_class=MockWorker
    )

    pool.start()

    pool.join()

    assert pool.get_active_worker_count() == 0


# ==================================================
# Test Active Worker Count
# ==================================================

def test_active_worker_count():

    reset_mock_workers()

    pool = AIWorkerPool(
        worker_count=3,
        worker_class=MockWorker
    )

    assert pool.get_active_worker_count() == 0

    pool.start()

    pool.join()

    assert pool.get_active_worker_count() == 0


# ==================================================
# Test Status
# ==================================================

def test_status():

    reset_mock_workers()

    pool = AIWorkerPool(
        worker_count=3,
        worker_class=MockWorker
    )

    status = pool.get_status()

    assert status["running"] is False

    assert status["worker_count"] == 0

    assert status["active_workers"] == 0


# ==================================================
# Test Status After Start
# ==================================================

def test_status_after_start():

    reset_mock_workers()

    pool = AIWorkerPool(
        worker_count=3,
        worker_class=MockWorker
    )

    pool.start()

    pool.join()

    status = pool.get_status()

    assert status["running"] is True

    assert status["worker_count"] == 3

    assert status["active_workers"] == 0

    pool.stop()


# ==================================================
# Test Worker Error Isolation
# ==================================================

def test_worker_error_isolation():

    pool = AIWorkerPool(
        worker_count=3,
        worker_class=FailingWorker
    )

    result = pool.start()

    assert result is True

    pool.join()

    assert pool.running is True

    assert pool.get_worker_count() == 3

    pool.stop()


# ==================================================
# Test Worker Class Injection
# ==================================================

def test_worker_class_injection():

    reset_mock_workers()

    pool = AIWorkerPool(
        worker_count=2,
        worker_class=MockWorker
    )

    pool.create_workers()

    assert all(
        isinstance(
            worker,
            MockWorker
        )
        for worker in pool.workers
    )


# ==================================================
# Test Repr
# ==================================================

def test_repr():

    pool = AIWorkerPool(
        worker_count=3,
        worker_class=MockWorker
    )

    result = repr(pool)

    assert "AIWorkerPool" in result

    assert "worker_count=3" in result

    assert "running=False" in result
