"""
tests/test_archive_version.py

AutoSearch V4

P2.2.2 Step 2

ArchiveVersion Model Test
"""

from models.archive_version import ArchiveVersion


def test_create_archive_version():

    version = ArchiveVersion(
        article_id=1,
        raw_document_id=1,
        version_number=1,
        file_hash="abc123",
        storage_path="archive/html/2026/08/07/test.html",
        file_size=1024,
        mime_type="text/html"
    )

    assert version.id is None

    assert version.article_id == 1

    assert version.raw_document_id == 1

    assert version.version_number == 1

    assert version.file_hash == "abc123"

    assert (
        version.storage_path
        == "archive/html/2026/08/07/test.html"
    )

    assert version.file_size == 1024

    assert version.mime_type == "text/html"


def test_archive_version_filename():

    version = ArchiveVersion(
        storage_path=(
            "archive/html/2026/08/07/test.html"
        )
    )

    assert version.filename == "test.html"


def test_archive_version_is_html():

    version = ArchiveVersion(
        mime_type="text/html"
    )

    assert version.is_html is True


def test_archive_version_to_dict():

    version = ArchiveVersion(
        article_id=1,
        raw_document_id=2,
        version_number=3
    )

    data = version.to_dict()

    assert data["article_id"] == 1

    assert data["raw_document_id"] == 2

    assert data["version_number"] == 3


def test_archive_version_repr():

    version = ArchiveVersion(
        article_id=1,
        raw_document_id=2,
        version_number=3,
        storage_path="test.html"
    )

    result = repr(version)

    assert "ArchiveVersion" in result

    assert "article_id=1" in result

    assert "version=3" in result