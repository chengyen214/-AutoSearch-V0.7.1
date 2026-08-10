"""
tests/test_knowledge_api.py

AutoSearch V4

P1.4 Knowledge Retrieval API Test

"""


from fastapi.testclient import TestClient


from api.main import app



client = TestClient(app)





def test_get_article_knowledge():


    response = client.get(

        "/knowledge/article/1"

    )


    print(response.json())


    assert response.status_code == 200





def test_topic_search():


    response = client.get(

        "/knowledge/topic/Semiconductor"

    )


    print(response.json())


    assert response.status_code == 200





def test_entity_search():


    response = client.get(

        "/knowledge/entity/AI"

    )


    print(response.json())


    assert response.status_code == 200





def test_relation_search():


    response = client.get(

        "/knowledge/relation/台積電"

    )


    print(response.json())


    assert response.status_code == 200





def test_full_search():


    response = client.get(

        "/knowledge/search?q=CoWoS"

    )


    print(response.json())


    assert response.status_code == 200





def test_latest():


    response = client.get(

        "/knowledge/latest"

    )


    print(response.json())


    assert response.status_code == 200