"""
tests/test_search_index_api.py

AutoSearch V4

P2.2 Step 6.3

Search Index API Test

"""


from fastapi.testclient import TestClient


from api.main import app



client = TestClient(app)






# ==================================
# Test Build Index
# ==================================


def test_build_index_api():


    response = client.post(

        "/knowledge/search-index/build/1"

    )


    print()

    print("================")

    print("Build Search Index API")

    print("================")


    print(response.json())



    assert response.status_code in [

        200,

        404

    ]



    if response.status_code == 200:


        data = response.json()


        assert data["success"] is True







# ==================================
# Test Get Index
# ==================================


def test_get_index_api():


    response = client.get(

        "/knowledge/search-index/1"

    )


    print()

    print("================")

    print("Get Search Index API")

    print("================")


    print(response.json())



    assert response.status_code in [

        200,

        404

    ]



    if response.status_code == 200:


        data = response.json()


        assert data["success"] is True







# ==================================
# Test Keyword Search
# ==================================


def test_keyword_search_api():


    response = client.get(

        "/knowledge/search-index/keyword",

        params={

            "q": "AI"

        }

    )


    print()

    print("================")

    print("Keyword Search API")

    print("================")


    print(response.json())



    assert response.status_code == 200



    data = response.json()



    assert data["success"] is True


    assert data["count"] >= 0







# ==================================
# Test Entity Search
# ==================================


def test_entity_search_api():


    response = client.get(

        "/knowledge/search-index/entity",

        params={

            "name": "台積電"

        }

    )


    print()

    print("================")

    print("Entity Search API")

    print("================")


    print(response.json())



    assert response.status_code == 200



    data = response.json()



    assert data["success"] is True


    assert data["count"] >= 0







# ==================================
# Test Rebuild
# ==================================


def test_rebuild_index_api():


    response = client.post(

        "/knowledge/search-index/rebuild/1"

    )


    print()

    print("================")

    print("Rebuild Search Index API")

    print("================")


    print(response.json())



    assert response.status_code in [

        200,

        404

    ]



    if response.status_code == 200:


        data = response.json()


        assert data["success"] is True







# ==================================
# Missing Parameter
# ==================================


def test_keyword_missing_parameter():


    response = client.get(

        "/knowledge/search-index/keyword"

    )


    print()

    print("================")

    print("Keyword Missing Parameter")

    print("================")


    print(response.json())



    assert response.status_code == 422