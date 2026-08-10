"""
tests/test_knowledge_pipeline.py

AutoSearch V4

P1.6 Step 3

AI -> Knowledge Pipeline Test

流程:

Article Content

        |
        v

AI Analyzer

        |
        v

Knowledge Extractor

        |
        v

Knowledge Archive

"""


from pipeline.knowledge_pipeline import (
    KnowledgePipeline
)


from models.article import Article





def test_knowledge_pipeline():



    # ==========================
    # 建立測試 Article
    # ==========================


    article = Article(

        keyword="IC",

        title="台積電2nm製程量產與CoWoS需求成長",

        content="""

        台積電宣布2nm先進製程量產。

        AI Chip需求快速增加，

        CoWoS先進封裝需求提升。

        HBM記憶體市場同步成長。

        """

    )




    # ==========================
    # Pipeline
    # ==========================


    pipeline = KnowledgePipeline()



    knowledge = pipeline.run(

        article

    )





    # ==========================
    # Output
    # ==========================


    print()

    print("================")

    print("Knowledge Pipeline")

    print("================")


    print(

        knowledge.to_dict()

    )





    # ==========================
    # Assertion
    # ==========================


    assert knowledge is not None


    assert knowledge.article_id == article.id



    assert knowledge.topic is not None



    assert len(

        knowledge.entities

    ) > 0



    assert len(

        knowledge.relations

    ) > 0