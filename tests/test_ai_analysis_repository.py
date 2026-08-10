"""
tests/test_ai_analysis_repository.py

AutoSearch V4

P2.2.5 Step 3

AI Analysis Repository Test


Test:

    Async AI Pipeline Database Layer


"""


from database.article_repository import ArticleRepository

from models.ai_analysis import AIAnalysis

from models.article import Article





def create_repository():

    return ArticleRepository()







# ==================================================
# Test Pending AI
# ==================================================


def test_find_pending_ai():


    repo = create_repository()


    result = repo.find_pending_ai(
        limit=10
    )


    assert isinstance(
        result,
        list
    )


    repo.close()







# ==================================================
# Test AI Status Update
# ==================================================


def test_update_ai_status():


    repo = create_repository()


    articles = repo.find_pending_ai(
        limit=1
    )


    if len(articles) == 0:

        repo.close()

        return



    article_id = articles[0]["id"]



    result = repo.update_ai_status(

        article_id,

        "processing"

    )



    assert result is True



    status = repo.get_ai_status(

        article_id

    )



    assert status["ai_status"] == "processing"



    # restore

    repo.update_ai_status(

        article_id,

        "pending"

    )


    repo.close()







# ==================================================
# Test Update AI Analysis
# ==================================================


def test_update_ai_analysis():


    repo = create_repository()



    articles = repo.find_all(

        limit=1

    )



    if len(articles) == 0:


        repo.close()

        return




    article_row = articles[0]



    article = Article(


        keyword=article_row["keyword"],


        title=article_row["title"],


        url=article_row["url"],


        published=article_row["published"],


        source=article_row["source"],


        content=article_row["content"],


        crawl_time=article_row["crawl_time"],


        status=article_row["status"]


    )



    article.id = article_row["id"]




    article.ai_analysis = AIAnalysis(


        article_id=article.id,


        summary="Repository Test Summary",


        category="Test",


        keywords=[

            "AI",

            "Repository"

        ],


        importance=8,


        ai_model="TestModel",


        ai_version="1.0",


        confidence=0.95


    )





    result = repo.update_ai_analysis(

        article

    )




    assert result is True



    status = repo.get_ai_status(

        article.id

    )



    assert status["ai_status"] == "completed"



    repo.close()







# ==================================================
# Test Failed AI Retry
# ==================================================


def test_find_failed_ai():


    repo = create_repository()



    result = repo.find_failed_ai(

        limit=10

    )


    assert isinstance(

        result,

        list

    )



    repo.close()







# ==================================================
# Test AI Status Query
# ==================================================


def test_get_ai_status():


    repo = create_repository()



    articles = repo.find_all(

        limit=1

    )


    if len(articles) == 0:


        repo.close()

        return



    article_id = articles[0]["id"]



    result = repo.get_ai_status(

        article_id

    )


    assert result is not None


    assert "ai_status" in result



    repo.close()