"""
tests/test_p24_9_end_to_end_pipeline.py

AutoSearch V4

P2.4.9

Async AI Pipeline End-to-End Integration Test

Flow:

ArticleService
      ↓
AITaskRepository
      ↓
AIBatchTriggerService
      ↓
AIScheduler
      ↓
AIWorkerPool
      ↓
AIWorker

驗證:

1. Article 建立後產生 AI Task
2. AI Task 狀態為 WAITING
3. Batch Threshold 達成
4. Scheduler 啟動
5. Worker Pool 啟動
6. Multiple Worker 執行
7. AI Task Pipeline 完成
8. Batch → Scheduler → Pool 狀態一致
9. 不重複啟動 Scheduler
10. Worker Failure 不影響 Pipeline
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
#
# Mock AI Task
#
# ==================================================

class MockAITask:

    def __init__(
        self,
        article_id
    ):

        self.article_id = article_id

        self.status = "WAITING"


# ==================================================
#
# Mock AI Task Repository
#
# ==================================================

class MockAITaskRepository:

    def __init__(
        self
    ):

        self.tasks = []

        self.created_tasks = []

    # ----------------------------------------------
    # Create AI Task
    # ----------------------------------------------

    def create_task(
        self,
        article_id
    ):

        task = MockAITask(
            article_id=article_id
        )

        self.tasks.append(
            task
        )

        self.created_tasks.append(
            task
        )

        return task

    # ----------------------------------------------
    # Waiting Tasks
    # ----------------------------------------------

    def get_waiting_tasks(
        self,
        limit=None
    ):

        waiting = [
            task
            for task in self.tasks
            if task.status == "WAITING"
        ]

        if limit is None:

            return waiting

        return waiting[:limit]


# ==================================================
#
# Mock Article Service
#
# ==================================================

class MockArticleService:

    """
    模擬 ArticleService。

    真正流程:

        Article
          ↓
        articles
          ↓
        ai_tasks

    本測試只驗證
    AI Task 是否正確建立。
    """

    def __init__(
        self,
        task_repository
    ):

        self.task_repository = (
            task_repository
        )

        self.saved_articles = []

    def save_article(
        self,
        article_id
    ):

        self.saved_articles.append(
            article_id
        )

        return (
            self.task_repository
            .create_task(
                article_id
            )
        )


# ==================================================
#
# Successful Worker
#
# ==================================================

class SuccessfulWorker:

    executed = 0

    def run_once(
        self
    ):

        type(self).executed += 1

        return 1


# ==================================================
#
# Failing Worker
#
# ==================================================

class FailingWorker:

    executed = 0

    def run_once(
        self
    ):

        type(self).executed += 1

        raise RuntimeError(
            "End-to-End Worker Failure"
        )


# ==================================================
#
# Reset Worker State
#
# ==================================================

def reset_worker_state():

    SuccessfulWorker.executed = 0

    FailingWorker.executed = 0


# ==================================================
#
# Factory
#
# ==================================================

def create_pipeline(
    worker_class=SuccessfulWorker,
    worker_count=3,
    threshold=3
):

    repository = (
        MockAITaskRepository()
    )

    article_service = (
        MockArticleService(
            task_repository=repository
        )
    )

    pool = AIWorkerPool(
        worker_count=worker_count,
        worker_class=worker_class
    )

    scheduler = AIScheduler(
        interval=30,
        worker_pool=pool
    )

    batch_trigger = (
        AIBatchTriggerService(
            task_repository=repository,
            scheduler=scheduler,
            threshold=threshold
        )
    )

    return {
        "repository": repository,
        "article_service": article_service,
        "pool": pool,
        "scheduler": scheduler,
        "batch_trigger": batch_trigger
    }


# ==================================================
#
# Article → AI Task
#
# ==================================================

def test_article_creates_ai_task():

    reset_worker_state()

    pipeline = create_pipeline(
        worker_count=1,
        threshold=1
    )

    article_service = (
        pipeline["article_service"]
    )

    repository = (
        pipeline["repository"]
    )

    task = (
        article_service
        .save_article(
            article_id=1
        )
    )

    assert task is not None

    assert (
        task.article_id
        == 1
    )

    assert (
        task.status
        == "WAITING"
    )

    assert (
        len(
            repository.tasks
        )
        == 1
    )


# ==================================================
#
# WAITING Task Count
#
# ==================================================

def test_waiting_task_reaches_threshold():

    reset_worker_state()

    pipeline = create_pipeline(
        worker_count=1,
        threshold=3
    )

    article_service = (
        pipeline["article_service"]
    )

    batch_trigger = (
        pipeline["batch_trigger"]
    )

    for article_id in range(
        1,
        4
    ):

        article_service.save_article(
            article_id
        )

    assert (
        batch_trigger
        .count_waiting_tasks()
        == 3
    )

    assert (
        batch_trigger
        .should_trigger()
        is True
    )


# ==================================================
#
# Below Threshold Does Not Start
#
# ==================================================

def test_end_to_end_below_threshold_does_not_start():

    reset_worker_state()

    pipeline = create_pipeline(
        worker_count=3,
        threshold=3
    )

    article_service = (
        pipeline["article_service"]
    )

    batch_trigger = (
        pipeline["batch_trigger"]
    )

    scheduler = (
        pipeline["scheduler"]
    )

    pool = (
        pipeline["pool"]
    )

    article_service.save_article(
        1
    )

    article_service.save_article(
        2
    )

    result = (
        batch_trigger
        .check_and_trigger()
    )

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
#
# Full End-to-End Pipeline
#
# ==================================================

def test_end_to_end_full_pipeline():

    reset_worker_state()

    pipeline = create_pipeline(
        worker_count=3,
        threshold=3
    )

    article_service = (
        pipeline["article_service"]
    )

    repository = (
        pipeline["repository"]
    )

    batch_trigger = (
        pipeline["batch_trigger"]
    )

    scheduler = (
        pipeline["scheduler"]
    )

    pool = (
        pipeline["pool"]
    )

    # ----------------------------------------------
    # Article → AI Task
    # ----------------------------------------------

    for article_id in range(
        1,
        4
    ):

        article_service.save_article(
            article_id
        )

    assert (
        len(
            repository.tasks
        )
        == 3
    )

    assert (
        batch_trigger
        .count_waiting_tasks()
        == 3
    )

    # ----------------------------------------------
    # Batch Trigger
    # ----------------------------------------------

    result = (
        batch_trigger
        .check_and_trigger()
    )

    assert result is True

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
        pool.running
        is True
    )

    assert (
        pool.get_worker_count()
        == 3
    )

    # ----------------------------------------------
    # Wait Workers
    # ----------------------------------------------

    pool.join(
        timeout=1
    )

    # ----------------------------------------------
    # AI Worker
    # ----------------------------------------------

    assert (
        SuccessfulWorker.executed
        == 3
    )

    # ----------------------------------------------
    # Pool Status
    # ----------------------------------------------

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

    # ----------------------------------------------
    # Cleanup
    # ----------------------------------------------

    batch_trigger.stop()


# ==================================================
#
# Scheduler → Pool Status
#
# ==================================================

def test_scheduler_and_pool_status():

    reset_worker_state()

    pipeline = create_pipeline(
        worker_count=2,
        threshold=2
    )

    article_service = (
        pipeline["article_service"]
    )

    batch_trigger = (
        pipeline["batch_trigger"]
    )

    scheduler = (
        pipeline["scheduler"]
    )

    for article_id in range(
        1,
        3
    ):

        article_service.save_article(
            article_id
        )

    assert (
        batch_trigger
        .trigger()
        is True
    )

    scheduler_status = (
        scheduler.get_status()
    )

    assert (
        scheduler_status["running"]
        is True
    )

    assert (
        scheduler_status[
            "worker_pool_running"
        ]
        is True
    )

    assert (
        scheduler_status[
            "worker_count"
        ]
        == 2
    )

    scheduler.worker_pool.join(
        timeout=1
    )

    scheduler_status = (
        scheduler.get_status()
    )

    assert (
        scheduler_status[
            "active_workers"
        ]
        == 0
    )

    batch_trigger.stop()


# ==================================================
#
# Repeated Trigger
#
# ==================================================

def test_end_to_end_repeated_trigger_does_not_duplicate_pool():

    reset_worker_state()

    pipeline = create_pipeline(
        worker_count=3,
        threshold=3
    )

    article_service = (
        pipeline["article_service"]
    )

    batch_trigger = (
        pipeline["batch_trigger"]
    )

    pool = (
        pipeline["pool"]
    )

    for article_id in range(
        1,
        4
    ):

        article_service.save_article(
            article_id
        )

    first = (
        batch_trigger.trigger()
    )

    second = (
        batch_trigger.trigger()
    )

    assert first is True

    assert second is True

    assert (
        pool.get_worker_count()
        == 3
    )

    assert (
        len(
            pool.workers
        )
        == 3
    )

    batch_trigger.stop()


# ==================================================
#
# Worker Failure Isolation
#
# ==================================================

def test_end_to_end_worker_failure_isolated():

    reset_worker_state()

    pipeline = create_pipeline(
        worker_class=FailingWorker,
        worker_count=3,
        threshold=3
    )

    article_service = (
        pipeline["article_service"]
    )

    batch_trigger = (
        pipeline["batch_trigger"]
    )

    pool = (
        pipeline["pool"]
    )

    for article_id in range(
        1,
        4
    ):

        article_service.save_article(
            article_id
        )

    result = (
        batch_trigger.trigger()
    )

    assert result is True

    pool.join(
        timeout=1
    )

    assert (
        FailingWorker.executed
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
        status["failed_workers"]
        == 3
    )

    # Worker failure
    # 不應該讓 Scheduler / Pool
    # 整體 Crash。

    assert (
        pool.running
        is True
    )

    batch_trigger.stop()


# ==================================================
#
# Full Lifecycle
#
# ==================================================

def test_end_to_end_full_lifecycle():

    reset_worker_state()

    pipeline = create_pipeline(
        worker_count=2,
        threshold=2
    )

    article_service = (
        pipeline["article_service"]
    )

    batch_trigger = (
        pipeline["batch_trigger"]
    )

    scheduler = (
        pipeline["scheduler"]
    )

    pool = (
        pipeline["pool"]
    )

    # ----------------------------------------------
    # 1. Create Tasks
    # ----------------------------------------------

    article_service.save_article(
        1
    )

    article_service.save_article(
        2
    )

    assert (
        batch_trigger
        .count_waiting_tasks()
        == 2
    )

    # ----------------------------------------------
    # 2. Trigger
    # ----------------------------------------------

    assert (
        batch_trigger.trigger()
        is True
    )

    # ----------------------------------------------
    # 3. Scheduler Running
    # ----------------------------------------------

    assert (
        scheduler.is_running()
        is True
    )

    # ----------------------------------------------
    # 4. Pool Running
    # ----------------------------------------------

    assert (
        pool.running
        is True
    )

    # ----------------------------------------------
    # 5. Workers Complete
    # ----------------------------------------------

    pool.join(
        timeout=1
    )

    assert (
        SuccessfulWorker.executed
        == 2
    )

    # ----------------------------------------------
    # 6. Stop
    # ----------------------------------------------

    assert (
        batch_trigger.stop()
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
