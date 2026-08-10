from services.knowledge_intelligent_search_service import (
    KnowledgeIntelligentSearchService
)





def test_intelligent_search():


    service = KnowledgeIntelligentSearchService()



    result = service.search(

        "CoWoS"

    )


    print()

    print("================")

    print("Intelligent Search")

    print("================")

    print(result)



    assert len(result) > 0


    assert "knowledge" in result[0]


    assert "score" in result[0]