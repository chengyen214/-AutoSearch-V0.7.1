"""
test_crawler_ai_pipeline.py

AutoSearch V4

P2.2.6

Crawler -> Async AI Task Pipeline Test

"""


from unittest.mock import MagicMock

from services.article_service import ArticleService


# ==========================================
# Mock Article
# ==========================================


class MockArticle:


    def __init__(self):

        self.id = 10

        self.title = "AI Semiconductor News"

        self.content = "TSMC NVIDIA AI Chip"

        self.source = "Crawler"

        self.ai_status = "pending"





# ==========================================
# Test
# ==========================================


def test_crawler_to_async_ai_pipeline():


    service = ArticleService()



    # Replace database

    service.repo = MagicMock()

    service.task_repo = MagicMock()





    article = MockArticle()





    # crawler insert article success

    service.repo.insert.return_value = article





    # create article

    result = service.create(

        article

    )





    # ==========================
    # Article
    # ==========================

    assert result is not None

    assert result.id == 10





    service.repo.insert.assert_called_once()





    # ==========================
    # AI Task
    # ==========================

    service.task_repo.insert.assert_called_once()





    task = (

        service.task_repo

        .insert

        .call_args[0][0]

    )





    assert task.article_id == 10


    assert task.task_type == "AI_ANALYSIS"


    assert task.status == "WAITING"


    assert task.retry_count == 0