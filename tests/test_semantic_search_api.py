"""
tests/test_semantic_search_api.py

AutoSearch V4

P1.7 Step 4.4

Semantic Search API Test

"""


from fastapi.testclient import TestClient


from api.main import app



client = TestClient(app)



# ==================================================
# Semantic Search API
# ==================================================


def test_semantic_search_api():


    response = client.get(

        "/semantic-search?q=CoWoS"

    )


    print()

    print("================")
    print("Semantic Search API")
    print("================")


    print(

        response.json()

    )


    assert response.status_code == 200


    data = response.json()


    assert data["success"] is True


    assert data["keyword"] == "CoWoS"


    assert data["count"] >= 0


    assert "data" in data



# ==================================================
# Semantic Search Result
# ==================================================


def test_semantic_search_result():


    response = client.get(

        "/semantic-search?q=AI"

    )


    data = response.json()


    print()

    print("================")
    print("Semantic Search Result")
    print("================")


    print(

        data

    )


    assert response.status_code == 200


    if data["count"] > 0:


        item = data["data"][0]


        assert "knowledge" in item


        assert "semantic_score" in item


        assert (

            item["semantic_score"]

            >= 0

        )


        assert (

            item["semantic_score"]

            <= 1

        )



# ==================================================
# Empty Keyword
# ==================================================


def test_semantic_search_empty():


    response = client.get(

        "/semantic-search?q="

    )


    print()

    print("================")
    print("Empty Semantic Search")
    print("================")


    print(

        response.json()

    )


    assert response.status_code == 200


    data = response.json()


    assert data["success"] is True



# ==================================================
# Missing Parameter
# ==================================================


def test_semantic_search_missing_parameter():


    response = client.get(

        "/semantic-search"

    )


    print()

    print("================")
    print("Missing Parameter")
    print("================")


    print(

        response.json()

    )


    assert response.status_code == 422