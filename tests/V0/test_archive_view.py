"""
tests/test_archive_view.py

AutoSearch V4

P2.3.5 Archive Viewer

測試：

1. ArchiveView 建立
2. 預設值
3. Version metadata
4. Historical content
5. has_content
6. content_length
7. to_dict
8. __repr__
9. None / 空內容
"""

from models.archive_view import ArchiveView


# ==================================
# Create
# ==================================

def test_create_archive_view():

    view = ArchiveView(
        article_id=1,
        version_id=10,
        version_number=2,
        title="Test Article",
        content="Historical article content",
    )

    assert view.article_id == 1
    assert view.version_id == 10
    assert view.version_number == 2
    assert view.title == "Test Article"
    assert view.content == "Historical article content"


# ==================================
# Default Values
# ==================================

def test_default_values():

    view = ArchiveView()

    assert view.article_id is None
    assert view.version_id is None
    assert view.version_number is None
    assert view.title == ""
    assert view.content == ""


# ==================================
# Version Metadata
# ==================================

def test_version_metadata():

    view = ArchiveView(
        article_id=100,
        version_id=200,
        version_number=5,
        title="Version Test",
    )

    assert view.article_id == 100
    assert view.version_id == 200
    assert view.version_number == 5
    assert view.title == "Version Test"


# ==================================
# Historical Content
# ==================================

def test_historical_content():

    content = """\
第一版歷史內容
第二行內容
第三行內容
"""

    view = ArchiveView(
        article_id=1,
        version_id=2,
        version_number=1,
        title="Historical Test",
        content=content,
    )

    assert view.content == content


# ==================================
# Has Content
# ==================================

def test_has_content():

    view = ArchiveView(
        content="Historical content"
    )

    assert view.has_content is True


def test_has_no_content():

    view = ArchiveView()

    assert view.has_content is False


# ==================================
# Content Length
# ==================================

def test_content_length():

    content = "AutoSearch V4"

    view = ArchiveView(
        content=content
    )

    assert view.content_length == len(content)


def test_empty_content_length():

    view = ArchiveView()

    assert view.content_length == 0


# ==================================
# None Content
# ==================================

def test_none_content():

    view = ArchiveView(
        content=None
    )

    assert view.has_content is False
    assert view.content_length == 0


# ==================================
# To Dict
# ==================================

def test_to_dict():

    view = ArchiveView(
        article_id=1,
        version_id=10,
        version_number=3,
        title="Test Article",
        content="Test Content",
    )

    result = view.to_dict()

    assert isinstance(result, dict)

    assert result["article_id"] == 1
    assert result["version_id"] == 10
    assert result["version_number"] == 3
    assert result["title"] == "Test Article"
    assert result["content"] == "Test Content"


# ==================================
# To Dict Empty
# ==================================

def test_to_dict_empty():

    view = ArchiveView()

    result = view.to_dict()

    assert isinstance(result, dict)

    assert result["article_id"] is None
    assert result["version_id"] is None
    assert result["version_number"] is None
    assert result["title"] == ""
    assert result["content"] == ""


# ==================================
# Repr
# ==================================

def test_repr():

    view = ArchiveView(
        article_id=1,
        version_id=10,
        version_number=2,
        title="Test Article",
        content="Test Content",
    )

    result = repr(view)

    assert isinstance(result, str)
    assert "ArchiveView" in result