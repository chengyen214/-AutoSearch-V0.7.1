"""
tests/V7_6/test_metadata.py

AutoSearch V7

RAG-6.3

Metadata Handling Functional Test
"""

from rag.context.metadata import (
    SOURCE_METADATA_FIELDS,
    AI_METADATA_FIELDS,
    MetadataHandler,
)


# ============================================================
# Test 1
# ============================================================

def test_metadata_handler_basic():
    handler = MetadataHandler()

    metadata = {
        "title": "台灣半導體產業分析",
        "url": "https://example.com/article/101",
        "source": "Google News",
        "crawl_time": "2026-08-20",

        "ai_summary": "台灣半導體產業持續成長。",
        "ai_category": "Semiconductor",
        "ai_keywords": [
            "TSMC",
            "AI",
            "Semiconductor",
        ],
        "ai_importance": 5,
        "ai_confidence": 0.92,
    }

    result = handler.handle(metadata)

    assert isinstance(result, dict)

    assert "source" in result
    assert "ai" in result


# ============================================================
# Test 2
# ============================================================

def test_source_metadata():
    handler = MetadataHandler()

    metadata = {
        "title": "台灣半導體產業分析",
        "url": "https://example.com/article/101",
        "source": "Google News",
        "crawl_time": "2026-08-20",
    }

    result = handler.get_source_metadata(
        metadata
    )

    assert result["title"] == (
        "台灣半導體產業分析"
    )

    assert result["url"] == (
        "https://example.com/article/101"
    )

    assert result["source"] == (
        "Google News"
    )

    assert result["crawl_time"] == (
        "2026-08-20"
    )


# ============================================================
# Test 3
# ============================================================

def test_ai_metadata():
    handler = MetadataHandler()

    metadata = {
        "ai_summary": "台灣半導體產業持續成長。",
        "ai_category": "Semiconductor",
        "ai_keywords": [
            "TSMC",
            "AI",
        ],
        "ai_importance": 5,
        "ai_confidence": 0.92,
    }

    result = handler.get_ai_metadata(
        metadata
    )

    assert result["ai_summary"] == (
        "台灣半導體產業持續成長。"
    )

    assert result["ai_category"] == (
        "Semiconductor"
    )

    assert result["ai_keywords"] == [
        "TSMC",
        "AI",
    ]

    assert result["ai_importance"] == 5

    assert result["ai_confidence"] == 0.92


# ============================================================
# Test 4
# ============================================================

def test_metadata_missing_fields():
    handler = MetadataHandler()

    metadata = {
        "title": "只有標題",
    }

    result = handler.handle(metadata)

    for field in SOURCE_METADATA_FIELDS:
        if field == "title":
            assert result["source"][field] == (
                "只有標題"
            )
        else:
            assert result["source"][field] is None

    for field in AI_METADATA_FIELDS:
        assert result["ai"][field] is None


# ============================================================
# Test 5
# ============================================================

def test_metadata_none():
    handler = MetadataHandler()

    result = handler.handle(None)

    assert isinstance(result, dict)

    assert "source" in result
    assert "ai" in result

    for field in SOURCE_METADATA_FIELDS:
        assert result["source"][field] is None

    for field in AI_METADATA_FIELDS:
        assert result["ai"][field] is None


# ============================================================
# Test 6
# ============================================================

def test_metadata_does_not_modify_original():
    handler = MetadataHandler()

    metadata = {
        "title": "Original Title",
        "url": "https://example.com",
        "custom_field": "should remain",
    }

    original = dict(metadata)

    handler.handle(metadata)

    assert metadata == original

    assert metadata["custom_field"] == (
        "should remain"
    )


# ============================================================
# Test 7
# ============================================================

def test_metadata_custom_fields_are_not_promoted():
    handler = MetadataHandler()

    metadata = {
        "title": "Test Article",
        "url": "https://example.com",
        "unknown_field": "test value",
    }

    result = handler.handle(metadata)

    assert "unknown_field" not in (
        result["source"]
    )

    assert "unknown_field" not in (
        result["ai"]
    )


# ============================================================
# Test 8
# ============================================================

def test_metadata_invalid_type():
    handler = MetadataHandler()

    invalid_metadata = [
        "invalid",
        123,
        [],
    ]

    for metadata in invalid_metadata:
        try:
            handler.handle(metadata)
        except TypeError:
            pass
        else:
            raise AssertionError(
                "Expected TypeError for invalid metadata type."
            )


# ============================================================
# Main
# ============================================================

def main():
    print("=" * 60)
    print("RAG-6.3 Metadata Handling Functional Test")
    print("=" * 60)

    test_metadata_handler_basic()
    print("[PASS] Basic Metadata Handling")

    test_source_metadata()
    print("[PASS] Source Metadata")

    test_ai_metadata()
    print("[PASS] AI Metadata")

    test_metadata_missing_fields()
    print("[PASS] Missing Metadata Fields")

    test_metadata_none()
    print("[PASS] None Metadata")

    test_metadata_does_not_modify_original()
    print("[PASS] Original Metadata Preservation")

    test_metadata_custom_fields_are_not_promoted()
    print("[PASS] Unknown Metadata Fields")

    test_metadata_invalid_type()
    print("[PASS] Invalid Metadata Type")

    print()
    print("RAG-6.3 METADATA HANDLING TEST PASSED")


if __name__ == "__main__":
    main()