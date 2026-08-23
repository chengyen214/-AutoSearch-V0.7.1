"""
tests/V5-3/test_target_validator.py

AutoSearch V5

V5.3 P3.2

Target Validator Tests
"""


from models.target import Target
from utils.target_validator import TargetValidator


# ==================================================
# Target Type
# ==================================================


def test_validate_url_target_type():

    assert TargetValidator.validate_target_type(
        Target.TYPE_URL
    ) is True


def test_validate_search_target_type():

    assert TargetValidator.validate_target_type(
        Target.TYPE_SEARCH
    ) is True


def test_invalid_target_type():

    try:
        TargetValidator.validate_target_type(
            "invalid"
        )
        assert False
    except ValueError:
        assert True


# ==================================================
# URL Validation
# ==================================================


def test_validate_http_url():

    assert TargetValidator.validate_url(
        "http://example.com"
    ) is True


def test_validate_https_url():

    assert TargetValidator.validate_url(
        "https://example.com/news"
    ) is True


def test_validate_url_with_query():

    assert TargetValidator.validate_url(
        "https://example.com/search?q=AI"
    ) is True


def test_empty_url():

    try:
        TargetValidator.validate_url("")
        assert False
    except ValueError:
        assert True


def test_none_url():

    try:
        TargetValidator.validate_url(None)
        assert False
    except ValueError:
        assert True


def test_invalid_url_scheme():

    try:
        TargetValidator.validate_url(
            "ftp://example.com"
        )
        assert False
    except ValueError:
        assert True


def test_url_without_host():

    try:
        TargetValidator.validate_url(
            "https://"
        )
        assert False
    except ValueError:
        assert True


# ==================================================
# URL Normalization
# ==================================================


def test_normalize_url():

    result = TargetValidator.normalize_url(
        "  https://example.com/news  "
    )

    assert result == (
        "https://example.com/news"
    )


# ==================================================
# Keyword Validation
# ==================================================


def test_validate_keyword():

    assert TargetValidator.validate_keyword(
        "TSMC"
    ) is True


def test_keyword_with_spaces():

    assert TargetValidator.validate_keyword(
        "  TSMC semiconductor  "
    ) is True


def test_empty_keyword():

    try:
        TargetValidator.validate_keyword("")
        assert False
    except ValueError:
        assert True


def test_none_keyword():

    try:
        TargetValidator.validate_keyword(None)
        assert False
    except ValueError:
        assert True


# ==================================================
# Search Provider
# ==================================================


def test_google_search_provider():

    assert TargetValidator.validate_search_provider(
        Target.PROVIDER_GOOGLE_SEARCH
    ) is True


def test_google_news_provider():

    assert TargetValidator.validate_search_provider(
        Target.PROVIDER_GOOGLE_NEWS
    ) is True


def test_invalid_search_provider():

    try:
        TargetValidator.validate_search_provider(
            "invalid_provider"
        )
        assert False
    except ValueError:
        assert True


# ==================================================
# Status
# ==================================================


def test_active_status():

    assert TargetValidator.validate_status(
        "active"
    ) is True


def test_inactive_status():

    assert TargetValidator.validate_status(
        "inactive"
    ) is True


def test_invalid_status():

    try:
        TargetValidator.validate_status(
            "invalid"
        )
        assert False
    except ValueError:
        assert True


# ==================================================
# Complete URL Target
# ==================================================


def test_validate_complete_url_target():

    target = Target(

        name="TSMC",

        target_type=Target.TYPE_URL,

        url="https://example.com/news",

        status="active",

    )

    assert TargetValidator.validate(
        target
    ) is True


# ==================================================
# Complete Search Target
# ==================================================


def test_validate_complete_google_search_target():

    target = Target(

        name="AI Search",

        target_type=Target.TYPE_SEARCH,

        keyword="AI semiconductor",

        search_provider=(
            Target.PROVIDER_GOOGLE_SEARCH
        ),

        status="active",

    )

    assert TargetValidator.validate(
        target
    ) is True


def test_validate_complete_google_news_target():

    target = Target(

        name="TSMC News",

        target_type=Target.TYPE_SEARCH,

        keyword="TSMC",

        search_provider=(
            Target.PROVIDER_GOOGLE_NEWS
        ),

        status="active",

    )

    assert TargetValidator.validate(
        target
    ) is True


# ==================================================
# Invalid Complete Target
# ==================================================


def test_search_target_without_keyword():

    target = Target(

        target_type=Target.TYPE_SEARCH,

        keyword="",

        search_provider=(
            Target.PROVIDER_GOOGLE_NEWS
        ),

    )

    try:
        TargetValidator.validate(
            target
        )
        assert False
    except ValueError:
        assert True


def test_search_target_without_provider():

    target = Target(

        target_type=Target.TYPE_SEARCH,

        keyword="TSMC",

        search_provider="",

    )

    try:
        TargetValidator.validate(
            target
        )
        assert False
    except ValueError:
        assert True


def test_url_target_without_url():

    target = Target(

        target_type=Target.TYPE_URL,

        url="",

    )

    try:
        TargetValidator.validate(
            target
        )
        assert False
    except ValueError:
        assert True


# ==================================================
# Normalize Target
# ==================================================


def test_normalize_url_target():

    target = Target(

        name="  TSMC  ",

        target_type=Target.TYPE_URL,

        url="  https://example.com/news  ",

        description="  News Target  ",

        status="active",

    )

    result = TargetValidator.normalize(
        target
    )

    assert result is target

    assert result.name == "TSMC"

    assert result.url == (
        "https://example.com/news"
    )

    assert result.description == (
        "News Target"
    )


def test_normalize_search_target():

    target = Target(

        name="  TSMC News  ",

        target_type=Target.TYPE_SEARCH,

        keyword="  TSMC semiconductor  ",

        search_provider="  google_news  ",

        status="active",

    )

    result = TargetValidator.normalize(
        target
    )

    assert result is target

    assert result.name == "TSMC News"

    assert result.keyword == (
        "TSMC semiconductor"
    )

    assert result.search_provider == (
        "google_news"
    )


# ==================================================
# Invalid Target Type
# ==================================================


def test_validate_invalid_target_object():

    try:
        TargetValidator.validate(
            None
        )
        assert False
    except TypeError:
        assert True
