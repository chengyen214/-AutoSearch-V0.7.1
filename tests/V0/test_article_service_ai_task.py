"""
tests/test_article_service_ai_task.py

AutoSearch V4

P2.4.2

ArticleService
AI Task + AI Batch Trigger Integration

Test Flow:

ArticleService
|
v
ArticleRepository
|
v
ArchiveService
|
v
AITaskRepository
|
v
AIBatchTriggerService
|
+--> WAITING < 50
|       |
|       v
|     不啟動 Scheduler
|
+--> WAITING >= 50
        |
        v
    AIScheduler
"""


from unittest.mock import MagicMock


from services.article_service import (
    ArticleService
)


from models.ai_task import (
    AITask
)


# ==================================================
#
# Mock Article
#
# ==================================================

class MockArticle:

    def __init__(
        self,
        article_id=100
    ):

        self.id = article_id

        self.title = (
            "台積電 AI 晶片"
        )

        self.content = (
            "NVIDIA 與台積電合作"
        )

        self.keyword = ""

        self.url = (
            "https://example.com/article"
        )

        self.source = (
            "Example"
        )

        self.published = None

        self.status = "Success"

        self.document_id = (
            "test-document"
        )


# ==================================================
#
# Mock Search Result
#
# ==================================================

class MockSearchResult:

    def __init__(
        self,
        url="https://example.com/article"
    ):

        self.title = (
            "台積電 AI 晶片"
        )

        self.url = url

        self.source = (
            "Example"
        )

        self.published = None


# ==================================================
#
# Build Service
#
# ==================================================

def create_service():

    service = ArticleService()

    # ----------------------------------------------
    # Article Repository
    # ----------------------------------------------

    service.repo = MagicMock()


    # ----------------------------------------------
    # AI Task Repository
    # ----------------------------------------------

    service.task_repo = MagicMock()


    # ----------------------------------------------
    # Archive Service
    # ----------------------------------------------

    service.archive_service = MagicMock()


    # ----------------------------------------------
    # Archive Integration
    # ----------------------------------------------

    service.archive_integration = MagicMock()


    # ----------------------------------------------
    # Batch Trigger
    # ----------------------------------------------

    service.batch_trigger = MagicMock()


    return service


# ==================================================
#
# Test Create AI Task
#
# ==================================================

def test_create_ai_task():

    service = create_service()


    service.task_repo.insert.return_value = (
        AITask(

            article_id=200,

            task_type="analysis",

            status="WAITING",

            priority=0,

            retry_count=0

        )
    )


    task = service.create_ai_task(
        200
    )


    assert task is not None


    assert task.article_id == 200


    assert task.task_type == (
        "analysis"
    )


    assert task.status == (
        "WAITING"
    )


    service.task_repo.insert.assert_called_once()


# ==================================================
#
# Test AI Task Create Failure
#
# ==================================================

def test_create_ai_task_failure():

    service = create_service()


    service.task_repo.insert.return_value = (
        None
    )


    task = service.create_ai_task(
        200
    )


    assert task is None


    service.task_repo.insert.assert_called_once()


# ==================================================
#
# Test Batch Trigger
#
# ==================================================

def test_trigger_ai_batch():

    service = create_service()


    service.batch_trigger.check_and_trigger.return_value = (
        False
    )


    result = service._trigger_ai_batch()


    assert result is False


    service.batch_trigger.check_and_trigger.assert_called_once()


# ==================================================
#
# Test Batch Trigger Reached
#
# ==================================================

def test_trigger_ai_batch_reached():

    service = create_service()


    service.batch_trigger.check_and_trigger.return_value = (
        True
    )


    result = service._trigger_ai_batch()


    assert result is True


    service.batch_trigger.check_and_trigger.assert_called_once()


# ==================================================
#
# Test Batch Trigger Exception
#
# ==================================================

