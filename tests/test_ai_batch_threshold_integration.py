"""
tests/test_ai_batch_threshold_integration.py

AutoSearch V4

P2.4.5

Batch Threshold Integration Test

Flow:

AITaskRepository
        ↓
AIPendingTaskMonitor
        ↓
AIBatchTriggerService
        ↓
AIScheduler
        ↓
AIWorker

測試：

1. WAITING < threshold
2. WAITING == threshold
3. WAITING > threshold
4. WAITING == 0
5. Scheduler already running
6. Force trigger
7. Monitor → Trigger → Scheduler
8. Repository error
9. Custom threshold
10. Status integration
"""

from unittest.mock import MagicMock

from services.ai_batch_trigger_service import (
    AIBatchTriggerService
)


# ==================================================
#
# Mock Task
#
# ==================================================

class MockTask:

    def __init__(
        self,
        article_id=1
    ):

        self.article_id = article_id

        self.status = "WAITING"


# ==================================================
#
# Mock Scheduler
#
# ==================================================

class MockScheduler:

    def __init__(
        self,
        running=False
    ):

        self.running = running

        self.start_count = 0

        self.stop_count = 0

    def start(
        self
    ):

        self.start_count += 1

        self.running = True

        return True

    def stop(
        self
    ):

        self.stop_count += 1

        self.running = False

        return True


# ==================================================
#
# Factory
#
# ==================================================

def create_integration(
    waiting_count=0,
    threshold=50,
    scheduler=None
):

    repository = MagicMock()

    repository.get_waiting_tasks.return_value = [
        MockTask(
            article_id=index + 1
        )
        for index in range(
            waiting_count
        )
    ]

    if scheduler is None:

        scheduler = MockScheduler()

    service = AIBatchTriggerService(

        task_repository=repository,

        scheduler=scheduler,

        threshold=threshold

    )

    return (
        service,
        repository,
        scheduler
    )


# ==================================================
#
# Below Threshold
#
# ==================================================

def test_batch_threshold_below_threshold():

    service, repository, scheduler = (
        create_integration(
            waiting_count=49,
            threshold=50
        )
    )

    result = service.trigger()

    assert result is False

    assert scheduler.start_count == 0

    assert scheduler.running is False

    repository.get_waiting_tasks.assert_called_once_with(
        limit=None
    )


# ==================================================
#
# At Threshold
#
# ==================================================

def test_batch_threshold_at_threshold():

    service, repository, scheduler = (
        create_integration(
            waiting_count=50,
            threshold=50
        )
    )

    result = service.trigger()

    assert result is True

    assert scheduler.start_count == 1

    assert scheduler.running is True

    repository.get_waiting_tasks.assert_called_once_with(
        limit=None
    )


# ==================================================
#
# Above Threshold
#
# ==================================================

def test_batch_threshold_above_threshold():

    service, repository, scheduler = (
        create_integration(
            waiting_count=75,
            threshold=50
        )
    )

    result = service.trigger()

    assert result is True

    assert scheduler.start_count == 1

    assert scheduler.running is True


# ==================================================
#
# Zero Tasks
#
# ==================================================

def test_batch_threshold_zero_tasks():

    service, repository, scheduler = (
        create_integration(
            waiting_count=0,
            threshold=50
        )
    )

    result = service.trigger()

    assert result is False

    assert scheduler.start_count == 0

    assert scheduler.running is False


# ==================================================
#
# Scheduler Already Running
#
# ==================================================

def test_batch_threshold_scheduler_already_running():

    scheduler = MockScheduler(
        running=True
    )

    service, repository, scheduler = (
        create_integration(
            waiting_count=50,
            threshold=50,
            scheduler=scheduler
        )
    )

    result = service.trigger()

    assert result is True

    assert scheduler.start_count == 0

    assert scheduler.running is True


# ==================================================
#
# Force Trigger
#
# ==================================================

def test_batch_threshold_force_trigger():

    service, repository, scheduler = (
        create_integration(
            waiting_count=0,
            threshold=50
        )
    )

    result = service.force_trigger()

    assert result is True

    assert scheduler.start_count == 1

    assert scheduler.running is True


# ==================================================
#
# Force Trigger While Running
#
# ==================================================

