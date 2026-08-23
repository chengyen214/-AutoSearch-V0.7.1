"""
tests/V5-3/test_target_service.py

AutoSearch V5

V5.3 P3.4

Target Service Tests
"""

import pytest

from models.target import Target
from services.target_service import TargetService


# ============================================================
# Fake Repository
# ============================================================

class FakeTargetRepository:

    def __init__(self):

        self.targets = []

        self.next_id = 1

    # ========================================================
    # Save
    # ========================================================

    def save(self, target):

        target.id = self.next_id

        self.next_id += 1

        self.targets.append(target)

        return target

    # ========================================================
    # Get By ID
    # ========================================================

    def get_by_id(self, target_id):

        for target in self.targets:

            if target.id == target_id:

                return target

        return None

    # ========================================================
    # Get By URL
    # ========================================================

    def get_by_url(self, url):

        for target in self.targets:

            if (
                target.target_type == "url"
                and target.url == url
            ):

                return target

        return None

    # ========================================================
    # Get By Keyword
    # ========================================================

    def get_by_keyword(self, keyword):

        for target in self.targets:

            if (
                target.target_type == "search"
                and target.keyword == keyword
            ):

                return target

        return None

    # ========================================================
    # Get By Search
    # ========================================================

    def get_by_search(
        self,
        keyword,
        search_provider,
    ):

        for target in self.targets:

            if (
                target.target_type == "search"
                and target.keyword == keyword
                and target.search_provider == search_provider
            ):

                return target

        return None

    # ========================================================
    # Find All
    # ========================================================

    def find_all(self):

        return list(self.targets)

    # ========================================================
    # Find Active
    # ========================================================

    def find_active(self):

        return [
            target
            for target in self.targets
            if target.status == "active"
        ]

    # ========================================================
    # Find By Type
    # ========================================================

    def find_by_type(self, target_type):

        return [
            target
            for target in self.targets
            if target.target_type == target_type
        ]

    # ========================================================
    # Find URL Targets
    # ========================================================

    def find_url_targets(self):

        return self.find_by_type("url")

    # ========================================================
    # Find Search Targets
    # ========================================================

    def find_search_targets(self):

        return self.find_by_type("search")

    # ========================================================
    # Exists
    # ========================================================

    def exists(self, target_id):

        return self.get_by_id(target_id) is not None

    # ========================================================
    # Exists By URL
    # ========================================================

    def exists_by_url(self, url):

        return self.get_by_url(url) is not None

    # ========================================================
    # Exists By Search
    # ========================================================

    def exists_by_search(
        self,
        keyword,
        search_provider,
    ):

        return (
            self.get_by_search(
                keyword,
                search_provider,
            )
            is not None
        )

    # ========================================================
    # Update
    # ========================================================

    def update(self, target):

        existing = self.get_by_id(
            target.id
        )

        if existing is None:

            return False

        index = self.targets.index(
            existing
        )

        self.targets[index] = target

        return True

    # ========================================================
    # Enable
    # ========================================================

    def enable(self, target_id):

        target = self.get_by_id(
            target_id
        )

        if target is None:

            return False

        target.status = "active"

        return True

    # ========================================================
    # Disable
    # ========================================================

    def disable(self, target_id):

        target = self.get_by_id(
            target_id
        )

        if target is None:

            return False

        target.status = "inactive"

        return True

    # ========================================================
    # Delete
    # ========================================================

    def delete_by_id(self, target_id):

        target = self.get_by_id(
            target_id
        )

        if target is None:

            return False

        self.targets.remove(
            target
        )

        return True

    # ========================================================
    # Count
    # ========================================================

    def count(self):

        return len(self.targets)

    # ========================================================
    # Count Active
    # ========================================================

    def count_active(self):

        return len(
            self.find_active()
        )

    # ========================================================
    # Count By Type
    # ========================================================

    def count_by_type(self, target_type):

        return len(
            self.find_by_type(
                target_type
            )
        )


# ============================================================
# Fixtures
# ============================================================

@pytest.fixture
def repository():

    return FakeTargetRepository()


@pytest.fixture
def service(repository):

    return TargetService(
        repository=repository
    )


# ============================================================
# Create Target
# ============================================================

def test_create_url_target(service):

    target = service.create_url_target(
        url="https://example.com/",
        name="Example",
    )

    assert target.id == 1
    assert target.target_type == "url"
    assert target.url == "https://example.com"
    assert target.status == "active"


