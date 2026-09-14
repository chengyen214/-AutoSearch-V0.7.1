"""
tests/V7_6/test_rag_query.py

AutoSearch V7

RAG Query Integration Test

驗證：

    User Query
        ↓
    RAGQuery
        ↓
    RAG-5 → RAG-6 → RAG-7.2 → RAG-7.4 → RAG-7.5
        ↓
    RAG Result
"""

from rag.rag_query import RAGQuery


TEST_QUERY = (
    "分析半導體產業目前的重要發展趨勢，"
    "並根據 Retrieved Context 說明主要變化。"
)


def test_rag_query():

    print("=" * 70)
    print("RAG QUERY INTEGRATION TEST")
    print("=" * 70)

    print()
    print(f"User Query: {TEST_QUERY}")

    # ========================================================
    # RAG Query
    # ========================================================

    rag_query = RAGQuery()

    result = rag_query.run(
        TEST_QUERY
    )

    # ========================================================
    # Validate Result
    # ========================================================

    assert isinstance(
        result,
        dict,
    )

    assert "answer_text" in result
    assert "source_references" in result

    assert isinstance(
        result["answer_text"],
        str,
    )

    assert len(
        result["answer_text"].strip()
    ) > 0

    assert isinstance(
        result["source_references"],
        list,
    )

    print()
    print("[PASS] RAG Query completed")

    # ========================================================
    # Display Answer
    # ========================================================

    print()
    print("=" * 70)
    print("RAG QUERY ANSWER")
    print("=" * 70)

    print(
        result["answer_text"]
    )

    # ========================================================
    # Display Sources
    # ========================================================

    print()
    print("=" * 70)
    print("SOURCE REFERENCES")
    print("=" * 70)

    if not result["source_references"]:

        print(
            "[INFO] No source references."
        )

    else:

        for source in result["source_references"]:

            print()
            print(
                f"[Source "
                f"{source['source_index']}]"
            )

            print(
                f"Document ID : "
                f"{source['document_id']}"
            )

            print(
                f"Chunk Index : "
                f"{source['chunk_index']}"
            )

            print(
                f"Title       : "
                f"{source['title']}"
            )

            print(
                f"URL         : "
                f"{source['url']}"
            )

    # ========================================================
    # Final
    # ========================================================

    print()
    print("=" * 70)
    print(
        "RAG QUERY INTEGRATION TEST PASSED"
    )
    print("=" * 70)


def main():

    test_rag_query()


if __name__ == "__main__":
    main()