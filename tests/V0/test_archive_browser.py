"""
tests/test_archive_browser.py

AutoSearch V4

P2.3.6 Archive Browser Tests

測試:

1. 建立 ArchiveBrowser
2. 取得 Article
3. 取得所有 Versions
4. 取得指定 Version
5. 取得 Version By ID
6. 取得 Latest
7. 取得 First
8. 取得 Timeline
9. 取得 Previous Version
10. 取得 Next Version
11. Has History
12. Count Versions
13. Summary
14. Get View
15. Get View By Version ID
16. Get Content
17. Get Latest Content
18. Get First Content
19. Browse
20. Browse Dict
21. 不存在 Article
22. 不存在 Version
23. 空 History
24. repr
"""

from archive.archive_browser import ArchiveBrowser


# ==================================
# Fake Article
# ==================================

class FakeArticle:

    def __init__(
        self,
        article_id=1,
        title="AutoSearch V4 Test Article"
    ):
        self.id = article_id
        self.title = title

    def to_dict(self):

        return {
            "id": self.id,
            "title": self.title
        }


# ==================================
# Fake Version
# ==================================

class FakeVersion:

    def __init__(
        self,
        version_id,
        article_id,
        version_number
    ):
        self.id = version_id
        self.article_id = article_id
        self.version_number = version_number

    def to_dict(self):

        return {
            "id": self.id,
            "article_id": self.article_id,
            "version_number": self.version_number
        }


# ==================================
# Fake View
# ==================================

class FakeView:

    def __init__(
        self,
        article_id,
        version_number,
        content
    ):
        self.article_id = article_id
        self.version_number = version_number
        self.content = content

    def to_dict(self):

        return {
            "article_id": self.article_id,
            "version_number": self.version_number,
            "content": self.content
        }


# ==================================
# Fake Article Repository
# ==================================

class FakeArticleRepository:

    def __init__(self):

        self.article = FakeArticle()

    def get_by_id(
        self,
        article_id
    ):

        if article_id != 1:
            return None

        return self.article


# ==================================
# Fake Version Repository
# ==================================

class FakeVersionRepository:

    def __init__(self):

        self.versions = [

            FakeVersion(
                101,
                1,
                1
            ),

            FakeVersion(
                102,
                1,
                2
            ),

            FakeVersion(
                103,
                1,
                3
            )
        ]

    def get_by_article_id(
        self,
        article_id
    ):

        if article_id != 1:
            return []

        return self.versions

    def get_by_id(
        self,
        version_id
    ):

        for version in self.versions:

            if version.id == version_id:
                return version

        return None

    def get_latest_version(
        self,
        article_id
    ):

        versions = self.get_by_article_id(
            article_id
        )

        if not versions:
            return None

        return versions[-1]


# ==================================
# Fake History Repository
# ==================================

class FakeHistoryRepository:

    def __init__(self):

        self.timeline = [
            {
                "version_number": 1,
                "created_time": "2026-08-01"
            },
            {
                "version_number": 2,
                "created_time": "2026-08-02"
            },
            {
                "version_number": 3,
                "created_time": "2026-08-03"
            }
        ]

    def has_history(
        self,
        article_id
    ):

        return article_id == 1

    def count_versions(
        self,
        article_id
    ):

        if article_id != 1:
            return 0

        return 3

    def get_timeline(
        self,
        article_id
    ):

        if article_id != 1:
            return []

        return self.timeline

    def get_summary(
        self,
        article_id
    ):

        if article_id != 1:
            return None

        return {
            "total_versions": 3,
            "first_version": 1,
            "latest_version": 3
        }


# ==================================
# Fake Archive Viewer
# ==================================

class FakeArchiveViewer:

    def get_view(
        self,
        article_id,
        version_number
    ):

        if article_id != 1:
            return None

        if version_number not in [1, 2, 3]:
            return None

        return FakeView(
            article_id,
            version_number,
            f"Historical content v{version_number}"
        )

    def get_view_by_version_id(
        self,
        version_id
    ):

        mapping = {
            101: 1,
            102: 2,
            103: 3
        }

        version_number = mapping.get(
            version_id
        )

        if version_number is None:
            return None

        return FakeView(
            1,
            version_number,
            f"Historical content v{version_number}"
        )

    def get_latest(
        self,
        article_id
    ):

        if article_id != 1:
            return None

        return FakeView(
            1,
            3,
            "Historical content v3"
        )

    def get_first(
        self,
        article_id
    ):

        if article_id != 1:
            return None

        return FakeView(
            1,
            1,
            "Historical content v1"
        )


# ==================================
# Fixture
# ==================================

def create_browser():

    return ArchiveBrowser(

        article_repository=(
            FakeArticleRepository()
        ),

        version_repository=(
            FakeVersionRepository()
        ),

        history_repository=(
            FakeHistoryRepository()
        ),

        viewer=(
            FakeArchiveViewer()
        )
    )


# ==================================
# Create
# ==================================

def test_create_archive_browser():

    browser = create_browser()

    assert browser is not None


# ==================================
# Get Article
# ==================================

def test_get_article():

    browser = create_browser()

    article = browser.get_article(
        1
    )

    assert article is not None

    assert article.id == 1


# ==================================
# Get Versions
# ==================================

def test_get_versions():

    browser = create_browser()

    versions = browser.get_versions(
        1
    )

    assert len(versions) == 3

    assert versions[0].version_number == 1

    assert versions[-1].version_number == 3


# ==================================
# Get Version
# ==================================

def test_get_version():

    browser = create_browser()

    version = browser.get_version(
        1,
        2
    )

    assert version is not None

    assert version.version_number == 2


