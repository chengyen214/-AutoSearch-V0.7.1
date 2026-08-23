"""
tests/V5-1/test_target_status.py

AutoSearch V5

V5.1 P1.4

Target Status Tests
"""


import pytest

from models.target_status import TargetStatus


# ==================================
# Status Constants
# ==================================

def test_target_status_constants():

    assert TargetStatus.ACTIVE == "active"

    assert TargetStatus.INACTIVE == "inactive"


# ==================================
# All Status
# ==================================

def test_target_status_all():

    assert TargetStatus.ALL == (
        "active",
        "inactive"
    )


# ==================================
# Validation
# ==================================

def test_is_valid():

    assert TargetStatus.is_valid(
        "active"
    )

    assert TargetStatus.is_valid(
        "inactive"
    )


def test_is_valid_case_insensitive():

    assert TargetStatus.is_valid(
        "ACTIVE"
    )

    assert TargetStatus.is_valid(
        "INACTIVE"
    )


def test_is_valid_with_spaces():

    assert TargetStatus.is_valid(
        " active "
    )

    assert TargetStatus.is_valid(
        " inactive "
    )


def test_is_invalid():

    assert not TargetStatus.is_valid(
        "unknown"
    )

    assert not TargetStatus.is_valid(
        ""
    )

    assert not TargetStatus.is_valid(
        None
    )


# ==================================
# Normalize
# ==================================

def test_normalize():

    assert TargetStatus.normalize(
        " ACTIVE "
    ) == "active"

    assert TargetStatus.normalize(
        "INACTIVE"
    ) == "inactive"


def test_normalize_invalid():

    with pytest.raises(
        ValueError
    ):

        TargetStatus.normalize(
            "unknown"
        )


def test_normalize_none():

    with pytest.raises(
        ValueError
    ):

        TargetStatus.normalize(
            None
        )


def test_normalize_empty():

    with pytest.raises(
        ValueError
    ):

        TargetStatus.normalize(
            "   "
        )


# ==================================
# Display Name
# ==================================

def test_display_name():

    assert TargetStatus.display_name(
        "active"
    ) == "Active"

    assert TargetStatus.display_name(
        "inactive"
    ) == "Inactive"


def test_display_name_normalization():

    assert TargetStatus.display_name(
        " ACTIVE "
    ) == "Active"

    assert TargetStatus.display_name(
        "INACTIVE"
    ) == "Inactive"


# ==================================
# Is Active
# ==================================

def test_is_active():

    assert TargetStatus.is_active(
        "active"
    )

    assert TargetStatus.is_active(
        " ACTIVE "
    )

    assert not TargetStatus.is_active(
        "inactive"
    )


# ==================================
# Is Inactive
# ==================================

def test_is_inactive():

    assert TargetStatus.is_inactive(
        "inactive"
    )

    assert TargetStatus.is_inactive(
        " INACTIVE "
    )

    assert not TargetStatus.is_inactive(
        "active"
    )