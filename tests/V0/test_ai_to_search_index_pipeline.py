"""
test_ai_to_search_index_pipeline.py

AutoSearch V4

P2.2.5 Step 4

Test:

AI Analysis
    |
    v
Knowledge
    |
    v
Search Index

"""


from unittest.mock import MagicMock


from ai.worker import AIWorker


from models.ai_analysis import AIAnalysis



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





def test_ai_to_search_index_pipeline():


    worker = AIWorker()



    # Replace dependencies


    worker.article_repository = MagicMock()

    worker.task_repository = MagicMock()

    worker.ai_service = MagicMock()

    worker.knowledge_service = MagicMock()





    article = MockArticle()

    task = MockTask()





    worker.article_repository.find_model_by_id.return_value = article





    # AI Result


    analysis = AIAnalysis(


        article_id=10,


        summary="AI Semiconductor summary",


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





    worker.ai_service.analyze.return_value = analysis





    worker.article_repository.update_ai_analysis.return_value = True





    # Knowledge Auto Index success


    worker.knowledge_service.create_with_index.return_value = True





    result = worker.process_task(

        task

    )






    assert result is True



    assert article.ai_analysis is not None



    worker.knowledge_service.create_with_index.assert_called_once()





    knowledge = (

        worker.knowledge_service

        .create_with_index

        .call_args[0][0]

    )





    assert knowledge.article_id == 10



    assert knowledge.topic == "Semiconductor"



    assert "台積電" in knowledge.entities



    assert "NVIDIA" in knowledge.entities



    assert (

        "台積電 -> 生產 -> AI晶片"

        in knowledge.relations

    )