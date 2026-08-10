"""
tests/test_historical_search_result.py

AutoSearch V4

P2.3.7 Historical Search

測試:

    HistoricalSearchResult Model
"""

from models.historical_search_result import (
    HistoricalSearchResult
)


# ==================================
# Create
# ==================================

def test_create_historical_search_result():

    result = HistoricalSearchResult(

        article_id=100,

        version_id=200,

        version_number=3,

        keyword="2nm",

        matched_content=(
            "台積電推出2nm新製程"
        ),

        match_position=15
    )

    assert result.article_id == 100

    assert result.version_id == 200

    assert result.version_number == 3

    assert result.keyword == "2nm"

    assert (
        result.matched_content
        == "台積電推出2nm新製程"
    )

    assert result.match_position == 15


# ==================================
# Default Values
# ==================================

def test_default_values():

    result = HistoricalSearchResult()

    assert result.article_id is None

    assert result.version_id is None

    assert result.version_number is None

    assert result.keyword == ""

    assert result.matched_content == ""

    assert result.match_position is None

    assert result.created_time is not None


# ==================================
# Has Match
# ==================================

def test_has_match():

    result = HistoricalSearchResult(

        keyword="2nm",

        matched_content=(
            "台積電推出2nm新製程"
        )
    )

    assert result.has_match() is True


# ==================================
# Has No Match
# ==================================

def test_has_no_match():

    result = HistoricalSearchResult()

    assert result.has_match() is False


# ==================================
# None Content
# ==================================

def test_none_content():

    result = HistoricalSearchResult(

        matched_content=None
    )

    assert result.matched_content == ""

    assert result.has_match() is False


# ==================================
# Content Length
# ==================================

def test_content_length():

    content = "AutoSearch V4"

    result = HistoricalSearchResult(

        matched_content=content
    )

    assert (
        result.content_length()
        == len(content)
    )


# ==================================
# Empty Content Length
# ==================================

def test_empty_content_length():

    result = HistoricalSearchResult()

    assert result.content_length() == 0


# ==================================
# Version Info
# ==================================

def test_version_info():

    result = HistoricalSearchResult(

        version_id=500,

        version_number=7
    )

    info = result.version_info()

    assert info["version_id"] == 500

    assert info["version_number"] == 7


# ==================================
# Summary
# ==================================

def test_summary():

    result = HistoricalSearchResult(

        article_id=100,

        version_id=200,

        version_number=3,

        keyword="2nm",

        matched_content=(
            "台積電推出2nm新製程"
        ),

        match_position=15
    )

    summary = result.summary()

    assert summary["article_id"] == 100

    assert summary["version_id"] == 200

    assert summary["version_number"] == 3

    assert summary["keyword"] == "2nm"

    assert (
        summary["matched_content"]
        == "台積電推出2nm新製程"
    )

    assert summary["match_position"] == 15


# ==================================
# To Dict
# ==================================

def test_to_dict():

    result = HistoricalSearchResult(

        article_id=100,

        version_id=200,

        version_number=3,

        keyword="2nm",

        matched_content=(
            "台積電推出2nm新製程"
        ),

        match_position=15
    )

    data = result.to_dict()

    assert data["article_id"] == 100

    assert data["version_id"] == 200

    assert data["version_number"] == 3

    assert data["keyword"] == "2nm"

    assert (
        data["matched_content"]
        == "台積電推出2nm新製程"
    )

    assert data["match_position"] == 15

    assert data["created_time"] is not None


# ==================================
# Repr
# ==================================

def test_repr():

    result = HistoricalSearchResult(

        article_id=100,

        version_id=200,

        version_number=3,

        keyword="2nm"
    )

    text = repr(result)

    assert (
        "HistoricalSearchResult"
        in text
    )

    assert "article_id=100" in text

    assert "version_id=200" in text

    assert "version_number=3" in text

    assert "keyword='2nm'" in text