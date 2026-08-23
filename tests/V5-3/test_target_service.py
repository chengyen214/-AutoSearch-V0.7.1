"""
tests/V5-3/test_target_service.py

AutoSearch V5

V5.3 P3.4

Target Service Tests

測試：

    - TargetService initialization
    - Create Target
    - Create URL Target
    - Create Search Target
    - Google Search Target
    - Google News Target
    - Get Target
    - Find Target
    - Update Target
    - Enable / Disable
    - Delete
    - Exists
    - Duplicate Detection
    - Count
"""


from datetime import datetime

import pytest

from models.target import Target

from services.target_service import (
    TargetService,
)


# ==================================================
# Fake Repository
# ==================================================


class FakeRepository:
    """
    不連接 MySQL 的測試 Repository。

    模擬目前 TargetRepository
    已提供的 Service API。
    """

    def __init__(self):

        self.targets = []

        self.next_id = 1

    # ==============================================
    # Create
    # ==============================================

    def save(
        self,
        target,
    ):

        target.id = self.next_id

        self.next_id += 1

        self.targets.append(
            target
        )

        return target

    # ==============================================
    # Query
    # ==============================================

    def get_by_id(
        self,
        target_id,
    ):

        for target in self.targets:

            if target.id == target_id:

                return target

        return None

    def get_by_url(
        self,
        url,
    ):

        if not url:

            return None

        url = str(
            url
        ).strip()

        for target in self.targets:

            if (
                target.target_type == "url"
                and
                target.url == url
            ):

                return target

        return None

    def get_by_keyword(
        self,
        keyword,
    ):

        if not keyword:

            return None

        keyword = str(
            keyword
        ).strip()

        for target in self.targets:

            if (
                target.target_type == "search"
                and
                target.keyword == keyword
            ):

                return target

        return None

    def get_by_search(
        self,
        keyword,
        search_provider,
    ):

        if not keyword:
            return None

        if not search_provider:
            return None

        keyword = str(
            keyword
        ).strip()

        search_provider = str(
            search_provider
        ).strip()

        for target in self.targets:

            if (
                target.target_type == "search"
                and
                target.keyword == keyword
                and
                target.search_provider
                == search_provider
            ):

                return target

        return None

    # ==============================================
    # Find
    # ==============================================

    def find_all(
        self,
    ):

        return list(
            self.targets
        )

    def find_active(
        self,
    ):

        return [
            target
            for target in self.targets
            if target.status == "active"
        ]

    def find_by_type(
        self,
        target_type,
    ):

        return [
            target
            for target in self.targets
            if target.target_type
            == target_type
        ]

    def find_url_targets(
        self,
    ):

        return self.find_by_type(
            "url"
        )

    def find_search_targets(
        self,
    ):

        return self.find_by_type(
            "search"
        )

    # ==============================================
    # Exists
    # ==============================================

    def exists(
        self,
        target_id,
    ):

        return (
            self.get_by_id(
                target_id
            )
            is not None
        )

    def exists_by_url(
        self,
        url,
    ):

        return (
            self.get_by_url(
                url
            )
            is not None
        )

    def exists_by_search(
        self,
        keyword,
        search_provider,
    ):

        return (
            self.get_by_search(
                keyword,
                search_provider
            )
            is not None
        )

    # ==============================================
    # Update
    # ==============================================

    def update(
        self,
        target,
    ):

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

    # ==============================================
    # Status
    # ==============================================

    def enable(
        self,
        target_id,
    ):

        target = self.get_by_id(
            target_id
        )

        if target is None:

            return False

        target.status = "active"

        return True

    def disable(
        self,
        target_id,
    ):

        target = self.get_by_id(
            target_id
        )

        if target is None:

            return False

        target.status = "inactive"

        return True

    # ==============================================
    # Delete
    # ==============================================

    def delete_by_id(
        self,
        target_id,
    ):

        target = self.get_by_id(
            target_id
        )

        if target is None:

            return False

        self.targets.remove(
            target
        )

        return True

    # ==============================================
    # Count
    # ==============================================

    def count(
        self,
    ):

        return len(
            self.targets
        )

    def count_active(
        self,
    ):

        return len(
            self.find_active()
        )

    def count_by_type(
        self,
        target_type,
    ):

        return len(
            self.find_by_type(
                target_type
            )
        )


# ==================================================
# Fake Validator
# ==================================================


