"""
tests/test_archive_composite_search_api.py

AutoSearch V4

P2.4.2

Composite Archive Search API Tests
"""

from fastapi.testclient import TestClient

from api.main import app

from api.routes import archive_management


client = TestClient(app)


# ============================================================
# Basic Search
# ============================================================

def test_composite_search():

    response = client.get(
        "/management/archive/search"
    )

    assert response.status_code == 200

    data = response.json()

    assert "results" in data

    assert "total" in data

    assert "page" in data

    assert "page_size" in data

    assert "filters" in data


# ============================================================
# Keyword
# ============================================================

def test_composite_search_keyword():

    response = client.get(
        "/management/archive/search",
        params={
            "keyword": "TSMC"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert (
        data["filters"]["keyword"]
        == "TSMC"
    )


# ============================================================
# Multiple Filters
# ============================================================

def test_composite_search_multiple_filters():

    response = client.get(
        "/management/archive/search",
        params={
            "keyword": "TSMC",
            "source": "CNA",
            "category": "Semiconductor",
            "importance_min": 8
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert (
        data["filters"]["keyword"]
        == "TSMC"
    )

    assert (
        data["filters"]["source"]
        == "CNA"
    )

    assert (
        data["filters"]["category"]
        == "Semiconductor"
    )

    assert (
        float(
            data["filters"]["importance_min"]
        )
        == 8
    )


# ============================================================
# Date Filter
# ============================================================

def test_composite_search_date():

    response = client.get(
        "/management/archive/search",
        params={
            "date_from": "2026-08-01",
            "date_to": "2026-08-09"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert (
        data["filters"]["date_from"]
        == "2026-08-01"
    )

    assert (
        data["filters"]["date_to"]
        == "2026-08-09"
    )


# ============================================================
# Year / Month
# ============================================================

def test_composite_search_year_month():

    response = client.get(
        "/management/archive/search",
        params={
            "year": 2026,
            "month": 8
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["filters"]["year"] == 2026

    assert data["filters"]["month"] == 8


# ============================================================
# Pagination
# ============================================================

def test_composite_search_pagination():

    response = client.get(
        "/management/archive/search",
        params={
            "page": 2,
            "page_size": 10
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["page"] == 2

    assert data["page_size"] == 10


# ============================================================
# Empty Filters
# ============================================================

def test_composite_search_empty_filters():

    response = client.get(
        "/management/archive/search"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["filters"] is not None


# ============================================================
# P2.4.1 Regression
# ============================================================

def test_management_status_regression():

    response = client.get(
        "/management/archive/status"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"

    assert (
        data["service"]
        == "archive-management"
    )

    assert (
        data["version"]
        == "V4-P2.4.1"
    )