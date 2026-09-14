"""
tests/V7_6/test_rag_8_response.py

AutoSearch V7

RAG-8 Response Formatting Integration Test

測試流程：

    User Query
        ↓
    RAGQuery
        ↓
    RAG-5 ~ RAG-7
        ↓
    ResponseFormatter
        ↓
    Final Response
"""

from rag.rag_query import RAGQuery
from rag.response_formatter import ResponseFormatter


TEST_QUERY = (
    "分析半導體產業目前的重要發展趨勢，"
    "並根據 Retrieved Context 說明主要變化。"
)


def main():

    print("=" * 70)
    print("RAG-8 RESPONSE FORMATTING TEST")
    print("=" * 70)

    # --------------------------------------------------
    # 1. RAG-5 ~ RAG-7
    # --------------------------------------------------

    print("\n[1] Running RAG Query...")

    rag_query = RAGQuery()

    rag_result = rag_query.run(TEST_QUERY)

    if not isinstance(rag_result, dict):
        raise AssertionError(
            "RAGQuery result must be a dict."
        )

    if "answer_text" not in rag_result:
        raise AssertionError(
            "RAGQuery result missing 'answer_text'."
        )

    if "source_references" not in rag_result:
        raise AssertionError(
            "RAGQuery result missing 'source_references'."
        )

    print("[PASS] RAG Query completed")

    # --------------------------------------------------
    # 2. RAG-8 Response Formatting
    # --------------------------------------------------

    print("\n[2] Formatting Response...")

    formatter = ResponseFormatter()

    response = formatter.format(rag_result)

    # --------------------------------------------------
    # 3. Validate Final Response
    # --------------------------------------------------

    if not isinstance(response, dict):
        raise AssertionError(
            "Final response must be a dict."
        )

    if "answer" not in response:
        raise AssertionError(
            "Final response missing 'answer'."
        )

    if "sources" not in response:
        raise AssertionError(
            "Final response missing 'sources'."
        )

    if not isinstance(response["answer"], str):
        raise AssertionError(
            "'answer' must be a string."
        )

    if not response["answer"].strip():
        raise AssertionError(
            "'answer' cannot be empty."
        )

    if not isinstance(response["sources"], list):
        raise AssertionError(
            "'sources' must be a list."
        )

    # --------------------------------------------------
    # 4. Validate Source Structure
    # --------------------------------------------------

    for source in response["sources"]:

        if not isinstance(source, dict):
            raise AssertionError(
                "Each source must be a dict."
            )

        required_fields = [
            "source_index",
            "title",
            "url",
        ]

        for field in required_fields:
            if field not in source:
                raise AssertionError(
                    f"Source missing '{field}'."
                )

    # --------------------------------------------------
    # 5. Display Final Response
    # --------------------------------------------------

    print("\n" + "=" * 70)
    print("FINAL RESPONSE")
    print("=" * 70)

    print("\nANSWER:\n")
    print(response["answer"])

    print("\n" + "-" * 70)
    print("SOURCES")
    print("-" * 70)

    if response["sources"]:

        for source in response["sources"]:

            print(
                f"[Source {source['source_index']}] "
                f"{source['title']}"
            )

            print(f"URL: {source['url']}")
            print()

    else:
        print("No sources.")

    # --------------------------------------------------
    # 6. Final Result
    # --------------------------------------------------

    print("=" * 70)
    print("RAG-8 RESPONSE FORMATTING TEST PASSED")
    print("=" * 70)


if __name__ == "__main__":
    main()