"""
test_ai_to_knowledge_pipeline.py

AutoSearch V4

P2.2.5

AI Analysis -> Knowledge Pipeline Test

Flow:

Article
 |
 v
AIWorker
 |
 v
AIAnalysisService
 |
 v
KnowledgeService
 |
 v
KnowledgeRepository

"""


from unittest.mock import MagicMock


from ai.worker import AIWorker

from models.ai_analysis import AIAnalysis

from models.knowledge import Knowledge




class MockArticle:


    def __init__(self):


        self.id = 10


        self.title = "台積電AI晶片量產"


        self.content = """
        NVIDIA與台積電合作，
        推動AI GPU與2nm製程。
        """



        self.ai_analysis = None






class MockTask:


    def __init__(self):


        self.id = 1


        self.article_id = 10






def test_ai_to_knowledge_pipeline():


    worker = AIWorker()



    # Mock repositories


    worker.article_repository = MagicMock()

    worker.task_repository = MagicMock()

    worker.ai_service = MagicMock()

    worker.knowledge_service = MagicMock()






    article = MockArticle()


    task = MockTask()





    # Article


    worker.article_repository.find_model_by_id.return_value = article





    # AI Result


    analysis = AIAnalysis(


        article_id=10,


        summary="AI晶片產業分析",


        category="Semiconductor",


        keywords=[

            "AI",

            "GPU",

            "2nm"

        ],


        entities=[

            "台積電",

            "NVIDIA"

        ],


        relations=[

            "台積電 -> 生產 -> AI晶片"

        ],


        importance=9,


        ai_model="Test",


        ai_version="1.0",


        confidence=0.9

    )





    worker.ai_service.analyze.return_value = analysis





    # Article update success


    worker.article_repository.update_ai_analysis.return_value = True






    # Knowledge create success


    knowledge = Knowledge(


        article_id=10,


        topic="Semiconductor",


        entities=[

            "台積電",

            "NVIDIA"

        ],


        relations=[

            "台積電 -> 生產 -> AI晶片"

        ]

    )




    worker.knowledge_service.create_from_ai.return_value = knowledge







    result = worker.process_task(

        task

    )






    assert result is True





    # AI Analysis attached


    assert article.ai_analysis is not None





    # Knowledge pipeline called


    worker.knowledge_service.create_from_ai.assert_called_once_with(

        article,

        analysis

    )





    # Task completed


    worker.task_repository.mark_done.assert_called_once_with(

        task.id

    )
