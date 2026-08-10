"""
tests/test_knowledge_search_ranking.py

AutoSearch V4

P1.7 Step 3

Knowledge Search Ranking Optimization Test

"""


from services.knowledge_intelligent_search_service import (
    KnowledgeIntelligentSearchService
)





def test_search_ranking():



    service = KnowledgeIntelligentSearchService()





    # ==========================
    # Search
    # ==========================


    result = service.search(

        "CoWoS"

    )





    # ==========================
    # Output
    # ==========================


    print()

    print("================")

    print("Knowledge Search Ranking")

    print("================")



    for item in result:


        print()


        print(

            "Knowledge:"

        )


        print(

            item["knowledge"]

        )



        print()


        print(

            "Score:"

        )


        print(

            item["score"]

        )



        print()


        print(

            "Search Score:"

        )


        print(

            item["search_score"]

        )







    # ==========================
    # Assertion
    # ==========================


    assert len(result) > 0



    assert (

        "search_score"

        in result[0]

    )



    assert (

        "final_score"

        in result[0]["search_score"]

    )



    assert (

        result[0]["search_score"]["final_score"]

        > 0

    )