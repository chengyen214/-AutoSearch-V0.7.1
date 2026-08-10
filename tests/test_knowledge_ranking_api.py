"""
tests/test_knowledge_ranking_api.py

AutoSearch V4

P1.5 Step 6

Knowledge Ranking API Test


測試:

1. Top Ranking API

2. Score Filter API


"""


from fastapi.testclient import TestClient


from api.main import app





client = TestClient(app)






# ==================================================
# Top Ranking API
# ==================================================


def test_top_ranking_api():


    response = client.get(

        "/knowledge/ranking/top"

    )



    print()

    print("================")

    print("Top Ranking API")

    print("================")

    print(

        response.json()

    )



    assert response.status_code == 200



    data = response.json()



    assert data["success"] is True


    assert "data" in data










# ==================================================
# Score Filter API
# ==================================================


def test_score_filter_api():


    response = client.get(

        "/knowledge/ranking/score/8"

    )



    print()

    print("================")

    print("Score Filter API")

    print("================")

    print(

        response.json()

    )



    assert response.status_code == 200



    data = response.json()



    assert data["success"] is True


    assert data["score"] == 8



    assert "data" in data