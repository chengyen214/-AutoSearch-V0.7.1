"""
tests/test_ai_batch_trigger_service.py

AutoSearch V4

P2.4.2

Test:

AIBatchTriggerService

測試:

1. WAITING Task 數量
2. Threshold 判斷
3. Batch Trigger
4. Scheduler Already Running
5. Force Trigger
6. Stop
7. Status
"""

from unittest.mock import MagicMock

from services.ai_batch_trigger_service import (
    AIBatchTriggerService
)


# ==================================================
# Mock Repository
# ==================================================

def create_repository(
    waiting_count
):
    """
    建立 Mock AITaskRepository。

    P2.4.2 現在使用:

        count_waiting_tasks()

    直接取得 WAITING Task 數量。
    """

    repository = MagicMock()

    repository.count_waiting_tasks.return_value = (
        waiting_count
    )

    return repository


# ==================================================
# Mock Scheduler
# ==================================================

def create_scheduler(
    running=False
):
    """
    建立 Mock AIScheduler。
    """

    scheduler = MagicMock()

    scheduler.running = running

    return scheduler


# ==================================================
# Test Count Waiting Tasks
# ==================================================

def test_count_waiting_tasks():
    """
    WAITING Task 數量應正確取得。
    """

    repository = create_repository(
        25
    )

    scheduler = create_scheduler()

    service = AIBatchTriggerService(
        task_repository=repository,
        scheduler=scheduler
    )

    result = service.count_waiting_tasks()

    assert result == 25

    repository.count_waiting_tasks.assert_called_once()


# ==================================================
# Test Count Waiting Tasks Empty
# ==================================================

def test_count_waiting_tasks_empty():
    """
    沒有 WAITING Task 時應回傳 0。
    """

    repository = create_repository(
        0
    )

    scheduler = create_scheduler()

    service = AIBatchTriggerService(
        task_repository=repository,
        scheduler=scheduler
    )

    result = service.count_waiting_tasks()

    assert result == 0

    repository.count_waiting_tasks.assert_called_once()


# ==================================================
# Test Should Trigger Below Threshold
# ==================================================

def test_should_trigger_below_threshold():
    """
    WAITING < 50

    不應 Trigger。
    """

    repository = create_repository(
        49
    )

    scheduler = create_scheduler()

    service = AIBatchTriggerService(
        task_repository=repository,
        scheduler=scheduler,
        threshold=50
    )

    result = service.should_trigger()

    assert result is False

    scheduler.start.assert_not_called()


# ==================================================
# Test Should Trigger At Threshold
# ==================================================

def test_should_trigger_at_threshold():
    """
    WAITING == 50

    應達到 Trigger Threshold。
    """

    repository = create_repository(
        50
    )

    scheduler = create_scheduler()

    service = AIBatchTriggerService(
        task_repository=repository,
        scheduler=scheduler,
        threshold=50
    )

    result = service.should_trigger()

    assert result is True


# ==================================================
# Test Should Trigger Above Threshold
# ==================================================

def test_should_trigger_above_threshold():
    """
    WAITING > 50

    應達到 Trigger Threshold。
    """

    repository = create_repository(
        51
    )

    scheduler = create_scheduler()

    service = AIBatchTriggerService(
        task_repository=repository,
        scheduler=scheduler,
        threshold=50
    )

    result = service.should_trigger()

    assert result is True


# ==================================================
# Test Trigger Below Threshold
# ==================================================

def test_trigger_below_threshold():
    """
    WAITING = 49

    不應啟動 Scheduler。
    """

    repository = create_repository(
        49
    )

    scheduler = create_scheduler()

    service = AIBatchTriggerService(
        task_repository=repository,
        scheduler=scheduler,
        threshold=50
    )

    result = service.trigger()

    assert result is False

    scheduler.start.assert_not_called()


# ==================================================
# Test Trigger At Threshold
# ==================================================

def test_trigger_at_threshold():
    """
    WAITING = 50

    應啟動 Scheduler。
    """

    repository = create_repository(
        50
    )

    scheduler = create_scheduler(
        running=False
    )

    service = AIBatchTriggerService(
        task_repository=repository,
        scheduler=scheduler,
        threshold=50
    )

    result = service.trigger()

    assert result is True

    scheduler.start.assert_called_once()


# ==================================================
# Test Trigger Above Threshold
# ==================================================

def test_trigger_above_threshold():
    """
    WAITING = 100

    應啟動 Scheduler。
    """

    repository = create_repository(
        100
    )

    scheduler = create_scheduler(
        running=False
    )

    service = AIBatchTriggerService(
        task_repository=repository,
        scheduler=scheduler,
        threshold=50
    )

    result = service.trigger()

    assert result is True

    scheduler.start.assert_called_once()


# ==================================================
# Test Scheduler Already Running
# ==================================================

