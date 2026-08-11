"""
tests/test_article_service_batch_trigger.py

AutoSearch V4

P2.4.2

ArticleService
+
AIBatchTriggerService

測試：

ArticleService
    |
    v
AI Task
    |
    v
Batch Trigger
    |
    +--> WAITING < 50
    |       |
    |       v
    |    不啟動 Scheduler
    |
    +--> WAITING >= 50
            |
            v
       啟動 Scheduler


測試重點：

1. WAITING < threshold
2. WAITING == threshold
3. WAITING > threshold
4. Scheduler 已啟動時避免重複啟動
5. ArticleService 建立 AI Task
6. ArticleService + Batch Trigger
7. Force Trigger
8. Status
"""

from unittest.mock import MagicMock

from services.article_service import (
    ArticleService
)

from services.ai_batch_trigger_service import (
    AIBatchTriggerService
)

from models.ai_task import (
    AITask
)


# ==================================================
#
# Fake AI Task Repository
#
# ==================================================

class FakeAITaskRepository:

    """
    P2.4.2 Test Repository

    不連接 MySQL。

    直接模擬：

        ai_tasks
        |
        +--> WAITING Tasks
    """

    def __init__(
        self,
        waiting_count=0
    ):

        self.waiting_count = (
            waiting_count
        )

        self.get_waiting_tasks_count = 0

    def get_waiting_tasks(
        self,
        limit=None
    ):
        """
        模擬 WAITING Task。

        每一個 object
        代表一筆 WAITING Task。
        """

        self.get_waiting_tasks_count += 1

        tasks = [

            MagicMock()

            for _ in range(
                self.waiting_count
            )

        ]

        if limit is not None:

            return tasks[:limit]

        return tasks


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

    def start(self):

        self.start_count += 1

        self.running = True

    def stop(self):

        self.stop_count += 1

        self.running = False


# ==================================================
#
# Helper
#
# ==================================================

def create_batch_trigger(
    waiting_count,
    threshold=50,
    scheduler=None
):
    """
    建立測試用 AIBatchTriggerService。

    使用 FakeAITaskRepository
    模擬 Database。

    Parameters
    ----------

    waiting_count:
        WAITING AI Task 數量

    threshold:
        Batch Trigger Threshold
    """

    task_repository = (
        FakeAITaskRepository(
            waiting_count=waiting_count
        )
    )

    if scheduler is None:

        scheduler = MockScheduler()

    service = AIBatchTriggerService(

        task_repository=(
            task_repository
        ),

        scheduler=scheduler,

        threshold=threshold

    )

    return (
        service,
        task_repository,
        scheduler
    )


# ==================================================
#
# Test 1
#
# WAITING < 50
#
# ==================================================

def test_batch_trigger_below_threshold():

    service, task_repository, scheduler = (
        create_batch_trigger(
            waiting_count=49
        )
    )

    result = service.trigger()

    assert result is False

    assert scheduler.start_count == 0

    assert scheduler.running is False

    assert (
        task_repository
        .get_waiting_tasks_count
        == 1
    )


# ==================================================
#
# Test 2
#
# WAITING == 50
#
# ==================================================

def test_batch_trigger_at_threshold():

    service, task_repository, scheduler = (
        create_batch_trigger(
            waiting_count=50
        )
    )

    result = service.trigger()

    assert result is True

    assert scheduler.start_count == 1

    assert scheduler.running is True

    assert (
        task_repository
        .get_waiting_tasks_count
        == 1
    )


# ==================================================
#
# Test 3
#
# WAITING > 50
#
# ==================================================

def test_batch_trigger_above_threshold():

    service, task_repository, scheduler = (
        create_batch_trigger(
            waiting_count=75
        )
    )

    result = service.trigger()

    assert result is True

    assert scheduler.start_count == 1

    assert scheduler.running is True

    assert (
        task_repository
        .get_waiting_tasks_count
        == 1
    )


# ==================================================
#
# Test 4
#
# Scheduler Already Running
#
# ==================================================

def test_batch_trigger_scheduler_already_running():

    scheduler = MockScheduler(
        running=True
    )

    service, task_repository, scheduler = (
        create_batch_trigger(
            waiting_count=50,
            scheduler=scheduler
        )
    )

    result = service.trigger()

    assert result is True

    # 不應重複啟動
    assert scheduler.start_count == 0

    assert scheduler.running is True


# ==================================================
#
# Test 5
#
# ArticleService Create AI Task
#
# ==================================================

def test_article_service_create_ai_task():

    service = ArticleService()

    service.task_repo = MagicMock()

    service.task_repo.insert.return_value = AITask(

        article_id=100,

        task_type="analysis",

        status="WAITING",

        priority=0,

        retry_count=0

    )

    task = service.create_ai_task(
        100
    )

    assert task is not None

    assert task.article_id == 100

    assert task.task_type == "analysis"

    assert task.status == "WAITING"

    service.task_repo.insert.assert_called_once()


# ==================================================
#
# Test 6
#
# ArticleService + Batch Trigger
#
# WAITING < 50
#
# ==================================================

def test_article_service_batch_trigger_below_threshold():

    article_service = ArticleService()

    article_service.task_repo = MagicMock()

    article_service.task_repo.insert.return_value = AITask(

        article_id=100,

        task_type="analysis",

        status="WAITING",

        priority=0,

        retry_count=0

    )

    scheduler = MockScheduler()

    (
        trigger_service,
        task_repository,
        scheduler
    ) = create_batch_trigger(

        waiting_count=49,

        scheduler=scheduler

    )

    task = article_service.create_ai_task(
        100
    )

    assert task is not None

    result = (
        trigger_service
        .check_and_trigger()
    )

    assert result is False

    assert scheduler.start_count == 0

    assert scheduler.running is False


# ==================================================
#
# Test 7
#
# ArticleService + Batch Trigger
#
# WAITING == 50
#
# ==================================================

def test_article_service_batch_trigger_at_threshold():

    article_service = ArticleService()

    article_service.task_repo = MagicMock()

    article_service.task_repo.insert.return_value = AITask(

        article_id=100,

        task_type="analysis",

        status="WAITING",

        priority=0,

        retry_count=0

    )

    scheduler = MockScheduler()

    (
        trigger_service,
        task_repository,
        scheduler
    ) = create_batch_trigger(

        waiting_count=50,

        scheduler=scheduler

    )

    task = article_service.create_ai_task(
        100
    )

    assert task is not None

    result = (
        trigger_service
        .check_and_trigger()
    )

    assert result is True

    assert scheduler.start_count == 1

    assert scheduler.running is True


# ==================================================
#
# Test 8
#
# Force Trigger
#
# ==================================================

def test_batch_trigger_force_trigger():

    service, task_repository, scheduler = (
        create_batch_trigger(
            waiting_count=0
        )
    )

    result = service.force_trigger()

    assert result is True

    assert scheduler.start_count == 1

    assert scheduler.running is True


# ==================================================
#
# Test 9
#
# Status
#
# ==================================================

def test_batch_trigger_status():

    service, task_repository, scheduler = (
        create_batch_trigger(
            waiting_count=50
        )
    )

    result = service.get_status()

    assert result["waiting"] == 50

    assert result["threshold"] == 50

    assert result["trigger"] is True

    assert result["scheduler_running"] is False
