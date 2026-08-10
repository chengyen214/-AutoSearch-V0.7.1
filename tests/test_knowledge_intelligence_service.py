"""
V4 P1.6 Step 5

Knowledge Intelligence Service Test
"""


from services.knowledge_intelligence_service import (
    KnowledgeIntelligenceService
)





def test_get_knowledge():


    service = KnowledgeIntelligenceService()



    result = service.get_knowledge(

        1

    )


    print()

    print("================")

    print("Knowledge Intelligence")

    print("================")


    print(result)



    assert result is not None



    assert "knowledge" in result



    assert "score" in result






def test_top_intelligence():


    service = KnowledgeIntelligenceService()



    result = service.get_top_intelligence(

        10

    )



    print()

    print("================")

    print("Top Intelligence")

    print("================")

    print(result)



    assert result is not None