class FakeValidator:
    """
    測試用 Validator。

    模擬目前 TargetValidator：

        normalize()
        validate()
    """

    def __init__(self):

        self.normalize_called = False

        self.validate_called = False

    def normalize(
        self,
        target,
    ):

        self.normalize_called = True

        # ------------------------------------------
        # URL Target
        # ------------------------------------------

        if (
            target.target_type
            == "url"
        ):

            if target.url:

                target.url = (
                    str(
                        target.url
                    )
                    .strip()
                )

        # ------------------------------------------
        # Search Target
        # ------------------------------------------

        if (
            target.target_type
            == "search"
        ):

            if target.keyword:

                target.keyword = (
                    str(
                        target.keyword
                    )
                    .strip()
                )

            if target.search_provider:

                target.search_provider = (
                    str(
                        target.search_provider
                    )
                    .strip()
                    .lower()
                )

        return target

    def validate(
        self,
        target,
    ):

        self.validate_called = True

        if target.target_type == "url":

            if not target.url:

                raise ValueError(
                    "URL cannot be empty"
                )

        elif target.target_type == "search":

            if not target.keyword:

                raise ValueError(
                    "keyword cannot be empty"
                )

            if not target.search_provider:

                raise ValueError(
                    "search_provider cannot be empty"
                )

        else:

            raise ValueError(
                "invalid target_type"
            )

        return True


# ==================================================
# Fixtures
# ==================================================


@pytest.fixture
def repository():

    return FakeRepository()


@pytest.fixture
def validator():

    return FakeValidator()


@pytest.fixture
def service(
    repository,
    validator,
):

    return TargetService(
        repository=repository,
        validator=validator,
    )


# ==================================================
# Constructor
# ==================================================


def test_service_instance():

    service = TargetService(
        repository=FakeRepository(),
        validator=FakeValidator(),
    )

    assert isinstance(
        service,
        TargetService,
    )


def test_service_uses_injected_repository(
    repository,
    validator,
):

    service = TargetService(
        repository=repository,
        validator=validator,
    )

    assert service.repository is repository


def test_service_uses_injected_validator(
    repository,
    validator,
):

    service = TargetService(
        repository=repository,
        validator=validator,
    )

    assert service.validator is validator


# ==================================================
# Create
# ==================================================


def test_create_url_target(
    service,
):

    target = Target(
        target_type="url",
        url="https://example.com",
    )

    result = service.create(
        target
    )

    assert result.id == 1

    assert result.target_type == "url"

    assert result.url == (
        "https://example.com"
    )


def test_create_search_target(
    service,
):

    target = Target(
        target_type="search",
        keyword="TSMC",
        search_provider="google_search",
    )

    result = service.create(
        target
    )

    assert result.id == 1

    assert result.target_type == "search"

    assert result.keyword == "TSMC"

    assert (
        result.search_provider
        == "google_search"
    )


def test_create_calls_normalize(
    service,
    validator,
):

    target = Target(
        target_type="url",
        url="  https://example.com  ",
    )

    result = service.create(
        target
    )

    assert validator.normalize_called

    assert result.url == (
        "https://example.com"
    )


def test_create_calls_validate(
    service,
    validator,
):

    target = Target(
        target_type="url",
        url="https://example.com",
    )

    service.create(
        target
    )

    assert validator.validate_called


def test_create_invalid_object(
    service,
):

    with pytest.raises(
        TypeError
    ):

        service.create(
            "invalid"
        )


# ==================================================
# URL Target
# ==================================================


def test_create_url_target_helper(
    service,
):

    result = service.create_url_target(
        url="https://example.com",
        name="Example",
        description="Example website",
    )

    assert result.target_type == "url"

    assert result.url == (
        "https://example.com"
    )

    assert result.name == "Example"

    assert (
        result.description
        == "Example website"
    )

    assert result.status == "active"


def test_create_url_target_inactive(
    service,
):

    result = service.create_url_target(
        url="https://example.com",
        status="inactive",
    )

    assert result.status == "inactive"


# ==================================================
# Search Target
# ==================================================


def test_create_search_target_helper(
    service,
):

    result = service.create_search_target(
        keyword="semiconductor",
        search_provider="google_search",
    )

    assert result.target_type == "search"

    assert result.keyword == (
        "semiconductor"
    )

    assert (
        result.search_provider
        == "google_search"
    )


def test_create_google_search_target(
    service,
):

    result = (
        service.create_google_search_target(
            keyword="AI",
        )
    )

    assert result.target_type == "search"

    assert result.keyword == "AI"

    assert (
        result.search_provider
        == "google_search"
    )


def test_create_google_news_target(
    service,
):

    result = (
        service.create_google_news_target(
            keyword="TSMC",
        )
    )

    assert result.target_type == "search"

    assert result.keyword == "TSMC"

    assert (
        result.search_provider
        == "google_news"
    )


def test_create_search_target_custom_fields(
    service,
):

    result = service.create_search_target(
        keyword="AI",
        search_provider="google_news",
        name="AI News",
        description="AI news target",
        status="inactive",
    )

    assert result.name == "AI News"

    assert (
        result.description
        == "AI news target"
    )

    assert result.status == "inactive"


