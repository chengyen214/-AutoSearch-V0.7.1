"""
tests/test_ai_scheduler.py

AutoSearch V4

P2.4.4

Test:

Async AI Scheduler

測試:

1. Initialization
2. Run Once
3. Worker Lock
4. Worker Error
5. Start
6. Duplicate Start
7. Stop
8. Stop When Already Stopped
9. Is Running
10. Status
11. Invalid Interval
12. Worker Injection
13. Repr
"""

import time

from unittest.mock import (
    MagicMock,
    patch
)

from services.ai_scheduler import (
    AIScheduler
)


# ==================================================
#
# Mock Worker
#
# ==================================================

class MockWorker:

    def __init__(
        self,
        result=0
    ):

        self.result = result

        self.run_count = 0

    def run_once(
        self
    ):

        self.run_count += 1

        return self.result


# ==================================================
#
# Initialization
#
# ==================================================

def test_ai_scheduler_initialization():

    scheduler = AIScheduler(
        interval=10
    )

    assert scheduler.interval == 10

    assert scheduler.running is False

    assert scheduler.thread is None

    assert scheduler.worker is not None

    assert scheduler.lock is not None


# ==================================================
#
# Run Once Success
#
# ==================================================

def test_ai_scheduler_run_once():

    scheduler = AIScheduler(
        interval=10
    )

    scheduler.worker = MagicMock()

    scheduler.worker.run_once.return_value = 5

    result = scheduler.run_once()

    assert result == 5

    scheduler.worker.run_once.assert_called_once()


# ==================================================
#
# Run Once None Result
#
# ==================================================

def test_ai_scheduler_run_once_none():

    scheduler = AIScheduler()

    scheduler.worker = MagicMock()

    scheduler.worker.run_once.return_value = None

    result = scheduler.run_once()

    assert result == 0

    scheduler.worker.run_once.assert_called_once()


# ==================================================
#
# Run Once Worker Error
#
# ==================================================

def test_ai_scheduler_run_once_worker_error():

    scheduler = AIScheduler()

    scheduler.worker = MagicMock()

    scheduler.worker.run_once.side_effect = (
        Exception(
            "Worker error"
        )
    )

    result = scheduler.run_once()

    assert result == 0

    scheduler.worker.run_once.assert_called_once()

    assert scheduler.lock.locked() is False


# ==================================================
#
# Lock Protection
#
# ==================================================

def test_ai_scheduler_lock():

    scheduler = AIScheduler()

    scheduler.worker = MagicMock()

    scheduler.worker.run_once.return_value = 1

    # ----------------------------------------------
    # Manually acquire lock
    # ----------------------------------------------

    scheduler.lock.acquire()

    try:

        result = scheduler.run_once()

        assert result == 0

        scheduler.worker.run_once.assert_not_called()

    finally:

        scheduler.lock.release()


# ==================================================
#
# Lock Released After Success
#
# ==================================================

def test_ai_scheduler_lock_released_after_success():

    scheduler = AIScheduler()

    scheduler.worker = MagicMock()

    scheduler.worker.run_once.return_value = 3

    result = scheduler.run_once()

    assert result == 3

    assert scheduler.lock.locked() is False


# ==================================================
#
# Worker Injection
#
# ==================================================

def test_ai_scheduler_worker_injection():

    worker = MockWorker(
        result=7
    )

    scheduler = AIScheduler(
        interval=10,
        worker=worker
    )

    result = scheduler.run_once()

    assert result == 7

    assert worker.run_count == 1

    assert scheduler.worker is worker


# ==================================================
#
# Invalid Interval
#
# ==================================================

def test_ai_scheduler_invalid_interval():

    scheduler = AIScheduler(
        interval=0
    )

    assert scheduler.interval == 30


# ==================================================
#
# None Interval
#
# ==================================================

def test_ai_scheduler_none_interval():

    scheduler = AIScheduler(
        interval=None
    )

    assert scheduler.interval == 30


