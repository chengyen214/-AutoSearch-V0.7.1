"""
tests/test_final_search_score.py

AutoSearch V4

P2.6 Step 9

Final Search Score Test

Purpose:

    Test KnowledgeSearchScore.final_score.

Formula:

    Keyword      25%
    Entity       20%
    Topic        10%
    Importance   15%
    Confidence   10%
    Freshness    10%
    Ranking      10%

    Total        100%

Test Scope:

    1. All maximum scores
    2. All zero scores
    3. Keyword only
    4. Entity only
    5. Topic only
    6. Importance only
    7. Confidence only
    8. Freshness only
    9. Ranking only
    10. Mixed scores
    11. Complete ranking score
    12. Final score rounding
    13. Dictionary output
    14. Representation
"""


from models.knowledge_search_score import (
    KnowledgeSearchScore
)


# ==========================================
# All Score Tests
# ==========================================


def test_all_maximum_scores():

    score = KnowledgeSearchScore(

        keyword_score=10,

        entity_score=10,

        topic_score=10,

        importance_score=10,

        confidence_score=10,

        freshness_score=10,

        ranking_score=10

    )

    assert score.final_score == 10.0

    print(
        "PASS: test_all_maximum_scores"
    )


def test_all_zero_scores():

    score = KnowledgeSearchScore(

        keyword_score=0,

        entity_score=0,

        topic_score=0,

        importance_score=0,

        confidence_score=0,

        freshness_score=0,

        ranking_score=0

    )

    assert score.final_score == 0.0

    print(
        "PASS: test_all_zero_scores"
    )


# ==========================================
# Individual Weight Tests
# ==========================================


def test_keyword_only():

    score = KnowledgeSearchScore(

        keyword_score=10

    )

    assert score.final_score == 2.5

    print(
        "PASS: test_keyword_only"
    )


def test_entity_only():

    score = KnowledgeSearchScore(

        entity_score=10

    )

    assert score.final_score == 2.0

    print(
        "PASS: test_entity_only"
    )


def test_topic_only():

    score = KnowledgeSearchScore(

        topic_score=10

    )

    assert score.final_score == 1.0

    print(
        "PASS: test_topic_only"
    )


def test_importance_only():

    score = KnowledgeSearchScore(

        importance_score=10

    )

    assert score.final_score == 1.5

    print(
        "PASS: test_importance_only"
    )


def test_confidence_only():

    score = KnowledgeSearchScore(

        confidence_score=10

    )

    assert score.final_score == 1.0

    print(
        "PASS: test_confidence_only"
    )


def test_freshness_only():

    score = KnowledgeSearchScore(

        freshness_score=10

    )

    assert score.final_score == 1.0

    print(
        "PASS: test_freshness_only"
    )


def test_ranking_only():

    score = KnowledgeSearchScore(

        ranking_score=10

    )

    assert score.final_score == 1.0

    print(
        "PASS: test_ranking_only"
    )


# ==========================================
# Mixed Score Tests
# ==========================================


def test_mixed_scores():

    score = KnowledgeSearchScore(

        keyword_score=8,

        entity_score=6,

        topic_score=7,

        importance_score=9,

        confidence_score=8,

        freshness_score=5,

        ranking_score=7

    )

    expected = round(

        8 * 0.25

        + 6 * 0.20

        + 7 * 0.10

        + 9 * 0.15

        + 8 * 0.10

        + 5 * 0.10

        + 7 * 0.10,

        2

    )

    assert score.final_score == expected

    print(
        "PASS: test_mixed_scores"
    )


def test_complete_ranking_score():

    score = KnowledgeSearchScore(

        keyword_score=10,

        entity_score=8,

        topic_score=6,

        importance_score=9,

        confidence_score=8,

        freshness_score=7,

        ranking_score=9

    )

    # Expected:
    #
    # 10 * 0.25 = 2.50
    #  8 * 0.20 = 1.60
    #  6 * 0.10 = 0.60
    #  9 * 0.15 = 1.35
    #  8 * 0.10 = 0.80
    #  7 * 0.10 = 0.70
    #  9 * 0.10 = 0.90
    #
    # Total = 8.45

    assert score.final_score == 8.45

    print(
        "PASS: test_complete_ranking_score"
    )


# ==========================================
# Rounding
# ==========================================


def test_final_score_rounding():

    score = KnowledgeSearchScore(

        keyword_score=1,

        entity_score=2,

        topic_score=3,

        importance_score=4,

        confidence_score=5,

        freshness_score=6,

        ranking_score=7

    )

    expected = round(

        1 * 0.25

        + 2 * 0.20

        + 3 * 0.10

        + 4 * 0.15

        + 5 * 0.10

        + 6 * 0.10

        + 7 * 0.10,

        2

    )

    assert score.final_score == expected

    assert isinstance(
        score.final_score,
        float
    )

    print(
        "PASS: test_final_score_rounding"
    )


# ==========================================
# Dictionary
# ==========================================


def test_to_dict_contains_final_score():

    score = KnowledgeSearchScore(

        keyword_score=10,

        entity_score=8,

        topic_score=6,

        importance_score=9,

        confidence_score=8,

        freshness_score=7,

        ranking_score=9

    )

    data = score.to_dict()

    assert (
        "final_score"
        in data
    )

    assert (
        data["final_score"]
        == 8.45
    )

    print(
        "PASS: test_to_dict_contains_final_score"
    )


# ==========================================
# Representation
# ==========================================


def test_repr_contains_final_score():

    score = KnowledgeSearchScore(

        keyword_score=10,

        entity_score=10,

        topic_score=10,

        importance_score=10,

        confidence_score=10,

        freshness_score=10,

        ranking_score=10

    )

    result = repr(
        score
    )

    assert (
        "KnowledgeSearchScore"
        in result
    )

    assert (
        "10.0"
        in result
    )

    print(
        "PASS: test_repr_contains_final_score"
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
        "P2.6 Step 9"
    )

    print(
        "Final Search Score Test"
    )

    print(
        "=========="
    )

    print()


    tests = [

        # ------------------------------
        # All Scores
        # ------------------------------

        test_all_maximum_scores,

        test_all_zero_scores,

        # ------------------------------
        # Individual Weights
        # ------------------------------

        test_keyword_only,

        test_entity_only,

        test_topic_only,

        test_importance_only,

        test_confidence_only,

        test_freshness_only,

        test_ranking_only,

        # ------------------------------
        # Mixed Scores
        # ------------------------------

        test_mixed_scores,

        test_complete_ranking_score,

        # ------------------------------
        # Rounding
        # ------------------------------

        test_final_score_rounding,

        # ------------------------------
        # Output
        # ------------------------------

        test_to_dict_contains_final_score,

        test_repr_contains_final_score

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
