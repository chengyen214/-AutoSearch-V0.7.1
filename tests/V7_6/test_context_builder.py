"""
tests/V7_6/test_context_builder.py

AutoSearch V7

RAG-6.6

Context Builder Functional Test
"""

from rag.context.context_builder import (
    ContextBuilder,
)

from rag.retriever.retrieval_result import (
    RetrievalResult,
)


# ============================================================
# Test Data
# ============================================================

def create_result(
    document_id,
    chunk_index,
    distance,
):
    return RetrievalResult(
        chunk=(
            f"Content from "
            f"{document_id} "
            f"chunk {chunk_index}."
        ),
        distance=distance,
        similarity=1.0 - distance,
        document_id=document_id,
        chunk_index=chunk_index,
        metadata={
            "title": f"Title {document_id}",
            "url": (
                f"https://example.com/"
                f"{document_id}"
            ),
        },
    )


def create_results():
    return [
        create_result(
            "doc-C",
            2,
            0.10,
        ),
        create_result(
            "doc-A",
            0,
            0.20,
        ),
        create_result(
            "doc-B",
            1,
            0.30,
        ),
    ]


# ============================================================
# Functional Tests
# ============================================================

def test_context_builder_basic():
    builder = ContextBuilder()

    results = create_results()

    context = builder.build(
        results
    )

    assert isinstance(
        context,
        dict,
    )

    assert "entries" in context
    assert "context_text" in context
    assert "count" in context

    print("[PASS] Basic Context Builder")


def test_pipeline_output_count():
    builder = ContextBuilder()

    results = create_results()

    context = builder.build(
        results
    )

    assert context["count"] == 3
    assert len(
        context["entries"]
    ) == 3

    print("[PASS] Pipeline Output Count")


def test_retrieval_order_preserved():
    builder = ContextBuilder()

    results = create_results()

    context = builder.build(
        results
    )

    document_ids = [
        entry["document_id"]
        for entry in context["entries"]
    ]

    assert document_ids == [
        "doc-C",
        "doc-A",
        "doc-B",
    ]

    print("[PASS] Retrieval Order Preserved")


def test_source_index_order():
    builder = ContextBuilder()

    results = create_results()

    context = builder.build(
        results
    )

    source_indexes = [
        entry["source_index"]
        for entry in context["entries"]
    ]

    assert source_indexes == [
        1,
        2,
        3,
    ]

    print("[PASS] Source Index Order")


def test_context_entry_fields():
    builder = ContextBuilder()

    results = create_results()

    context = builder.build(
        results
    )

    required_fields = {
        "source_index",
        "document_id",
        "chunk_index",
        "title",
        "url",
        "content",
    }

    for entry in context["entries"]:
        assert required_fields.issubset(
            entry.keys()
        )

    print("[PASS] Context Entry Fields")


def test_metadata_pipeline():
    builder = ContextBuilder()

    results = create_results()

    context = builder.build(
        results
    )

    for entry in context["entries"]:
        assert "source_metadata" in entry
        assert "ai_metadata" in entry

        assert entry[
            "source_metadata"
        ]["title"] == entry["title"]

        assert entry[
            "source_metadata"
        ]["url"] == entry["url"]

        assert "ai_summary" in (
            entry["ai_metadata"]
        )

    print("[PASS] Metadata Pipeline")


def test_context_text():
    builder = ContextBuilder()

    results = create_results()

    context = builder.build(
        results
    )

    assert isinstance(
        context["context_text"],
        str,
    )

    assert "[Source 1]" in (
        context["context_text"]
    )

    assert "Title: Title doc-C" in (
        context["context_text"]
    )

    assert (
        "Content from doc-C chunk 2."
        in context["context_text"]
    )

    print("[PASS] Context Text")


def test_empty_results():
    builder = ContextBuilder()

    context = builder.build([])

    assert context["entries"] == []
    assert context["context_text"] == ""
    assert context["count"] == 0

    print("[PASS] Empty RetrievalResult")


def test_original_results_unchanged():
    builder = ContextBuilder()

    results = create_results()

    original_order = [
        (
            result.document_id,
            result.chunk_index,
            result.chunk,
        )
        for result in results
    ]

    builder.build(
        results
    )

    current_order = [
        (
            result.document_id,
            result.chunk_index,
            result.chunk,
        )
        for result in results
    ]

    assert current_order == original_order

    print("[PASS] Original RetrievalResult Unchanged")


def test_none_input():
    builder = ContextBuilder()

    try:
        builder.build(None)
    except ValueError:
        print("[PASS] None Input Validation")
        return

    raise AssertionError(
        "None input should raise ValueError."
    )


# ============================================================
# Main
# ============================================================

def main():
    print("=" * 60)
    print("RAG-6.6 Context Builder Functional Test")
    print("=" * 60)

    test_context_builder_basic()
    test_pipeline_output_count()
    test_retrieval_order_preserved()
    test_source_index_order()
    test_context_entry_fields()
    test_metadata_pipeline()
    test_context_text()
    test_empty_results()
    test_original_results_unchanged()
    test_none_input()

    print()
    print("RAG-6.6 CONTEXT BUILDER TEST PASSED")


if __name__ == "__main__":
    main()