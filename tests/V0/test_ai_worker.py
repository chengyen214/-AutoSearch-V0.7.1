"""
tests/test_ai_worker.py

AutoSearch V4

P2.2.5

AI Worker Test
"""

from unittest.mock import MagicMock

from ai.worker import AIWorker

from models.ai_analysis import AIAnalysis


# ==================================================
# Mock Article
# ==================================================

class MockArticle:

    def __init__(self):

        self.id = 10

        self.title = "台積電 AI 晶片"

        self.content = """
        NVIDIA 與台積電合作，

        推動 AI GPU 與 2nm 製程。
        """

        self.ai_analysis = None


# ==================================================
# Mock Task
# ==================================================

class MockTask:

    def __init__(self):

        self.id = 1

        self.article_id = 10

        self.task_type = "AI_ANALYSIS"

        self.status = "WAITING"

        self.priority = 10

        self.retry_count = 0


# ==================================================
#
# Success Flow
#
# ==================================================

def test_ai_worker_success():

    worker = AIWorker()


    # ==================================================
    # Replace repositories / services
    # ==================================================

    worker.article_repository = MagicMock()

    worker.task_repository = MagicMock()

    worker.ai_service = MagicMock()

    # V4 Knowledge Archive
    #
    # 避免測試真的寫入 MySQL
    #
    worker.knowledge_service = MagicMock()


    article = MockArticle()

    task = MockTask()


    # ==================================================
    # Article
    # ==================================================

    worker.article_repository.find_model_by_id.return_value = article


    # ==================================================
    # AI Analysis
    # ==================================================

    worker.ai_service.analyze.return_value = AIAnalysis(

        article_id=10,

        summary="AI Summary",

        category="Semiconductor",

        keywords=[

            "AI",

            "TSMC"

        ],

        entities=[

            "台積電",

            "NVIDIA"

        ],

        relations=[

            "台積電 -> 生產 -> AI晶片"

        ],

        importance=8,

        ai_model="Test",

        ai_version="1.0",

        confidence=0.9

    )


    # ==================================================
    # Article AI Analysis Update
    # ==================================================

    worker.article_repository.update_ai_analysis.return_value = True


    # ==================================================
    # Knowledge Archive
    # ==================================================

    worker.knowledge_service.create_with_index.return_value = True


    # ==================================================
    # Execute
    # ==================================================

    result = worker.process_task(

        task

    )


    # ==================================================
    # Result
    # ==================================================

    assert result is True

    assert article.ai_analysis is not None


    # ==================================================
    # Queue status
    # ==================================================

    worker.task_repository.mark_running.assert_called_with(

        task.id

    )

    worker.task_repository.mark_done.assert_called_with(

        task.id

    )


    # ==================================================
    # Article status
    # ==================================================

    worker.article_repository.update_ai_status.assert_any_call(

        article.id,

        "processing"

    )

    worker.article_repository.update_ai_status.assert_any_call(

        article.id,

        "completed"

    )


    # ==================================================
    # Knowledge Archive
    # ==================================================

    worker.knowledge_service.create_with_index.assert_called_once()


# ==================================================
#
# Failed Flow
#
# ==================================================

def test_ai_worker_failed():

    worker = AIWorker()


    # ==================================================
    # Replace repositories / services
    # ==================================================

    worker.article_repository = MagicMock()

    worker.task_repository = MagicMock()

    worker.ai_service = MagicMock()

    # V4 Knowledge Archive
    #
    # AI 分析失敗時不應該建立 Knowledge
    #
    worker.knowledge_service = MagicMock()


    article = MockArticle()

    task = MockTask()


    # ==================================================
    # Article
    # ==================================================

    worker.article_repository.find_model_by_id.return_value = article


    # ==================================================
    # AI Analysis Failed
    # ==================================================

    worker.ai_service.analyze.return_value = None


    # ==================================================
    # Execute
    # ==================================================

    result = worker.process_task(

        task

    )


    # ==================================================
    # Result
    # ==================================================

    assert result is False


    # ==================================================
    # Queue status
    # ==================================================

    worker.task_repository.mark_running.assert_called_with(

        task.id

    )

    worker.task_repository.mark_failed.assert_called_with(

        task.id

    )


    # ==================================================
    # Article status
    # ==================================================

    worker.article_repository.update_ai_status.assert_any_call(

        article.id,

        "processing"

    )

    worker.article_repository.update_ai_status.assert_any_call(

        article.id,

        "failed"

    )


    # ==================================================
    # Knowledge Archive
    # ==================================================

    worker.knowledge_service.create_with_index.assert_not_called()
