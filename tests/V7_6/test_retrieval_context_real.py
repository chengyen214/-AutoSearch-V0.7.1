"""
tests/V7_6/test_retrieval_context_real.py

AutoSearch V7

RAG-5 → RAG-6 Real Integration Test

使用目前實際的：

    RAGRetriever
    QueryEmbedding
    ChromaDB
    RetrievalResult
    ContextBuilder

不使用 Mock。
"""

from rag.retrieval_context import RetrievalContext


# ============================================================
# Test Query
# ============================================================

TEST_QUERY = "semiconductor industry"


# ============================================================
# Real Integration Test
# ============================================================

def test_real_retrieval_context():
    print("=" * 60)
    print("RAG-5 → RAG-6 REAL INTEGRATION TEST")
    print("=" * 60)

    print()
    print(f"Query: {TEST_QUERY}")

    # --------------------------------------------------------
    # 建立真正的 RetrievalContext
    # --------------------------------------------------------

    retrieval_context = RetrievalContext()

    print()
    print("[1] Running RAG-5 Retrieval...")

    context = retrieval_context.build(
        TEST_QUERY
    )

    # --------------------------------------------------------
    # 驗證 Context 基本結構
    # --------------------------------------------------------

    assert isinstance(
        context,
        dict,
    )

    assert "entries" in context
    assert "context_text" in context
    assert "count" in context

    entries = context["entries"]

    assert isinstance(
        entries,
        list,
    )

    assert context["count"] == len(entries)

    # --------------------------------------------------------
    # 必須真的有 Retrieval Result
    # --------------------------------------------------------

    assert len(entries) > 0, (
        "RAG-5 returned no retrieval results."
    )

    print(
        f"[PASS] RAG-5 returned "
        f"{len(entries)} result(s)"
    )

    # --------------------------------------------------------
    # 顯示實際 Retrieval → Context 結果
    # --------------------------------------------------------

    print()
    print("[2] RAG-5 → RAG-6 Results")
    print("-" * 60)

    for entry in entries:

        source_index = entry["source_index"]
        document_id = entry["document_id"]
        chunk_index = entry["chunk_index"]
        title = entry["title"]
        url = entry["url"]
        content = entry["content"]

        print()
        print(
            f"[Source {source_index}]"
        )

        print(
            f"Document ID : {document_id}"
        )

        print(
            f"Chunk Index  : {chunk_index}"
        )

        print(
            f"Title        : {title}"
        )

        print(
            f"URL          : {url}"
        )

        print(
            "Content      : "
            f"{content[:300]}"
        )

    # --------------------------------------------------------
    # Context Text
    # --------------------------------------------------------

    print()
    print("[3] Final Context")
    print("-" * 60)

    context_text = context["context_text"]

    assert isinstance(
        context_text,
        str,
    )

    assert len(context_text) > 0

    print(context_text[:3000])

    if len(context_text) > 3000:
        print()
        print(
            "... "
            "(context output truncated for display)"
        )

    # --------------------------------------------------------
    # 最終驗證
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print(
        "RAG-5 → RAG-6 REAL INTEGRATION "
        "TEST PASSED"
    )
    print("=" * 60)


# ============================================================
# Main
# ============================================================

def main():
    test_real_retrieval_context()


if __name__ == "__main__":
    main()