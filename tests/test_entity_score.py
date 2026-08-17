"""
tests/test_entity_score.py

AutoSearch V4

P2.6 Step 3

Entity Score Calculator Test

Purpose:

    Test EntityScoreCalculator.

Test Scope:

    1. Full entity match
    2. Partial entity match
    3. No entity match
    4. Empty entity list
    5. None entity list
    6. Empty query
    7. None query
    8. None search index
    9. Case insensitive entity match
    10. Entity parsing
    11. Entity JSON parsing
    12. Entity tuple parsing
    13. Single entity parsing
    14. Multi-word entity match
    15. Entity tokenization
    16. Score limit
"""


from services.ranking.entity_score import (
    EntityScoreCalculator
)


class MockSearchIndex:
    """
    Minimal SearchIndex object
    used for unit testing.
    """

    def __init__(
        self,
        search_text="",
        entities=None
    ):

        self.search_text = search_text

        self.entities = entities


# ==========================================
# P2.6 Step 3
# Entity Score Tests
# ==========================================


def test_full_entity_match():

    calculator = EntityScoreCalculator()

    search_index = MockSearchIndex(

        "AI NVIDIA semiconductor",

        entities=[
            "NVIDIA",
            "AI",
            "semiconductor"
        ]

    )

    score = calculator.calculate(

        "NVIDIA AI semiconductor",

        search_index

    )

    assert score == 10.0

    print(
        "PASS: test_full_entity_match"
    )


def test_partial_entity_match():

    calculator = EntityScoreCalculator()

    search_index = MockSearchIndex(

        "AI NVIDIA semiconductor",

        entities=[
            "NVIDIA",
            "AI"
        ]

    )

    score = calculator.calculate(

        "NVIDIA AI AMD",

        search_index

    )

    # 2 / 3 * 10 = 6.67

    assert score == 6.67

    print(
        "PASS: test_partial_entity_match"
    )


def test_no_entity_match():

    calculator = EntityScoreCalculator()

    search_index = MockSearchIndex(

        "AI NVIDIA semiconductor",

        entities=[
            "NVIDIA",
            "AI"
        ]

    )

    score = calculator.calculate(

        "AMD Intel",

        search_index

    )

    assert score == 0.0

    print(
        "PASS: test_no_entity_match"
    )


def test_empty_entity_list():

    calculator = EntityScoreCalculator()

    search_index = MockSearchIndex(

        "AI semiconductor",

        entities=[]

    )

    score = calculator.calculate(

        "AI",

        search_index

    )

    assert score == 0.0

    print(
        "PASS: test_empty_entity_list"
    )


def test_none_entity_list():

    calculator = EntityScoreCalculator()

    search_index = MockSearchIndex(

        "AI semiconductor",

        entities=None

    )

    score = calculator.calculate(

        "AI",

        search_index

    )

    assert score == 0.0

    print(
        "PASS: test_none_entity_list"
    )


def test_empty_query():

    calculator = EntityScoreCalculator()

    search_index = MockSearchIndex(

        "AI NVIDIA",

        entities=[
            "AI",
            "NVIDIA"
        ]

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

    calculator = EntityScoreCalculator()

    search_index = MockSearchIndex(

        "AI NVIDIA",

        entities=[
            "AI",
            "NVIDIA"
        ]

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

    calculator = EntityScoreCalculator()

    score = calculator.calculate(

        "AI",

        None

    )

    assert score == 0.0

    print(
        "PASS: test_none_search_index"
    )


def test_case_insensitive_entity_match():

    calculator = EntityScoreCalculator()

    search_index = MockSearchIndex(

        "NVIDIA AI",

        entities=[
            "NVIDIA",
            "AI"
        ]

    )

    score = calculator.calculate(

        "nvidia ai",

        search_index

    )

    assert score == 10.0

    print(
        "PASS: test_case_insensitive_entity_match"
    )


def test_entity_parsing():

    calculator = EntityScoreCalculator()

    search_index = MockSearchIndex(

        "NVIDIA AI",

        entities="NVIDIA,AI"

    )

    entities = calculator._get_entities(

        search_index

    )

    assert entities == [
        "nvidia",
        "ai"
    ]

    print(
        "PASS: test_entity_parsing"
    )


def test_entity_json_parsing():

    calculator = EntityScoreCalculator()

    search_index = MockSearchIndex(

        "NVIDIA AI",

        entities='["NVIDIA", "AI"]'

    )

    entities = calculator._get_entities(

        search_index

    )

    assert entities == [
        "nvidia",
        "ai"
    ]

    print(
        "PASS: test_entity_json_parsing"
    )


def test_entity_tuple_parsing():

    calculator = EntityScoreCalculator()

    search_index = MockSearchIndex(

        "NVIDIA AI",

        entities=(
            "NVIDIA",
            "AI"
        )

    )

    entities = calculator._get_entities(

        search_index

    )

    assert entities == [
        "nvidia",
        "ai"
    ]

    print(
        "PASS: test_entity_tuple_parsing"
    )


def test_single_entity_parsing():

    calculator = EntityScoreCalculator()

    search_index = MockSearchIndex(

        "NVIDIA",

        entities="NVIDIA"

    )

    entities = calculator._get_entities(

        search_index

    )

    assert entities == [
        "nvidia"
    ]

    print(
        "PASS: test_single_entity_parsing"
    )


def test_multi_word_entity_match():

    calculator = EntityScoreCalculator()

    search_index = MockSearchIndex(

        "NVIDIA Corporation AI",

        entities=[
            "NVIDIA Corporation",
            "AI"
        ]

    )

    score = calculator.calculate(

        "NVIDIA AI",

        search_index

    )

    assert score == 10.0

    print(
        "PASS: test_multi_word_entity_match"
    )


def test_entity_tokenization():

    calculator = EntityScoreCalculator()

    tokens = calculator._tokenize_keywords(

        "NVIDIA Corporation AI"

    )

    assert tokens == [
        "nvidia",
        "corporation",
        "ai"
    ]

    print(
        "PASS: test_entity_tokenization"
    )


def test_score_limit():

    calculator = EntityScoreCalculator()

    search_index = MockSearchIndex(

        "NVIDIA AI",

        entities=[
            "NVIDIA",
            "AI"
        ]

    )

    score = calculator.calculate(

        "NVIDIA AI",

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
        "P2.6 Step 3"
    )

    print(
        "Entity Score Test"
    )

    print(
        "=========="
    )

    print()

    tests = [

        test_full_entity_match,
        test_partial_entity_match,
        test_no_entity_match,
        test_empty_entity_list,
        test_none_entity_list,
        test_empty_query,
        test_none_query,
        test_none_search_index,
        test_case_insensitive_entity_match,
        test_entity_parsing,
        test_entity_json_parsing,
        test_entity_tuple_parsing,
        test_single_entity_parsing,
        test_multi_word_entity_match,
        test_entity_tokenization,
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