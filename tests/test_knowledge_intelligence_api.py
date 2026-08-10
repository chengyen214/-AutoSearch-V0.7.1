"""
V4 P1.6 Step 6

Knowledge Intelligence API Test

"""


from fastapi.testclient import TestClient


from api.main import app





client = TestClient(app)





# ==================================
# Article Intelligence API
# ==================================


def test_article_intelligence():


    response = client.get(

        "/intelligence/article/1"

    )


    print()

    print("================")

    print("Article Intelligence API")

    print("================")

    print(response.json())



    assert response.status_code == 200



    data = response.json()


    assert data["success"] is True





# ==================================
# Top Intelligence API
# ==================================


def test_top_intelligence():


    response = client.get(

        "/intelligence/top"

    )



    print()

    print("================")

    print("Top Intelligence API")

    print("================")

    print(response.json())



    assert response.status_code == 200



    data = response.json()


    assert data["success"] is True



    assert "data" in data






# ==================================
# High Quality API
# ==================================


def test_high_quality():


    response = client.get(

        "/intelligence/high-quality?score=8"

    )



    print()

    print("================")

    print("High Quality API")

    print("================")

    print(response.json())



    assert response.status_code == 200



    data = response.json()


    assert data["success"] is True