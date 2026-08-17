"""
tests/test_importance_score.py

AutoSearch V4

P2.6 Step 5

Importance Score Calculator Test

Purpose:

    Test ImportanceScoreCalculator.

Test Scope:

    1. Zero importance
    2. Full importance
    3. Middle importance
    4. None KnowledgeScore
    5. None importance
    6. Negative importance
    7. Importance above maximum
    8. Decimal importance
    9. String importance
    10. Invalid importance
    11. Get importance
"""


from models.knowledge_score import (
    KnowledgeScore
)

from services.ranking.importance_score import (
    ImportanceScoreCalculator
)


# ==========================================
# Basic Score
# ==========================================


def test_zero_importance():

    calculator = ImportanceScoreCalculator()

    knowledge_score = KnowledgeScore(
        importance=0
    )

    score = calculator.calculate(
        knowledge_score
    )

    assert score == 0.0

    print(
        "PASS: test_zero_importance"
    )


def test_full_importance():

    calculator = ImportanceScoreCalculator()

    knowledge_score = KnowledgeScore(
        importance=10
    )

    score = calculator.calculate(
        knowledge_score
    )

    assert score == 10.0

    print(
        "PASS: test_full_importance"
    )


def test_middle_importance():

    calculator = ImportanceScoreCalculator()

    knowledge_score = KnowledgeScore(
        importance=5
    )

    score = calculator.calculate(
        knowledge_score
    )

    assert score == 5.0

    print(
        "PASS: test_middle_importance"
    )


# ==========================================
# None
# ==========================================


def test_none_knowledge_score():

    calculator = ImportanceScoreCalculator()

    score = calculator.calculate(
        None
    )

    assert score == 0.0

    print(
        "PASS: test_none_knowledge_score"
    )


def test_none_importance():

    calculator = ImportanceScoreCalculator()

    knowledge_score = KnowledgeScore(
        importance=None
    )

    score = calculator.calculate(
        knowledge_score
    )

    assert score == 0.0

    print(
        "PASS: test_none_importance"
    )


# ==========================================
# Boundary
# ==========================================


def test_negative_importance():

    calculator = ImportanceScoreCalculator()

    knowledge_score = KnowledgeScore(
        importance=-5
    )

    score = calculator.calculate(
        knowledge_score
    )

    assert score == 0.0

    print(
        "PASS: test_negative_importance"
    )


def test_importance_above_max():

    calculator = ImportanceScoreCalculator()

    knowledge_score = KnowledgeScore(
        importance=20
    )

    score = calculator.calculate(
        knowledge_score
    )

    assert score == 10.0

    print(
        "PASS: test_importance_above_max"
    )


# ==========================================
# Decimal
# ==========================================


def test_decimal_importance():

    calculator = ImportanceScoreCalculator()

    knowledge_score = KnowledgeScore(
        importance=7.5
    )

    score = calculator.calculate(
        knowledge_score
    )

    assert score == 7.5

    print(
        "PASS: test_decimal_importance"
    )


# ==========================================
# String
# ==========================================


def test_string_importance():

    calculator = ImportanceScoreCalculator()

    knowledge_score = KnowledgeScore(
        importance="8"
    )

    score = calculator.calculate(
        knowledge_score
    )

    assert score == 8.0

    print(
        "PASS: test_string_importance"
    )


def test_invalid_importance():

    calculator = ImportanceScoreCalculator()

    knowledge_score = KnowledgeScore(
        importance="invalid"
    )

    score = calculator.calculate(
        knowledge_score
    )

    assert score == 0.0

    print(
        "PASS: test_invalid_importance"
    )


# ==========================================
# Internal Getter
# ==========================================


def test_get_importance():

    calculator = ImportanceScoreCalculator()

    knowledge_score = KnowledgeScore(
        importance=9
    )

    importance = calculator._get_importance(
        knowledge_score
    )

    assert importance == 9.0

    print(
        "PASS: test_get_importance"
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
        "P2.6 Step 5"
    )

    print(
        "Importance Score Test"
    )

    print(
        "=========="
    )

    print()

    tests = [

        test_zero_importance,
        test_full_importance,
        test_middle_importance,

        test_none_knowledge_score,
        test_none_importance,

        test_negative_importance,
        test_importance_above_max,

        test_decimal_importance,

        test_string_importance,
        test_invalid_importance,

        test_get_importance

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
