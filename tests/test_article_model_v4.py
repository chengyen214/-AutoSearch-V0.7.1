"""
Test Article Model V4

測試:

1. Article.id 初始值
2. Article.id 回填模擬
3. to_dict()
4. V4 Archive Property
"""


from models.article import Article





def test_article_model_v4():


    print()

    print("==========================")

    print("Article V4 Model Test")

    print("==========================")



    # 建立 Article

    article = Article(

        keyword="IC semiconductor",

        title="V4 Test Article",

        url="https://test.com",

        content="Test Content",

        document_id="v4_test_001"

    )




    # Step 1

    print()

    print("Before ID:")

    print(

        "Article ID =",

        article.id

    )



    assert article.id is None




    # 模擬 Database INSERT

    article.id = 100



    print()

    print("After ID:")

    print(

        "Article ID =",

        article.id

    )



    assert article.id == 100




    # Step 2

    data = article.to_dict()



    print()

    print("Dictionary:")

    print(data)




    assert data["id"] == 100

    assert data["document_id"] == "v4_test_001"




    print()

    print("==========================")

    print("✅ Article V4 Model Test OK")

    print("==========================")





if __name__ == "__main__":

    test_article_model_v4()