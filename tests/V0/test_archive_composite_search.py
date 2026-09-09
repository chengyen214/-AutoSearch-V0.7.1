from fastapi.testclient import TestClient

from api.main import app


client = TestClient(app)


def test_composite_search_page():

    response = client.get(
        "/archive/composite-search"
    )

    assert response.status_code == 200

    assert (
        "Composite Archive Search"
        in response.text
    )


def test_composite_search_api():

    response = client.get(
        "/archive/composite-search/api"
    )

    assert response.status_code == 200

    assert response.headers[
        "content-type"
    ].startswith(
        "application/json"
    )


def test_composite_search_keyword():

    response = client.get(
        "/archive/composite-search/api",
        params={
            "keyword": "台積電"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(
        data,
        dict
    )


def test_composite_search_multiple_filters():

    response = client.get(
        "/archive/composite-search/api",
        params={
            "keyword": "台積電",
            "source": "中央通訊社",
            "category": "半導體",
            "year": 2026,
            "month": 8,
            "importance_min": 8,
            "importance_max": 10,
            "page": 1,
            "page_size": 20
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(
        data,
        dict
    )


def test_composite_search_invalid_importance():

    response = client.get(
        "/archive/composite-search/api",
        params={
            "importance_min": 10,
            "importance_max": 5
        }
    )

    assert response.status_code == 400


def test_composite_search_invalid_month():

    response = client.get(
        "/archive/composite-search/api",
        params={
            "month": 13
        }
    )

    assert response.status_code == 422


def test_composite_search_pagination():

    response = client.get(
        "/archive/composite-search/api",
        params={
            "page": 2,
            "page_size": 10
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(
        data,
        dict
    )