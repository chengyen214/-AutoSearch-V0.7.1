"""
api/routes/system.py

AutoSearch V4

P3.10

System / Health API Router


功能:

1. Basic Health
2. Database Health
3. System Status
4. Version Information


API:

GET /system/health
GET /system/database
GET /system/status
GET /system/version


Architecture:

Client
    |
    v
System API
    |
    +---- Health Check
    |
    +---- Database Check
    |
    +---- System Status
    |
    +---- Version
"""


from datetime import datetime

from fastapi import APIRouter

from database.connection import get_connection


# ==================================================
# Router
# ==================================================

router = APIRouter(

    prefix="/system",

    tags=[
        "System / Health"
    ]

)


# ==================================================
# System Information
# ==================================================

APP_NAME = "AutoSearch V4"

APP_VERSION = "4.0.0"

API_VERSION = "P3.10"


# ==================================================
# Database Health Helper
# ==================================================

def _check_database():

    conn = None

    cursor = None

    try:

        conn = get_connection()

        cursor = conn.cursor()

        cursor.execute(
            "SELECT 1"
        )

        result = cursor.fetchone()

        if result:

            return {

                "status": "healthy",

                "connected": True

            }

        return {

            "status": "unhealthy",

            "connected": False

        }

    except Exception as exc:

        return {

            "status": "unhealthy",

            "connected": False,

            "error": str(exc)

        }

    finally:

        if cursor is not None:

            cursor.close()

        if conn is not None:

            conn.close()


# ==================================================
# P3.10.1
# Basic Health
#
# GET /system/health
# ==================================================

@router.get(
    "/health"
)
def health_check():

    database = _check_database()

    database_healthy = (

        database["status"]
        == "healthy"

    )

    status = (

        "healthy"

        if database_healthy

        else "unhealthy"

    )

    return {

        "success": database_healthy,

        "status": status,

        "service": APP_NAME,

        "database": database["status"],

        "timestamp": datetime.now()

    }


# ==================================================
# P3.10.2
# Database Health
#
# GET /system/database
# ==================================================

@router.get(
    "/database"
)
def database_health():

    result = _check_database()

    return {

        "success": (

            result["status"]
            == "healthy"

        ),

        "database": result

    }


# ==================================================
# P3.10.3
# System Status
#
# GET /system/status
# ==================================================

@router.get(
    "/status"
)
def system_status():

    database = _check_database()

    return {

        "success": True,

        "service": APP_NAME,

        "status": (

            "healthy"

            if database["status"]
            == "healthy"

            else "degraded"

        ),

        "api_version": API_VERSION,

        "database": database["status"],

        "timestamp": datetime.now()

    }


# ==================================================
# P3.10.4
# Version Information
#
# GET /system/version
# ==================================================

@router.get(
    "/version"
)
def system_version():

    return {

        "success": True,

        "service": APP_NAME,

        "version": APP_VERSION,

        "api_version": API_VERSION

    }