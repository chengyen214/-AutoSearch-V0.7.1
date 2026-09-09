"""
tests/test_knowledge_history_engine.py

AutoSearch V4

P2.3.8 Knowledge History Engine

測試:

    1. 建立 Engine
    2. get_history
    3. get_latest
    4. get_first
    5. get_version
    6. get_timeline
    7. get_changes
    8. get_categories
    9. get_keywords
    10. get_importance_history
    11. get_confidence_history
    12. has_history
    13. count
    14. get_knowledge_evolution
    15. 不存在 Article
    16. repr
"""

from models.knowledge_history import (
    KnowledgeHistory
)

from archive.knowledge_history import (
    KnowledgeHistoryEngine
)


# ==================================
# Fake Repository
# ==================================

class FakeKnowledgeRepository:

    """
    測試用 Knowledge Repository。
    """

    def __init__(self):

        self.data = {

            100: [

                KnowledgeHistory(

                    article_id=100,

                    version_id=1001,

                    version_number=1,

                    summary="台積電推出新製程",

                    category="Semiconductor",

                    keywords=[
                        "台積電",
                        "製程"
                    ],

                    importance=7,

                    confidence=0.80
                ),

                KnowledgeHistory(

                    article_id=100,

                    version_id=1002,

                    version_number=2,

                    summary="台積電推出2nm新製程",

                    category="Semiconductor",

                    keywords=[
                        "台積電",
                        "2nm",
                        "製程"
                    ],

                    importance=8,

                    confidence=0.90
                ),

                KnowledgeHistory(

                    article_id=100,

                    version_id=1003,

                    version_number=3,

                    summary="台積電2nm進入量產",

                    category="Advanced Process",

                    keywords=[
                        "台積電",
                        "2nm",
                        "量產"
                    ],

                    importance=9,

                    confidence=0.95
                )
            ]
        }

    # ==================================
    # Get History
    # ==================================

    def get_history(
        self,
        article_id
    ):

        return self.data.get(
            article_id,
            []
        )


# ==================================
# Fixture
# ==================================

def create_engine():

    repository = (
        FakeKnowledgeRepository()
    )

    return KnowledgeHistoryEngine(
        knowledge_repository=repository
    )


# ==================================
# Create
# ==================================

def test_create_engine():

    engine = create_engine()

    assert (
        isinstance(
            engine,
            KnowledgeHistoryEngine
        )
    )

    assert (
        engine.knowledge_repository
        is not None
    )


# ==================================
# Get History
# ==================================

def test_get_history():

    engine = create_engine()

    history = engine.get_history(
        100
    )

    assert len(history) == 3

    assert (
        history[0].version_number
        == 1
    )

    assert (
        history[2].version_number
        == 3
    )


# ==================================
# Get Latest
# ==================================

def test_get_latest():

    engine = create_engine()

    latest = engine.get_latest(
        100
    )

    assert latest is not None

    assert (
        latest.version_number
        == 3
    )

    assert (
        latest.importance
        == 9
    )


# ==================================
# Get First
# ==================================

def test_get_first():

    engine = create_engine()

    first = engine.get_first(
        100
    )

    assert first is not None

    assert (
        first.version_number
        == 1
    )

    assert (
        first.importance
        == 7
    )


# ==================================
# Get Version
# ==================================

def test_get_version():

    engine = create_engine()

    version = engine.get_version(
        100,
        2
    )

    assert version is not None

    assert (
        version.version_id
        == 1002
    )

    assert (
        version.version_number
        == 2
    )


# ==================================
# Get Nonexistent Version
# ==================================

def test_get_nonexistent_version():

    engine = create_engine()

    version = engine.get_version(
        100,
        99
    )

    assert version is None


# ==================================
# Get Timeline
# ==================================

def test_get_timeline():

    engine = create_engine()

    timeline = engine.get_timeline(
        100
    )

    assert len(timeline) == 3

    assert [
        item.version_number
        for item in timeline
    ] == [
        1,
        2,
        3
    ]


