"""
tests/test_confidence_score.py

AutoSearch V4

P2.6 Step 6

Confidence Score Calculator Test

Purpose:

    Test Confidence Score calculation.

Test Scope:

    1. Full confidence
    2. High confidence
    3. Medium confidence
    4. Low confidence
    5. Zero confidence
    6. None confidence
    7. Missing confidence
    8. String confidence
    9. Invalid confidence
    10. Confidence above maximum
    11. Confidence below minimum
"""


from services.ranking.confidence_score import (
    ConfidenceScoreCalculator
)


class MockSearchIndex:
    """
    Minimal SearchIndex object
    used for unit testing.
    """

    def __init__(
        self,
        confidence=None
    ):

        self.confidence = confidence


# ==========================================
# Full Confidence
# ==========================================


def test_full_confidence():

    calculator = ConfidenceScoreCalculator()

    search_index = MockSearchIndex(

        confidence=1.0

    )

    score = calculator.calculate(

        search_index

    )

    assert score == 10.0

    print(
        "PASS: test_full_confidence"
    )


# ==========================================
# High Confidence
# ==========================================


def test_high_confidence():

    calculator = ConfidenceScoreCalculator()

    search_index = MockSearchIndex(

        confidence=0.9

    )

    score = calculator.calculate(

        search_index

    )

    assert score == 9.0

    print(
        "PASS: test_high_confidence"
    )


# ==========================================
# Medium Confidence
# ==========================================


def test_medium_confidence():

    calculator = ConfidenceScoreCalculator()

    search_index = MockSearchIndex(

        confidence=0.8

    )

    score = calculator.calculate(

        search_index

    )

    assert score == 8.0

    print(
        "PASS: test_medium_confidence"
    )


# ==========================================
# Low Confidence
# ==========================================


def test_low_confidence():

    calculator = ConfidenceScoreCalculator()

    search_index = MockSearchIndex(

        confidence=0.5

    )

    score = calculator.calculate(

        search_index

    )

    assert score == 5.0

    print(
        "PASS: test_low_confidence"
    )


# ==========================================
# Zero Confidence
# ==========================================


def test_zero_confidence():

    calculator = ConfidenceScoreCalculator()

    search_index = MockSearchIndex(

        confidence=0.0

    )

    score = calculator.calculate(

        search_index

    )

    assert score == 0.0

    print(
        "PASS: test_zero_confidence"
    )


# ==========================================
# None Confidence
# ==========================================


def test_none_confidence():

    calculator = ConfidenceScoreCalculator()

    search_index = MockSearchIndex(

        confidence=None

    )

    score = calculator.calculate(

        search_index

    )

    assert score == 0.0

    print(
        "PASS: test_none_confidence"
    )


# ==========================================
# Missing Confidence
# ==========================================


def test_missing_confidence():

    calculator = ConfidenceScoreCalculator()

    search_index = object()

    score = calculator.calculate(

        search_index

    )

    assert score == 0.0

    print(
        "PASS: test_missing_confidence"
    )


# ==========================================
# String Confidence
# ==========================================


def test_string_confidence():

    calculator = ConfidenceScoreCalculator()

    search_index = MockSearchIndex(

        confidence="0.8"

    )

    score = calculator.calculate(

        search_index

    )

    assert score == 8.0

    print(
        "PASS: test_string_confidence"
    )


# ==========================================
# Invalid Confidence
# ==========================================


def test_invalid_confidence():

    calculator = ConfidenceScoreCalculator()

    search_index = MockSearchIndex(

        confidence="invalid"

    )

    score = calculator.calculate(

        search_index

    )

    assert score == 0.0

    print(
        "PASS: test_invalid_confidence"
    )


# ==========================================
# Confidence Above Maximum
# ==========================================


def test_confidence_above_maximum():

    calculator = ConfidenceScoreCalculator()

    search_index = MockSearchIndex(

        confidence=1.5

    )

    score = calculator.calculate(

        search_index

    )

    assert score == 10.0

    print(
        "PASS: test_confidence_above_maximum"
    )


# ==========================================
# Confidence Below Minimum
# ==========================================


def test_confidence_below_minimum():

    calculator = ConfidenceScoreCalculator()

    search_index = MockSearchIndex(

        confidence=-0.5

    )

    score = calculator.calculate(

        search_index

    )

    assert score == 0.0

    print(
        "PASS: test_confidence_below_minimum"
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
        "P2.6 Step 6"
    )

    print(
        "Confidence Score Calculator Test"
    )

    print(
        "=========="
    )

    print()


    tests = [

        test_full_confidence,

        test_high_confidence,

        test_medium_confidence,

        test_low_confidence,

        test_zero_confidence,

        test_none_confidence,

        test_missing_confidence,

        test_string_confidence,

        test_invalid_confidence,

        test_confidence_above_maximum,

        test_confidence_below_minimum

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