# ==================================
# Get Nonexistent Version
# ==================================

def test_get_nonexistent_version():

    browser = create_browser()

    version = browser.get_version(
        1,
        99
    )

    assert version is None


# ==================================
# Get Version By ID
# ==================================

def test_get_version_by_id():

    browser = create_browser()

    version = browser.get_version_by_id(
        102
    )

    assert version is not None

    assert version.id == 102

    assert version.version_number == 2


# ==================================
# Get Latest
# ==================================

def test_get_latest():

    browser = create_browser()

    version = browser.get_latest(
        1
    )

    assert version is not None

    assert version.version_number == 3


# ==================================
# Get First
# ==================================

def test_get_first():

    browser = create_browser()

    version = browser.get_first(
        1
    )

    assert version is not None

    assert version.version_number == 1


# ==================================
# Get Timeline
# ==================================

def test_get_timeline():

    browser = create_browser()

    timeline = browser.get_timeline(
        1
    )

    assert len(timeline) == 3

    assert timeline[0]["version_number"] == 1

    assert timeline[-1]["version_number"] == 3


# ==================================
# Get Previous
# ==================================

def test_get_previous_version():

    browser = create_browser()

    version = browser.get_previous_version(
        1,
        2
    )

    assert version is not None

    assert version.version_number == 1


# ==================================
# Previous First
# ==================================

def test_get_previous_version_first():

    browser = create_browser()

    version = browser.get_previous_version(
        1,
        1
    )

    assert version is None


# ==================================
# Get Next
# ==================================

def test_get_next_version():

    browser = create_browser()

    version = browser.get_next_version(
        1,
        2
    )

    assert version is not None

    assert version.version_number == 3


# ==================================
# Next Latest
# ==================================

def test_get_next_version_latest():

    browser = create_browser()

    version = browser.get_next_version(
        1,
        3
    )

    assert version is None


# ==================================
# Has History
# ==================================

def test_has_history():

    browser = create_browser()

    assert browser.has_history(
        1
    ) is True


# ==================================
# No History
# ==================================

def test_has_no_history():

    browser = create_browser()

    assert browser.has_history(
        999
    ) is False


# ==================================
# Count Versions
# ==================================

def test_count_versions():

    browser = create_browser()

    count = browser.count_versions(
        1
    )

    assert count == 3


# ==================================
# Empty Version Count
# ==================================

def test_count_versions_empty():

    browser = create_browser()

    count = browser.count_versions(
        999
    )

    assert count == 0


# ==================================
# Summary
# ==================================

def test_get_summary():

    browser = create_browser()

    summary = browser.get_summary(
        1
    )

    assert summary is not None

    assert summary["total_versions"] == 3

    assert summary["first_version"] == 1

    assert summary["latest_version"] == 3


# ==================================
# Get View
# ==================================

def test_get_view():

    browser = create_browser()

    view = browser.get_view(
        1,
        2
    )

    assert view is not None

    assert view.version_number == 2

    assert (
        view.content
        == "Historical content v2"
    )


# ==================================
# Get View By Version ID
# ==================================

def test_get_view_by_version_id():

    browser = create_browser()

    view = browser.get_view_by_version_id(
        102
    )

    assert view is not None

    assert view.version_number == 2


# ==================================
# Get Content
# ==================================

def test_get_content():

    browser = create_browser()

    content = browser.get_content(
        1,
        2
    )

    assert (
        content
        == "Historical content v2"
    )


# ==================================
# Get Latest Content
# ==================================

def test_get_latest_content():

    browser = create_browser()

    content = browser.get_latest_content(
        1
    )

    assert (
        content
        == "Historical content v3"
    )


# ==================================
# Get First Content
# ==================================

def test_get_first_content():

    browser = create_browser()

    content = browser.get_first_content(
        1
    )

    assert (
        content
        == "Historical content v1"
    )


# ==================================
# Browse
# ==================================

def test_browse():

    browser = create_browser()

    result = browser.browse(
        1
    )

    assert result is not None

    assert result["article"] is not None

    assert len(
        result["versions"]
    ) == 3

    assert (
        result["latest"].version_number
        == 3
    )

    assert (
        result["first"].version_number
        == 1
    )

    assert result["has_history"] is True

    assert result["count"] == 3


# ==================================
# Browse Dictionary
# ==================================

def test_browse_dict():

    browser = create_browser()

    result = browser.browse_dict(
        1
    )

    assert result is not None

    assert result["article"]["id"] == 1

    assert len(
        result["versions"]
    ) == 3

    assert (
        result["latest"]["version_number"]
        == 3
    )

    assert (
        result["first"]["version_number"]
        == 1
    )

    assert result["has_history"] is True

    assert result["count"] == 3


# ==================================
# Nonexistent Article
# ==================================

def test_browse_nonexistent_article():

    browser = create_browser()

    result = browser.browse(
        999
    )

    assert result is None


# ==================================
# Nonexistent Version By ID
# ==================================

def test_get_nonexistent_version_by_id():

    browser = create_browser()

    result = browser.get_version_by_id(
        999
    )

    assert result is None


# ==================================
# Nonexistent View
# ==================================

def test_get_nonexistent_view():

    browser = create_browser()

    result = browser.get_view(
        1,
        999
    )

    assert result is None


# ==================================
# Dictionary Empty
# ==================================

def test_browse_dict_nonexistent():

    browser = create_browser()

    result = browser.browse_dict(
        999
    )

    assert result is None


# ==================================
# Representation
# ==================================

def test_repr():

    browser = create_browser()

    result = repr(
        browser
    )

    assert "ArchiveBrowser" in result