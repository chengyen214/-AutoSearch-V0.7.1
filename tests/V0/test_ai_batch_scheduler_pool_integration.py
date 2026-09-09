"""
tests/test_ai_batch_scheduler_pool_integration.py

AutoSearch V4

P2.4.8

AI Batch Trigger
+
AI Scheduler
+
AI Worker Pool

Integration Test

Flow:

AITaskRepository
        ↓
AIBatchTriggerService
        ↓
AIScheduler
        ↓
AIWorkerPool
        ↓
AIWorker × N
"""

from services.ai_batch_trigger_service import (
    AIBatchTriggerService
)

from services.ai_scheduler import (
    AIScheduler
)

from services.ai_worker_pool import (
    AIWorkerPool
)


# ==================================================
# Mock Task Repository
# ==================================================

class MockTaskRepository:

    def __init__(
        self,
        waiting_count=0
    ):

        self.waiting_count = (
            waiting_count
        )

    def get_waiting_tasks(
        self,
        limit=None
    ):

        return [
            object()
            for _ in range(
                self.waiting_count
            )
        ]


# ==================================================
# Successful Worker
# ==================================================

class SuccessfulWorker:

    executed = 0

    def run_once(
        self
    ):

        type(self).executed += 1

        return 1


# ==================================================
# Failing Worker
# ==================================================

class FailingWorker:

    executed = 0

    def run_once(
        self
    ):

        type(self).executed += 1

        raise RuntimeError(
            "Integration worker failure"
        )


# ==================================================
# Reset
# ==================================================

def reset_worker_state():

    SuccessfulWorker.executed = 0

    FailingWorker.executed = 0


# ==================================================
# Below Threshold
# ==================================================

def test_batch_scheduler_pool_below_threshold():

    reset_worker_state()

    repository = MockTaskRepository(
        waiting_count=49
    )

    pool = AIWorkerPool(
        worker_count=3,
        worker_class=SuccessfulWorker
    )

    scheduler = AIScheduler(
        interval=30,
        worker_pool=pool
    )

    service = AIBatchTriggerService(
        task_repository=repository,
        scheduler=scheduler,
        threshold=50
    )

    result = service.trigger()

    assert result is False

    assert (
        scheduler.is_running()
        is False
    )

    assert (
        pool.running
        is False
    )

    assert (
        SuccessfulWorker.executed
        == 0
    )


# ==================================================
# Threshold → Scheduler → Pool
# ==================================================

def test_batch_scheduler_pool_threshold_integration():

    reset_worker_state()

    repository = MockTaskRepository(
        waiting_count=50
    )

    pool = AIWorkerPool(
        worker_count=3,
        worker_class=SuccessfulWorker
    )

    scheduler = AIScheduler(
        interval=30,
        worker_pool=pool
    )

    service = AIBatchTriggerService(
        task_repository=repository,
        scheduler=scheduler,
        threshold=50
    )

    result = service.trigger()

    assert result is True

    assert (
        scheduler.is_running()
        is True
    )

    assert (
        pool.running
        is True
    )

    assert (
        pool.get_worker_count()
        == 3
    )

    pool.join(
        timeout=1
    )

    assert (
        SuccessfulWorker.executed
        == 3
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

    assert (
        status["failed_workers"]
        == 0
    )

    service.stop()


# ==================================================
# Multiple Workers
# ==================================================

def test_batch_scheduler_pool_multiple_workers():

    reset_worker_state()

    repository = MockTaskRepository(
        waiting_count=50
    )

    pool = AIWorkerPool(
        worker_count=5,
        worker_class=SuccessfulWorker
    )

    scheduler = AIScheduler(
        worker_pool=pool
    )

    service = AIBatchTriggerService(
        task_repository=repository,
        scheduler=scheduler,
        threshold=50
    )

    assert (
        service.trigger()
        is True
    )

    pool.join(
        timeout=1
    )

    assert (
        SuccessfulWorker.executed
        == 5
    )

    assert (
        pool.get_worker_count()
        == 5
    )

    service.stop()


# ==================================================
# Repeated Trigger
# ==================================================

def test_batch_scheduler_pool_repeated_trigger():

    reset_worker_state()

    repository = MockTaskRepository(
        waiting_count=50
    )

    pool = AIWorkerPool(
        worker_count=3,
        worker_class=SuccessfulWorker
    )

    scheduler = AIScheduler(
        worker_pool=pool
    )

    service = AIBatchTriggerService(
        task_repository=repository,
        scheduler=scheduler,
        threshold=50
    )

    first = (
        service.trigger()
    )

    second = (
        service.trigger()
    )

    assert first is True

    assert second is True

    assert (
        pool.get_worker_count()
        == 3
    )

    assert (
        len(pool.workers)
        == 3
    )

    service.stop()


# ==================================================
# Worker Failure Isolation
# ==================================================

def test_batch_scheduler_pool_worker_failure():

    reset_worker_state()

    repository = MockTaskRepository(
        waiting_count=50
    )

    pool = AIWorkerPool(
        worker_count=3,
        worker_class=FailingWorker
    )

    scheduler = AIScheduler(
        worker_pool=pool
    )

    service = AIBatchTriggerService(
        task_repository=repository,
        scheduler=scheduler,
        threshold=50
    )

    result = (
        service.trigger()
    )

    assert result is True

    pool.join(
        timeout=1
    )

    assert (
        FailingWorker.executed
        == 3
    )

    assert (
        pool.get_worker_count()
        == 3
    )

    status = (
        pool.get_status()
    )

    assert (
        status["active_workers"]
        == 0
    )

    assert (
        status["failed_workers"]
        == 3
    )

    assert (
        status["completed_workers"]
        == 3
    )

    service.stop()


# ==================================================
# Full Status Integration
# ==================================================

def test_batch_scheduler_pool_status():

    reset_worker_state()

    repository = MockTaskRepository(
        waiting_count=50
    )

    pool = AIWorkerPool(
        worker_count=2,
        worker_class=SuccessfulWorker
    )

    scheduler = AIScheduler(
        worker_pool=pool
    )

    service = AIBatchTriggerService(
        task_repository=repository,
        scheduler=scheduler,
        threshold=50
    )

    assert (
        service.trigger()
        is True
    )

    pool.join(
        timeout=1
    )

    status = (
        service.get_status()
    )

    assert (
        status["waiting"]
        == 50
    )

    assert (
        status["threshold"]
        == 50
    )

    assert (
        status["trigger"]
        is True
    )

    assert (
        status["scheduler_running"]
        is True
    )

    assert (
        status["scheduler"]
        is not None
    )

    assert (
        status["worker_pool"]
        is not None
    )

    assert (
        status["worker_pool"]
        ["worker_count"]
        == 2
    )

    assert (
        status["worker_pool"]
        ["completed_workers"]
        == 2
    )

    service.stop()


# ==================================================
# Scheduler Failure
# ==================================================

def test_batch_scheduler_pool_scheduler_failure():

    reset_worker_state()

    repository = MockTaskRepository(
        waiting_count=50
    )

    class FailedScheduler:

        running = False

        def start(
            self
        ):

            return False

        def stop(
            self
        ):

            return True

    scheduler = FailedScheduler()

    service = AIBatchTriggerService(
        task_repository=repository,
        scheduler=scheduler,
        threshold=50
    )

    result = (
        service.trigger()
    )

    assert result is False

    assert (
        scheduler.running
        is False
    )

    assert (
        SuccessfulWorker.executed
        == 0
    )
