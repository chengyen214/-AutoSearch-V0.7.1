"""
tests/test_system_api.py

AutoSearch V4

P3.10

System / Health API Tests


測試:

1. Basic Health
2. Database Health
3. System Status
4. Version Information
5. OpenAPI Routes
6. HTTP Methods
7. Database Failure
"""


import pytest

from fastapi import FastAPI

from fastapi.testclient import TestClient


# ==================================================
# Import Router
# ==================================================

from api.routes.system import (
    router,
)


# ==================================================
# Import Module
# ==================================================

import api.routes.system as system_module


# ==================================================
# Test App
# ==================================================

app = FastAPI()

app.include_router(
    router
)


client = TestClient(
    app
)


# ==================================================
# Fake Database Connection
# ==================================================

class FakeCursor:

    def execute(
        self,
        sql
    ):

        self.sql = sql


    def fetchone(
        self
    ):

        return (1,)


    def close(
        self
    ):

        pass


class FakeConnection:

    def cursor(
        self
    ):

        return FakeCursor()


    def close(
        self
    ):

        pass


# ==================================================
# Mock Database
# ==================================================

@pytest.fixture(
    autouse=True
)
def mock_database(
    monkeypatch
):

    monkeypatch.setattr(

        system_module,

        "get_connection",

        lambda:
            FakeConnection()

    )


# ==================================================
# P3.10.1
# Basic Health
# ==================================================

def test_health():

    response = client.get(
        "/system/health"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    assert data["status"] == "healthy"

    assert data["service"] == (
        "AutoSearch V4"
    )

    assert data["database"] == "healthy"

    assert "timestamp" in data


# ==================================================
# P3.10.2
# Database Health
# ==================================================

def test_database_health():

    response = client.get(
        "/system/database"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    assert data["database"]["status"] == (
        "healthy"
    )

    assert data["database"]["connected"] is True


# ==================================================
# P3.10.3
# System Status
# ==================================================

def test_system_status():

    response = client.get(
        "/system/status"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    assert data["service"] == (
        "AutoSearch V4"
    )

    assert data["status"] == "healthy"

    assert data["api_version"] == (
        "P3.10"
    )

    assert data["database"] == "healthy"

    assert "timestamp" in data


# ==================================================
# P3.10.4
# Version
# ==================================================

def test_system_version():

    response = client.get(
        "/system/version"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    assert data["service"] == (
        "AutoSearch V4"
    )

    assert data["version"] == "4.0.0"

    assert data["api_version"] == (
        "P3.10"
    )


# ==================================================
# Database Failure
# ==================================================

def test_database_failure(
    monkeypatch
):

    def broken_connection():

        raise Exception(
            "Database connection failed"
        )


    monkeypatch.setattr(

        system_module,

        "get_connection",

        broken_connection

    )


    response = client.get(
        "/system/database"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is False

    assert data["database"]["status"] == (
        "unhealthy"
    )

    assert data["database"]["connected"] is False

    assert "error" in data["database"]


# ==================================================
# Health Failure
# ==================================================

def test_health_failure(
    monkeypatch
):

    def broken_connection():

        raise Exception(
            "Database unavailable"
        )


    monkeypatch.setattr(

        system_module,

        "get_connection",

        broken_connection

    )


    response = client.get(
        "/system/health"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is False

    assert data["status"] == (
        "unhealthy"
    )

    assert data["database"] == (
        "unhealthy"
    )


# ==================================================
# OpenAPI Paths
# ==================================================

def test_system_openapi_paths():

    response = client.get(
        "/openapi.json"
    )

    assert response.status_code == 200

    paths = response.json()["paths"]

    assert (
        "/system/health"
        in paths
    )

    assert (
        "/system/database"
        in paths
    )

    assert (
        "/system/status"
        in paths
    )

    assert (
        "/system/version"
        in paths
    )


# ==================================================
# HTTP Methods
# ==================================================

def test_system_http_methods():

    response = client.get(
        "/openapi.json"
    )

    assert response.status_code == 200

    paths = response.json()["paths"]

    assert "get" in paths[
        "/system/health"
    ]

    assert "get" in paths[
        "/system/database"
    ]

    assert "get" in paths[
        "/system/status"
    ]

    assert "get" in paths[
        "/system/version"
    ]


# ==================================================
# Version Structure
# ==================================================

def test_version_structure():

    response = client.get(
        "/system/version"
    )

    assert response.status_code == 200

    data = response.json()

    assert set(
        data.keys()
    ) == {

        "success",

        "service",

        "version",

        "api_version"

    }


# ==================================================
# Health Structure
# ==================================================

def test_health_structure():

    response = client.get(
        "/system/health"
    )

    assert response.status_code == 200

    data = response.json()

    assert "success" in data

    assert "status" in data

    assert "service" in data

    assert "database" in data

    assert "timestamp" in data