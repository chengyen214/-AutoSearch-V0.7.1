"""
tests/test_knowledge_history.py

AutoSearch V4

P2.3.8 Knowledge History

測試：

1. 建立 KnowledgeHistory
2. 預設值
3. Knowledge 判斷
4. Summary 判斷
5. Category 判斷
6. Keywords 判斷
7. Keyword Count
8. Knowledge Score
9. Summary Text
10. To Dict
11. None Values
12. Keywords Copy
13. Repr
"""

from models.knowledge_history import (
    KnowledgeHistory
)


# ==================================
# Import
# ==================================

def test_knowledge_history_import():

    assert KnowledgeHistory is not None


# ==================================
# Create
# ==================================

def test_create_knowledge_history():

    history = KnowledgeHistory(

        article_id=100,

        version_id=10,

        version_number=3,

        summary="台積電2nm製程進入量產",

        category="Semiconductor",

        keywords=[
            "2nm",
            "台積電",
            "先進製程"
        ],

        importance=9,

        confidence=0.95
    )

    assert history.article_id == 100

    assert history.version_id == 10

    assert history.version_number == 3

    assert (
        history.summary
        == "台積電2nm製程進入量產"
    )

    assert (
        history.category
        == "Semiconductor"
    )

    assert history.keywords == [
        "2nm",
        "台積電",
        "先進製程"
    ]

    assert history.importance == 9

    assert history.confidence == 0.95


# ==================================
# Default Values
# ==================================

def test_default_values():

    history = KnowledgeHistory()

    assert history.article_id is None

    assert history.version_id is None

    assert history.version_number is None

    assert history.summary == ""

    assert history.category == ""

    assert history.keywords == []

    assert history.importance == 0

    assert history.confidence == 0.0

    assert history.analyze_time is None


# ==================================
# Has Knowledge
# ==================================

def test_has_knowledge():

    history = KnowledgeHistory(

        summary="Knowledge summary"
    )

    assert (
        history.has_knowledge()
        is True
    )


def test_has_no_knowledge():

    history = KnowledgeHistory()

    assert (
        history.has_knowledge()
        is False
    )


# ==================================
# Has Summary
# ==================================

def test_has_summary():

    history = KnowledgeHistory(

        summary="AI semiconductor"
    )

    assert (
        history.has_summary()
        is True
    )


def test_has_no_summary():

    history = KnowledgeHistory()

    assert (
        history.has_summary()
        is False
    )


# ==================================
# Has Category
# ==================================

def test_has_category():

    history = KnowledgeHistory(

        category="Semiconductor"
    )

    assert (
        history.has_category()
        is True
    )


def test_has_no_category():

    history = KnowledgeHistory()

    assert (
        history.has_category()
        is False
    )


# ==================================
# Has Keywords
# ==================================

def test_has_keywords():

    history = KnowledgeHistory(

        keywords=[
            "AI",
            "GPU"
        ]
    )

    assert (
        history.has_keywords()
        is True
    )


def test_has_no_keywords():

    history = KnowledgeHistory()

    assert (
        history.has_keywords()
        is False
    )


# ==================================
# Keyword Count
# ==================================

def test_keyword_count():

    history = KnowledgeHistory(

        keywords=[
            "AI",
            "GPU",
            "HBM"
        ]
    )

    assert (
        history.keyword_count()
        == 3
    )


def test_empty_keyword_count():

    history = KnowledgeHistory()

    assert (
        history.keyword_count()
        == 0
    )


# ==================================
# Knowledge Score
# ==================================

def test_knowledge_score():

    history = KnowledgeHistory(

        importance=8,

        confidence=0.75
    )

    assert (
        history.knowledge_score()
        == 6.0
    )


def test_zero_knowledge_score():

    history = KnowledgeHistory()

    assert (
        history.knowledge_score()
        == 0
    )


# ==================================
# Summary Text
# ==================================

def test_summary_text():

    history = KnowledgeHistory(

        summary="Historical knowledge"
    )

    assert (
        history.summary_text()
        == "Historical knowledge"
    )


def test_empty_summary_text():

    history = KnowledgeHistory()

    assert (
        history.summary_text()
        == ""
    )


# ==================================
# None Values
# ==================================

def test_none_values():

    history = KnowledgeHistory(

        summary=None,

        category=None,

        keywords=None,

        importance=None,

        confidence=None
    )

    assert history.summary == ""

    assert history.category == ""

    assert history.keywords == []

    assert history.importance == 0

    assert history.confidence == 0.0


# ==================================
# Keywords Copy
# ==================================

def test_keywords_are_copied():

    keywords = [
        "AI",
        "GPU"
    ]

    history = KnowledgeHistory(

        keywords=keywords
    )

    keywords.append(
        "HBM"
    )

    assert history.keywords == [
        "AI",
        "GPU"
    ]


# ==================================
# To Dict
# ==================================

def test_to_dict():

    history = KnowledgeHistory(

        article_id=100,

        version_id=20,

        version_number=2,

        summary="Knowledge summary",

        category="Semiconductor",

        keywords=[
            "2nm",
            "CoWoS"
        ],

        importance=9,

        confidence=0.9,

        analyze_time="2026-08-08 12:00:00"
    )

    result = history.to_dict()

    assert result["article_id"] == 100

    assert result["version_id"] == 20

    assert result["version_number"] == 2

    assert (
        result["summary"]
        == "Knowledge summary"
    )

    assert (
        result["category"]
        == "Semiconductor"
    )

    assert result["keywords"] == [
        "2nm",
        "CoWoS"
    ]

    assert result["importance"] == 9

    assert result["confidence"] == 0.9

    assert (
        result["analyze_time"]
        == "2026-08-08 12:00:00"
    )


# ==================================
# Repr
# ==================================

def test_repr():

    history = KnowledgeHistory(

        article_id=100,

        version_id=20,

        version_number=2,

        category="Semiconductor",

        importance=9,

        confidence=0.9
    )

    result = repr(
        history
    )

    assert (
        "KnowledgeHistory"
        in result
    )

    assert (
        "article_id=100"
        in result
    )

    assert (
        "version_id=20"
        in result
    )

    assert (
        "version_number=2"
        in result
    )

    assert (
        "Semiconductor"
        in result
    )

    assert (
        "importance=9"
        in result
    )

    assert (
        "confidence=0.9"
        in result
    )