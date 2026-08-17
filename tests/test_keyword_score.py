"""
tests/test_keyword_score.py

AutoSearch V4

P2.6 Step 2

Keyword Score Calculator Test

Purpose:

    Test KeywordScoreCalculator.

Test Scope:

    1. Full keyword match
    2. Partial keyword match
    3. No keyword match
    4. Empty query
    5. None query
    6. Empty search index
    7. None search index
    8. Case insensitive match
    9. Keyword tokenization
    10. Search text extraction
    11. Score limit
"""


from services.ranking.keyword_score import (
    KeywordScoreCalculator
)


class MockSearchIndex:
    """
    Minimal SearchIndex object
    used for unit testing.
    """

    def __init__(
        self,
        search_text=""
    ):

        self.search_text = search_text


# ==========================================
# P2.6 Step 2
# Keyword Score Tests
# ==========================================


def test_full_keyword_match():

    calculator = KeywordScoreCalculator()

    search_index = MockSearchIndex(
        "AI semiconductor technology"
    )

    score = calculator.calculate(
        "AI semiconductor technology",
        search_index
    )

    assert score == 10.0

    print(
        "PASS: test_full_keyword_match"
    )


def test_partial_keyword_match():

    calculator = KeywordScoreCalculator()

    search_index = MockSearchIndex(
        "AI semiconductor technology"
    )

    score = calculator.calculate(
        "AI semiconductor computer",
        search_index
    )

    # 2 / 3 * 10 = 6.67

    assert score == 6.67

    print(
        "PASS: test_partial_keyword_match"
    )


def test_no_keyword_match():

    calculator = KeywordScoreCalculator()

    search_index = MockSearchIndex(
        "AI semiconductor technology"
    )

    score = calculator.calculate(
        "football baseball",
        search_index
    )

    assert score == 0.0

    print(
        "PASS: test_no_keyword_match"
    )


def test_empty_query():

    calculator = KeywordScoreCalculator()

    search_index = MockSearchIndex(
        "AI semiconductor technology"
    )

    score = calculator.calculate(
        "",
        search_index
    )

    assert score == 0.0

    print(
        "PASS: test_empty_query"
    )


def test_none_query():

    calculator = KeywordScoreCalculator()

    search_index = MockSearchIndex(
        "AI semiconductor technology"
    )

    score = calculator.calculate(
        None,
        search_index
    )

    assert score == 0.0

    print(
        "PASS: test_none_query"
    )


def test_empty_search_index():

    calculator = KeywordScoreCalculator()

    search_index = MockSearchIndex(
        ""
    )

    score = calculator.calculate(
        "AI",
        search_index
    )

    assert score == 0.0

    print(
        "PASS: test_empty_search_index"
    )


def test_none_search_index():

    calculator = KeywordScoreCalculator()

    score = calculator.calculate(
        "AI",
        None
    )

    assert score == 0.0

    print(
        "PASS: test_none_search_index"
    )


def test_case_insensitive_match():

    calculator = KeywordScoreCalculator()

    search_index = MockSearchIndex(
        "Artificial Intelligence AI"
    )

    score = calculator.calculate(
        "ai",
        search_index
    )

    assert score == 10.0

    print(
        "PASS: test_case_insensitive_match"
    )


def test_keyword_tokenization():

    calculator = KeywordScoreCalculator()

    keywords = calculator._tokenize_keywords(
        "AI semiconductor technology"
    )

    assert keywords == [
        "ai",
        "semiconductor",
        "technology"
    ]

    print(
        "PASS: test_keyword_tokenization"
    )


def test_search_text_extraction():

    calculator = KeywordScoreCalculator()

    search_index = MockSearchIndex(
        "AI semiconductor"
    )

    search_text = calculator._get_search_text(
        search_index
    )

    assert search_text == "ai semiconductor"

    print(
        "PASS: test_search_text_extraction"
    )


def test_score_limit():

    calculator = KeywordScoreCalculator()

    search_index = MockSearchIndex(
        "AI AI AI AI AI"
    )

    score = calculator.calculate(
        "AI",
        search_index
    )

    assert score <= 10.0

    assert score == 10.0

    print(
        "PASS: test_score_limit"
    )


# ==========================================
# Test Runner
# ==========================================


def main():

    print()

    print(
        "=========="
    )

    print(
        "AutoSearch V4"
    )

    print(
        "P2.6 Step 2"
    )

    print(
        "Keyword Score Test"
    )

    print(
        "=========="
    )

    print()

    tests = [

        test_full_keyword_match,
        test_partial_keyword_match,
        test_no_keyword_match,
        test_empty_query,
        test_none_query,
        test_empty_search_index,
        test_none_search_index,
        test_case_insensitive_match,
        test_keyword_tokenization,
        test_search_text_extraction,
        test_score_limit

    ]

    passed = 0

    failed = 0

    for test in tests:

        try:

            test()

            passed += 1

        except Exception as e:

            failed += 1

            print(
                f"FAIL: {test.__name__}"
            )

            print(
                f"      {e}"
            )

    print()

    print(
        "========== Test Result =========="
    )

    print(
        f"Passed: {passed}"
    )

    print(
        f"Failed: {failed}"
    )

    print(
        "================================="
    )

    if failed > 0:

        raise SystemExit(1)


if __name__ == "__main__":

    main()