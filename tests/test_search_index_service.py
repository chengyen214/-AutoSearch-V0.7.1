"""
tests/test_search_index_service.py

AutoSearch V4

P2.2 Step 6.2

Search Index Service Test

"""


from datetime import datetime



from services.search_index_service import (
    SearchIndexService
)



from models.knowledge import (
    Knowledge
)





service = SearchIndexService()







# ==================================
# Mock Knowledge
# ==================================


def create_mock_knowledge():


    knowledge = Knowledge()



    knowledge.id = 1



    knowledge.article_id = 1



    knowledge.topic = (

        "Semiconductor"

    )



    knowledge.entities = (

        "台積電,NVIDIA"

    )



    knowledge.relations = (

        "AI,2nm,CoWoS"

    )



    knowledge.knowledge_version = (

        "1.0"

    )



    knowledge.created_time = (

        datetime.now()

    )



    return knowledge







# ==================================
# Test Build Index
# ==================================


def test_build_index():


    knowledge = create_mock_knowledge()



    result = service.build_index(

        knowledge

    )



    print()

    print("================")

    print("Build Search Index")

    print("================")



    print(result)



    assert result is not None



    assert result.knowledge_id == 1







# ==================================
# Test Get Index
# ==================================


def test_get_index():


    result = service.get_knowledge_index(

        1

    )



    print()

    print("================")

    print("Get Knowledge Index")

    print("================")



    print(result)



    assert result is not None







# ==================================
# Test Keyword Search
# ==================================


def test_keyword_search():


    results = service.keyword_search(

        "Semiconductor"

    )



    print()

    print("================")

    print("Keyword Search")

    print("================")



    print(results)



    assert isinstance(

        results,

        list

    )









# ==================================
# Test Entity Search
# ==================================


def test_entity_search():


    results = service.entity_search(

        "台積電"

    )



    print()

    print("================")

    print("Entity Search")

    print("================")



    print(results)



    assert isinstance(

        results,

        list

    )









# ==================================
# Test Rebuild Index
# ==================================


def test_rebuild_index():


    knowledge = create_mock_knowledge()



    knowledge.topic = (

        "AI Packaging"

    )



    result = service.rebuild_index(

        knowledge

    )



    print()

    print("================")

    print("Rebuild Search Index")

    print("================")



    print(result)



    assert result is not None