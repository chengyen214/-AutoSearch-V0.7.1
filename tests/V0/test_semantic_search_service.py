"""
tests/test_semantic_search_service.py

AutoSearch V4

P1.7 Step 4.3

Semantic Search Service Test

"""


from services.semantic_search_service import (
    SemanticSearchService
)



# ==================================================
# Semantic Search
# ==================================================


def test_semantic_search():

    service = SemanticSearchService()


    results = service.search(

        "CoWoS"

    )


    print()

    print("================")
    print("Semantic Search")
    print("================")


    for item in results:

        print()

        print("Knowledge:")

        print(

            item["knowledge"].to_dict()

        )


        print()

        print("Semantic Score:")

        print(

            item["semantic_score"]

        )



    assert len(results) > 0


    assert (

        "semantic_score"

        in results[0]

    )


    assert (

        results[0]["semantic_score"]

        >= 0

    )


    assert (

        results[0]["semantic_score"]

        <= 1

    )



# ==================================================
# Ranking
# ==================================================


def test_semantic_ranking():


    service = SemanticSearchService()


    results = service.search(

        "AI"

    )


    print()

    print("================")
    print("Semantic Ranking")
    print("================")


    scores = []


    for item in results:


        score = item[

            "semantic_score"

        ]


        scores.append(

            score

        )


        print(

            score

        )


    assert scores == sorted(

        scores,

        reverse=True

    )



# ==================================================
# Top K
# ==================================================


def test_semantic_top_k():


    service = SemanticSearchService()


    results = service.search(

        "半導體",

        top_k=1

    )


    print()

    print("================")
    print("Semantic Top K")
    print("================")


    print(

        results

    )


    assert len(results) <= 1



# ==================================================
# Empty Query
# ==================================================


def test_empty_query():


    service = SemanticSearchService()


    results = service.search(

        ""

    )


    print()

    print("================")
    print("Empty Query")
    print("================")


    print(

        results

    )


    assert results == []