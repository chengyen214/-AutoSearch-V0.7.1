"""
tests/test_archive_content_reader.py

AutoSearch V4

P2.3.5

Archive Content Reader Tests

測試：

1. Reader 建立
2. Path Normalize
3. File Exists
4. Read HTML
5. Read Bytes
6. File Size
7. Generate Hash
8. Verify Hash
9. Invalid Hash
10. Read Version
11. Verify Version
12. Get Metadata
13. Contains
14. Case Sensitive Search
15. Missing File
16. Empty Path
17. Repr
"""

import hashlib

from archive.archive_content_reader import (
    ArchiveContentReader
)


# ==========================================
# Test HTML
# ==========================================

TEST_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>TSMC 2nm</title>
</head>
<body>
    <h1>TSMC 2nm Process</h1>
    <p>
        TSMC 2nm mass production.
    </p>
    <p>
        CoWoS and HBM demand continue to grow.
    </p>
</body>
</html>
"""


# ==========================================
# Mock Archive Version
# ==========================================

class MockArchiveVersion:

    def __init__(
        self,
        storage_path,
        file_hash
    ):

        self.storage_path = storage_path

        self.file_hash = file_hash


# ==========================================
# Helper
# ==========================================

def create_archive_file(
    tmp_path
):
    """
    建立測試 Archive File。
    """

    archive_dir = (
        tmp_path
        / "archive"
        / "html"
        / "2026"
        / "08"
        / "08"
    )

    archive_dir.mkdir(
        parents=True
    )

    file_path = (
        archive_dir
        / "test_hash.html"
    )

    file_path.write_text(
        TEST_HTML,
        encoding="utf-8"
    )

    storage_path = (
        "archive/html/"
        "2026/08/08/"
        "test_hash.html"
    )

    return (
        file_path,
        storage_path
    )


# ==========================================
# Create Reader
# ==========================================

def test_create_archive_content_reader(
    tmp_path
):

    reader = ArchiveContentReader(
        archive_root=str(
            tmp_path
        )
    )

    assert reader is not None

    assert reader.archive_root == (
        str(
            tmp_path
        )
        .replace(
            "/",
            "\\"
        )
        if "\\" in str(tmp_path)
        else str(tmp_path)
    )


# ==========================================
# Get Path
# ==========================================

def test_get_path(
    tmp_path
):

    reader = ArchiveContentReader(
        archive_root=str(
            tmp_path
        )
    )

    _, storage_path = (
        create_archive_file(
            tmp_path
        )
    )

    path = reader.get_path(
        storage_path
    )

    assert path is not None

    assert path.endswith(
        "test_hash.html"
    )


# ==========================================
# Exists
# ==========================================

def test_exists(
    tmp_path
):

    reader = ArchiveContentReader(
        archive_root=str(
            tmp_path
        )
    )

    _, storage_path = (
        create_archive_file(
            tmp_path
        )
    )

    assert reader.exists(
        storage_path
    ) is True


# ==========================================
# Missing File
# ==========================================

def test_missing_file(
    tmp_path
):

    reader = ArchiveContentReader(
        archive_root=str(
            tmp_path
        )
    )

    assert reader.exists(
        "archive/html/missing.html"
    ) is False


# ==========================================
# Read HTML
# ==========================================

def test_read_html(
    tmp_path
):

    reader = ArchiveContentReader(
        archive_root=str(
            tmp_path
        )
    )

    _, storage_path = (
        create_archive_file(
            tmp_path
        )
    )

    content = reader.read(
        storage_path
    )

    assert content is not None

    assert (
        "TSMC 2nm"
        in content
    )

    assert (
        "CoWoS"
        in content
    )


# ==========================================
# Read Bytes
# ==========================================

def test_read_bytes(
    tmp_path
):

    reader = ArchiveContentReader(
        archive_root=str(
            tmp_path
        )
    )

    file_path, storage_path = (
        create_archive_file(
            tmp_path
        )
    )

    content = reader.read_bytes(
        storage_path
    )

    expected = (
        file_path.read_bytes()
    )

    assert content == expected

    assert isinstance(
        content,
        bytes
    )


# ==========================================
# File Size
# ==========================================

def test_get_file_size(
    tmp_path
):

    reader = ArchiveContentReader(
        archive_root=str(
            tmp_path
        )
    )

    file_path, storage_path = (
        create_archive_file(
            tmp_path
        )
    )

    size = reader.get_file_size(
        storage_path
    )

    assert size == (
        file_path.stat().st_size
    )

    assert size > 0


# ==========================================
# Generate Hash
# ==========================================

def test_generate_hash(
    tmp_path
):

    reader = ArchiveContentReader(
        archive_root=str(
            tmp_path
        )
    )

    file_path, storage_path = (
        create_archive_file(
            tmp_path
        )
    )

    actual = reader.generate_hash(
        storage_path
    )

    expected = (
        hashlib.sha256(
            file_path.read_bytes()
        )
        .hexdigest()
    )

    assert actual == expected


# ==========================================
# Verify Hash
# ==========================================

def test_verify_hash(
    tmp_path
):

    reader = ArchiveContentReader(
        archive_root=str(
            tmp_path
        )
    )

    _, storage_path = (
        create_archive_file(
            tmp_path
        )
    )

    file_hash = reader.generate_hash(
        storage_path
    )

    assert reader.verify_hash(
        storage_path,
        file_hash
    ) is True


# ==========================================
# Invalid Hash
# ==========================================

def test_verify_invalid_hash(
    tmp_path
):

    reader = ArchiveContentReader(
        archive_root=str(
            tmp_path
        )
    )

    _, storage_path = (
        create_archive_file(
            tmp_path
        )
    )

    assert reader.verify_hash(
        storage_path,
        "invalid_hash"
    ) is False


# ==========================================
# Read Version
# ==========================================

def test_read_version(
    tmp_path
):

    reader = ArchiveContentReader(
        archive_root=str(
            tmp_path
        )
    )

    _, storage_path = (
        create_archive_file(
            tmp_path
        )
    )

    file_hash = reader.generate_hash(
        storage_path
    )

    version = MockArchiveVersion(

        storage_path=storage_path,

        file_hash=file_hash

    )

    content = reader.read_version(
        version
    )

    assert content is not None

    assert (
        "TSMC 2nm"
        in content
    )


# ==========================================
# Read Version From Dict
# ==========================================

def test_read_version_from_dict(
    tmp_path
):

    reader = ArchiveContentReader(
        archive_root=str(
            tmp_path
        )
    )

    _, storage_path = (
        create_archive_file(
            tmp_path
        )
    )

    version = {

        "storage_path":
            storage_path

    }

    content = reader.read_version(
        version
    )

    assert content is not None

    assert (
        "CoWoS"
        in content
    )


# ==========================================
# Verify Version
# ==========================================

def test_verify_version(
    tmp_path
):

    reader = ArchiveContentReader(
        archive_root=str(
            tmp_path
        )
    )

    _, storage_path = (
        create_archive_file(
            tmp_path
        )
    )

    file_hash = reader.generate_hash(
        storage_path
    )

    version = MockArchiveVersion(

        storage_path=storage_path,

        file_hash=file_hash

    )

    assert reader.verify_version(
        version
    ) is True


# ==========================================
# Verify Invalid Version
# ==========================================

def test_verify_invalid_version(
    tmp_path
):

    reader = ArchiveContentReader(
        archive_root=str(
            tmp_path
        )
    )

    _, storage_path = (
        create_archive_file(
            tmp_path
        )
    )

    version = MockArchiveVersion(

        storage_path=storage_path,

        file_hash="wrong_hash"

    )

    assert reader.verify_version(
        version
    ) is False


# ==========================================
# Metadata
# ==========================================

def test_get_metadata(
    tmp_path
):

    reader = ArchiveContentReader(
        archive_root=str(
            tmp_path
        )
    )

    file_path, storage_path = (
        create_archive_file(
            tmp_path
        )
    )

    metadata = reader.get_metadata(
        storage_path
    )

    assert metadata is not None

    assert (
        metadata["storage_path"]
        == storage_path
    )

    assert (
        metadata["file_size"]
        == file_path.stat().st_size
    )

    assert (
        metadata["file_hash"]
        == reader.generate_hash(
            storage_path
        )
    )


# ==========================================
# Contains
# ==========================================

def test_contains(
    tmp_path
):

    reader = ArchiveContentReader(
        archive_root=str(
            tmp_path
        )
    )

    _, storage_path = (
        create_archive_file(
            tmp_path
        )
    )

    assert reader.contains(
        storage_path,
        "TSMC 2nm"
    ) is True

    assert reader.contains(
        storage_path,
        "CoWoS"
    ) is True

    assert reader.contains(
        storage_path,
        "NVIDIA"
    ) is False


# ==========================================
# Case Insensitive
# ==========================================

def test_contains_case_insensitive(
    tmp_path
):

    reader = ArchiveContentReader(
        archive_root=str(
            tmp_path
        )
    )

    _, storage_path = (
        create_archive_file(
            tmp_path
        )
    )

    assert reader.contains(
        storage_path,
        "tsmc 2nm"
    ) is True


# ==========================================
# Case Sensitive
# ==========================================

def test_contains_case_sensitive(
    tmp_path
):

    reader = ArchiveContentReader(
        archive_root=str(
            tmp_path
        )
    )

    _, storage_path = (
        create_archive_file(
            tmp_path
        )
    )

    assert reader.contains(

        storage_path,

        "tsmc 2nm",

        case_sensitive=True

    ) is False


# ==========================================
# Empty Keyword
# ==========================================

def test_contains_empty_keyword(
    tmp_path
):

    reader = ArchiveContentReader(
        archive_root=str(
            tmp_path
        )
    )

    _, storage_path = (
        create_archive_file(
            tmp_path
        )
    )

    assert reader.contains(
        storage_path,
        ""
    ) is False


# ==========================================
# Empty Path
# ==========================================

def test_empty_path(
    tmp_path
):

    reader = ArchiveContentReader(
        archive_root=str(
            tmp_path
        )
    )

    assert reader.read(
        ""
    ) is None

    assert reader.exists(
        ""
    ) is False

    assert reader.generate_hash(
        ""
    ) is None


# ==========================================
# Missing File Read
# ==========================================

def test_missing_file_read(
    tmp_path
):

    reader = ArchiveContentReader(
        archive_root=str(
            tmp_path
        )
    )

    result = reader.read(
        "archive/html/missing.html"
    )

    assert result is None


# ==========================================
# Missing File Metadata
# ==========================================

def test_missing_file_metadata(
    tmp_path
):

    reader = ArchiveContentReader(
        archive_root=str(
            tmp_path
        )
    )

    result = reader.get_metadata(
        "archive/html/missing.html"
    )

    assert result is None


# ==========================================
# Repr
# ==========================================

def test_repr(
    tmp_path
):

    reader = ArchiveContentReader(
        archive_root=str(
            tmp_path
        )
    )

    result = repr(
        reader
    )

    assert (
        "ArchiveContentReader"
        in result
    )