# ==================================================
# Duplicate Detection
# ==================================================


def test_duplicate_url_target(
    service,
):

    service.create_url_target(
        url="https://example.com",
    )

    with pytest.raises(
        ValueError,
        match="Target URL already exists",
    ):

        service.create_url_target(
            url="https://example.com",
        )


def test_duplicate_search_target(
    service,
):

    service.create_google_search_target(
        keyword="AI",
    )

    with pytest.raises(
        ValueError,
        match="Search Target already exists",
    ):

        service.create_google_search_target(
            keyword="AI",
        )


def test_same_keyword_different_provider_allowed(
    service,
):

    google = (
        service.create_google_search_target(
            keyword="AI",
        )
    )

    news = (
        service.create_google_news_target(
            keyword="AI",
        )
    )

    assert google.id != news.id

    assert (
        google.search_provider
        == "google_search"
    )

    assert (
        news.search_provider
        == "google_news"
    )


# ==================================================
# Get
# ==================================================


def test_get_by_id(
    service,
):

    created = service.create_url_target(
        url="https://example.com",
    )

    result = service.get_by_id(
        created.id
    )

    assert result is created


def test_get_by_url(
    service,
):

    created = service.create_url_target(
        url="https://example.com",
    )

    result = service.get_by_url(
        "https://example.com"
    )

    assert result is created


def test_get_by_keyword(
    service,
):

    created = (
        service.create_google_search_target(
            keyword="AI",
        )
    )

    result = service.get_by_keyword(
        "AI"
    )

    assert result is created


def test_get_by_search(
    service,
):

    created = (
        service.create_google_news_target(
            keyword="TSMC",
        )
    )

    result = service.get_by_search(
        "TSMC",
        "google_news",
    )

    assert result is created


# ==================================================
# Find
# ==================================================


def test_find_all(
    service,
):

    service.create_url_target(
        "https://example.com",
    )

    service.create_google_search_target(
        "AI",
    )

    results = service.find_all()

    assert len(results) == 2


def test_find_active(
    service,
):

    service.create_url_target(
        "https://example.com",
    )

    service.create_url_target(
        "https://inactive.example.com",
        status="inactive",
    )

    results = service.find_active()

    assert len(results) == 1

    assert results[0].status == "active"


def test_find_by_type(
    service,
):

    service.create_url_target(
        "https://example.com",
    )

    service.create_google_search_target(
        "AI",
    )

    results = service.find_by_type(
        "search"
    )

    assert len(results) == 1

    assert (
        results[0].target_type
        == "search"
    )


def test_find_url_targets(
    service,
):

    service.create_url_target(
        "https://example.com",
    )

    service.create_google_search_target(
        "AI",
    )

    results = service.find_url_targets()

    assert len(results) == 1

    assert (
        results[0].target_type
        == "url"
    )


def test_find_search_targets(
    service,
):

    service.create_url_target(
        "https://example.com",
    )

    service.create_google_news_target(
        "TSMC",
    )

    results = service.find_search_targets()

    assert len(results) == 1

    assert (
        results[0].target_type
        == "search"
    )


# ==================================================
# Update
# ==================================================


def test_update_target(
    service,
):

    target = service.create_url_target(
        "https://example.com",
    )

    target.name = "Updated"

    result = service.update(
        target
    )

    assert result is True

    stored = service.get_by_id(
        target.id
    )

    assert stored.name == "Updated"


def test_update_search_target(
    service,
):

    target = (
        service.create_google_search_target(
            keyword="AI",
        )
    )

    target.name = "AI Search"

    result = service.update(
        target
    )

    assert result is True

    assert (
        service.get_by_id(
            target.id
        ).name
        == "AI Search"
    )


def test_update_invalid_object(
    service,
):

    with pytest.raises(
        TypeError
    ):

        service.update(
            "invalid"
        )


def test_update_without_id(
    service,
):

    target = Target(
        target_type="url",
        url="https://example.com",
    )

    with pytest.raises(
        ValueError
    ):

        service.update(
            target
        )


# ==================================================
# Enable / Disable
# ==================================================


def test_enable_target(
    service,
):

    target = service.create_url_target(
        "https://example.com",
        status="inactive",
    )

    result = service.enable(
        target.id
    )

    assert result is True

    assert target.status == "active"


def test_disable_target(
    service,
):

    target = service.create_url_target(
        "https://example.com",
    )

    result = service.disable(
        target.id
    )

    assert result is True

    assert target.status == "inactive"


# ==================================================
# Delete
# ==================================================