# ==================================
# Get Changes
# ==================================

def test_get_changes():

    engine = create_engine()

    old = engine.get_version(
        100,
        1
    )

    new = engine.get_version(
        100,
        2
    )

    changes = engine.get_changes(
        old,
        new
    )

    assert (
        changes["summary_changed"]
        is True
    )

    assert (
        changes["category_changed"]
        is False
    )

    assert (
        "2nm"
        in changes["keywords_added"]
    )

    assert (
        "importance_changed"
        in changes
    )

    assert (
        changes["importance_changed"]
        is True
    )

    assert (
        changes["confidence_changed"]
        is True
    )


# ==================================
# Get Categories
# ==================================

def test_get_categories():

    engine = create_engine()

    categories = engine.get_categories(
        100
    )

    assert len(categories) == 3

    assert (
        categories[0]["category"]
        == "Semiconductor"
    )

    assert (
        categories[2]["category"]
        == "Advanced Process"
    )


# ==================================
# Get Keywords
# ==================================

def test_get_keywords():

    engine = create_engine()

    keywords = engine.get_keywords(
        100
    )

    assert len(keywords) == 3

    assert (
        keywords[0]["keywords"]
        == [
            "台積電",
            "製程"
        ]
    )

    assert (
        "量產"
        in keywords[2]["keywords"]
    )


# ==================================
# Get Importance History
# ==================================

def test_get_importance_history():

    engine = create_engine()

    history = (
        engine.get_importance_history(
            100
        )
    )

    assert history == [

        {
            "version_number": 1,
            "importance": 7
        },

        {
            "version_number": 2,
            "importance": 8
        },

        {
            "version_number": 3,
            "importance": 9
        }
    ]


# ==================================
# Get Confidence History
# ==================================

def test_get_confidence_history():

    engine = create_engine()

    history = (
        engine.get_confidence_history(
            100
        )
    )

    assert history == [

        {
            "version_number": 1,
            "confidence": 0.80
        },

        {
            "version_number": 2,
            "confidence": 0.90
        },

        {
            "version_number": 3,
            "confidence": 0.95
        }
    ]


# ==================================
# Has History
# ==================================

def test_has_history():

    engine = create_engine()

    assert (
        engine.has_history(100)
        is True
    )


def test_has_no_history():

    engine = create_engine()

    assert (
        engine.has_history(999)
        is False
    )


# ==================================
# Count
# ==================================

def test_count():

    engine = create_engine()

    assert (
        engine.count(100)
        == 3
    )


def test_count_empty():

    engine = create_engine()

    assert (
        engine.count(999)
        == 0
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

    assert len(evolution) == 3

    assert (
        evolution[0]["version_number"]
        == 1
    )

    assert (
        evolution[1]["importance"]
        == 8
    )

    assert (
        evolution[2]["confidence"]
        == 0.95
    )

    assert (
        evolution[2]["category"]
        == "Advanced Process"
    )


# ==================================
# Empty Article
# ==================================

def test_empty_article():

    engine = create_engine()

    history = engine.get_history(
        999
    )

    assert history == []

    assert (
        engine.get_latest(999)
        is None
    )

    assert (
        engine.get_first(999)
        is None
    )

    assert (
        engine.get_version(999, 1)
        is None
    )

    assert (
        engine.get_timeline(999)
        == []
    )


# ==================================
# Empty Changes
# ==================================

def test_empty_changes():

    engine = create_engine()

    changes = engine.get_changes(
        None,
        None
    )

    assert (
        changes["summary_changed"]
        is False
    )

    assert (
        changes["category_changed"]
        is False
    )

    assert (
        changes["keywords_added"]
        == []
    )

    assert (
        changes["keywords_removed"]
        == []
    )


# ==================================
# Repr
# ==================================

def test_repr():

    engine = create_engine()

    result = repr(
        engine
    )

    assert (
        "KnowledgeHistoryEngine"
        in result
    )