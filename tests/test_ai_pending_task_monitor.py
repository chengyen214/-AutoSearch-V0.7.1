"""
tests/test_ai_pending_task_monitor.py

AutoSearch V4

P2.4.3

Pending Task Monitor Test

功能:

    監控 AI Task Queue

測試:

    1. WAITING Task Count
    2. Pending Detection
    3. Threshold Detection
    4. Empty Queue
    5. Repository Exception
    6. Check
    7. Status
"""

from unittest.mock import MagicMock

from services.ai_pending_task_monitor import (
    AIPendingTaskMonitor
)


# ==================================================
#
# Mock Task
#
# ==================================================

class MockTask:

    def __init__(
        self,
        status="WAITING"
    ):

        self.status = status


# ==================================================
#
# Factory
#
# ==================================================

def create_monitor(
    waiting_count=0,
    threshold=50
):

    repository = MagicMock()

    repository.get_waiting_tasks.return_value = [
        MockTask()
        for _ in range(waiting_count)
    ]

    monitor = AIPendingTaskMonitor(
        task_repository=repository,
        threshold=threshold
    )

    return (
        monitor,
        repository
    )


# ==================================================
#
# Test Count Waiting Tasks
#
# ==================================================

def test_count_waiting_tasks():

    monitor, repository = (
        create_monitor(
            waiting_count=10
        )
    )

    result = (
        monitor.count_waiting_tasks()
    )

    assert result == 10

    repository.get_waiting_tasks.assert_called_once_with(
        limit=None
    )


# ==================================================
#
# Test Empty Queue
#
# ==================================================

def test_count_waiting_tasks_empty():

    monitor, repository = (
        create_monitor(
            waiting_count=0
        )
    )

    result = (
        monitor.count_waiting_tasks()
    )

    assert result == 0

    repository.get_waiting_tasks.assert_called_once_with(
        limit=None
    )


# ==================================================
#
# Test Pending Below Threshold
#
# ==================================================

def test_pending_below_threshold():

    monitor, repository = (
        create_monitor(
            waiting_count=49,
            threshold=50
        )
    )

    result = (
        monitor.has_pending_tasks()
    )

    assert result is True

    assert (
        monitor.is_threshold_reached()
        is False
    )


# ==================================================
#
# Test Threshold Reached
#
# ==================================================

def test_threshold_reached():

    monitor, repository = (
        create_monitor(
            waiting_count=50,
            threshold=50
        )
    )

    result = (
        monitor.is_threshold_reached()
    )

    assert result is True


# ==================================================
#
# Test Threshold Above
#
# ==================================================

def test_threshold_above():

    monitor, repository = (
        create_monitor(
            waiting_count=75,
            threshold=50
        )
    )

    result = (
        monitor.is_threshold_reached()
    )

    assert result is True


# ==================================================
#
# Test No Pending Tasks
#
# ==================================================

def test_no_pending_tasks():

    monitor, repository = (
        create_monitor(
            waiting_count=0
        )
    )

    result = (
        monitor.has_pending_tasks()
    )

    assert result is False


# ==================================================
#
# Test Check
#
# ==================================================

def test_check_below_threshold():

    monitor, repository = (
        create_monitor(
            waiting_count=20,
            threshold=50
        )
    )

    result = (
        monitor.check()
    )

    assert result is False


# ==================================================
#
# Test Check At Threshold
#
# ==================================================

def test_check_at_threshold():

    monitor, repository = (
        create_monitor(
            waiting_count=50,
            threshold=50
        )
    )

    result = (
        monitor.check()
    )

    assert result is True


# ==================================================
#
# Test Get Status
#
# ==================================================

def test_get_status():

    monitor, repository = (
        create_monitor(
            waiting_count=50,
            threshold=50
        )
    )

    result = (
        monitor.get_status()
    )

    assert result["waiting"] == 50

    assert result["threshold"] == 50

    assert result["pending"] is True

    assert result["threshold_reached"] is True


# ==================================================
#
# Test Repository Exception
#
# ==================================================

def test_count_waiting_tasks_repository_error():

    repository = MagicMock()

    repository.get_waiting_tasks.side_effect = (
        Exception(
            "Database error"
        )
    )

    monitor = AIPendingTaskMonitor(
        task_repository=repository,
        threshold=50
    )

    result = (
        monitor.count_waiting_tasks()
    )

    assert result == 0


# ==================================================
#
# Test Invalid Threshold
#
# ==================================================

def test_invalid_threshold():

    repository = MagicMock()

    repository.get_waiting_tasks.return_value = []

    monitor = AIPendingTaskMonitor(
        task_repository=repository,
        threshold=0
    )

    assert monitor.threshold == 50


# ==================================================
#
# Test Repr
#
# ==================================================

def test_repr():

    monitor, repository = (
        create_monitor(
            waiting_count=10,
            threshold=50
        )
    )

    result = repr(
        monitor
    )

    assert (
        "AIPendingTaskMonitor"
        in result
    )

    assert (
        "threshold=50"
        in result
    )