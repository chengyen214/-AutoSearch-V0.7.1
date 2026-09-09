"""
tests/test_api.py

AutoSearch V4

API Retrieval Test

測試：

V4:
    Dashboard
    API Root
    Article API
    Search API
    Keyword Search
    Entity Search
    Hybrid Search
    Search Pagination
    Hybrid Search Pagination
    Search Index
"""

import requests


BASE_URL = "http://127.0.0.1:8000"


# ==================================================
# Helper
# ==================================================

def assert_json_response(response):
    """
    確認 API 回傳 JSON。
    """

    assert "application/json" in response.headers.get(
        "content-type",
        ""
    )

    return response.json()


def assert_search_response(
    data,
    query_key,
    query_value
):
    """
    確認一般 Search API Response。
    """

    assert data["success"] is True

    assert data[query_key] == query_value

    assert "count" in data

    assert "data" in data

    assert isinstance(
        data["count"],
        int
    )

    assert isinstance(
        data["data"],
        list
    )


def assert_paginated_response(
    data,
    query
):
    """
    確認 Pagination Search API Response。
    """

    assert data["success"] is True

    assert data["keyword"] == query

    assert data["page"] == 1

    assert data["page_size"] == 20

    assert "count" in data

    assert "total" in data

    assert "data" in data

    assert isinstance(
        data["count"],
        int
    )

    assert isinstance(
        data["total"],
        int
    )

    assert isinstance(
        data["data"],
        list
    )


# ==================================================
# Test Dashboard
# ==================================================

def test_root():

    response = requests.get(
        f"{BASE_URL}/"
    )

    assert response.status_code == 200

    assert "text/html" in response.headers.get(
        "content-type",
        ""
    )

    print(
        "Dashboard:",
        response.status_code
    )


# ==================================================
# Test API Root
# ==================================================

def test_api_root():

    response = requests.get(
        f"{BASE_URL}/api"
    )

    assert response.status_code == 200

    data = assert_json_response(
        response
    )

    print(
        "API Root:",
        data
    )

    assert data["project"] == "AutoSearch V4"

    assert data["version"] == "4.0"

    assert data["status"] == "running"


# ==================================================
# Test All Articles
# ==================================================

def test_get_articles():

    response = requests.get(
        f"{BASE_URL}/articles"
    )

    assert response.status_code == 200

    data = assert_json_response(
        response
    )

    print(
        "文章數量:",
        len(data)
    )

    assert isinstance(
        data,
        list
    )

    assert len(data) > 0


# ==================================================
# Test Article ID
# ==================================================

def test_get_article_by_id():

    article_id = 5

    response = requests.get(
        f"{BASE_URL}/articles/{article_id}"
    )

    assert response.status_code == 200

    data = assert_json_response(
        response
    )

    print(
        "Article:",
        data["title"]
    )

    assert "id" in data

    assert "title" in data

    assert data["id"] == article_id


# ==================================================
# Test Full Search
# ==================================================

def test_search_keyword():

    query = "IC semiconductor"

    response = requests.get(
        f"{BASE_URL}/search",
        params={
            "q": query
        }
    )

    assert response.status_code == 200

    data = assert_json_response(
        response
    )

    print(
        "Full Search:",
        len(data["data"])
    )

    assert_search_response(
        data,
        "keyword",
        query
    )


# ==================================================
# Test Keyword Search
# ==================================================

def test_search_keyword_route():

    keyword = "semiconductor"

    response = requests.get(
        f"{BASE_URL}/search/keyword/{keyword}"
    )

    assert response.status_code == 200

    data = assert_json_response(
        response
    )

    print(
        "Keyword Search:",
        len(data["data"])
    )

    assert_search_response(
        data,
        "keyword",
        keyword
    )


# ==================================================
# Test Entity Search
# ==================================================

def test_search_entity():

    entity = "NVIDIA"

    response = requests.get(
        f"{BASE_URL}/search/entity/{entity}"
    )

    assert response.status_code == 200

    data = assert_json_response(
        response
    )

    print(
        "Entity Search:",
        len(data["data"])
    )

    assert_search_response(
        data,
        "entity",
        entity
    )


# ==================================================
# Test Hybrid Search
# ==================================================

def test_search_hybrid():

    query = "IC semiconductor"

    response = requests.get(
        f"{BASE_URL}/search/hybrid",
        params={
            "q": query
        }
    )

    assert response.status_code == 200

    data = assert_json_response(
        response
    )

    print(
        "Hybrid Search:",
        len(data["data"])
    )

    assert_search_response(
        data,
        "keyword",
        query
    )


# ==================================================
# Test Search Pagination
# ==================================================

def test_search_paginated():

    query = "IC semiconductor"

    response = requests.get(
        f"{BASE_URL}/search/paginated",
        params={
            "q": query,
            "page": 1,
            "page_size": 20
        }
    )

    assert response.status_code == 200

    data = assert_json_response(
        response
    )

    print(
        "Paginated Search:",
        data
    )

    assert_paginated_response(
        data,
        query
    )


# ==================================================
# Test Hybrid Search Pagination
# ==================================================

def test_search_hybrid_paginated():

    query = "IC semiconductor"

    response = requests.get(
        f"{BASE_URL}/search/hybrid/paginated",
        params={
            "q": query,
            "page": 1,
            "page_size": 20
        }
    )

    assert response.status_code == 200

    data = assert_json_response(
        response
    )

    print(
        "Hybrid Paginated Search:",
        data
    )

    assert_paginated_response(
        data,
        query
    )


# ==================================================
# Test Search Index
# ==================================================

def test_search_index_all():

    response = requests.get(
        f"{BASE_URL}/search/all"
    )

    assert response.status_code == 200

    data = assert_json_response(
        response
    )

    print(
        "Search Index:",
        data
    )

    assert data["success"] is True

    assert "count" in data

    assert "data" in data

    assert isinstance(
        data["count"],
        int
    )

    assert isinstance(
        data["data"],
        list
    )
