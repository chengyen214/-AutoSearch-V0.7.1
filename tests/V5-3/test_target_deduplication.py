"""
tests/V5-3/test_target_deduplication.py

AutoSearch V5

V5.3 P3.5

Target Deduplication Tests

測試：

    - URL Target Deduplication
    - Search Target Deduplication
    - URL Normalization Deduplication
    - Search Keyword Normalization Deduplication
    - Search Provider Deduplication
    - Same Keyword Different Provider
    - Update Self Deduplication
    - Update Conflict Deduplication
    - URL / Search Target Isolation

注意：

    本測試只確認 Target 層級的 Deduplication。

    不測試：

        - Article Deduplication
        - URL + Context Hash
        - Crawl Deduplication
        - Archive Deduplication

    上述能力屬於 V4 Existing Crawl / Article Pipeline。
"""


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
    P3.5 測試用 Repository。

    模擬 TargetRepository 的 Deduplication
    相關 API。
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
                and target.url == url
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
        ).strip().lower()

        for target in self.targets:

            if (
                target.target_type == "search"
                and target.keyword == keyword
                and target.search_provider
                == search_provider
            ):

                return target

        return None

    # ==============================================
    # Exists
    # ==============================================

    def exists_by_url(
        self,
        url,
    ):

        return (
            self.get_by_url(url)
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
                search_provider,
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


# ==================================================
# Fake Validator
# ==================================================


class FakeValidator:
    """
    P3.5 測試用 Validator。

    模擬 V5 TargetValidator 的：

        normalize()
        validate()
    """

    def normalize(
        self,
        target,
    ):

        # ------------------------------------------
        # URL
        # ------------------------------------------

        if (
            target.target_type == "url"
            and target.url
        ):

            target.url = (
                str(target.url)
                .strip()
            )

        # ------------------------------------------
        # Search
        # ------------------------------------------

        if (
            target.target_type == "search"
        ):

            if target.keyword:

                target.keyword = (
                    str(target.keyword)
                    .strip()
                )

            if target.search_provider:

                target.search_provider = (
                    str(target.search_provider)
                    .strip()
                    .lower()
                )

        return target

    def validate(
        self,
        target,
    ):

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
# URL Target Deduplication
# ==================================================


def test_duplicate_url_target_is_rejected(
    service,
):

    service.create_url_target(
        "https://example.com"
    )

    with pytest.raises(
        ValueError,
        match="Target URL already exists",
    ):

        service.create_url_target(
            "https://example.com"
        )


def test_duplicate_url_with_surrounding_spaces_is_rejected(
    service,
):

    service.create_url_target(
        "https://example.com"
    )

    with pytest.raises(
        ValueError,
        match="Target URL already exists",
    ):

        service.create_url_target(
            "  https://example.com  "
        )


def test_different_url_is_allowed(
    service,
):

    first = service.create_url_target(
        "https://example.com"
    )

    second = service.create_url_target(
        "https://example.org"
    )

    assert first.id != second.id


# ==================================================
# Search Target Deduplication
# ==================================================


def test_duplicate_search_target_is_rejected(
    service,
):

    service.create_search_target(
        keyword="AI",
        search_provider="google_search",
    )

    with pytest.raises(
        ValueError,
        match="Search Target already exists",
    ):

        service.create_search_target(
            keyword="AI",
            search_provider="google_search",
        )


def test_duplicate_search_keyword_after_normalization_is_rejected(
    service,
):

    service.create_search_target(
        keyword="AI",
        search_provider="google_search",
    )

    with pytest.raises(
        ValueError,
        match="Search Target already exists",
    ):

        service.create_search_target(
            keyword="  AI  ",
            search_provider="google_search",
        )


def test_duplicate_search_provider_after_normalization_is_rejected(
    service,
):

    service.create_search_target(
        keyword="AI",
        search_provider="google_search",
    )

    with pytest.raises(
        ValueError,
        match="Search Target already exists",
    ):

        service.create_search_target(
            keyword="AI",
            search_provider=" GOOGLE_SEARCH ",
        )


# ==================================================
# Search Provider Isolation
# ==================================================


def test_same_keyword_different_provider_is_allowed(
    service,
):

    google = service.create_search_target(
        keyword="AI",
        search_provider="google_search",
    )

    news = service.create_search_target(
        keyword="AI",
        search_provider="google_news",
    )

    assert google.id != news.id


def test_same_provider_different_keyword_is_allowed(
    service,
):

    first = service.create_search_target(
        keyword="AI",
        search_provider="google_search",
    )

    second = service.create_search_target(
        keyword="TSMC",
        search_provider="google_search",
    )

    assert first.id != second.id


# ==================================================
# URL / Search Isolation
# ==================================================


def test_url_and_search_targets_are_independent(
    service,
):

    url_target = service.create_url_target(
        "https://example.com"
    )

    search_target = service.create_search_target(
        keyword="https://example.com",
        search_provider="google_search",
    )

    assert url_target.id != search_target.id

    assert url_target.target_type == "url"

    assert search_target.target_type == "search"


# ==================================================
# Update Deduplication
# ==================================================


def test_update_same_url_target_is_allowed(
    service,
):

    target = service.create_url_target(
        "https://example.com"
    )

    target.name = "Updated"

    result = service.update(
        target
    )

    assert result is True

    assert target.name == "Updated"


def test_update_same_search_target_is_allowed(
    service,
):

    target = service.create_search_target(
        keyword="AI",
        search_provider="google_search",
    )

    target.name = "Updated"

    result = service.update(
        target
    )

    assert result is True

    assert target.name == "Updated"


def test_update_url_to_existing_url_is_rejected(
    service,
):

    first = service.create_url_target(
        "https://example.com"
    )

    second = service.create_url_target(
        "https://example.org"
    )

    second.url = "https://example.com"

    with pytest.raises(
        ValueError,
        match="Target URL already exists",
    ):

        service.update(
            second
        )

    assert first.url == "https://example.com"


def test_update_search_to_existing_search_is_rejected(
    service,
):

    first = service.create_search_target(
        keyword="AI",
        search_provider="google_search",
    )

    second = service.create_search_target(
        keyword="TSMC",
        search_provider="google_search",
    )

    second.keyword = "AI"

    with pytest.raises(
        ValueError,
        match="Search Target already exists",
    ):

        service.update(
            second
        )

    assert first.keyword == "AI"


def test_update_search_to_same_keyword_different_provider_is_allowed(
    service,
):

    first = service.create_search_target(
        keyword="AI",
        search_provider="google_search",
    )

    second = service.create_search_target(
        keyword="TSMC",
        search_provider="google_news",
    )

    second.keyword = "AI"

    result = service.update(
        second
    )

    assert result is True

    assert first.id != second.id

    assert second.keyword == "AI"

    assert (
        second.search_provider
        == "google_news"
    )


# ==================================================
# Existence Checks
# ==================================================


def test_exists_by_url_detects_duplicate(
    service,
):

    service.create_url_target(
        "https://example.com"
    )

    assert service.exists_by_url(
        "https://example.com"
    )


def test_exists_by_search_detects_duplicate(
    service,
):

    service.create_search_target(
        keyword="AI",
        search_provider="google_search",
    )

    assert service.exists_by_search(
        "AI",
        "google_search",
    )


def test_exists_by_search_respects_provider(
    service,
):

    service.create_search_target(
        keyword="AI",
        search_provider="google_search",
    )

    assert service.exists_by_search(
        "AI",
        "google_search",
    )

    assert not service.exists_by_search(
        "AI",
        "google_news",
    )


# ==================================================
# Empty Repository
# ==================================================


def test_empty_repository_has_no_duplicates(
    service,
):

    assert not service.exists_by_url(
        "https://example.com"
    )

    assert not service.exists_by_search(
        "AI",
        "google_search",
    )


