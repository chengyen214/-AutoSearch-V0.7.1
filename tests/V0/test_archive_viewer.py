"""
tests/test_archive_viewer.py

AutoSearch V4

P2.3.5 Archive Viewer / Historical Content Retrieval

測試：

1. ArchiveViewer 建立
2. 取得 Article
3. 取得指定 Version
4. 取得 Version By ID
5. 取得 Latest
6. 取得 First
7. 取得指定 ArchiveView
8. 取得 Version ID ArchiveView
9. 取得 History
10. 取得 Timeline
11. 取得 Historical Content
12. 取得 Latest Content
13. 取得 First Content
14. Has History
15. Count Versions
16. 不存在資料
17. Dictionary / Object 相容
18. ArchiveViewer repr
"""

from types import SimpleNamespace

from archive.archive_viewer import ArchiveViewer


# ==================================
# Fake Article Repository
# ==================================

class FakeArticleRepository:

    def __init__(self):

        self.articles = {
            1: SimpleNamespace(
                id=1,
                title="AutoSearch V4 Test Article"
            )
        }

    def get_by_id(
        self,
        article_id
    ):

        return self.articles.get(
            article_id
        )


# ==================================
# Fake History Repository
# ==================================

class FakeHistoryRepository:

    def __init__(self):

        self.versions = {

            1: [
                SimpleNamespace(
                    id=101,
                    article_id=1,
                    version_number=1,
                    content="Version 1 Content"
                ),

                SimpleNamespace(
                    id=102,
                    article_id=1,
                    version_number=2,
                    content="Version 2 Content"
                ),

                SimpleNamespace(
                    id=103,
                    article_id=1,
                    version_number=3,
                    content="Version 3 Content"
                )
            ]
        }

    # ==================================
    # Get Version
    # ==================================

    def get_version(
        self,
        article_id,
        version_number
    ):

        versions = self.versions.get(
            article_id,
            []
        )

        for version in versions:

            if version.version_number == version_number:

                return version

        return None

    # ==================================
    # Get Version By ID
    # ==================================

    def get_version_by_id(
        self,
        version_id
    ):

        for versions in self.versions.values():

            for version in versions:

                if version.id == version_id:

                    return version

        return None

    # ==================================
    # Get Latest
    # ==================================

    def get_latest(
        self,
        article_id
    ):

        versions = self.versions.get(
            article_id,
            []
        )

        if not versions:

            return None

        return versions[-1]

    # ==================================
    # Get First
    # ==================================

    def get_first(
        self,
        article_id
    ):

        versions = self.versions.get(
            article_id,
            []
        )

        if not versions:

            return None

        return versions[0]

    # ==================================
    # Get History
    # ==================================

    def get_history(
        self,
        article_id
    ):

        return self.versions.get(
            article_id,
            []
        )

    # ==================================
    # Get Timeline
    # ==================================

    def get_timeline(
        self,
        article_id
    ):

        versions = self.versions.get(
            article_id,
            []
        )

        return [
            {
                "version_number": version.version_number,
                "version_id": version.id
            }
            for version in versions
        ]

    # ==================================
    # Has History
    # ==================================

    def has_history(
        self,
        article_id
    ):

        return bool(
            self.versions.get(
                article_id,
                []
            )
        )

    # ==================================
    # Count Versions
    # ==================================

    def count_versions(
        self,
        article_id
    ):

        return len(
            self.versions.get(
                article_id,
                []
            )
        )


# ==================================
# Fake Version Repository
# ==================================

class FakeVersionRepository:
    """
    P2.3.5 目前 ArchiveViewer
    不直接使用 VersionRepository
    進行主要 Retrieval。

    保留 Fake Repository，
    確認 Dependency Injection 正常。
    """

    pass


# ==================================
# Fixture
# ==================================

def create_viewer():

    return ArchiveViewer(

        article_repository=(
            FakeArticleRepository()
        ),

        version_repository=(
            FakeVersionRepository()
        ),

        history_repository=(
            FakeHistoryRepository()
        )
    )


# ==================================
# Create
# ==================================

def test_create_archive_viewer():

    viewer = create_viewer()

    assert viewer is not None

    assert isinstance(
        viewer,
        ArchiveViewer
    )


# ==================================
# Get Article
# ==================================

def test_get_article():

    viewer = create_viewer()

    article = viewer.get_article(
        1
    )

    assert article is not None
    assert article.id == 1
    assert article.title == (
        "AutoSearch V4 Test Article"
    )


# ==================================
# Get Version
# ==================================

def test_get_version():

    viewer = create_viewer()

    version = viewer.get_version(
        1,
        2
    )

    assert version is not None
    assert version.id == 102
    assert version.version_number == 2
    assert version.content == (
        "Version 2 Content"
    )


# ==================================
# Get Version By ID
# ==================================

def test_get_version_by_id():

    viewer = create_viewer()

    version = viewer.get_version_by_id(
        103
    )

    assert version is not None
    assert version.id == 103
    assert version.version_number == 3


# ==================================
# Get Latest
# ==================================

def test_get_latest():

    viewer = create_viewer()

    view = viewer.get_latest(
        1
    )

    assert view is not None

    assert view.article_id == 1
    assert view.version_id == 103
    assert view.version_number == 3
    assert view.title == (
        "AutoSearch V4 Test Article"
    )
    assert view.content == (
        "Version 3 Content"
    )


# ==================================
# Get First
# ==================================

