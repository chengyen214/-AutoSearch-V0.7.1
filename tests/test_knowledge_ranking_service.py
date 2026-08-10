from services.knowledge_ranking_service import (
    KnowledgeRankingService
)



def test_ranking_service():


    service = KnowledgeRankingService()



    print()


    print("================")

    print("Ranking Calculate")

    print("================")



    score = service.calculate_ranking(

        importance=10,

        confidence=0.95,

        quality_score=9,

        freshness_score=10

    )


    print(

        "Ranking:",

        score

    )



    assert score > 8






def test_top_ranking():


    service = KnowledgeRankingService()



    result = service.get_top_ranking(

        10

    )


    print()


    print("================")

    print("Top Ranking")

    print("================")



    print(result)



    assert isinstance(

        result,

        list

    )