# ==================================================
#
# Start
#
# ==================================================

def test_ai_scheduler_start():

    scheduler = AIScheduler(
        interval=1
    )

    scheduler.worker = MagicMock()

    scheduler.worker.run_once.return_value = 0

    result = scheduler.start()

    assert result is True

    assert scheduler.running is True

    assert scheduler.thread is not None

    # ----------------------------------------------
    # Stop
    # ----------------------------------------------

    scheduler.stop()

    assert scheduler.running is False

    assert scheduler.thread is None


# ==================================================
#
# Duplicate Start
#
# ==================================================

def test_ai_scheduler_duplicate_start():

    scheduler = AIScheduler(
        interval=1
    )

    scheduler.worker = MagicMock()

    scheduler.worker.run_once.return_value = 0

    first = scheduler.start()

    second = scheduler.start()

    assert first is True

    assert second is True

    assert scheduler.running is True

    scheduler.stop()


# ==================================================
#
# Stop
#
# ==================================================

def test_ai_scheduler_stop():

    scheduler = AIScheduler(
        interval=1
    )

    scheduler.worker = MagicMock()

    scheduler.worker.run_once.return_value = 0

    scheduler.start()

    assert scheduler.running is True

    result = scheduler.stop()

    assert result is True

    assert scheduler.running is False

    assert scheduler.thread is None


# ==================================================
#
# Stop Already Stopped
#
# ==================================================

def test_ai_scheduler_stop_already_stopped():

    scheduler = AIScheduler()

    assert scheduler.running is False

    result = scheduler.stop()

    assert result is True

    assert scheduler.running is False


# ==================================================
#
# Is Running
#
# ==================================================

def test_ai_scheduler_is_running():

    scheduler = AIScheduler()

    assert scheduler.is_running() is False

    scheduler.running = True

    assert scheduler.is_running() is True

    scheduler.running = False

    assert scheduler.is_running() is False


# ==================================================
#
# Status Initial
#
# ==================================================

def test_ai_scheduler_status_initial():

    scheduler = AIScheduler(
        interval=15
    )

    result = scheduler.get_status()

    assert result["running"] is False

    assert result["thread_alive"] is False

    assert result["interval"] == 15


# ==================================================
#
# Status Running
#
# ==================================================

def test_ai_scheduler_status_running():

    scheduler = AIScheduler(
        interval=1
    )

    scheduler.worker = MagicMock()

    scheduler.worker.run_once.return_value = 0

    scheduler.start()

    try:

        result = scheduler.get_status()

        assert result["running"] is True

        assert result["thread_alive"] is True

        assert result["interval"] == 1

    finally:

        scheduler.stop()


# ==================================================
#
# Start Failure
#
# ==================================================

@patch(
    "services.ai_scheduler.threading.Thread"
)
def test_ai_scheduler_start_failure(
    mock_thread
):

    mock_thread.side_effect = (
        Exception(
            "Thread start error"
        )
    )

    scheduler = AIScheduler()

    result = scheduler.start()

    assert result is False

    assert scheduler.running is False

    assert scheduler.thread is None


# ==================================================
#
# Run Once Multiple Times
#
# ==================================================

def test_ai_scheduler_run_once_multiple():

    scheduler = AIScheduler()

    scheduler.worker = MagicMock()

    scheduler.worker.run_once.side_effect = [
        1,
        2,
        3
    ]

    assert scheduler.run_once() == 1

    assert scheduler.run_once() == 2

    assert scheduler.run_once() == 3

    assert (
        scheduler.worker.run_once.call_count
        == 3
    )


# ==================================================
#
# Repr
#
# ==================================================

def test_ai_scheduler_repr():

    scheduler = AIScheduler(
        interval=20
    )

    result = repr(
        scheduler
    )

    assert (
        "AIScheduler"
        in result
    )

    assert (
        "interval=20"
        in result
    )
