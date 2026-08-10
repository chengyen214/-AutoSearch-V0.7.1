"""
tests/test_knowledge_service.py

AutoSearch V4

P1.4 Knowledge Retrieval Layer

Knowledge Service Test

"""


from services.knowledge_service import (
    KnowledgeService
)





def test_get_by_article_id():


    service = KnowledgeService()


    result = service.get_by_article_id(

        1

    )


    print()

    print("================")

    print("Article Knowledge")

    print("================")

    print(result)


    assert result is not None







def test_search_topic():


    service = KnowledgeService()


    result = service.search_topic(

        "半導體"

    )


    print()

    print("================")

    print("Topic Search")

    print("================")

    print(result)


    assert isinstance(

        result,

        list

    )







def test_search_entity():


    service = KnowledgeService()


    result = service.search_entity(

        "TSMC"

    )


    print()

    print("================")

    print("Entity Search")

    print("================")

    print(result)


    assert isinstance(

        result,

        list

    )







def test_search_relation():


    service = KnowledgeService()


    result = service.search_relation(

        "製程"

    )


    print()

    print("================")

    print("Relation Search")

    print("================")

    print(result)


    assert isinstance(

        result,

        list

    )








def test_search():


    service = KnowledgeService()


    result = service.search(

        "AI"

    )


    print()

    print("================")

    print("Full Search")

    print("================")

    print(result)


    assert isinstance(

        result,

        list

    )








def test_latest():


    service = KnowledgeService()


    result = service.latest(

        5

    )


    print()

    print("================")

    print("Latest Knowledge")

    print("================")

    print(result)


    assert isinstance(

        result,

        list

    )


    assert len(result) <= 5