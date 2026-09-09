"""
tests/test_archive_version_repository.py

AutoSearch V4

P2.2.2 Step 3

ArchiveVersionRepository Test
"""

from database.archive_version_repository import (
    ArchiveVersionRepository
)

from models.archive_version import (
    ArchiveVersion
)


def test_archive_version_repository():

    repo = ArchiveVersionRepository()

    article_id = 1

    # ==================================
    # 取得下一個 Version
    # ==================================

    version_number = repo.get_next_version_number(
        article_id
    )

    assert version_number >= 1

    # ==================================
    # 建立 Version
    # ==================================

    archive_version = ArchiveVersion(

        article_id=article_id,

        raw_document_id=1,

        version_number=version_number,

        file_hash="test_archive_hash",

        storage_path=(
            "archive/html/test/test_archive.html"
        ),

        file_size=1024,

        mime_type="text/html"
    )

    # ==================================
    # Save
    # ==================================

    saved = repo.save(
        archive_version
    )

    assert saved is not None

    assert saved.id is not None

    assert saved.article_id == article_id

    assert (
        saved.version_number
        == version_number
    )

    # ==================================
    # Get By ID
    # ==================================

    result = repo.get_by_id(
        saved.id
    )

    assert result is not None

    assert result.id == saved.id

    assert (
        result.article_id
        == article_id
    )

    # ==================================
    # Get By Article
    # ==================================

    versions = repo.get_by_article_id(
        article_id
    )

    assert len(versions) >= 1

    assert any(
        version.id == saved.id
        for version in versions
    )

    # ==================================
    # Latest Version
    # ==================================

    latest = repo.get_latest_version(
        article_id
    )

    assert latest is not None

    assert (
        latest.version_number
        >= version_number
    )

    # ==================================
    # Exists
    # ==================================

    exists = repo.exists(

        article_id,

        version_number
    )

    assert exists is True

    # ==================================
    # Next Version
    # ==================================

    next_version = (
        repo.get_next_version_number(
            article_id
        )
    )

    assert (
        next_version
        > version_number
    )

    # ==================================
    # Cleanup
    # ==================================

    repo.delete_by_article_id(
        article_id
    )