def test_create_search_target(service):

    target = service.create_search_target(
        keyword="AI",
        search_provider="google_search",
    )

    assert target.id == 1
    assert target.target_type == "search"
    assert target.keyword == "AI"
    assert target.search_provider == "google_search"


# ============================================================
# Google Search
# ============================================================

def test_create_google_search_target(service):

    target = service.create_google_search_target(
        keyword="semiconductor",
    )

    assert target.target_type == "search"
    assert target.keyword == "semiconductor"
    assert target.search_provider == "google_search"


# ============================================================
# Google News
# ============================================================

def test_create_google_news_target(service):

    target = service.create_google_news_target(
        keyword="semiconductor",
    )

    assert target.target_type == "search"
    assert target.keyword == "semiconductor"
    assert target.search_provider == "google_news"


# ============================================================
# Create Generic Target
# ============================================================

def test_create_target(service):

    target = Target(
        name="Example",
        target_type="url",
        url="https://example.com/",
    )

    result = service.create(
        target
    )

    assert result.id == 1
    assert result.url == "https://example.com"


def test_create_invalid_target_type(service):

    target = Target(
        target_type="invalid",
        url="https://example.com",
    )

    with pytest.raises(
        ValueError,
        match="Invalid target_type",
    ):

        service.create(target)


# ============================================================
# URL Validation
# ============================================================

def test_create_invalid_url(service):

    with pytest.raises(
        ValueError
    ):

        service.create_url_target(
            url="not-a-url"
        )


def test_create_empty_url(service):

    with pytest.raises(
        ValueError
    ):

        service.create_url_target(
            url=""
        )


def test_create_https_url(service):

    target = service.create_url_target(
        url="https://example.com/test"
    )

    assert target.url == (
        "https://example.com/test"
    )


# ============================================================
# Search Validation
# ============================================================

def test_create_empty_keyword(service):

    with pytest.raises(
        ValueError,
        match="keyword cannot be empty",
    ):

        service.create_google_search_target(
            keyword=""
        )


def test_create_none_keyword(service):

    with pytest.raises(
        ValueError,
        match="keyword cannot be None",
    ):

        service.create_google_search_target(
            keyword=None
        )


def test_create_invalid_search_provider(service):

    with pytest.raises(
        ValueError,
        match="Invalid search_provider",
    ):

        service.create_search_target(
            keyword="AI",
            search_provider="invalid",
        )


# ============================================================
# Status Validation
# ============================================================

def test_create_active_target(service):

    target = service.create_url_target(
        url="https://example.com",
        status="active",
    )

    assert target.status == "active"


def test_create_inactive_target(service):

    target = service.create_url_target(
        url="https://example.com",
        status="inactive",
    )

    assert target.status == "inactive"


def test_create_invalid_status(service):

    with pytest.raises(
        ValueError,
        match="Invalid status",
    ):

        service.create_url_target(
            url="https://example.com",
            status="invalid",
        )


# ============================================================
# Duplicate URL
# ============================================================

def test_duplicate_url_target(service):

    service.create_url_target(
        url="https://example.com/"
    )

    with pytest.raises(
        ValueError,
        match="Target URL already exists",
    ):

        service.create_url_target(
            url="https://example.com"
        )


# ============================================================
# Duplicate Search Target
# ============================================================

def test_duplicate_search_target(service):

    service.create_google_search_target(
        keyword="AI"
    )

    with pytest.raises(
        ValueError,
        match="Search Target already exists",
    ):

        service.create_google_search_target(
            keyword="AI"
        )


def test_same_keyword_different_provider(
    service
):

    google = service.create_google_search_target(
        keyword="AI"
    )

    news = service.create_google_news_target(
        keyword="AI"
    )

    assert google.id != news.id
    assert google.search_provider == "google_search"
    assert news.search_provider == "google_news"


# ============================================================
# Get
# ============================================================

def test_get_by_id(service):

    target = service.create_url_target(
        url="https://example.com"
    )

    result = service.get_by_id(
        target.id
    )

    assert result is target


def test_get_by_url(service):

    target = service.create_url_target(
        url="https://example.com/"
    )

    result = service.get_by_url(
        "https://example.com"
    )

    assert result is target


def test_get_by_keyword(service):

    target = service.create_google_search_target(
        keyword="AI"
    )

    result = service.get_by_keyword(
        "AI"
    )

    assert result is target


def test_get_by_search(service):

    target = service.create_google_news_target(
        keyword="TSMC"
    )

    result = service.get_by_search(
        "TSMC",
        "google_news",
    )

    assert result is target


