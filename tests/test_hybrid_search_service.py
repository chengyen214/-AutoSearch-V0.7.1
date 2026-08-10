"""
tests/test_hybrid_search_service.py

AutoSearch V4

P2.1 Step 2

Hybrid Search Service Test

"""


from services.hybrid_search_service import (
    HybridSearchService
)





# ==================================================
# Basic Hybrid Search
# ==================================================


def test_hybrid_search():


    service = HybridSearchService()


    results = service.search(

        "CoWoS"

    )


    print()

    print("================")
    print("Hybrid Search")
    print("================")


    print(results)



    assert isinstance(

        results,

        list

    )



    if results:


        item = results[0]


        assert "knowledge" in item


        assert "score" in item


        assert (

            "final_score"

            in item["score"]

        )





# ==================================================
# Hybrid Ranking
# ==================================================


def test_hybrid_ranking():


    service = HybridSearchService()


    results = service.search(

        "AI"

    )


    print()

    print("================")
    print("Hybrid Ranking")
    print("================")


    print(results)



    if len(results) >= 2:


        assert (

            results[0]["score"]["final_score"]

            >=

            results[1]["score"]["final_score"]

        )





# ==================================================
# Hybrid Score
# ==================================================


def test_hybrid_score():


    service = HybridSearchService()


    results = service.search(

        "半導體"

    )


    print()

    print("================")
    print("Hybrid Score")
    print("================")



    print(results)



    if results:


        score = results[0]["score"]



        assert (

            score["keyword_score"]

            >= 0

        )


        assert (

            score["ranking_score"]

            >= 0

        )


        assert (

            score["semantic_score"]

            >= 0

        )


        assert (

            score["final_score"]

            >= 0

        )





# ==================================================
# Empty Query
# ==================================================


def test_empty_query():


    service = HybridSearchService()


    results = service.search(

        ""

    )


    print()

    print("================")
    print("Empty Hybrid Search")
    print("================")


    print(results)



    assert results == []