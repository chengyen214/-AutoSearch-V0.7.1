"""
tests/V7_6/test_retrieval_context.py

AutoSearch V7

RAG-5 → RAG-6 Integration Functional Test
"""

from rag.retrieval_context import (
    RetrievalContext,
)

from rag.retriever.retrieval_result import (
    RetrievalResult,
)


# ============================================================
# Mock RAG-5 Retriever
# ============================================================

class MockRetriever:

    def __init__(self):
        self.received_query = None

    def search(
        self,
        query,
    ):
        self.received_query = query

        return [
            RetrievalResult(
                chunk="Content A",
                distance=0.10,
                similarity=0.90,
                document_id="doc-A",
                chunk_index=0,
                metadata={
                    "title": "Document A",
                    "url": "https://example.com/a",
                },
            ),
            RetrievalResult(
                chunk="Content B",
                distance=0.20,
                similarity=0.80,
                document_id="doc-B",
                chunk_index=1,
                metadata={
                    "title": "Document B",
                    "url": "https://example.com/b",
                },
            ),
        ]


# ============================================================
# Mock RAG-6 Context Builder
# ============================================================

class MockContextBuilder:

    def __init__(self):
        self.received_results = None

    def build(
        self,
        retrieval_results,
    ):
        self.received_results = retrieval_results

        return {
            "entries": [
                {
                    "source_index": 1,
                    "document_id": "doc-A",
                    "chunk_index": 0,
                    "title": "Document A",
                    "url": "https://example.com/a",
                    "content": "Content A",
                },
                {
                    "source_index": 2,
                    "document_id": "doc-B",
                    "chunk_index": 1,
                    "title": "Document B",
                    "url": "https://example.com/b",
                    "content": "Content B",
                },
            ],
            "context_text": (
                "[Source 1]\n"
                "Title: Document A\n"
                "Content:\n"
                "Content A\n\n"
                "[Source 2]\n"
                "Title: Document B\n"
                "Content:\n"
                "Content B"
            ),
            "count": 2,
        }


# ============================================================
# Functional Tests
# ============================================================

def test_query_to_context():
    retriever = MockRetriever()
    context_builder = MockContextBuilder()

    integration = RetrievalContext(
        retriever=retriever,
        context_builder=context_builder,
    )

    query = "semiconductor packaging"

    context = integration.build(
        query
    )

    assert retriever.received_query == query

    assert context["count"] == 2
    assert len(context["entries"]) == 2

    print("[PASS] Query → Context")


def test_retriever_output_passed_to_context_builder():
    retriever = MockRetriever()
    context_builder = MockContextBuilder()

    integration = RetrievalContext(
        retriever=retriever,
        context_builder=context_builder,
    )

    integration.build(
        "test query"
    )

    assert (
        context_builder.received_results
        is not None
    )

    assert len(
        context_builder.received_results
    ) == 2

    assert (
        context_builder.received_results[0]
        .document_id
        == "doc-A"
    )

    assert (
        context_builder.received_results[1]
        .document_id
        == "doc-B"
    )

    print(
        "[PASS] RetrievalResult → ContextBuilder"
    )


def test_retrieval_order_preserved():
    retriever = MockRetriever()
    context_builder = MockContextBuilder()

    integration = RetrievalContext(
        retriever=retriever,
        context_builder=context_builder,
    )

    context = integration.build(
        "test query"
    )

    document_ids = [
        entry["document_id"]
        for entry in context["entries"]
    ]

    assert document_ids == [
        "doc-A",
        "doc-B",
    ]

    print("[PASS] Retrieval Order Preserved")


def test_context_output_structure():
    retriever = MockRetriever()
    context_builder = MockContextBuilder()

    integration = RetrievalContext(
        retriever=retriever,
        context_builder=context_builder,
    )

    context = integration.build(
        "test query"
    )

    assert isinstance(
        context,
        dict,
    )

    assert "entries" in context
    assert "context_text" in context
    assert "count" in context

    assert isinstance(
        context["entries"],
        list,
    )

    assert isinstance(
        context["context_text"],
        str,
    )

    assert isinstance(
        context["count"],
        int,
    )

    print("[PASS] Context Output Structure")


def test_component_getters():
    retriever = MockRetriever()
    context_builder = MockContextBuilder()

    integration = RetrievalContext(
        retriever=retriever,
        context_builder=context_builder,
    )

    assert (
        integration.get_retriever()
        is retriever
    )

    assert (
        integration.get_context_builder()
        is context_builder
    )

    print("[PASS] Component Getters")


def test_empty_retrieval_results():
    class EmptyRetriever:

        def search(self, query):
            return []

    class EmptyContextBuilder:

        def build(self, retrieval_results):
            assert retrieval_results == []

            return {
                "entries": [],
                "context_text": "",
                "count": 0,
            }

    integration = RetrievalContext(
        retriever=EmptyRetriever(),
        context_builder=EmptyContextBuilder(),
    )

    context = integration.build(
        "test query"
    )

    assert context["entries"] == []
    assert context["context_text"] == ""
    assert context["count"] == 0

    print("[PASS] Empty Retrieval Results")


def test_custom_components_are_used():
    retriever = MockRetriever()
    context_builder = MockContextBuilder()

    integration = RetrievalContext(
        retriever=retriever,
        context_builder=context_builder,
    )

    assert integration.retriever is retriever
    assert (
        integration.context_builder
        is context_builder
    )

    integration.build(
        "custom component test"
    )

    assert (
        retriever.received_query
        == "custom component test"
    )

    assert (
        context_builder.received_results
        is not None
    )

    print("[PASS] Custom Components")


# ============================================================
# Main
# ============================================================

def main():
    print("=" * 60)
    print(
        "RAG-5 → RAG-6 Retrieval Context "
        "Functional Test"
    )
    print("=" * 60)

    test_query_to_context()
    test_retriever_output_passed_to_context_builder()
    test_retrieval_order_preserved()
    test_context_output_structure()
    test_component_getters()
    test_empty_retrieval_results()
    test_custom_components_are_used()

    print()
    print(
        "RAG-5 → RAG-6 RETRIEVAL CONTEXT "
        "TEST PASSED"
    )


if __name__ == "__main__":
    main()