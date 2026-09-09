"""
Test Knowledge Extractor

V4 P1.6 Step 2

"""


from ai.knowledge_extractor import KnowledgeExtractor

from models.ai_analysis import AIAnalysis





def test_knowledge_extractor():


    ai = AIAnalysis(

        summary="台積電2nm製程量產，AI Chip需求成長",

        category="Semiconductor",

        keywords=[

            "2nm",

            "AI Chip",

            "CoWoS"

        ],

        importance=10

    )



    extractor = KnowledgeExtractor()



    knowledge = extractor.extract(

        ai,

        article_id=1

    )



    print()

    print("================")

    print("Knowledge Extractor")

    print("================")



    print(

        knowledge.to_dict()

    )



    assert knowledge.article_id == 1


    assert knowledge.topic == "Semiconductor"


    assert "2nm" in knowledge.entities


    assert len(

        knowledge.relations

    ) > 0