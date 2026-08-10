"""
test_article_service_ai_task.py

AutoSearch V4

Test:

ArticleService

P2.2.6 Step 7

Article Create
        |
        v
ArticleRepository
        |
        v
AITaskRepository

"""


from unittest.mock import MagicMock


from services.article_service import ArticleService

from models.ai_task import AITask





class MockArticle:

    def __init__(self):

        self.id = 100

        self.title = "台積電 AI 晶片"

        self.content = "NVIDIA 與台積電合作"







# ==================================================
#
# Test Create Article + AI Task
#
# ==================================================


def test_create_article_success():


    service = ArticleService()



    # Mock Repository

    service.repo = MagicMock()

    service.task_repo = MagicMock()



    article = MockArticle()



    service.repo.insert.return_value = article



    service.task_repo.insert.return_value = AITask(

        article_id=100,

        task_type="AI_ANALYSIS",

        status="WAITING",

        priority=0,

        retry_count=0

    )





    result = service.create(

        article

    )





    assert result is not None


    assert result.id == 100




    service.repo.insert.assert_called_once_with(

        article

    )





    service.task_repo.insert.assert_called_once()







# ==================================================
#
# Test AI Task Create
#
# ==================================================


def test_create_ai_task():


    service = ArticleService()



    service.task_repo = MagicMock()



    service.task_repo.insert.return_value = AITask(

        article_id=200,

        task_type="AI_ANALYSIS",

        status="WAITING",

        priority=0,

        retry_count=0

    )





    task = service.create_ai_task(

        200

    )





    assert task is not None



    assert task.article_id == 200


    assert task.task_type == "AI_ANALYSIS"


    assert task.status == "WAITING"





    service.task_repo.insert.assert_called_once()
