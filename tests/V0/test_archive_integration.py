"""
tests/test_archive_integration.py

AutoSearch V4

P2.3 Archive Integration Test

測試：

1. 建立 ArchiveIntegration
2. 新 Article 建立 Version 1
3. 已存在 Article + 相同內容
4. 已存在 Article + 新內容
5. Version Number 遞增
6. Article History
7. Version Timeline
8. Version Retrieval
9. Content Change Detection
10. Version Diff
11. Knowledge History
12. Knowledge Evolution
13. Archive Status
14. Empty Article
"""

from types import SimpleNamespace

from archive.archive_integration import (
    ArchiveIntegration
)


# ==================================
# Mock Repository
# ==================================

class MockArchiveRepository:

    def __init__(self):

        self.articles = {}

        self.versions = {}

    # ----------------------------------
    # Article
    # ----------------------------------

    def get_article(
        self,
        article_id
    ):

        return self.articles.get(
            article_id
        )

    # ----------------------------------
    # Latest
    # ----------------------------------

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

        return max(
            versions,
            key=lambda item: (
                item.version_number
            )
        )

    # ----------------------------------
    # Create Version
    # ----------------------------------

    def create_version(
        self,
        article_id,
        article,
        version_number
    ):

        content = getattr(
            article,
            "content",
            ""
        )

        version = SimpleNamespace(

            id=(
                article_id * 100
                + version_number
            ),

            article_id=article_id,

            version_number=version_number,

            content=content
        )

        self.versions.setdefault(
            article_id,
            []
        ).append(
            version
        )

        self.articles[
            article_id
        ] = article

        return version


# ==================================
# Mock Article History Repository
# ==================================

class MockArticleHistoryRepository:

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

        return self.archive_repository.versions.get(
            article_id,
            []
        )

    def get_latest(
        self,
        article_id
    ):

        versions = self.get_history(
            article_id
        )

        if not versions:

            return None

        return max(
            versions,
            key=lambda item: (
                item.version_number
            )
        )


# ==================================
# Mock Knowledge History Engine
# ==================================

class MockKnowledgeHistoryEngine:

    def __init__(self):

        self.history = {

            100: [

                SimpleNamespace(

                    article_id=100,

                    version_id=10001,

                    version_number=1,

                    summary="First knowledge",

                    category="Semiconductor",

                    keywords=[
                        "TSMC"
                    ],

                    importance=7,

                    confidence=0.8
                ),

                SimpleNamespace(

                    article_id=100,

                    version_id=10002,

                    version_number=2,

                    summary="Updated knowledge",

                    category="Semiconductor",

                    keywords=[
                        "TSMC",
                        "2nm"
                    ],

                    importance=9,

                    confidence=0.95
                )
            ]
        }

    def get_history(
        self,
        article_id
    ):

        return self.history.get(
            article_id,
            []
        )

    def get_knowledge_evolution(
        self,
        article_id
    ):

        history = self.get_history(
            article_id
        )

        return [

            {
                "article_id":
                    item.article_id,

                "version_id":
                    item.version_id,

                "version_number":
                    item.version_number,

                "summary":
                    item.summary,

                "category":
                    item.category,

                "keywords":
                    item.keywords,

                "importance":
                    item.importance,

                "confidence":
                    item.confidence
            }

            for item in history
        ]


# ==================================
# Fixture Helper
# ==================================

def create_engine():

    archive_repository = (
        MockArchiveRepository()
    )

    history_repository = (
        MockArticleHistoryRepository(
            archive_repository
        )
    )

    knowledge_engine = (
        MockKnowledgeHistoryEngine()
    )

    engine = ArchiveIntegration(

        archive_repository=(
            archive_repository
        ),

        article_history_repository=(
            history_repository
        ),

        knowledge_history_engine=(
            knowledge_engine
        )
    )

    return engine


# ==================================
# Article Helper
# ==================================

def create_article(
    content
):

    return SimpleNamespace(

        title="TSMC 2nm",

        url=(
            "https://example.com/"
            "tsmc-2nm"
        ),

        content=content
    )


# ==================================
# Tests
# ==================================

def test_create_archive_integration():

    engine = create_engine()

    assert isinstance(
        engine,
        ArchiveIntegration
    )


# ==================================
# New Article
# ==================================

def test_new_article_creates_version():

    engine = create_engine()

    article = create_article(
        "TSMC announces 2nm"
    )

    result = engine.process_article(

        article_id=100,

        article=article
    )

    assert result[
        "created"
    ] is True

    assert result[
        "changed"
    ] is True

    assert result[
        "version"
    ].version_number == 1


# ==================================
# Same Content
# ==================================

def test_same_content_does_not_create_version():

    engine = create_engine()

    article1 = create_article(
        "TSMC announces 2nm"
    )

    engine.process_article(
        100,
        article1
    )

    article2 = create_article(
        "TSMC announces 2nm"
    )

    result = engine.process_article(
        100,
        article2
    )

    assert result[
        "created"
    ] is False

    assert result[
        "changed"
    ] is False

    assert result[
        "version"
    ].version_number == 1


