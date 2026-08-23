"""
tests/V5-1/test_target_type.py

AutoSearch V5

V5.1 P1.3

Target Type Tests
"""

import pytest

from models.target_type import TargetType


# ==================================
# Type Constants
# ==================================

def test_target_type_constants():

    assert TargetType.WEBSITE == "website"

    assert TargetType.RSS == "rss"

    assert TargetType.API == "api"

    assert TargetType.CUSTOM == "custom"


# ==================================
# All Types
# ==================================

def test_target_type_all():

    assert TargetType.ALL == (
        "website",
        "rss",
        "api",
        "custom"
    )


# ==================================
# Validation
# ==================================

def test_is_valid():

    assert TargetType.is_valid(
        "website"
    )

    assert TargetType.is_valid(
        "rss"
    )

    assert TargetType.is_valid(
        "api"
    )

    assert TargetType.is_valid(
        "custom"
    )


def test_is_valid_case_insensitive():

    assert TargetType.is_valid(
        "WEBSITE"
    )

    assert TargetType.is_valid(
        "RSS"
    )

    assert TargetType.is_valid(
        "Api"
    )


def test_is_valid_with_spaces():

    assert TargetType.is_valid(
        " website "
    )


def test_is_invalid():

    assert not TargetType.is_valid(
        "unknown"
    )

    assert not TargetType.is_valid(
        ""
    )

    assert not TargetType.is_valid(
        None
    )


# ==================================
# Normalize
# ==================================

def test_normalize():

    assert TargetType.normalize(
        " WEBSITE "
    ) == "website"

    assert TargetType.normalize(
        "RSS"
    ) == "rss"

    assert TargetType.normalize(
        " Api "
    ) == "api"

    assert TargetType.normalize(
        "CUSTOM"
    ) == "custom"


def test_normalize_invalid():

    with pytest.raises(
        ValueError
    ):

        TargetType.normalize(
            "unknown"
        )


def test_normalize_none():

    with pytest.raises(
        ValueError
    ):

        TargetType.normalize(
            None
        )


def test_normalize_empty():

    with pytest.raises(
        ValueError
    ):

        TargetType.normalize(
            "   "
        )


# ==================================
# Display Name
# ==================================

def test_display_name():

    assert TargetType.display_name(
        "website"
    ) == "Website"

    assert TargetType.display_name(
        "rss"
    ) == "RSS"

    assert TargetType.display_name(
        "api"
    ) == "API"

    assert TargetType.display_name(
        "custom"
    ) == "Custom"


# ==================================
# Type Check
# ==================================

def test_is_website():

    assert TargetType.is_website(
        "website"
    )

    assert TargetType.is_website(
        " WEBSITE "
    )

    assert not TargetType.is_website(
        "rss"
    )


def test_is_rss():

    assert TargetType.is_rss(
        "rss"
    )

    assert TargetType.is_rss(
        " RSS "
    )

    assert not TargetType.is_rss(
        "website"
    )


def test_is_api():

    assert TargetType.is_api(
        "api"
    )

    assert TargetType.is_api(
        " API "
    )

    assert not TargetType.is_api(
        "rss"
    )


def test_is_custom():

    assert TargetType.is_custom(
        "custom"
    )

    assert TargetType.is_custom(
        " CUSTOM "
    )

    assert not TargetType.is_custom(
        "api"
    )