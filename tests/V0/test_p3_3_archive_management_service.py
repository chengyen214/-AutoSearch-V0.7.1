"""
tests/test_p3_3_archive_management_service.py

AutoSearch V4

P3.3

Archive Management Service Tests

測試：

    1. Service Initialization
    2. Article Metadata Management
    3. Archive Version Management
    4. Archive Article Management
    5. Archive Statistics
    6. Search Index Management
    7. Health Check

注意：

    本測試使用 Mock Repository。

    不直接操作 MySQL。
"""


from types import SimpleNamespace

import pytest

from services.archive_management_service import (
    ArchiveManagementService
)


# ============================================================
# Mock Metadata Repository
# ============================================================

class MockMetadataRepository:

    def __init__(self):

        self.metadata = {}

        self.insert_count = 0

        self.update_count = 0


    def insert(
        self,
        metadata
    ):

        self.insert_count += 1

        metadata.id = 1

        self.metadata[
            metadata.article_id
        ] = metadata

        return metadata


    def get_by_article_id(
        self,
        article_id
    ):

        return self.metadata.get(
            article_id
        )


    def exists(
        self,
        article_id
    ):

        return article_id in self.metadata


    def update(
        self,
        article_id,
        metadata
    ):

        if article_id not in self.metadata:

            return False

        self.metadata[
            article_id
        ] = metadata

        self.update_count += 1

        return True


# ============================================================
# Mock Version Repository
# ============================================================

class MockVersionRepository:

    def __init__(self):

        self.versions = {

            1: [

                SimpleNamespace(

                    id=1,

                    article_id=1,

                    raw_document_id=1,

                    version_number=1,

                    file_hash="hash-1",

                    storage_path="/archive/1",

                    file_size=100,

                    mime_type="text/html"

                ),

                SimpleNamespace(

                    id=2,

                    article_id=1,

                    raw_document_id=2,

                    version_number=2,

                    file_hash="hash-2",

                    storage_path="/archive/2",

                    file_size=200,

                    mime_type="text/html"

                )

            ]

        }


    def get_version(
        self,
        article_id,
        version_number
    ):

        for version in self.versions.get(
            article_id,
            []
        ):

            if version.version_number == (
                version_number
            ):

                return version

        return None


    def get_by_id(
        self,
        version_id
    ):

        for versions in self.versions.values():

            for version in versions:

                if version.id == version_id:

                    return version

        return None


    def get_by_article_id(
        self,
        article_id
    ):

        return self.versions.get(
            article_id,
            []
        )


    def get_latest_version(
        self,
        article_id
    ):

        versions = self.get_by_article_id(
            article_id
        )

        if not versions:

            return None

        return max(
            versions,
            key=lambda version:
                version.version_number
        )


    def get_latest_version_number(
        self,
        article_id
    ):

        latest = self.get_latest_version(
            article_id
        )

        if latest is None:

            return 0

        return latest.version_number


    def get_next_version_number(
        self,
        article_id
    ):

        return (
            self.get_latest_version_number(
                article_id
            )
            + 1
        )


    def exists(
        self,
        article_id,
        version_number
    ):

        return (
            self.get_version(
                article_id,
                version_number
            )
            is not None
        )


    def count_by_article_id(
        self,
        article_id
    ):

        return len(
            self.get_by_article_id(
                article_id
            )
        )


    def delete_by_id(
        self,
        version_id
    ):

        for article_id, versions in (
            self.versions.items()
        ):

            for version in list(
                versions
            ):

                if version.id == version_id:

                    versions.remove(
                        version
                    )

                    return True

        return False


# ============================================================
# Mock Archive Repository
# ============================================================

class MockArchiveRepository:

    def __init__(self):

        self.articles = {

            1: {

                "id": 1,

                "title":
                    "Test Article",

                "source":
                    "CNA"

            },

            2: {

                "id": 2,

                "title":
                    "Second Article",

                "source":
                    "Reuters"

            }

        }


    def get_article(
        self,
        article_id
    ):

        return self.articles.get(
            article_id
        )


    def get_articles(
        self,
        limit=None
    ):

        articles = list(
            self.articles.values()
        )

        if limit is None:

            return articles

        return articles[
            :limit
        ]


    def count_articles(
        self
    ):

        return len(
            self.articles
        )


    def count(
        self
    ):

        return len(
            self.articles
        )


    def get_statistics(
        self
    ):

        return {

            "articles":
                len(self.articles),

            "archive_versions":
                2

        }


# ============================================================
# Fixtures
# ============================================================

@pytest.fixture
def metadata_repository():

    return MockMetadataRepository()


@pytest.fixture
def version_repository():

    return MockVersionRepository()


@pytest.fixture
def archive_repository():

    return MockArchiveRepository()


@pytest.fixture
def service(
    metadata_repository,
    version_repository,
    archive_repository
):

    return ArchiveManagementService(

        metadata_repository=
            metadata_repository,

        version_repository=
            version_repository,

        archive_repository=
            archive_repository

    )


# ============================================================
# Service Initialization
# ============================================================

def test_service_initialization(
    service
):

    assert service is not None

    assert service.metadata_repository is not None

    assert service.version_repository is not None

    assert service.archive_repository is not None


# ============================================================
# Metadata
# ============================================================

def test_get_metadata_empty(
    service
):

    result = service.get_metadata(
        1
    )

    assert result is None


