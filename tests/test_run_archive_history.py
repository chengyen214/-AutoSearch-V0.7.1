"""
tests/test_run_archive_history.py

AutoSearch V4

P2.3.9 Run Flow Archive Integration

測試：

    Run Flow
        ↓
    ArchiveIntegration
        ↓
    Article / URL
        ↓
    Archive Version
        ↓
    Content Comparison
        ↓
    History / Timeline / Diff
"""

from dataclasses import dataclass

from archive.archive_integration import (
    ArchiveIntegration
)


# ============================================================
# Fake Models
# ============================================================

@dataclass
class FakeArticle:

    url: str
    title: str
    content: str = ""


@dataclass
class FakeVersion:

    article_id: int
    version_number: int
    content: str
    url: str = ""


# ============================================================
# Fake Archive Repository
# ============================================================

class FakeArchiveRepository:

    def __init__(self):

        self.articles = {}

        self.versions = {}

        self.next_article_id = 1

    # --------------------------------------------------------
    # Article
    # --------------------------------------------------------

    def get_article(self, article_id):

        return self.articles.get(
            article_id
        )

    # --------------------------------------------------------
    # Latest Version
    # --------------------------------------------------------

    def get_latest(self, article_id):

        history = self.versions.get(
            article_id,
            []
        )

        if not history:

            return None

        return max(
            history,
            key=lambda item:
            item.version_number
        )

    # --------------------------------------------------------
    # Create Version
    # --------------------------------------------------------

    def create_version(
        self,
        article_id,
        article,
        version_number
    ):

        if article_id not in self.articles:

            self.articles[article_id] = article

        version = FakeVersion(

            article_id=article_id,

            version_number=version_number,

            content=(
                getattr(
                    article,
                    "content",
                    ""
                )
            ),

            url=(
                getattr(
                    article,
                    "url",
                    ""
                )
            )
        )

        self.versions.setdefault(
            article_id,
            []
        ).append(
            version
        )

        return version


# ============================================================
# Fake Article History Repository
# ============================================================

class FakeArticleHistoryRepository:

    def __init__(
        self,
        archive_repository
    ):

        self.archive_repository = (
            archive_repository
        )

    def get_history(
        self,
        article_id
    ):

        return list(
            self.archive_repository.versions.get(
                article_id,
                []
            )
        )

    def get_by_article_id(
        self,
        article_id
    ):

        return self.get_history(
            article_id
        )

    def get_latest(
        self,
        article_id
    ):

        history = self.get_history(
            article_id
        )

        if not history:

            return None

        return max(
            history,
            key=lambda item:
            item.version_number
        )


# ============================================================
# Fake Knowledge History Engine
# ============================================================

class FakeKnowledgeHistoryEngine:

    def __init__(self):

        self.history = {}

    def get_history(
        self,
        article_id
    ):

        return list(
            self.history.get(
                article_id,
                []
            )
        )

    def get_knowledge_evolution(
        self,
        article_id
    ):

        history = self.get_history(
            article_id
        )

        return [

            item.to_dict()

            if hasattr(
                item,
                "to_dict"
            )

            else item

            for item in history
        ]


# ============================================================
# Test Fixture Helper
# ============================================================

class RunArchiveHistoryTest:

    def __init__(self):

        self.archive_repository = (
            FakeArchiveRepository()
        )

        self.history_repository = (
            FakeArticleHistoryRepository(
                self.archive_repository
            )
        )

        self.knowledge_engine = (
            FakeKnowledgeHistoryEngine()
        )

        self.integration = (
            ArchiveIntegration(

                archive_repository=(
                    self.archive_repository
                ),

                article_history_repository=(
                    self.history_repository
                ),

                knowledge_history_engine=(
                    self.knowledge_engine
                )
            )
        )


def create_engine():

    return RunArchiveHistoryTest()


# ============================================================
# Tests
# ============================================================

def test_first_run_creates_version():

    test = create_engine()

    article = FakeArticle(

        url="https://example.com/tsmc",

        title="TSMC 3nm",

        content="TSMC 3nm production"
    )

    result = test.integration.process_article(

        article_id=100,

        article=article
    )

    assert result["article_id"] == 100

    assert result["created"] is True

    assert result["changed"] is True

    assert result["version"] is not None

    assert (
        result["version"].version_number
        == 1
    )


def test_same_url_same_content_no_new_version():

    test = create_engine()

    article = FakeArticle(

        url="https://example.com/tsmc",

        title="TSMC 3nm",

        content="TSMC 3nm production"
    )

    test.integration.process_article(
        100,
        article
    )

    result = test.integration.process_article(
        100,
        article
    )

    assert result["created"] is False

    assert result["changed"] is False

    assert (
        result["version"].version_number
        == 1
    )


