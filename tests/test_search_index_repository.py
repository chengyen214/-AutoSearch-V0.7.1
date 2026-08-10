"""
tests/test_search_index_repository.py

AutoSearch V4

P2.2 Step 5

Search Index Repository Test

"""


from datetime import datetime


from database.search_index_repository import (
    SearchIndexRepository
)


from models.search_index import (
    SearchIndex
)





repository = SearchIndexRepository()







# ==================================
# Test Create
# ==================================


def test_create_search_index():


    index = SearchIndex(

        id=None,

        knowledge_id=1,

        search_text="CoWoS AI Semiconductor",

        keywords="CoWoS,AI",

        entities="台積電,NVIDIA",

        topic="Semiconductor",

        embedding_reference=1,

        index_version="1.0",

        created_time=datetime.now()

    )



    result = repository.create(

        index

    )



    print()

    print("================")

    print("Create Search Index")

    print("================")


    print(result)



    assert result.id is not None







# ==================================
# Test Get By ID
# ==================================


def test_get_by_id():


    result = repository.get_by_id(

        1

    )



    print()

    print("================")

    print("Get Search Index By ID")

    print("================")


    print(result)



    assert result is not None







# ==================================
# Test Get By Knowledge ID
# ==================================


def test_get_by_knowledge_id():


    result = repository.get_by_knowledge_id(

        1

    )



    print()

    print("================")

    print("Get By Knowledge ID")

    print("================")


    print(result)



    assert result is not None







# ==================================
# Test Keyword Search
# ==================================


def test_search_keyword():


    results = repository.search_keyword(

        "CoWoS"

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


def test_search_entity():


    results = repository.search_entity(

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
# Test Get All
# ==================================


def test_get_all():


    results = repository.get_all()



    print()

    print("================")

    print("Get All Search Index")

    print("================")


    print(results)



    assert isinstance(

        results,

        list

    )









# ==================================
# Test Update
# ==================================


def test_update_search_index():


    index = repository.get_by_id(

        1

    )



    assert index is not None



    index.topic = "AI Semiconductor"



    result = repository.update(

        index

    )



    print()

    print("================")

    print("Update Search Index")

    print("================")


    print(result)



    assert result.topic == "AI Semiconductor"









# ==================================
# Test Delete
# ==================================


def test_delete_search_index():


    result = repository.delete(

        999999

    )



    print()

    print("================")

    print("Delete Search Index")

    print("================")


    print(result)



    assert result is True