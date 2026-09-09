"""
tests/test_p24_12_stress_load.py

AutoSearch V4

P2.4.12

AI Async Pipeline Stress / Load Test

功能：

1. 100 Tasks
2. 500 Tasks
3. 1000 Tasks
4. Multi Worker
5. Worker Failure under Load
6. Repeated Trigger
7. Worker Count Stability
8. Pool Lifecycle
9. Scheduler Lifecycle
10. End-to-End Load Integration

測試架構：

Mock AITaskRepository
        ↓
AIBatchTriggerService
        ↓
Mock AIScheduler
        ↓
Mock AIWorkerPool
        ↓
Mock Workers

注意：

本測試不使用：

- 真實 Database
- 真實 AI API
- 真實 Network

目的：

確認 P2.4 Async AI Scaling
在大量 Task 與 Multi-Worker
情況下仍保持穩定。
"""

import threading
import time

from services.ai_batch_trigger_service import (
    AIBatchTriggerService
)

from services.ai_worker_pool import (
    AIWorkerPool
)

from services.ai_scheduler import (
    AIScheduler
)


# ==================================================
#
# Mock Task
#
# ==================================================

class MockTask:

    def __init__(
        self,
        article_id
    ):

        self.article_id = article_id

        self.status = "WAITING"


# ==================================================
#
# Mock Repository
#
# ==================================================

class MockTaskRepository:

    def __init__(
        self,
        task_count=0
    ):

        self.tasks = [

            MockTask(
                article_id=index + 1
            )

            for index in range(
                task_count
            )

        ]

    def get_waiting_tasks(
        self,
        limit=None
    ):

        if limit is None:

            return list(
                self.tasks
            )

        return self.tasks[
            :limit
        ]


# ==================================================
#
# Mock Worker
#
# ==================================================

class StressWorker:

    execution_count = 0

    lock = threading.Lock()

    def run_once(
        self
    ):

        with self.lock:

            type(self).execution_count += 1

        return 1


# ==================================================
#
# Failing Worker
#
# ==================================================

class StressFailingWorker:

    execution_count = 0

    lock = threading.Lock()

    def run_once(
        self
    ):

        with self.lock:

            type(
                self
            ).execution_count += 1

        raise RuntimeError(
            "Stress worker failure"
        )


# ==================================================
#
# Reset Worker State
#
# ==================================================

def reset_worker_state():

    StressWorker.execution_count = 0

    StressFailingWorker.execution_count = 0


# ==================================================
#
# Worker Factory
#
# ==================================================

def create_pool(
    worker_count
):

    return AIWorkerPool(

        worker_count=worker_count,

        worker_class=StressWorker

    )


# ==================================================
#
# 100 Tasks
#
# ==================================================

def test_p24_12_100_tasks():

    reset_worker_state()

    repository = MockTaskRepository(
        task_count=100
    )

    pool = create_pool(
        worker_count=3
    )

    scheduler = AIScheduler(
        worker_pool=pool,
        interval=1
    )

    service = AIBatchTriggerService(

        task_repository=repository,

        scheduler=scheduler,

        threshold=50

    )

    assert (
        service.count_waiting_tasks()
        == 100
    )

    assert (
        service.should_trigger()
        is True
    )


# ==================================================
#
# 500 Tasks
#
# ==================================================

def test_p24_12_500_tasks():

    reset_worker_state()

    repository = MockTaskRepository(
        task_count=500
    )

    pool = create_pool(
        worker_count=5
    )

    scheduler = AIScheduler(
        worker_pool=pool,
        interval=1
    )

    service = AIBatchTriggerService(

        task_repository=repository,

        scheduler=scheduler,

        threshold=50

    )

    assert (
        service.count_waiting_tasks()
        == 500
    )

    assert (
        service.should_trigger()
        is True
    )


# ==================================================
#
# 1000 Tasks
#
# ==================================================

def test_p24_12_1000_tasks():

    reset_worker_state()

    repository = MockTaskRepository(
        task_count=1000
    )

    pool = create_pool(
        worker_count=10
    )

    scheduler = AIScheduler(
        worker_pool=pool,
        interval=1
    )

    service = AIBatchTriggerService(

        task_repository=repository,

        scheduler=scheduler,

        threshold=50

    )

    assert (
        service.count_waiting_tasks()
        == 1000
    )

    assert (
        service.should_trigger()
        is True
    )


# ==================================================
#
# Multi Worker Execution
#
# ==================================================

def test_p24_12_multi_worker_execution():

    reset_worker_state()

    pool = create_pool(
        worker_count=10
    )

    result = pool.start()

    assert result is True

    pool.join(
        timeout=2
    )

    status = (
        pool.get_status()
    )

    assert (
        status["worker_count"]
        == 10
    )

    assert (
        status["active_workers"]
        == 0
    )

    assert (
        status["completed_workers"]
        == 10
    )

    pool.stop()