def test_same_url_changed_content_creates_version():

    test = create_engine()

    article_v1 = FakeArticle(

        url="https://example.com/tsmc",

        title="TSMC 3nm",

        content="TSMC 3nm production"
    )

    article_v2 = FakeArticle(

        url="https://example.com/tsmc",

        title="TSMC 2nm",

        content="TSMC 2nm production"
    )

    test.integration.process_article(
        100,
        article_v1
    )

    result = test.integration.process_article(
        100,
        article_v2
    )

    assert result["created"] is True

    assert result["changed"] is True

    assert (
        result["version"].version_number
        == 2
    )


def test_version_number_increases():

    test = create_engine()

    for content in [

        "Version 1",

        "Version 2",

        "Version 3"

    ]:

        article = FakeArticle(

            url="https://example.com/a",

            title="Article",

            content=content
        )

        test.integration.process_article(
            100,
            article
        )

    history = (
        test.integration.get_history(
            100
        )
    )

    assert len(history) == 3

    assert [
        item.version_number
        for item in history
    ] == [1, 2, 3]


def test_history_after_multiple_runs():

    test = create_engine()

    contents = [

        "first",

        "second",

        "third"

    ]

    for content in contents:

        article = FakeArticle(

            url="https://example.com/a",

            title="Article",

            content=content
        )

        test.integration.process_article(
            100,
            article
        )

    history = (
        test.integration.get_history(
            100
        )
    )

    assert len(history) == 3

    assert history[0].content == "first"

    assert history[1].content == "second"

    assert history[2].content == "third"


def test_history_unchanged_content():

    test = create_engine()

    article = FakeArticle(

        url="https://example.com/a",

        title="Article",

        content="same"
    )

    for _ in range(3):

        test.integration.process_article(
            100,
            article
        )

    history = (
        test.integration.get_history(
            100
        )
    )

    assert len(history) == 1


def test_content_change_creates_diff():

    test = create_engine()

    article_v1 = FakeArticle(

        url="https://example.com/a",

        title="Article",

        content="TSMC 3nm production"
    )

    article_v2 = FakeArticle(

        url="https://example.com/a",

        title="Article",

        content="TSMC 2nm production"
    )

    test.integration.process_article(
        100,
        article_v1
    )

    test.integration.process_article(
        100,
        article_v2
    )

    history = (
        test.integration.get_history(
            100
        )
    )

    diff = test.integration.get_diff(

        history[0].content,

        history[1].content,

        article_id=100,

        from_version=1,

        to_version=2
    )

    assert diff is not None

    assert diff.article_id == 100

    assert diff.from_version == 1

    assert diff.to_version == 2


def test_timeline():

    test = create_engine()

    for content in [

        "v1",

        "v2",

        "v3"

    ]:

        article = FakeArticle(

            url="https://example.com/a",

            title="Article",

            content=content
        )

        test.integration.process_article(
            100,
            article
        )

    timeline = (
        test.integration.get_timeline(
            100
        )
    )

    assert [
        item.version_number
        for item in timeline
    ] == [1, 2, 3]


def test_archive_status():

    test = create_engine()

    article = FakeArticle(

        url="https://example.com/a",

        title="Article",

        content="content"
    )

    test.integration.process_article(
        100,
        article
    )

    status = (
        test.integration.get_status(
            100
        )
    )

    assert status["article_id"] == 100

    assert status["has_history"] is True

    assert status["version_count"] == 1

    assert status["latest_version"] == 1

    assert (
        status["knowledge_history_count"]
        == 0
    )


def test_none_content():

    test = create_engine()

    article = FakeArticle(

        url="https://example.com/a",

        title="Article",

        content=None
    )

    result = (
        test.integration.process_article(
            100,
            article
        )
    )

    assert result["created"] is True

    assert result["changed"] is True


def test_empty_content():

    test = create_engine()

    article = FakeArticle(

        url="https://example.com/a",

        title="Article",

        content=""
    )

    result = (
        test.integration.process_article(
            100,
            article
        )
    )

    assert result["created"] is True

    assert result["changed"] is True


def test_different_urls_create_different_articles():

    test = create_engine()

    article_1 = FakeArticle(

        url="https://example.com/a",

        title="Article A",

        content="content A"
    )

    article_2 = FakeArticle(

        url="https://example.com/b",

        title="Article B",

        content="content B"
    )

    result_1 = (
        test.integration.process_article(
            100,
            article_1
        )
    )

    result_2 = (
        test.integration.process_article(
            101,
            article_2
        )
    )

    assert result_1["created"] is True

    assert result_2["created"] is True

    assert (
        result_1["version"].article_id
        != result_2["version"].article_id
    )

    assert (
        len(
            test.integration.get_history(
                100
            )
        )
        == 1
    )

    assert (
        len(
            test.integration.get_history(
                101
            )
        )
        == 1
    )