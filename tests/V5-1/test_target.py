"""
tests/V5-1/test_target.py

AutoSearch V5

V5.1 P1

Target Model Tests

測試範圍：

    - Target 建立
    - 預設值
    - 自訂值
    - ID
    - Status
    - is_active
    - to_dict()
    - created_time
    - updated_time
    - __repr__()

注意：

    P1 僅測試 Target Model。

    不測試：

        - Database
        - API
        - Crawler
        - Parser
        - Archive
        - AI Pipeline
"""


from datetime import datetime


from models.target import Target


# ==================================================
# Target Creation
# ==================================================


def test_target_creation():

    target = Target()

    assert target is not None

    assert isinstance(
        target,
        Target
    )


# ==================================================
# Default Values
# ==================================================


def test_target_default_values():

    target = Target()

    assert target.id is None

    assert target.name == ""

    assert target.target_type == "website"

    assert target.url == ""

    assert target.description == ""

    assert target.status == "active"


# ==================================================
# Time Fields
# ==================================================


def test_target_time_fields():

    target = Target()

    assert isinstance(
        target.created_time,
        datetime
    )

    assert isinstance(
        target.updated_time,
        datetime
    )


# ==================================================
# Active Status
# ==================================================


def test_target_is_active():

    target = Target(
        status="active"
    )

    assert target.is_active is True


def test_target_is_not_active():

    target = Target(
        status="disabled"
    )

    assert target.is_active is False


# ==================================================
# Custom Values
# ==================================================


def test_target_custom_values():

    target = Target(

        name="TSMC News",

        target_type="website",

        url="https://www.tsmc.com/",

        description="TSMC official website",

        status="active"
    )

    assert target.name == "TSMC News"

    assert target.target_type == "website"

    assert target.url == "https://www.tsmc.com/"

    assert target.description == (
        "TSMC official website"
    )

    assert target.status == "active"


# ==================================================
# Target Type
# ==================================================


def test_target_type():

    target = Target(
        target_type="paper"
    )

    assert target.target_type == "paper"


# ==================================================
# to_dict
# ==================================================


def test_target_to_dict():

    target = Target(

        name="Research Paper",

        target_type="paper",

        url="https://example.com/paper",

        description="Test paper",

        status="active"
    )

    result = target.to_dict()

    assert isinstance(
        result,
        dict
    )

    assert result["id"] is None

    assert result["name"] == (
        "Research Paper"
    )

    assert result["target_type"] == (
        "paper"
    )

    assert result["url"] == (
        "https://example.com/paper"
    )

    assert result["description"] == (
        "Test paper"
    )

    assert result["status"] == (
        "active"
    )

    assert isinstance(
        result["created_time"],
        datetime
    )

    assert isinstance(
        result["updated_time"],
        datetime
    )


# ==================================================
# ID
# ==================================================


def test_target_id():

    target = Target(
        name="Test Target"
    )

    assert target.id is None

    target.id = 123

    assert target.id == 123


# ==================================================
# Status
# ==================================================


def test_target_status():

    target = Target(
        status="disabled"
    )

    assert target.status == "disabled"

    assert target.is_active is False


# ==================================================
# Representation
# ==================================================


def test_target_repr():

    target = Target(

        name="Test Target",

        target_type="website",

        url="https://example.com",

        status="active"
    )

    result = repr(
        target
    )

    assert "Target(" in result

    assert "name=Test Target" in result

    assert "type=website" in result

    assert "url=https://example.com" in result

    assert "status=active" in result