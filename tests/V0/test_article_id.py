"""
tests/test_article_id.py

AutoSearch V4

Test:

Article insert
取得 MySQL Auto Increment ID

Step 3.0
"""



from datetime import datetime

import uuid



from models.article import Article

from database.repository import ArticleRepository





def test_article_id():


    repo = ArticleRepository()



    article = Article(


        keyword="V4 TEST",


        title="AutoSearch V4 Article ID Test",


        url="https://test.com",


        source="TEST",


        published=datetime.now(),


        # 避免 UNIQUE document_id 重複

        document_id=f"test_{uuid.uuid4().hex}",


        content="V4 Step 3.0 test"


    )





    print("\nBefore insert:")

    print(

        "Article ID =",

        article.id

    )





    result = repo.insert(article)





    print("\nAfter insert:")

    print(

        "Article ID =",

        result.id

    )





    assert result.id is not None





    print(

        "\n✅ Article ID Test OK"

    )








if __name__ == "__main__":


    test_article_id()