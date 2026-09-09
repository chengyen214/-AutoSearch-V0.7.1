"""
tests/test_ranking_score.py

AutoSearch V4

P2.6 Step 8

Ranking Score Calculator Test

Purpose:

    Test RankingScoreCalculator.

Test Scope:

    1. Maximum ranking score
    2. Normal ranking score
    3. Medium ranking score
    4. Zero ranking score
    5. None search index
    6. None ranking score
    7. Negative ranking score
    8. Ranking score greater than maximum
    9. String ranking score
    10. Invalid ranking score
    11. Private ranking score getter
"""


from services.ranking.ranking_score import (
    RankingScoreCalculator
)


class MockSearchIndex:
    """
    Minimal SearchIndex object
    used for testing.
    """

    def __init__(
        self,
        ranking_score=None
    ):

        self.ranking_score = ranking_score


# ==========================================
# Maximum Score
# ==========================================


def test_maximum_ranking_score():

    calculator = RankingScoreCalculator()

    search_index = MockSearchIndex(
        ranking_score=10
    )

    score = calculator.calculate(
        search_index
    )

    assert score == 10.0

    print(
        "PASS: test_maximum_ranking_score"
    )


# ==========================================
# Normal Score
# ==========================================


def test_normal_ranking_score():

    calculator = RankingScoreCalculator()

    search_index = MockSearchIndex(
        ranking_score=8
    )

    score = calculator.calculate(
        search_index
    )

    assert score == 8.0

    print(
        "PASS: test_normal_ranking_score"
    )


# ==========================================
# Medium Score
# ==========================================


def test_medium_ranking_score():

    calculator = RankingScoreCalculator()

    search_index = MockSearchIndex(
        ranking_score=5
    )

    score = calculator.calculate(
        search_index
    )

    assert score == 5.0

    print(
        "PASS: test_medium_ranking_score"
    )


# ==========================================
# Zero Score
# ==========================================


def test_zero_ranking_score():

    calculator = RankingScoreCalculator()

    search_index = MockSearchIndex(
        ranking_score=0
    )

    score = calculator.calculate(
        search_index
    )

    assert score == 0.0

    print(
        "PASS: test_zero_ranking_score"
    )


# ==========================================
# None Search Index
# ==========================================


def test_none_search_index():

    calculator = RankingScoreCalculator()

    score = calculator.calculate(
        None
    )

    assert score == 0.0

    print(
        "PASS: test_none_search_index"
    )


# ==========================================
# None Ranking Score
# ==========================================


def test_none_ranking_score():

    calculator = RankingScoreCalculator()

    search_index = MockSearchIndex(
        ranking_score=None
    )

    score = calculator.calculate(
        search_index
    )

    assert score == 0.0

    print(
        "PASS: test_none_ranking_score"
    )


# ==========================================
# Negative Score
# ==========================================


def test_negative_ranking_score():

    calculator = RankingScoreCalculator()

    search_index = MockSearchIndex(
        ranking_score=-5
    )

    score = calculator.calculate(
        search_index
    )

    assert score == 0.0

    print(
        "PASS: test_negative_ranking_score"
    )


# ==========================================
# Score Greater Than Maximum
# ==========================================


def test_ranking_score_above_maximum():

    calculator = RankingScoreCalculator()

    search_index = MockSearchIndex(
        ranking_score=15
    )

    score = calculator.calculate(
        search_index
    )

    assert score == 10.0

    print(
        "PASS: test_ranking_score_above_maximum"
    )


# ==========================================
# String Score
# ==========================================


def test_string_ranking_score():

    calculator = RankingScoreCalculator()

    search_index = MockSearchIndex(
        ranking_score="8.5"
    )

    score = calculator.calculate(
        search_index
    )

    assert score == 8.5

    print(
        "PASS: test_string_ranking_score"
    )


# ==========================================
# Invalid Score
# ==========================================


def test_invalid_ranking_score():

    calculator = RankingScoreCalculator()

    search_index = MockSearchIndex(
        ranking_score="invalid"
    )

    score = calculator.calculate(
        search_index
    )

    assert score == 0.0

    print(
        "PASS: test_invalid_ranking_score"
    )


# ==========================================
# Private Getter
# ==========================================


def test_get_ranking_score():

    calculator = RankingScoreCalculator()

    search_index = MockSearchIndex(
        ranking_score=7.5
    )

    score = calculator._get_ranking_score(
        search_index
    )

    assert score == 7.5

    print(
        "PASS: test_get_ranking_score"
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
        "P2.6 Step 8"
    )

    print(
        "Ranking Score Calculator Test"
    )

    print(
        "=========="
    )

    print()


    tests = [

        test_maximum_ranking_score,

        test_normal_ranking_score,

        test_medium_ranking_score,

        test_zero_ranking_score,

        test_none_search_index,

        test_none_ranking_score,

        test_negative_ranking_score,

        test_ranking_score_above_maximum,

        test_string_ranking_score,

        test_invalid_ranking_score,

        test_get_ranking_score

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