def test_trigger_ai_batch_exception():

    service = create_service()


    service.batch_trigger.check_and_trigger.side_effect = (
        Exception(
            "Batch Trigger Error"
        )
    )


    result = service._trigger_ai_batch()


    assert result is False


    service.batch_trigger.check_and_trigger.assert_called_once()


# ==================================================
#
# Test ArticleService
# Create AI Task + Batch Trigger
#
# ==================================================

def test_create_ai_task_then_batch_trigger():

    service = create_service()


    service.task_repo.insert.return_value = (
        AITask(

            article_id=100,

            task_type="analysis",

            status="WAITING",

            priority=0,

            retry_count=0

        )
    )


    service.batch_trigger.check_and_trigger.return_value = (
        False
    )


    task = service.create_ai_task(
        100
    )


    assert task is not None


    trigger_result = (
        service._trigger_ai_batch()
    )


    assert trigger_result is False


    service.task_repo.insert.assert_called_once()


    service.batch_trigger.check_and_trigger.assert_called_once()


# ==================================================
#
# Test Batch Trigger >= 50
#
# ==================================================

def test_batch_trigger_threshold_reached():

    service = create_service()


    service.batch_trigger.check_and_trigger.return_value = (
        True
    )


    result = service._trigger_ai_batch()


    assert result is True


    service.batch_trigger.check_and_trigger.assert_called_once()


# ==================================================
#
# Test Batch Trigger < 50
#
# ==================================================

def test_batch_trigger_threshold_not_reached():

    service = create_service()


    service.batch_trigger.check_and_trigger.return_value = (
        False
    )


    result = service._trigger_ai_batch()


    assert result is False


    service.batch_trigger.check_and_trigger.assert_called_once()


# ==================================================
#
# Test Batch Trigger Called Only After
# Successful AI Task Creation
#
# ==================================================

def test_batch_trigger_only_after_task_success():

    service = create_service()


    # ----------------------------------------------
    # AI Task Creation Failed
    # ----------------------------------------------

    service.task_repo.insert.return_value = (
        None
    )


    task = service.create_ai_task(
        300
    )


    assert task is None


    # ----------------------------------------------
    # Batch Trigger 不應自動執行
    #
    # ArticleService.create() 中只有
    # task != None 時才會呼叫
    # _trigger_ai_batch()
    #
    # ----------------------------------------------

    service.batch_trigger.check_and_trigger.assert_not_called()


# ==================================================
#
# Test Batch Trigger Injection
#
# ==================================================

def test_batch_trigger_injection():

    service = ArticleService(
        batch_trigger=MagicMock()
    )


    assert service.batch_trigger is not None


# ==================================================
#
# Test Task Repository Injection
#
# ==================================================

def test_task_repository_injection():

    task_repository = MagicMock()


    service = ArticleService(
        task_repo=task_repository
    )


    assert service.task_repo is (
        task_repository
    )


# ==================================================
#
# Test Complete P2.4.2 Integration Contract
#
# ==================================================

def test_p2_4_2_integration_contract():

    service = create_service()


    # ----------------------------------------------
    # Task Created
    # ----------------------------------------------

    task = AITask(

        article_id=500,

        task_type="analysis",

        status="WAITING",

        priority=0,

        retry_count=0

    )


    service.task_repo.insert.return_value = (
        task
    )


    # ----------------------------------------------
    # Batch Trigger Reached
    # ----------------------------------------------

    service.batch_trigger.check_and_trigger.return_value = (
        True
    )


    # ----------------------------------------------
    # Create AI Task
    # ----------------------------------------------

    result = service.create_ai_task(
        500
    )


    assert result is not None


    assert result.article_id == 500


    assert result.status == (
        "WAITING"
    )


    # ----------------------------------------------
    # Trigger Batch
    # ----------------------------------------------

    triggered = (
        service._trigger_ai_batch()
    )


    assert triggered is True


    # ----------------------------------------------
    # Verify
    # ----------------------------------------------

    service.task_repo.insert.assert_called_once()


    service.batch_trigger.check_and_trigger.assert_called_once()
