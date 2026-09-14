"""
tests/V7_5/test_rag_top_k.py

AutoSearch V7

RAG-5.4
Top-K Retrieval Integration Test
"""


from rag.retriever.top_k import (
    TopKRetrieval,
)

from rag.retriever.config import (
    TOP_K,
)


# ============================================================
# Fake Retrieval Result
# ============================================================

def build_fake_result():

    return {
        "ids": [
            [
                "doc001::chunk_0",
                "doc002::chunk_1",
                "doc003::chunk_0",
                "doc004::chunk_2",
                "doc005::chunk_1",
                "doc006::chunk_0",
                "doc007::chunk_3",
            ]
        ],
        "documents": [
            [
                "內容 A",
                "內容 B",
                "內容 C",
                "內容 D",
                "內容 E",
                "內容 F",
                "內容 G",
            ]
        ],
        "metadatas": [
            [
                {"document_id": "doc001"},
                {"document_id": "doc002"},
                {"document_id": "doc003"},
                {"document_id": "doc004"},
                {"document_id": "doc005"},
                {"document_id": "doc006"},
                {"document_id": "doc007"},
            ]
        ],
        "distances": [
            [
                0.10,
                0.20,
                0.30,
                0.40,
                0.50,
                0.60,
                0.70,
            ]
        ],
    }


# ============================================================
# Assertion
# ============================================================

def check(
    condition,
    message,
):

    if not condition:
        raise AssertionError(
            message
        )

    print(
        f"PASS: {message}"
    )


# ============================================================
# Main
# ============================================================

def main():

    print(
        "=" * 60
    )

    print(
        "RAG-5.4 Top-K Retrieval Integration Test"
    )

    print(
        "=" * 60
    )

    # --------------------------------------------------------
    # Initialization
    # --------------------------------------------------------

    retriever = (
        TopKRetrieval()
    )

    check(
        retriever is not None,
        "TopKRetrieval initialization",
    )

    check(
        retriever.get_top_k()
        == TOP_K,
        "Top-K configuration",
    )

    print(
        f"      Top-K: "
        f"{retriever.get_top_k()}"
    )

    # --------------------------------------------------------
    # Build Retrieval Result
    # --------------------------------------------------------

    raw_result = (
        build_fake_result()
    )

    check(
        len(raw_result["ids"][0]) == 7,
        "Raw retrieval result count",
    )

    # --------------------------------------------------------
    # Top-K Selection
    # --------------------------------------------------------

    result = (
        retriever.select(
            raw_result
        )
    )

    check(
        result is not None,
        "Top-K result",
    )

    check(
        isinstance(
            result,
            dict,
        ),
        "Top-K result type",
    )

    # --------------------------------------------------------
    # Result Count
    # --------------------------------------------------------

    check(
        len(result["ids"]) == TOP_K,
        "Top-K IDs count",
    )

    check(
        len(result["documents"]) == TOP_K,
        "Top-K documents count",
    )

    check(
        len(result["metadatas"]) == TOP_K,
        "Top-K metadata count",
    )

    check(
        len(result["distances"]) == TOP_K,
        "Top-K distances count",
    )

    # --------------------------------------------------------
    # Result Ordering
    # --------------------------------------------------------

    check(
        result["ids"][0]
        == "doc001::chunk_0",
        "Top-K first result",
    )

    check(
        result["ids"][4]
        == "doc005::chunk_1",
        "Top-K last result",
    )

    check(
        result["distances"][0]
        == 0.10,
        "Top-K first distance",
    )

    check(
        result["distances"][4]
        == 0.50,
        "Top-K last distance",
    )

    # --------------------------------------------------------
    # Result Integrity
    # --------------------------------------------------------

    for index in range(TOP_K):

        check(
            result["metadatas"][index]
            ["document_id"]
            == f"doc00{index + 1}",
            f"Metadata integrity {index + 1}",
        )

    # --------------------------------------------------------
    # Custom Top-K
    # --------------------------------------------------------

    custom_result = (
        retriever.select(
            raw_result,
            top_k=3,
        )
    )

    check(
        len(custom_result["ids"]) == 3,
        "Custom Top-K count",
    )

    check(
        custom_result["ids"][2]
        == "doc003::chunk_0",
        "Custom Top-K last result",
    )

    # --------------------------------------------------------
    # Top-K Greater Than Result Count
    # --------------------------------------------------------

    oversized_result = (
        retriever.select(
            raw_result,
            top_k=20,
        )
    )

    check(
        len(
            oversized_result["ids"]
        ) == 7,
        "Top-K larger than result count",
    )

    # --------------------------------------------------------
    # Validation
    # --------------------------------------------------------

    invalid_results = [
        (
            None,
            ValueError,
            "None retrieval result validation",
        ),
        (
            [],
            TypeError,
            "Non-dict retrieval result validation",
        ),
        (
            {},
            ValueError,
            "Missing retrieval fields validation",
        ),
    ]

    for (
        invalid_result,
        expected_exception,
        message,
    ) in invalid_results:

        try:

            retriever.select(
                invalid_result
            )

        except expected_exception:

            print(
                f"PASS: {message}"
            )

        else:

            raise AssertionError(
                f"FAIL: {message}"
            )

    # --------------------------------------------------------
    # Invalid Top-K
    # --------------------------------------------------------

    invalid_top_k = [
        0,
        -1,
        "abc",
    ]

    for value in invalid_top_k:

        try:

            retriever.select(
                raw_result,
                top_k=value,
            )

        except ValueError:

            print(
                f"PASS: Invalid Top-K validation "
                f"({value})"
            )

        else:

            raise AssertionError(
                "FAIL: Invalid Top-K validation "
                f"({value})"
            )

    # --------------------------------------------------------
    # Count Consistency
    # --------------------------------------------------------

    check(
        len(result["ids"])
        == len(result["documents"])
        == len(result["metadatas"])
        == len(result["distances"]),
        "Top-K result count consistency",
    )

    print()
    print(
        "=" * 60
    )

    print(
        "ALL RAG-5.4 TOP-K RETRIEVAL "
        "INTEGRATION TESTS PASSED"
    )

    print(
        "=" * 60
    )


if __name__ == "__main__":
    main()