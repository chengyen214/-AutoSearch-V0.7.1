
"""
tests/test_ai_scheduler_worker_pool.py

AutoSearch V4

P2.4.6.2

Test:

AI Scheduler / Multi-Worker Pool Integration

驗證：

1. Scheduler 建立 Worker Pool
2. Worker Pool Dependency Injection
3. Scheduler Start -> Worker Pool Start
4. Scheduler Stop -> Worker Pool Stop
5. Scheduler 不重複啟動 Worker Pool
6. Scheduler Status
7. Scheduler Lifecycle
8. Multi-Worker Pool Integration
"""

from unittest.mock import MagicMock

from services.ai_scheduler import AIScheduler


# ==================================================
# Mock Worker Pool
# ==================================================

class MockWorkerPool:

    def __init__(
        self,
        worker_count=3
    ):

        self.worker_count = (
            worker_count
        )

        self.running = False

        self.start_count = 0

        self.stop_count = 0

    # ----------------------------------------------
    # Start
    # ----------------------------------------------

    def start(self):

        self.start_count += 1

        self.running = True

        return True

    # ----------------------------------------------
    # Stop
    # ----------------------------------------------

    def stop(self):

        self.stop_count += 1

        self.running = False

        return True

    # ----------------------------------------------
    # Status
    # ----------------------------------------------

    def get_status(self):

        return {

            "running": self.running,

            "worker_count": (
                self.worker_count
            ),

            "active_workers": (
                self.worker_count
                if self.running
                else 0
            )

        }


# ==================================================
# Test Scheduler Worker Pool Injection
# ==================================================

def test_scheduler_worker_pool_injection():

    pool = MockWorkerPool(
        worker_count=3
    )

    scheduler = AIScheduler(
        interval=10,
        worker_pool=pool
    )

    assert (
        scheduler.worker_pool
        is pool
    )


# ==================================================
# Test Scheduler Start Worker Pool
# ==================================================

def test_scheduler_start_worker_pool():

    pool = MockWorkerPool(
        worker_count=3
    )

    scheduler = AIScheduler(
        interval=10,
        worker_pool=pool
    )

    result = scheduler.start()

    assert result is True

    assert scheduler.running is True

    assert pool.running is True

    assert pool.start_count == 1

    scheduler.stop()


# ==================================================
# Test Scheduler Stop Worker Pool
# ==================================================

def test_scheduler_stop_worker_pool():

    pool = MockWorkerPool(
        worker_count=3
    )

    scheduler = AIScheduler(
        interval=10,
        worker_pool=pool
    )

    scheduler.start()

    result = scheduler.stop()

    assert result is True

    assert scheduler.running is False

    assert pool.running is False

    assert pool.stop_count == 1


# ==================================================
# Test Scheduler Does Not Start Pool Twice
# ==================================================

def test_scheduler_start_worker_pool_only_once():

    pool = MockWorkerPool(
        worker_count=3
    )

    scheduler = AIScheduler(
        interval=10,
        worker_pool=pool
    )

    first = scheduler.start()

    second = scheduler.start()

    assert first is True

    assert second is True

    assert pool.start_count == 1

    scheduler.stop()


# ==================================================
# Test Scheduler Stop Already Stopped
# ==================================================

def test_scheduler_stop_worker_pool_already_stopped():

    pool = MockWorkerPool(
        worker_count=3
    )

    scheduler = AIScheduler(
        interval=10,
        worker_pool=pool
    )

    result = scheduler.stop()

    assert result is True

    assert pool.stop_count == 0


# ==================================================
# Test Worker Pool Status
# ==================================================

def test_scheduler_worker_pool_status():

    pool = MockWorkerPool(
        worker_count=3
    )

    scheduler = AIScheduler(
        interval=10,
        worker_pool=pool
    )

    scheduler.start()

    status = scheduler.get_status()

    assert status["running"] is True

    assert (
        status["worker_pool"]
        is not None
    )

    scheduler.stop()


# ==================================================
# Test Multi Worker Count
# ==================================================

def test_scheduler_multi_worker_count():

    pool = MockWorkerPool(
        worker_count=5
    )

    scheduler = AIScheduler(
        interval=10,
        worker_pool=pool
    )

    assert (
        scheduler.worker_pool
        .worker_count
        == 5
    )


# ==================================================
# Test Pool Start Failure
# ==================================================

def test_scheduler_worker_pool_start_failure():

    pool = MagicMock()

    pool.start.return_value = False

    scheduler = AIScheduler(
        interval=10,
        worker_pool=pool
    )

    result = scheduler.start()

    assert result is False

    assert scheduler.running is False

    pool.start.assert_called_once()


# ==================================================
# Test Pool Stop Failure
# ==================================================

def test_scheduler_worker_pool_stop_failure():

    pool = MagicMock()

    pool.running = True

    pool.stop.return_value = False

    scheduler = AIScheduler(
        interval=10,
        worker_pool=pool
    )

    scheduler.running = True

    result = scheduler.stop()

    assert result is False

    pool.stop.assert_called_once()


# ==================================================
# Test Scheduler Repr
# ==================================================

def test_scheduler_worker_pool_repr():

    pool = MockWorkerPool(
        worker_count=3
    )

    scheduler = AIScheduler(
        interval=10,
        worker_pool=pool
    )

    result = repr(
        scheduler
    )

    assert (
        "AIScheduler"
        in result
    )

    assert (
        "worker_pool"
        in result
    )