def test_delete_target(
    service,
):

    target = service.create_url_target(
        "https://example.com",
    )

    result = service.delete(
        target.id
    )

    assert result is True

    assert service.get_by_id(
        target.id
    ) is None


def test_delete_nonexistent_target(
    service,
):

    result = service.delete(
        999
    )

    assert result is False


# ==================================================
# Exists
# ==================================================


def test_exists(
    service,
):

    target = service.create_url_target(
        "https://example.com",
    )

    assert service.exists(
        target.id
    )


def test_exists_by_url(
    service,
):

    service.create_url_target(
        "https://example.com",
    )

    assert service.exists_by_url(
        "https://example.com"
    )


def test_exists_by_search(
    service,
):

    service.create_google_news_target(
        keyword="TSMC",
    )

    assert service.exists_by_search(
        "TSMC",
        "google_news",
    )


# ==================================================
# Count
# ==================================================


def test_count(
    service,
):

    assert service.count() == 0

    service.create_url_target(
        "https://example.com",
    )

    service.create_google_search_target(
        "AI",
    )

    assert service.count() == 2


def test_count_active(
    service,
):

    service.create_url_target(
        "https://example.com",
    )

    service.create_url_target(
        "https://inactive.example.com",
        status="inactive",
    )

    assert service.count_active() == 1


def test_count_by_type(
    service,
):

    service.create_url_target(
        "https://example.com",
    )

    service.create_google_search_target(
        "AI",
    )

    service.create_google_news_target(
        "TSMC",
    )

    assert (
        service.count_by_type(
            "url"
        )
        == 1
    )

    assert (
        service.count_by_type(
            "search"
        )
        == 2
    )

# ==================================================
# P3.5 Update Duplicate Detection
# ==================================================


def test_update_duplicate_url_target(
    service,
):
    """
    P3.5

    兩個不同 Target：

        Target A → URL A
        Target B → URL B

    將 B 更新成 A 的 URL：

        → 必須拒絕
    """

    target_a = service.create_url_target(
        "https://example.com/a",
    )

    target_b = service.create_url_target(
        "https://example.com/b",
    )

    target_b.url = (
        "https://example.com/a"
    )

    with pytest.raises(
        ValueError,
        match="Target URL already exists",
    ):

        service.update(
            target_b
        )

    # 原 Target 不應被破壞
    assert target_a.url == (
        "https://example.com/a"
    )


def test_update_duplicate_search_target(
    service,
):
    """
    P3.5

    兩個不同 Search Target：

        A = AI + google_search
        B = TSMC + google_search

    將 B 更新成：

        AI + google_search

    → 必須拒絕
    """

    target_a = (
        service.create_google_search_target(
            keyword="AI",
        )
    )

    target_b = (
        service.create_google_search_target(
            keyword="TSMC",
        )
    )

    target_b.keyword = "AI"

    with pytest.raises(
        ValueError,
        match="Search Target already exists",
    ):

        service.update(
            target_b
        )

    assert (
        target_a.keyword
        == "AI"
    )


def test_update_same_url_target_allowed(
    service,
):
    """
    P3.5

    Target 更新自己本身：

        ID = 1
        URL = A

    URL 不變：

        → 不應判定為 Duplicate
    """

    target = service.create_url_target(
        "https://example.com",
    )

    target.name = "Updated"

    result = service.update(
        target
    )

    assert result is True

    assert (
        service.get_by_id(
            target.id
        ).name
        == "Updated"
    )


def test_update_same_search_target_allowed(
    service,
):
    """
    P3.5

    Target 更新自己本身：

        keyword = AI
        provider = google_search

    identity 不變：

        → 不應判定為 Duplicate
    """

    target = (
        service.create_google_search_target(
            keyword="AI",
        )
    )

    target.name = "Updated AI Search"

    result = service.update(
        target
    )

    assert result is True

    assert (
        service.get_by_id(
            target.id
        ).name
        == "Updated AI Search"
    )


def test_update_same_keyword_different_provider_allowed(
    service,
):
    """
    P3.5

    Search Target Identity：

        keyword
        +
        search_provider

    因此：

        AI + google_search
        AI + google_news

    是兩個不同 Target。

    將 Target B 更新成相同 keyword，
    但不同 provider：

        → 必須允許
    """

    target_a = (
        service.create_google_search_target(
            keyword="AI",
        )
    )

    target_b = (
        service.create_google_news_target(
            keyword="TSMC",
        )
    )

    target_b.keyword = "AI"

    result = service.update(
        target_b
    )

    assert result is True

    assert (
        target_a.keyword
        == "AI"
    )

    assert (
        target_a.search_provider
        == "google_search"
    )

    assert (
        target_b.keyword
        == "AI"
    )

    assert (
        target_b.search_provider
        == "google_news"
    )