# ============================================================
# Find
# ============================================================

def test_find_all(service):

    service.create_url_target(
        "https://example.com"
    )

    service.create_google_search_target(
        "AI"
    )

    assert service.count() == 2


def test_find_active(service):

    service.create_url_target(
        "https://example.com",
        status="active",
    )

    service.create_url_target(
        "https://example.org",
        status="inactive",
    )

    results = service.find_active()

    assert len(results) == 1
    assert results[0].status == "active"


def test_find_by_type(service):

    service.create_url_target(
        "https://example.com"
    )

    service.create_google_search_target(
        "AI"
    )

    results = service.find_by_type(
        "search"
    )

    assert len(results) == 1
    assert results[0].target_type == "search"


def test_find_url_targets(service):

    service.create_url_target(
        "https://example.com"
    )

    service.create_google_search_target(
        "AI"
    )

    results = service.find_url_targets()

    assert len(results) == 1


def test_find_search_targets(service):

    service.create_url_target(
        "https://example.com"
    )

    service.create_google_search_target(
        "AI"
    )

    results = service.find_search_targets()

    assert len(results) == 1


# ============================================================
# Update
# ============================================================

def test_update_url_target(service):

    target = service.create_url_target(
        "https://example.com",
        name="Old",
    )

    target.name = "New"

    result = service.update(
        target
    )

    assert result is True
    assert target.name == "New"


def test_update_search_target(service):

    target = service.create_google_search_target(
        "AI"
    )

    target.keyword = "Artificial Intelligence"

    result = service.update(
        target
    )

    assert result is True
    assert target.keyword == (
        "Artificial Intelligence"
    )


def test_update_without_id(service):

    target = Target(
        target_type="url",
        url="https://example.com",
    )

    with pytest.raises(
        ValueError,
        match="target.id cannot be None",
    ):

        service.update(target)


def test_update_duplicate_url(service):

    first = service.create_url_target(
        "https://example.com"
    )

    second = service.create_url_target(
        "https://example.org"
    )

    second.url = first.url

    with pytest.raises(
        ValueError,
        match="Target URL already exists",
    ):

        service.update(second)


# ============================================================
# Enable / Disable
# ============================================================

def test_enable_target(service):

    target = service.create_url_target(
        "https://example.com",
        status="inactive",
    )

    result = service.enable(
        target.id
    )

    assert result is True
    assert target.status == "active"


def test_disable_target(service):

    target = service.create_url_target(
        "https://example.com"
    )

    result = service.disable(
        target.id
    )

    assert result is True
    assert target.status == "inactive"


# ============================================================
# Exists
# ============================================================

def test_exists(service):

    target = service.create_url_target(
        "https://example.com"
    )

    assert service.exists(
        target.id
    ) is True


def test_exists_by_url(service):

    service.create_url_target(
        "https://example.com"
    )

    assert service.exists_by_url(
        "https://example.com/"
    ) is True


def test_exists_by_search(service):

    service.create_google_news_target(
        "AI"
    )

    assert service.exists_by_search(
        "AI",
        "google_news",
    ) is True


# ============================================================
# Delete
# ============================================================

def test_delete_target(service):

    target = service.create_url_target(
        "https://example.com"
    )

    result = service.delete(
        target.id
    )

    assert result is True
    assert service.exists(
        target.id
    ) is False


# ============================================================
# Count
# ============================================================

def test_count(service):

    assert service.count() == 0

    service.create_url_target(
        "https://example.com"
    )

    service.create_google_search_target(
        "AI"
    )

    assert service.count() == 2


def test_count_active(service):

    service.create_url_target(
        "https://example.com",
        status="active",
    )

    service.create_url_target(
        "https://example.org",
        status="inactive",
    )

    assert service.count_active() == 1


def test_count_by_type(service):

    service.create_url_target(
        "https://example.com"
    )

    service.create_url_target(
        "https://example.org"
    )

    service.create_google_news_target(
        "AI"
    )

    assert service.count_by_type(
        "url"
    ) == 2

    assert service.count_by_type(
        "search"
    ) == 1


# ============================================================
# Invalid Object
# ============================================================

def test_create_invalid_object(service):

    with pytest.raises(
        TypeError,
        match="target must be an instance of Target",
    ):

        service.create(
            "invalid"
        )


def test_update_invalid_object(service):

    with pytest.raises(
        TypeError,
        match="target must be an instance of Target",
    ):

        service.update(
            "invalid"
        )