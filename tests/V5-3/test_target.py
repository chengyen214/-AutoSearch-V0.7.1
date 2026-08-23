"""
tests/V5-3/test_target.py

AutoSearch V5

V5.3 P3.1

Target Model Extension Tests

測試：

1. Default Target
2. URL Target
3. Search Target
4. Google Search Provider
5. Google News Provider
6. Active Status
7. Target Type Detection
8. Search Provider Detection
9. to_dict()
10. Representation
"""


from models.target import Target


# ==================================================
# Default
# ==================================================


def test_default_target():

    target = Target()

    assert target.id is None
    assert target.name == ""
    assert target.target_type == Target.TYPE_URL
    assert target.url == ""
    assert target.keyword == ""
    assert target.search_provider == ""
    assert target.status == "active"


# ==================================================
# URL Target
# ==================================================


def test_url_target():

    target = Target(

        name="TSMC",

        target_type="url",

        url="https://example.com",

    )

    assert target.is_url_target is True
    assert target.is_search_target is False

    assert target.url == (
        "https://example.com"
    )


# ==================================================
# Search Target
# ==================================================


def test_search_target():

    target = Target(

        name="TSMC News",

        target_type="search",

        keyword="TSMC",

    )

    assert target.is_search_target is True
    assert target.is_url_target is False

    assert target.keyword == "TSMC"


# ==================================================
# Google Search
# ==================================================


def test_google_search_provider():

    target = Target(

        name="AI Search",

        target_type="search",

        keyword="AI semiconductor",

        search_provider=(
            Target.PROVIDER_GOOGLE_SEARCH
        ),

    )

    assert target.has_search_provider is True
    assert target.is_google_search is True
    assert target.is_google_news is False


# ==================================================
# Google News
# ==================================================


def test_google_news_provider():

    target = Target(

        name="TSMC News",

        target_type="search",

        keyword="TSMC",

        search_provider=(
            Target.PROVIDER_GOOGLE_NEWS
        ),

    )

    assert target.has_search_provider is True
    assert target.is_google_news is True
    assert target.is_google_search is False


# ==================================================
# Search Provider
# ==================================================


def test_no_search_provider():

    target = Target(

        target_type="search",

        keyword="TSMC",

    )

    assert target.has_search_provider is False
    assert target.is_google_search is False
    assert target.is_google_news is False


# ==================================================
# Active
# ==================================================


def test_active_target():

    target = Target(
        status="active"
    )

    assert target.is_active is True


def test_inactive_target():

    target = Target(
        status="inactive"
    )

    assert target.is_active is False


# ==================================================
# None Normalization
# ==================================================


def test_none_values_are_normalized():

    target = Target(

        name=None,

        target_type=None,

        url=None,

        keyword=None,

        search_provider=None,

        description=None,

        status=None,

    )

    assert target.name == ""
    assert target.target_type == Target.TYPE_URL
    assert target.url == ""
    assert target.keyword == ""
    assert target.search_provider == ""
    assert target.description == ""
    assert target.status == "active"


# ==================================================
# Dictionary
# ==================================================


def test_to_dict():

    target = Target(

        name="TSMC News",

        target_type="search",

        keyword="TSMC",

        search_provider=(
            Target.PROVIDER_GOOGLE_NEWS
        ),

        description="TSMC News Target",

    )

    data = target.to_dict()

    assert data["id"] is None

    assert data["name"] == "TSMC News"

    assert data["target_type"] == "search"

    assert data["url"] == ""

    assert data["keyword"] == "TSMC"

    assert data["search_provider"] == (
        "google_news"
    )

    assert data["description"] == (
        "TSMC News Target"
    )

    assert data["status"] == "active"

    assert "created_time" in data
    assert "updated_time" in data


# ==================================================
# Representation
# ==================================================


def test_repr():

    target = Target(

        name="TSMC News",

        target_type="search",

        keyword="TSMC",

        search_provider="google_news",

    )

    text = repr(target)

    assert "Target(" in text
    assert "TSMC News" in text
    assert "search" in text
    assert "TSMC" in text
    assert "google_news" in text