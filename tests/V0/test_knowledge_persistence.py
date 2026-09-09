"""
test_knowledge_persistence.py

AutoSearch V4

P1.6 Step 4

Knowledge Persistence Pipeline Test


Flow:

Article

    |

AI Analyzer

    |

Knowledge Extractor

    |

Knowledge

    |

KnowledgeRepository

    |

knowledge_archive

"""


from pipeline.knowledge_pipeline import (
    KnowledgePipeline
)


from models.article import Article





def test_knowledge_persistence():



    # ==========================
    # 建立測試 Article
    # ==========================


    article = Article(


        keyword="IC",


        title="台積電2nm製程量產與CoWoS需求成長",


        content="""


        台積電宣布2nm先進製程量產。


        AI Chip需求快速增加。


        CoWoS先進封裝需求提升。


        HBM記憶體市場同步成長。


        """

    )

    article.id = 1


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

    print("Knowledge Persistence")

    print("================")



    print(

        knowledge.to_dict()

    )





    # ==========================
    # Assert
    # ==========================


    assert knowledge is not None


    assert knowledge.article_id == 1


    assert knowledge.topic is not None


    assert knowledge.has_knowledge