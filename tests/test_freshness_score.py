"""
tests/test_freshness_score.py

AutoSearch V4

P2.6 Step 7

Freshness Score Calculator Test

Purpose:

    Test Freshness Score calculation.

Test Scope:

    1. Fresh data
    2. 1 day boundary
    3. 7 day boundary
    4. 30 day boundary
    5. 90 day boundary
    6. 180 day boundary
    7. 365 day boundary
    8. Older than 365 days
    9. None search index
    10. Missing published
    11. Empty published
    12. Invalid published
    13. ISO datetime parsing
    14. Date object parsing
"""


from datetime import (
    datetime,
    timedelta,
    date
)


from services.ranking.freshness_score import (
    FreshnessScoreCalculator
)


class MockSearchIndex:
    """
    Minimal SearchIndex object
    used for unit testing.
    """

    def __init__(
        self,
        published=None
    ):

        self.published = published


# ==========================================
# Freshness Score Tests
# ==========================================


def test_fresh_data():

    calculator = FreshnessScoreCalculator()

    now = datetime(
        2026,
        8,
        13,
        12,
        0,
        0
    )

    search_index = MockSearchIndex(

        published=now

    )

    score = calculator.calculate(

        search_index,

        now=now

    )

    assert score == 10.0

    print(
        "PASS: test_fresh_data"
    )


def test_one_day_boundary():

    calculator = FreshnessScoreCalculator()

    now = datetime(
        2026,
        8,
        13
    )

    published = (
        now - timedelta(days=1)
    )

    search_index = MockSearchIndex(
        published=published
    )

    score = calculator.calculate(

        search_index,

        now=now

    )

    assert score == 10.0

    print(
        "PASS: test_one_day_boundary"
    )


def test_seven_day_boundary():

    calculator = FreshnessScoreCalculator()

    now = datetime(
        2026,
        8,
        13
    )

    published = (
        now - timedelta(days=7)
    )

    search_index = MockSearchIndex(
        published=published
    )

    score = calculator.calculate(

        search_index,

        now=now

    )

    assert score == 9.0

    print(
        "PASS: test_seven_day_boundary"
    )


def test_thirty_day_boundary():

    calculator = FreshnessScoreCalculator()

    now = datetime(
        2026,
        8,
        13
    )

    published = (
        now - timedelta(days=30)
    )

    search_index = MockSearchIndex(
        published=published
    )

    score = calculator.calculate(

        search_index,

        now=now

    )

    assert score == 8.0

    print(
        "PASS: test_thirty_day_boundary"
    )


def test_ninety_day_boundary():

    calculator = FreshnessScoreCalculator()

    now = datetime(
        2026,
        8,
        13
    )

    published = (
        now - timedelta(days=90)
    )

    search_index = MockSearchIndex(
        published=published
    )

    score = calculator.calculate(

        search_index,

        now=now

    )

    assert score == 6.0

    print(
        "PASS: test_ninety_day_boundary"
    )


def test_one_hundred_eighty_day_boundary():

    calculator = FreshnessScoreCalculator()

    now = datetime(
        2026,
        8,
        13
    )

    published = (
        now - timedelta(days=180)
    )

    search_index = MockSearchIndex(
        published=published
    )

    score = calculator.calculate(

        search_index,

        now=now

    )

    assert score == 4.0

    print(
        "PASS: test_one_hundred_eighty_day_boundary"
    )


def test_three_hundred_sixty_five_day_boundary():

    calculator = FreshnessScoreCalculator()

    now = datetime(
        2026,
        8,
        13
    )

    published = (
        now - timedelta(days=365)
    )

    search_index = MockSearchIndex(
        published=published
    )

    score = calculator.calculate(

        search_index,

        now=now

    )

    assert score == 2.0

    print(
        "PASS: test_three_hundred_sixty_five_day_boundary"
    )


def test_older_than_one_year():

    calculator = FreshnessScoreCalculator()

    now = datetime(
        2026,
        8,
        13
    )

    published = (
        now - timedelta(days=366)
    )

    search_index = MockSearchIndex(
        published=published
    )

    score = calculator.calculate(

        search_index,

        now=now

    )

    assert score == 0.0

    print(
        "PASS: test_older_than_one_year"
    )


# ==========================================
# Edge Cases
# ==========================================


def test_none_search_index():

    calculator = FreshnessScoreCalculator()

    score = calculator.calculate(

        None

    )

    assert score == 0.0

    print(
        "PASS: test_none_search_index"
    )


def test_missing_published():

    calculator = FreshnessScoreCalculator()

    class EmptySearchIndex:
        pass

    search_index = EmptySearchIndex()

    score = calculator.calculate(

        search_index

    )

    assert score == 0.0

    print(
        "PASS: test_missing_published"
    )


def test_empty_published():

    calculator = FreshnessScoreCalculator()

    search_index = MockSearchIndex(

        published=""

    )

    score = calculator.calculate(

        search_index

    )

    assert score == 0.0

    print(
        "PASS: test_empty_published"
    )


def test_invalid_published():

    calculator = FreshnessScoreCalculator()

    search_index = MockSearchIndex(

        published="invalid-date"

    )

    score = calculator.calculate(

        search_index

    )

    assert score == 0.0

    print(
        "PASS: test_invalid_published"
    )


# ==========================================
# Date Parsing
# ==========================================


def test_iso_datetime_parsing():

    calculator = FreshnessScoreCalculator()

    now = datetime(
        2026,
        8,
        13
    )

    search_index = MockSearchIndex(

        published="2026-08-12T12:00:00"

    )

    score = calculator.calculate(

        search_index,

        now=now

    )

    assert score == 10.0

    print(
        "PASS: test_iso_datetime_parsing"
    )


def test_date_object_parsing():

    calculator = FreshnessScoreCalculator()

    now = datetime(
        2026,
        8,
        13
    )

    search_index = MockSearchIndex(

        published=date(
            2026,
            8,
            12
        )

    )

    score = calculator.calculate(

        search_index,

        now=now

    )

    assert score == 10.0

    print(
        "PASS: test_date_object_parsing"
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
        "P2.6 Step 7"
    )

    print(
        "Freshness Score Calculator Test"
    )

    print(
        "=========="
    )

    print()

    tests = [

        # ------------------------------
        # Freshness
        # ------------------------------

        test_fresh_data,
        test_one_day_boundary,
        test_seven_day_boundary,
        test_thirty_day_boundary,
        test_ninety_day_boundary,
        test_one_hundred_eighty_day_boundary,
        test_three_hundred_sixty_five_day_boundary,
        test_older_than_one_year,

        # ------------------------------
        # Edge Cases
        # ------------------------------

        test_none_search_index,
        test_missing_published,
        test_empty_published,
        test_invalid_published,

        # ------------------------------
        # Parsing
        # ------------------------------

        test_iso_datetime_parsing,
        test_date_object_parsing

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
