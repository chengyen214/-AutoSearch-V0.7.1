"""
tests/V7_6/test_context_ordering.py

AutoSearch V7

RAG-6.4

Context Ordering Functional Test
"""

from rag.context.ordering import ContextOrdering
from rag.retriever.retrieval_result import RetrievalResult


def create_result(
    document_id,
    chunk_index,
    distance,
):
    return RetrievalResult(
        chunk=f"chunk-{document_id}-{chunk_index}",
        distance=distance,
        similarity=1.0 - distance,
        document_id=document_id,
        chunk_index=chunk_index,
        metadata={
            "title": f"Title {document_id}",
            "url": f"https://example.com/{document_id}",
        },
    )


def test_preserve_retrieval_order():
    results = [
        create_result("doc-C", 2, 0.10),
        create_result("doc-A", 0, 0.20),
        create_result("doc-B", 1, 0.30),
    ]

    ordering = ContextOrdering()

    ordered = ordering.order(results)

    assert [
        result.document_id
        for result in ordered
    ] == [
        "doc-C",
        "doc-A",
        "doc-B",
    ]

    print("[PASS] Preserve Retrieval Order")


def test_returns_new_list():
    results = [
        create_result("doc-A", 0, 0.10),
        create_result("doc-B", 1, 0.20),
    ]

    ordering = ContextOrdering()

    ordered = ordering.order(results)

    assert ordered is not results
    assert ordered == results

    print("[PASS] Returns New List")


def test_original_list_unchanged():
    results = [
        create_result("doc-C", 2, 0.10),
        create_result("doc-A", 0, 0.20),
        create_result("doc-B", 1, 0.30),
    ]

    original_order = [
        result.document_id
        for result in results
    ]

    ordering = ContextOrdering()

    ordering.order(results)

    assert [
        result.document_id
        for result in results
    ] == original_order

    print("[PASS] Original List Unchanged")


def test_empty_results():
    ordering = ContextOrdering()

    ordered = ordering.order([])

    assert ordered == []
    assert ordered is not None

    print("[PASS] Empty RetrievalResult")


def test_none_input():
    ordering = ContextOrdering()

    try:
        ordering.order(None)
    except ValueError:
        print("[PASS] None Input Validation")
        return

    raise AssertionError(
        "None input should raise ValueError."
    )


def test_invalid_input_type():
    ordering = ContextOrdering()

    try:
        ordering.order("invalid")
    except TypeError:
        print("[PASS] Invalid Input Type Validation")
        return

    raise AssertionError(
        "Invalid input type should raise TypeError."
    )


def test_invalid_result_element():
    ordering = ContextOrdering()

    try:
        ordering.order(
            [
                create_result(
                    "doc-A",
                    0,
                    0.10,
                ),
                "invalid-result",
            ]
        )
    except TypeError:
        print("[PASS] Invalid RetrievalResult Validation")
        return

    raise AssertionError(
        "Invalid RetrievalResult element should raise TypeError."
    )


def main():
    print("=" * 60)
    print("RAG-6.4 Context Ordering Functional Test")
    print("=" * 60)

    test_preserve_retrieval_order()
    test_returns_new_list()
    test_original_list_unchanged()
    test_empty_results()
    test_none_input()
    test_invalid_input_type()
    test_invalid_result_element()

    print()
    print("RAG-6.4 CONTEXT ORDERING TEST PASSED")


if __name__ == "__main__":
    main()