def test_metadata_exists_false(
    service
):

    assert (
        service.metadata_exists(1)
        is False
    )


def test_create_metadata(
    service,
    metadata_repository
):

    metadata = SimpleNamespace(

        id=None,

        article_id=1,

        author="Test Author",

        category="Technology",

        language="zh-TW",

        source_type="news",

        tags="test"

    )

    result = service.create_metadata(
        metadata
    )

    assert result is metadata

    assert result.id == 1

    assert (
        service.metadata_exists(1)
        is True
    )

    assert (
        metadata_repository.insert_count
        == 1
    )


def test_create_duplicate_metadata(
    service
):

    metadata = SimpleNamespace(

        id=None,

        article_id=1,

        author="Test Author",

        category="Technology",

        language="zh-TW",

        source_type="news",

        tags="test"

    )

    service.create_metadata(
        metadata
    )

    with pytest.raises(
        ValueError,
        match="already exists"
    ):

        service.create_metadata(
            metadata
        )


def test_update_metadata(
    service,
    metadata_repository
):

    original = SimpleNamespace(

        id=1,

        article_id=1,

        author="Old Author",

        category="Technology",

        language="zh-TW",

        source_type="news",

        tags="old"

    )

    service.create_metadata(
        original
    )

    updated = SimpleNamespace(

        id=1,

        article_id=1,

        author="New Author",

        category="Semiconductor",

        language="zh-TW",

        source_type="news",

        tags="TSMC"

    )

    result = service.update_metadata(
        1,
        updated
    )

    assert result is True

    assert (
        metadata_repository.update_count
        == 1
    )


def test_update_metadata_not_exists(
    service
):

    metadata = SimpleNamespace(

        article_id=999,

        author="Test",

        category="Test",

        language="zh-TW",

        source_type="news",

        tags="test"

    )

    result = service.update_metadata(
        999,
        metadata
    )

    assert result is False


# ============================================================
# Version
# ============================================================

def test_get_version(
    service
):

    result = service.get_version(
        1,
        1
    )

    assert result is not None

    assert result.version_number == 1


def test_get_version_not_found(
    service
):

    result = service.get_version(
        1,
        99
    )

    assert result is None


def test_get_version_by_id(
    service
):

    result = service.get_version_by_id(
        1
    )

    assert result is not None

    assert result.id == 1


def test_get_versions(
    service
):

    result = service.get_versions(
        1
    )

    assert len(result) == 2


def test_get_latest_version(
    service
):

    result = service.get_latest_version(
        1
    )

    assert result is not None

    assert result.version_number == 2


def test_get_latest_version_number(
    service
):

    assert (
        service.get_latest_version_number(1)
        == 2
    )


def test_get_next_version_number(
    service
):

    assert (
        service.get_next_version_number(1)
        == 3
    )


def test_version_exists(
    service
):

    assert (
        service.version_exists(1, 1)
        is True
    )

    assert (
        service.version_exists(1, 99)
        is False
    )


def test_count_versions(
    service
):

    assert (
        service.count_versions(1)
        == 2
    )


# ============================================================
# Version Delete
# ============================================================

def test_delete_version_protected(
    service
):

    with pytest.raises(
        ValueError,
        match="protected"
    ):

        service.delete_version(
            1
        )


def test_delete_version_not_found(
    service
):

    result = service.delete_version(
        999
    )

    assert result is False


# ============================================================
# Archive Article
# ============================================================

def test_get_article(
    service
):

    result = service.get_article(
        1
    )

    assert result is not None

    assert result["id"] == 1


def test_get_article_not_found(
    service
):

    result = service.get_article(
        999
    )

    assert result is None


def test_get_articles(
    service
):

    result = service.get_articles()

    assert len(result) == 2


def test_get_articles_with_limit(
    service
):

    result = service.get_articles(
        limit=1
    )

    assert len(result) == 1


# ============================================================
# Statistics
# ============================================================

def test_get_statistics(
    service
):

    result = service.get_statistics()

    assert result["articles"] == 2

    assert result["archive_versions"] == 2


# ============================================================
# Search Index
# ============================================================

def test_get_index_status(
    service
):

    result = service.get_index_status()

    assert result["status"] == "available"

    assert "refresh" in (
        result["operations"]
    )

    assert "rebuild" in (
        result["operations"]
    )


def test_refresh_index(
    service
):

    result = service.refresh_index()

    assert result["operation"] == "refresh"

    assert result["status"] == "not_implemented"


def test_rebuild_index(
    service
):

    result = service.rebuild_index()

    assert result["operation"] == "rebuild"

    assert result["status"] == "not_implemented"


# ============================================================
# Health
# ============================================================

def test_health_check(
    service
):

    result = service.health_check()

    assert result["status"] == "ok"

    assert result["service"] == (
        "archive-management-service"
    )

    assert result["version"] == "P3.3"


# ============================================================
# Validation
# ============================================================

def test_invalid_article_id(
    service
):

    assert (
        service.get_metadata(0)
        is None
    )

    assert (
        service.get_versions(0)
        == []
    )

    assert (
        service.get_article(0)
        is None
    )


def test_invalid_version_number(
    service
):

    assert (
        service.get_version(1, 0)
        is None
    )

    assert (
        service.version_exists(1, 0)
        is False
    )


# ============================================================
# Repr
# ============================================================

def test_repr(
    service
):

    result = repr(
        service
    )

    assert (
        "ArchiveManagementService"
        in result
    )