def test_get_first():

    viewer = create_viewer()

    view = viewer.get_first(
        1
    )

    assert view is not None

    assert view.article_id == 1
    assert view.version_id == 101
    assert view.version_number == 1
    assert view.content == (
        "Version 1 Content"
    )


# ==================================
# Get Specific View
# ==================================

def test_get_view():

    viewer = create_viewer()

    view = viewer.get_view(
        1,
        2
    )

    assert view is not None

    assert view.article_id == 1
    assert view.version_id == 102
    assert view.version_number == 2
    assert view.title == (
        "AutoSearch V4 Test Article"
    )
    assert view.content == (
        "Version 2 Content"
    )


# ==================================
# Get View By Version ID
# ==================================

def test_get_view_by_version_id():

    viewer = create_viewer()

    view = viewer.get_view_by_version_id(
        101
    )

    assert view is not None

    assert view.article_id == 1
    assert view.version_id == 101
    assert view.version_number == 1


# ==================================
# Get History
# ==================================

def test_get_history():

    viewer = create_viewer()

    history = viewer.get_history(
        1
    )

    assert len(history) == 3

    assert history[0].version_number == 1
    assert history[1].version_number == 2
    assert history[2].version_number == 3

    assert history[0].content == (
        "Version 1 Content"
    )

    assert history[2].content == (
        "Version 3 Content"
    )


# ==================================
# Get Timeline
# ==================================

def test_get_timeline():

    viewer = create_viewer()

    timeline = viewer.get_timeline(
        1
    )

    assert len(timeline) == 3

    assert timeline[0]["version_number"] == 1
    assert timeline[1]["version_number"] == 2
    assert timeline[2]["version_number"] == 3


# ==================================
# Get Historical Content
# ==================================

def test_get_content():

    viewer = create_viewer()

    content = viewer.get_content(
        1,
        2
    )

    assert content == (
        "Version 2 Content"
    )


# ==================================
# Get Latest Content
# ==================================

def test_get_latest_content():

    viewer = create_viewer()

    content = viewer.get_latest_content(
        1
    )

    assert content == (
        "Version 3 Content"
    )


# ==================================
# Get First Content
# ==================================

def test_get_first_content():

    viewer = create_viewer()

    content = viewer.get_first_content(
        1
    )

    assert content == (
        "Version 1 Content"
    )


# ==================================
# Has History
# ==================================

def test_has_history():

    viewer = create_viewer()

    assert viewer.has_history(
        1
    ) is True


def test_has_no_history():

    viewer = create_viewer()

    assert viewer.has_history(
        999
    ) is False


# ==================================
# Count Versions
# ==================================

def test_count_versions():

    viewer = create_viewer()

    count = viewer.count_versions(
        1
    )

    assert count == 3


def test_count_versions_empty():

    viewer = create_viewer()

    count = viewer.count_versions(
        999
    )

    assert count == 0


# ==================================
# Nonexistent Version
# ==================================

def test_get_nonexistent_version():

    viewer = create_viewer()

    view = viewer.get_view(
        1,
        999
    )

    assert view is None


# ==================================
# Nonexistent Article
# ==================================

def test_get_nonexistent_article():

    viewer = create_viewer()

    view = viewer.get_view(
        999,
        1
    )

    assert view is None


def test_get_latest_nonexistent_article():

    viewer = create_viewer()

    view = viewer.get_latest(
        999
    )

    assert view is None


# ==================================
# Dictionary Article
# ==================================

def test_dictionary_article():

    class DictionaryArticleRepository:

        def get_by_id(
            self,
            article_id
        ):

            return {
                "id": article_id,
                "title": "Dictionary Article"
            }

    viewer = ArchiveViewer(

        article_repository=(
            DictionaryArticleRepository()
        ),

        version_repository=(
            FakeVersionRepository()
        ),

        history_repository=(
            FakeHistoryRepository()
        )
    )

    view = viewer.get_view(
        1,
        1
    )

    assert view is not None

    assert view.article_id == 1
    assert view.title == (
        "Dictionary Article"
    )


# ==================================
# Dictionary Version
# ==================================

def test_dictionary_version():

    class DictionaryHistoryRepository:

        def get_version(
            self,
            article_id,
            version_number
        ):

            return {
                "id": 500,
                "article_id": article_id,
                "version_number": version_number,
                "content": "Dictionary Content"
            }

    viewer = ArchiveViewer(

        article_repository=(
            FakeArticleRepository()
        ),

        version_repository=(
            FakeVersionRepository()
        ),

        history_repository=(
            DictionaryHistoryRepository()
        )
    )

    view = viewer.get_view(
        1,
        5
    )

    assert view is not None

    assert view.version_id == 500
    assert view.version_number == 5
    assert view.content == (
        "Dictionary Content"
    )


# ==================================
# None Content
# ==================================

def test_none_content():

    class NoneContentHistoryRepository:

        def get_version(
            self,
            article_id,
            version_number
        ):

            return SimpleNamespace(
                id=600,
                article_id=article_id,
                version_number=version_number,
                content=None
            )

    viewer = ArchiveViewer(

        article_repository=(
            FakeArticleRepository()
        ),

        version_repository=(
            FakeVersionRepository()
        ),

        history_repository=(
            NoneContentHistoryRepository()
        )
    )

    view = viewer.get_view(
        1,
        1
    )

    assert view is not None
    assert view.content == ""


# ==================================
# Repr
# ==================================

def test_repr():

    viewer = create_viewer()

    result = repr(
        viewer
    )

    assert isinstance(
        result,
        str
    )

    assert "ArchiveViewer" in result