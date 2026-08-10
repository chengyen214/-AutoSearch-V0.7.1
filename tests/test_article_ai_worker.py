"""
Test AutoSearch V4

ArticleRepository
AI Worker Foundation

"""

from database.article_repository import ArticleRepository



def test_update_ai_analysis():
    

    from models.ai_analysis import AIAnalysis



    repo = ArticleRepository()



    article = repo.find_model_by_id(

        1

    )



    analysis = AIAnalysis()



    analysis.summary = "Test AI Summary"


    analysis.category = "Semiconductor"


    analysis.keywords = [

        "AI",

        "Chip"

    ]


    analysis.importance = 8


    analysis.confidence = 0.95


    analysis.ai_model = "test"



    article.ai_analysis = analysis





    result = repo.update_ai_analysis(

        article

    )



    print()

    print(

        "Update Result:",

        result

    )



    assert result is True



    repo.close()