"""
tests/V7_6/test_context_validation.py

AutoSearch V7

RAG-6.5

Context Validation Functional Test
"""

from rag.context.validation import (
    ContextValidator,
)


# ============================================================
# Test Data
# ============================================================

def create_valid_context():
    return {
        "entries": [
            {
                "source_index": 1,
                "document_id": "doc-A",
                "chunk_index": 0,
                "title": "Document A",
                "url": "https://example.com/a",
                "content": "This is document A.",
            },
            {
                "source_index": 2,
                "document_id": "doc-B",
                "chunk_index": 1,
                "title": "Document B",
                "url": "https://example.com/b",
                "content": "This is document B.",
            },
        ],
        "context_text": (
            "[Source 1]\n"
            "Title: Document A\n"
            "URL: https://example.com/a\n"
            "Content:\n"
            "This is document A.\n\n"
            "[Source 2]\n"
            "Title: Document B\n"
            "URL: https://example.com/b\n"
            "Content:\n"
            "This is document B."
        ),
        "count": 2,
    }


# ============================================================
# Functional Tests
# ============================================================

def test_valid_context():
    validator = ContextValidator()

    context = create_valid_context()

    assert validator.validate(context) is True

    print("[PASS] Valid Context")


def test_missing_context_field():
    validator = ContextValidator()

    context = create_valid_context()

    del context["entries"]

    try:
        validator.validate(context)
    except ValueError:
        print("[PASS] Missing Context Field")
        return

    raise AssertionError(
        "Missing context field should raise ValueError."
    )


def test_invalid_entries_type():
    validator = ContextValidator()

    context = create_valid_context()

    context["entries"] = "invalid"

    try:
        validator.validate(context)
    except TypeError:
        print("[PASS] Invalid Entries Type")
        return

    raise AssertionError(
        "Invalid entries type should raise TypeError."
    )


def test_missing_entry_field():
    validator = ContextValidator()

    context = create_valid_context()

    del context["entries"][0]["content"]

    try:
        validator.validate(context)
    except ValueError:
        print("[PASS] Missing Entry Field")
        return

    raise AssertionError(
        "Missing entry field should raise ValueError."
    )


def test_source_index_order():
    validator = ContextValidator()

    context = create_valid_context()

    context["entries"][1]["source_index"] = 3

    try:
        validator.validate(context)
    except ValueError:
        print("[PASS] Source Index Ordering")
        return

    raise AssertionError(
        "Invalid source_index ordering should raise ValueError."
    )


def test_count_matches_entries():
    validator = ContextValidator()

    context = create_valid_context()

    context["count"] = 1

    try:
        validator.validate(context)
    except ValueError:
        print("[PASS] Count Validation")
        return

    raise AssertionError(
        "Invalid count should raise ValueError."
    )


def test_negative_count():
    validator = ContextValidator()

    context = create_valid_context()

    context["count"] = -1

    try:
        validator.validate(context)
    except ValueError:
        print("[PASS] Negative Count Validation")
        return

    raise AssertionError(
        "Negative count should raise ValueError."
    )


def test_invalid_content_type():
    validator = ContextValidator()

    context = create_valid_context()

    context["entries"][0]["content"] = 123

    try:
        validator.validate(context)
    except TypeError:
        print("[PASS] Invalid Entry Content Type")
        return

    raise AssertionError(
        "Invalid entry content type should raise TypeError."
    )


def test_invalid_context_text_type():
    validator = ContextValidator()

    context = create_valid_context()

    context["context_text"] = 123

    try:
        validator.validate(context)
    except TypeError:
        print("[PASS] Invalid Context Text Type")
        return

    raise AssertionError(
        "Invalid context_text type should raise TypeError."
    )


def test_context_text_length():
    validator = ContextValidator(
        max_context_characters=10
    )

    context = create_valid_context()

    context["context_text"] = (
        "This context is longer than ten characters."
    )

    try:
        validator.validate(context)
    except ValueError:
        print("[PASS] Context Text Length Validation")
        return

    raise AssertionError(
        "Oversized context_text should raise ValueError."
    )


def test_none_context():
    validator = ContextValidator()

    try:
        validator.validate(None)
    except TypeError:
        print("[PASS] None Context Validation")
        return

    raise AssertionError(
        "None context should raise TypeError."
    )


def test_original_context_unchanged():
    validator = ContextValidator()

    context = create_valid_context()

    original_entries = [
        dict(entry)
        for entry in context["entries"]
    ]

    original_context_text = context["context_text"]
    original_count = context["count"]

    validator.validate(context)

    assert context["entries"] == original_entries
    assert context["context_text"] == original_context_text
    assert context["count"] == original_count

    print("[PASS] Original Context Unchanged")


# ============================================================
# Main
# ============================================================

def main():
    print("=" * 60)
    print("RAG-6.5 Context Validation Functional Test")
    print("=" * 60)

    test_valid_context()
    test_missing_context_field()
    test_invalid_entries_type()
    test_missing_entry_field()
    test_source_index_order()
    test_count_matches_entries()
    test_negative_count()
    test_invalid_content_type()
    test_invalid_context_text_type()
    test_context_text_length()
    test_none_context()
    test_original_context_unchanged()

    print()
    print("RAG-6.5 CONTEXT VALIDATION TEST PASSED")


if __name__ == "__main__":
    main()