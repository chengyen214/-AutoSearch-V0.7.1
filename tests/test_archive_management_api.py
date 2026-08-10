"""
tests/test_archive_management_api.py

AutoSearch V4

P2.4.1

Knowledge Archive Management API Tests

測試:

    1. Management Router
    2. Management Status
    3. Management Statistics
    4. Management Articles
    5. Management Article
    6. Management Article Not Found
    7. Management Article Versions
    8. Management Knowledge
    9. Management Knowledge History
    10. Management Knowledge Evolution
    11. Search Index Management
    12. Management Health
"""


from fastapi.testclient import TestClient

from api.main import app


# ============================================================
# Client
# ============================================================

client = TestClient(app)


# ============================================================
# Management Router
# ============================================================

def test_management_router():

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


# ============================================================
# Management Status
# ============================================================

def test_management_status():

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


# ============================================================
# Management Statistics
# ============================================================

def test_management_statistics():

    response = client.get(
        "/management/archive/statistics"
    )

    assert response.status_code == 200

    data = response.json()

    assert data is not None


# ============================================================
# Management Articles
# ============================================================

def test_management_articles():

    response = client.get(
        "/management/archive/articles"
    )

    assert response.status_code == 200

    data = response.json()

    assert data is not None


# ============================================================
# Management Article
# ============================================================

def test_management_article():

    response = client.get(
        "/management/archive/articles/1"
    )

    assert response.status_code in (
        200,
        404
    )


# ============================================================
# Management Article Not Found
# ============================================================

def test_management_article_not_found():

    response = client.get(
        "/management/archive/articles/999999999"
    )

    assert response.status_code == 404

    data = response.json()

    assert (
        data["detail"]
        == "Archive article not found"
    )


# ============================================================
# Management Article Versions
# ============================================================

def test_management_article_versions():

    response = client.get(
        "/management/archive/articles/1/versions"
    )

    assert response.status_code in (
        200,
        404
    )


# ============================================================
# Management Knowledge
# ============================================================

def test_management_knowledge():

    response = client.get(
        "/management/archive/knowledge/1"
    )

    assert response.status_code in (
        200,
        404
    )


# ============================================================
# Management Knowledge History
# ============================================================

def test_management_knowledge_history():

    response = client.get(
        "/management/archive/knowledge/1/history"
    )

    assert response.status_code in (
        200,
        404
    )


# ============================================================
# Management Knowledge Evolution
# ============================================================

def test_management_knowledge_evolution():

    response = client.get(
        "/management/archive/knowledge/1/evolution"
    )

    assert response.status_code in (
        200,
        404
    )


# ============================================================
# Search Index Management
# ============================================================

def test_management_index():

    response = client.get(
        "/management/archive/index"
    )

    assert response.status_code == 200

    data = response.json()

    assert (
        data["status"]
        == "available"
    )

    assert (
        data["service"]
        == "archive-search-index"
    )

    assert (
        data["version"]
        == "V4-P2.4.1"
    )

    assert "operations" in data

    assert (
        "status"
        in data["operations"]
    )

    assert (
        "refresh"
        in data["operations"]
    )

    assert (
        "rebuild"
        in data["operations"]
    )


# ============================================================
# Management Health
# ============================================================

def test_management_health():

    response = client.get(
        "/management/archive/health"
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