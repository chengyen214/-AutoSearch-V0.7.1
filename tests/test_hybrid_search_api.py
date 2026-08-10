"""
tests/test_hybrid_search_api.py

AutoSearch V4

P2.1 Step 3

Hybrid Search API Test

"""


from fastapi.testclient import TestClient


from api.main import app





client = TestClient(app)







# ==================================
# Test Basic API
# ==================================


def test_hybrid_search_api():


    response = client.get(

        "/knowledge/search/hybrid",

        params={

            "q": "CoWoS"

        }

    )



    print()

    print("================")

    print("Hybrid Search API")

    print("================")


    print(

        response.json()

    )



    assert response.status_code == 200



    data = response.json()



    assert (

        data["success"]

        is True

    )


    assert (

        data["keyword"]

        ==

        "CoWoS"

    )



    assert (

        "data"

        in

        data

    )







# ==================================
# Test Result Structure
# ==================================


def test_hybrid_search_result():


    response = client.get(

        "/knowledge/search/hybrid",

        params={

            "q": "AI"

        }

    )



    data = response.json()



    print()

    print("================")

    print("Hybrid Search Result")

    print("================")


    print(data)



    assert response.status_code == 200



    assert (

        data["count"]

        >=

        0

    )



    assert isinstance(

        data["data"],

        list

    )







# ==================================
# Test Top K
# ==================================


def test_hybrid_search_top_k():


    response = client.get(

        "/knowledge/search/hybrid",

        params={

            "q": "半導體",

            "top_k": 1

        }

    )



    data = response.json()



    print()

    print("================")

    print("Hybrid Search Top K")

    print("================")


    print(data)



    assert response.status_code == 200



    assert (

        data["top_k"]

        ==

        1

    )



    assert (

        len(data["data"])

        <=

        1

    )







# ==================================
# Test Missing Parameter
# ==================================


def test_hybrid_search_missing_parameter():


    response = client.get(

        "/knowledge/search/hybrid"

    )



    print()

    print("================")

    print("Hybrid Search Missing Parameter")

    print("================")


    print(response.json())



    assert (

        response.status_code

        ==

        422

    )