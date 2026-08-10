"""
test_api.py

AutoSearch V2.5 P5

測試 Retrieval API

"""

import requests


BASE_URL = "http://127.0.0.1:8000"



# ==========================
# Test Root
# ==========================

def test_root():

    response = requests.get(
        f"{BASE_URL}/"
    )


    assert response.status_code == 200


    data = response.json()


    print(data)



# ==========================
# Test All Articles
# ==========================

def test_get_articles():

    response = requests.get(
        f"{BASE_URL}/articles"
    )


    assert response.status_code == 200


    data = response.json()


    print(
        "文章數量:",
        len(data)
    )


    assert len(data) > 0



# ==========================
# Test Article ID
# ==========================

def test_get_article_by_id():

    article_id = 5


    response = requests.get(

        f"{BASE_URL}/articles/{article_id}"

    )


    assert response.status_code == 200


    data = response.json()


    print(
        data["title"]
    )



# ==========================
# Test Keyword Search
# ==========================

def test_search_keyword():

    keyword = "IC semiconductor"


    response = requests.get(

        f"{BASE_URL}/search",

        params={
            "keyword": keyword
        }

    )


    assert response.status_code == 200


    data = response.json()


    print(

        "搜尋結果:",

        len(data)

    )



# ==========================
# Test Source Search
# ==========================

def test_search_source():

    source = "TechNews 科技新報"


    response = requests.get(

        f"{BASE_URL}/source/{source}"

    )


    assert response.status_code == 200


    data = response.json()


    print(

        "來源文章:",

        len(data)

    )