def test_batch_threshold_force_trigger_already_running():

    scheduler = MockScheduler(
        running=True
    )

    service, repository, scheduler = (
        create_integration(
            waiting_count=0,
            threshold=50,
            scheduler=scheduler
        )
    )

    result = service.force_trigger()

    assert result is True

    assert scheduler.start_count == 0

    assert scheduler.running is True


# ==================================================
#
# Monitor → Trigger → Scheduler
#
# ==================================================

def test_batch_threshold_monitor_to_scheduler():

    service, repository, scheduler = (
        create_integration(
            waiting_count=50,
            threshold=50
        )
    )

    # ----------------------------------------------
    # Check
    # ----------------------------------------------

    assert (
        service.should_trigger()
        is True
    )

    # ----------------------------------------------
    # Trigger
    # ----------------------------------------------

    result = (
        service.check_and_trigger()
    )

    assert result is True

    # ----------------------------------------------
    # Scheduler
    # ----------------------------------------------

    assert scheduler.start_count == 1

    assert scheduler.running is True

    assert (
        repository
        .get_waiting_tasks
        .call_count
        == 2
    )


# ==================================================
#
# Repository Error
#
# ==================================================

def test_batch_threshold_repository_error():

    repository = MagicMock()

    repository.get_waiting_tasks.side_effect = (
        Exception(
            "Database error"
        )
    )

    scheduler = MockScheduler()

    service = AIBatchTriggerService(

        task_repository=repository,

        scheduler=scheduler,

        threshold=50

    )

    result = service.trigger()

    assert result is False

    assert scheduler.start_count == 0

    assert scheduler.running is False


# ==================================================
#
# Custom Threshold
#
# ==================================================

def test_batch_threshold_custom_threshold():

    service, repository, scheduler = (
        create_integration(
            waiting_count=10,
            threshold=10
        )
    )

    result = service.trigger()

    assert result is True

    assert scheduler.start_count == 1

    assert scheduler.running is True


# ==================================================
#
# Custom Threshold Below
#
# ==================================================

def test_batch_threshold_custom_threshold_below():

    service, repository, scheduler = (
        create_integration(
            waiting_count=9,
            threshold=10
        )
    )

    result = service.trigger()

    assert result is False

    assert scheduler.start_count == 0

    assert scheduler.running is False


# ==================================================
#
# Status Integration
#
# ==================================================

def test_batch_threshold_status():

    service, repository, scheduler = (
        create_integration(
            waiting_count=50,
            threshold=50
        )
    )

    result = service.get_status()

    assert result["waiting"] == 50

    assert result["threshold"] == 50

    assert result["trigger"] is True

    assert result["scheduler_running"] is False


# ==================================================
#
# Status After Trigger
#
# ==================================================

def test_batch_threshold_status_after_trigger():

    service, repository, scheduler = (
        create_integration(
            waiting_count=50,
            threshold=50
        )
    )

    service.trigger()

    result = service.get_status()

    assert result["waiting"] == 50

    assert result["threshold"] == 50

    assert result["trigger"] is True

    assert result["scheduler_running"] is True


# ==================================================
#
# Stop Scheduler
#
# ==================================================

def test_batch_threshold_stop_scheduler():

    service, repository, scheduler = (
        create_integration(
            waiting_count=50,
            threshold=50
        )
    )

    service.trigger()

    assert scheduler.running is True

    result = service.stop()

    assert result is True

    assert scheduler.stop_count == 1

    assert scheduler.running is False


# ==================================================
#
# Stop Already Stopped
#
# ==================================================

def test_batch_threshold_stop_already_stopped():

    service, repository, scheduler = (
        create_integration(
            waiting_count=0,
            threshold=50
        )
    )

    result = service.stop()

    assert result is True

    assert scheduler.stop_count == 0

    assert scheduler.running is False


# ==================================================
#
# Repeated Trigger
#
# ==================================================

def test_batch_threshold_repeated_trigger():

    service, repository, scheduler = (
        create_integration(
            waiting_count=50,
            threshold=50
        )
    )

    first = service.trigger()

    second = service.trigger()

    assert first is True

    assert second is True

    # Scheduler must only start once.

    assert scheduler.start_count == 1

    assert scheduler.running is True