# ==================================================
#
# Worker Failure under Load
#
# ==================================================

def test_p24_12_worker_failure_under_load():

    reset_worker_state()

    pool = AIWorkerPool(

        worker_count=10,

        worker_class=StressFailingWorker

    )

    result = pool.start()

    assert result is True

    pool.join(
        timeout=2
    )

    status = (
        pool.get_status()
    )

    assert (
        status["worker_count"]
        == 10
    )

    assert (
        status["active_workers"]
        == 0
    )

    assert (
        status["failed_workers"]
        == 10
    )

    assert (
        status["completed_workers"]
        == 0
    )

    assert (
        pool.get_worker_count()
        == 10
    )


# ==================================================
#
# Repeated Trigger
#
# ==================================================

def test_p24_12_repeated_trigger():

    repository = MockTaskRepository(
        task_count=1000
    )

    pool = create_pool(
        worker_count=5
    )

    scheduler = AIScheduler(
        worker_pool=pool,
        interval=1
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
        scheduler.is_running()
        is True
    )

    scheduler.stop()


# ==================================================
#
# Worker Count Stability
#
# ==================================================

def test_p24_12_worker_count_stability():

    reset_worker_state()

    pool = create_pool(
        worker_count=10
    )

    assert (
        pool.get_worker_count()
        == 0
    )

    pool.start()

    assert (
        pool.get_worker_count()
        == 10
    )

    pool.join(
        timeout=2
    )

    assert (
        pool.get_worker_count()
        == 10
    )

    pool.start()

    assert (
        pool.get_worker_count()
        == 10
    )

    pool.join(
        timeout=2
    )

    assert (
        pool.get_worker_count()
        == 10
    )

    pool.stop()


# ==================================================
#
# Pool Lifecycle
#
# ==================================================

def test_p24_12_pool_lifecycle():

    reset_worker_state()

    pool = create_pool(
        worker_count=5
    )

    assert (
        pool.running
        is False
    )

    assert (
        pool.start()
        is True
    )

    pool.join(
        timeout=2
    )

    assert (
        pool.get_worker_count()
        == 5
    )

    assert (
        pool.stop()
        is True
    )

    assert (
        pool.running
        is False
    )

    assert (
        pool.start()
        is True
    )

    pool.join(
        timeout=2
    )

    assert (
        pool.get_worker_count()
        == 5
    )

    assert (
        pool.stop()
        is True
    )


# ==================================================
#
# Scheduler Lifecycle
#
# ==================================================

def test_p24_12_scheduler_lifecycle():

    reset_worker_state()

    pool = create_pool(
        worker_count=5
    )

    scheduler = AIScheduler(

        worker_pool=pool,

        interval=1

    )

    assert (
        scheduler.is_running()
        is False
    )

    assert (
        scheduler.start()
        is True
    )

    assert (
        scheduler.is_running()
        is True
    )

    scheduler.stop()

    assert (
        scheduler.is_running()
        is False
    )

    assert (
        scheduler.start()
        is True
    )

    assert (
        scheduler.is_running()
        is True
    )

    scheduler.stop()

    assert (
        scheduler.is_running()
        is False
    )


# ==================================================
#
# End-to-End Stress Integration
#
# ==================================================

def test_p24_12_end_to_end_stress():

    reset_worker_state()

    repository = MockTaskRepository(
        task_count=1000
    )

    pool = create_pool(
        worker_count=10
    )

    scheduler = AIScheduler(

        worker_pool=pool,

        interval=1

    )

    service = AIBatchTriggerService(

        task_repository=repository,

        scheduler=scheduler,

        threshold=50

    )

    # ----------------------------------------------
    # Batch Detection
    # ----------------------------------------------

    assert (
        service.count_waiting_tasks()
        == 1000
    )

    assert (
        service.should_trigger()
        is True
    )

    # ----------------------------------------------
    # Trigger
    # ----------------------------------------------

    assert (
        service.trigger()
        is True
    )

    # ----------------------------------------------
    # Scheduler
    # ----------------------------------------------

    assert (
        scheduler.is_running()
        is True
    )

    # ----------------------------------------------
    # Worker Pool
    # ----------------------------------------------

    assert (
        pool.get_worker_count()
        == 10
    )

    pool.join(
        timeout=2
    )

    status = (
        pool.get_status()
    )

    # ----------------------------------------------
    # Final State
    # ----------------------------------------------

    assert (
        status["worker_count"]
        == 10
    )

    assert (
        status["active_workers"]
        == 0
    )

    assert (
        status["completed_workers"]
        == 10
    )

    # ----------------------------------------------
    # Cleanup
    # ----------------------------------------------

    assert (
        service.stop()
        is True
    )

    assert (
        scheduler.is_running()
        is False
    )

    assert (
        pool.running
        is False
    )