# ==================================
# Changed Content
# ==================================

def test_changed_content_creates_version():

    engine = create_engine()

    article1 = create_article(
        "TSMC announces 2nm"
    )

    engine.process_article(
        100,
        article1
    )

    article2 = create_article(
        "TSMC starts 2nm mass production"
    )

    result = engine.process_article(
        100,
        article2
    )

    assert result[
        "created"
    ] is True

    assert result[
        "changed"
    ] is True

    assert result[
        "version"
    ].version_number == 2


# ==================================
# Version Number
# ==================================

def test_version_number_increases():

    engine = create_engine()

    engine.process_article(
        100,
        create_article("Version 1")
    )

    engine.process_article(
        100,
        create_article("Version 2")
    )

    engine.process_article(
        100,
        create_article("Version 3")
    )

    timeline = engine.get_timeline(
        100
    )

    assert len(
        timeline
    ) == 3

    assert [
        item.version_number
        for item in timeline
    ] == [1, 2, 3]


# ==================================
# History
# ==================================

def test_get_history():

    engine = create_engine()

    engine.process_article(
        100,
        create_article("Version 1")
    )

    engine.process_article(
        100,
        create_article("Version 2")
    )

    history = engine.get_history(
        100
    )

    assert len(
        history
    ) == 2


# ==================================
# Timeline
# ==================================

def test_get_timeline():

    engine = create_engine()

    engine.process_article(
        100,
        create_article("Version 1")
    )

    engine.process_article(
        100,
        create_article("Version 2")
    )

    timeline = engine.get_timeline(
        100
    )

    assert (
        timeline[0]
        .version_number
        == 1
    )

    assert (
        timeline[1]
        .version_number
        == 2
    )


# ==================================
# Get Version
# ==================================

def test_get_version():

    engine = create_engine()

    engine.process_article(
        100,
        create_article("Version 1")
    )

    engine.process_article(
        100,
        create_article("Version 2")
    )

    version = engine.get_version(
        100,
        2
    )

    assert version is not None

    assert (
        version.version_number
        == 2
    )


# ==================================
# Nonexistent Version
# ==================================

def test_get_nonexistent_version():

    engine = create_engine()

    engine.process_article(
        100,
        create_article("Version 1")
    )

    assert engine.get_version(
        100,
        99
    ) is None


# ==================================
# Content Changed
# ==================================

def test_content_changed():

    assert ArchiveIntegration.content_changed(

        "old",

        "new"

    ) is True


def test_content_not_changed():

    assert ArchiveIntegration.content_changed(

        "same",

        "same"

    ) is False


def test_none_content():

    assert ArchiveIntegration.content_changed(

        None,

        ""

    ) is False


# ==================================
# Diff
# ==================================

def test_get_diff():

    engine = create_engine()

    diff = engine.get_diff(

        "TSMC 3nm",

        "TSMC 2nm",

        article_id=100,

        from_version=1,

        to_version=2
    )

    assert diff is not None

    assert diff.article_id == 100

    assert diff.from_version == 1

    assert diff.to_version == 2

    assert diff.has_changes is True


# ==================================
# Knowledge History
# ==================================

def test_get_knowledge_history():

    engine = create_engine()

    history = (
        engine.get_knowledge_history(
            100
        )
    )

    assert len(
        history
    ) == 2

    assert (
        history[0]
        .version_number
        == 1
    )


# ==================================
# Knowledge Evolution
# ==================================

def test_get_knowledge_evolution():

    engine = create_engine()

    evolution = (
        engine.get_knowledge_evolution(
            100
        )
    )

    assert len(
        evolution
    ) == 2

    assert (
        evolution[0][
            "version_number"
        ]
        == 1
    )

    assert (
        evolution[1][
            "importance"
        ]
        == 9
    )


# ==================================
# Archive Status
# ==================================

def test_get_status():

    engine = create_engine()

    engine.process_article(
        100,
        create_article("Version 1")
    )

    engine.process_article(
        100,
        create_article("Version 2")
    )

    status = engine.get_status(
        100
    )

    assert status[
        "article_id"
    ] == 100

    assert status[
        "has_history"
    ] is True

    assert status[
        "version_count"
    ] == 2

    assert status[
        "latest_version"
    ] == 2

    assert status[
        "knowledge_history_count"
    ] == 2


# ==================================
# Empty Article
# ==================================

def test_empty_article():

    engine = create_engine()

    assert engine.get_history(
        999
    ) == []

    assert engine.get_latest_version(
        999
    ) is None

    assert engine.get_timeline(
        999
    ) == []


# ==================================
# Repr
# ==================================

def test_repr():

    engine = create_engine()

    text = repr(
        engine
    )

    assert (
        "ArchiveIntegration"
        in text
    )