def test_trigger_scheduler_already_running():
    """
    Scheduler 已經 RUNNING。

    不應再次 start。
    """

    repository = create_repository(
        50
    )

    scheduler = create_scheduler(
        running=True
    )

    service = AIBatchTriggerService(
        task_repository=repository,
        scheduler=scheduler,
        threshold=50
    )

    result = service.trigger()

    assert result is True

    scheduler.start.assert_not_called()


# ==================================================
# Test Check And Trigger
# ==================================================

def test_check_and_trigger():
    """
    check_and_trigger()

    應等同於 trigger()。
    """

    repository = create_repository(
        50
    )

    scheduler = create_scheduler(
        running=False
    )

    service = AIBatchTriggerService(
        task_repository=repository,
        scheduler=scheduler,
        threshold=50
    )

    result = service.check_and_trigger()

    assert result is True

    scheduler.start.assert_called_once()


# ==================================================
# Test Force Trigger
# ==================================================

def test_force_trigger():
    """
    Force Trigger 不檢查 Threshold。

    即使只有 0 個 WAITING Task，
    仍然可以啟動 Scheduler。
    """

    repository = create_repository(
        0
    )

    scheduler = create_scheduler(
        running=False
    )

    service = AIBatchTriggerService(
        task_repository=repository,
        scheduler=scheduler,
        threshold=50
    )

    result = service.force_trigger()

    assert result is True

    scheduler.start.assert_called_once()


# ==================================================
# Test Force Trigger Already Running
# ==================================================

def test_force_trigger_already_running():
    """
    Scheduler 已經 RUNNING。

    Force Trigger 不應重複 start。
    """

    repository = create_repository(
        0
    )

    scheduler = create_scheduler(
        running=True
    )

    service = AIBatchTriggerService(
        task_repository=repository,
        scheduler=scheduler,
        threshold=50
    )

    result = service.force_trigger()

    assert result is True

    scheduler.start.assert_not_called()


# ==================================================
# Test Stop
# ==================================================

def test_stop():
    """
    Scheduler RUNNING。

    stop() 應呼叫 scheduler.stop()。
    """

    repository = create_repository(
        50
    )

    scheduler = create_scheduler(
        running=True
    )

    service = AIBatchTriggerService(
        task_repository=repository,
        scheduler=scheduler,
        threshold=50
    )

    result = service.stop()

    assert result is True

    scheduler.stop.assert_called_once()


# ==================================================
# Test Stop Already Stopped
# ==================================================

def test_stop_already_stopped():
    """
    Scheduler 已停止。

    不應再次呼叫 stop()。
    """

    repository = create_repository(
        0
    )

    scheduler = create_scheduler(
        running=False
    )

    service = AIBatchTriggerService(
        task_repository=repository,
        scheduler=scheduler
    )

    result = service.stop()

    assert result is True

    scheduler.stop.assert_not_called()


# ==================================================
# Test Get Status
# ==================================================

def test_get_status():
    """
    取得 Batch Trigger 狀態。
    """

    repository = create_repository(
        50
    )

    scheduler = create_scheduler(
        running=True
    )

    service = AIBatchTriggerService(
        task_repository=repository,
        scheduler=scheduler,
        threshold=50
    )

    result = service.get_status()

    assert result["waiting"] == 50

    assert result["threshold"] == 50

    assert result["trigger"] is True

    assert result["scheduler_running"] is True


# ==================================================
# Test Get Status Below Threshold
# ==================================================

def test_get_status_below_threshold():
    """
    WAITING < Threshold。
    """

    repository = create_repository(
        20
    )

    scheduler = create_scheduler(
        running=False
    )

    service = AIBatchTriggerService(
        task_repository=repository,
        scheduler=scheduler,
        threshold=50
    )

    result = service.get_status()

    assert result["waiting"] == 20

    assert result["threshold"] == 50

    assert result["trigger"] is False

    assert result["scheduler_running"] is False


# ==================================================
# Test Default Threshold
# ==================================================

def test_default_threshold():
    """
    預設 Threshold 應為 50。
    """

    repository = create_repository(
        0
    )

    scheduler = create_scheduler()

    service = AIBatchTriggerService(
        task_repository=repository,
        scheduler=scheduler
    )

    assert service.threshold == 50


# ==================================================
# Test Invalid Threshold
# ==================================================

def test_invalid_threshold():
    """
    threshold <= 0

    應回復預設值 50。
    """

    repository = create_repository(
        0
    )

    scheduler = create_scheduler()

    service = AIBatchTriggerService(
        task_repository=repository,
        scheduler=scheduler,
        threshold=0
    )

    assert service.threshold == 50


# ==================================================
# Test Repr
# ==================================================

def test_repr():
    """
    __repr__ 應正常運作。
    """

    repository = create_repository(
        0
    )

    scheduler = create_scheduler()

    service = AIBatchTriggerService(
        task_repository=repository,
        scheduler=scheduler,
        threshold=50
    )

    result = repr(
        service
    )

    assert "AIBatchTriggerService" in result

    assert "threshold=50" in result