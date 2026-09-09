"""
tests/test_topic_score.py

AutoSearch V4

P2.6 Step 4

Topic Score Calculator Test

Purpose:

    Test TopicScoreCalculator.

Test Scope:

    1. Full topic match
    2. Partial topic match
    3. No topic match
    4. Empty topic
    5. None topic
    6. Empty query
    7. None query
    8. None search index
    9. Case insensitive topic match
    10. Topic extraction
    11. Topic tokenization
    12. Topic punctuation parsing
    13. Partial topic with three tokens
    14. Score limit
"""


from services.ranking.topic_score import (
    TopicScoreCalculator
)


class MockSearchIndex:
    """
    Minimal SearchIndex object
    used for unit testing.
    """

    def __init__(
        self,
        search_text="",
        topic=""
    ):

        self.search_text = search_text

        self.topic = topic


# ==========================================
# P2.6 Step 4
# Topic Score Tests
# ==========================================


def test_full_topic_match():

    calculator = TopicScoreCalculator()

    search_index = MockSearchIndex(

        "AI semiconductor technology",

        topic="AI semiconductor technology"

    )

    score = calculator.calculate(

        "AI semiconductor technology",

        search_index

    )

    assert score == 10.0

    print(
        "PASS: test_full_topic_match"
    )


def test_partial_topic_match():

    calculator = TopicScoreCalculator()

    search_index = MockSearchIndex(

        "AI semiconductor technology",

        topic="AI semiconductor"

    )

    score = calculator.calculate(

        "AI semiconductor technology",

        search_index

    )

    # 2 / 3 * 10 = 6.67

    assert score == 6.67

    print(
        "PASS: test_partial_topic_match"
    )


def test_no_topic_match():

    calculator = TopicScoreCalculator()

    search_index = MockSearchIndex(

        "AI semiconductor technology",

        topic="football sports"

    )

    score = calculator.calculate(

        "AI semiconductor",

        search_index

    )

    assert score == 0.0

    print(
        "PASS: test_no_topic_match"
    )


def test_empty_topic():

    calculator = TopicScoreCalculator()

    search_index = MockSearchIndex(

        "AI semiconductor",

        topic=""

    )

    score = calculator.calculate(

        "AI semiconductor",

        search_index

    )

    assert score == 0.0

    print(
        "PASS: test_empty_topic"
    )


def test_none_topic():

    calculator = TopicScoreCalculator()

    search_index = MockSearchIndex(

        "AI semiconductor",

        topic=None

    )

    score = calculator.calculate(

        "AI",

        search_index

    )

    assert score == 0.0

    print(
        "PASS: test_none_topic"
    )


def test_empty_query():

    calculator = TopicScoreCalculator()

    search_index = MockSearchIndex(

        "AI semiconductor",

        topic="AI semiconductor"

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

    calculator = TopicScoreCalculator()

    search_index = MockSearchIndex(

        "AI semiconductor",

        topic="AI semiconductor"

    )

    score = calculator.calculate(

        None,

        search_index

    )

    assert score == 0.0

    print(
        "PASS: test_none_query"
    )


def test_none_search_index():

    calculator = TopicScoreCalculator()

    score = calculator.calculate(

        "AI",

        None

    )

    assert score == 0.0

    print(
        "PASS: test_none_search_index"
    )


def test_case_insensitive_topic_match():

    calculator = TopicScoreCalculator()

    search_index = MockSearchIndex(

        "Artificial Intelligence NVIDIA",

        topic="Artificial Intelligence NVIDIA"

    )

    score = calculator.calculate(

        "artificial intelligence nvidia",

        search_index

    )

    assert score == 10.0

    print(
        "PASS: test_case_insensitive_topic_match"
    )


def test_topic_extraction():

    calculator = TopicScoreCalculator()

    search_index = MockSearchIndex(

        "AI semiconductor",

        topic="AI semiconductor"

    )

    topic = calculator._get_topic(

        search_index

    )

    assert topic == "ai semiconductor"

    print(
        "PASS: test_topic_extraction"
    )


def test_topic_tokenization():

    calculator = TopicScoreCalculator()

    tokens = calculator._tokenize_keywords(

        "AI semiconductor technology"

    )

    assert tokens == [
        "ai",
        "semiconductor",
        "technology"
    ]

    print(
        "PASS: test_topic_tokenization"
    )


def test_topic_punctuation_parsing():

    calculator = TopicScoreCalculator()

    search_index = MockSearchIndex(

        "AI semiconductor technology",

        topic="AI, semiconductor technology"

    )

    score = calculator.calculate(

        "AI semiconductor technology",

        search_index

    )

    assert score == 10.0

    print(
        "PASS: test_topic_punctuation_parsing"
    )


def test_partial_topic_three_tokens():

    calculator = TopicScoreCalculator()

    search_index = MockSearchIndex(

        "AI semiconductor",

        topic="AI semiconductor"

    )

    score = calculator.calculate(

        "AI semiconductor technology",

        search_index

    )

    # 2 / 3 * 10 = 6.67

    assert score == 6.67

    print(
        "PASS: test_partial_topic_three_tokens"
    )


def test_score_limit():

    calculator = TopicScoreCalculator()

    search_index = MockSearchIndex(

        "AI semiconductor technology",

        topic="AI semiconductor technology"

    )

    score = calculator.calculate(

        "AI semiconductor technology",

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
        "P2.6 Step 4"
    )

    print(
        "Topic Score Test"
    )

    print(
        "=========="
    )

    print()

    tests = [

        test_full_topic_match,
        test_partial_topic_match,
        test_no_topic_match,
        test_empty_topic,
        test_none_topic,
        test_empty_query,
        test_none_query,
        test_none_search_index,
        test_case_insensitive_topic_match,
        test_topic_extraction,
        test_topic_tokenization,
        test_topic_punctuation_parsing,
        test_partial_topic_three_tokens,
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
