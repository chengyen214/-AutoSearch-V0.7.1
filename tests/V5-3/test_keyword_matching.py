"""
tests/V5-3/test_keyword_matching.py

AutoSearch V5

V5.3 P3.7

Keyword Matching Service Tests

測試：

    - Keyword Normalization
    - Case-insensitive Matching
    - Case-sensitive Matching
    - Whitespace Normalization
    - Empty Keyword Handling
    - Exact Keyword Matching
    - Target Keyword Matching
    - Match Any
    - Match All
    - Keyword Comparison
    - Invalid Configuration
    - Invalid Target
"""


import pytest

from services.keyword_matching_service import (
    KeywordMatchingService,
)

from models.target import Target


# ==================================================
# Fixtures
# ==================================================


@pytest.fixture
def service():

    return KeywordMatchingService()


@pytest.fixture
def case_sensitive_service():

    return KeywordMatchingService(
        case_sensitive=True
    )


# ==================================================
# Keyword Normalization
# ==================================================


def test_normalize_none():

    result = (
        KeywordMatchingService
        .normalize_keyword(
            None
        )
    )

    assert result == ""


def test_normalize_empty_string():

    result = (
        KeywordMatchingService
        .normalize_keyword(
            ""
        )
    )

    assert result == ""


def test_normalize_surrounding_spaces():

    result = (
        KeywordMatchingService
        .normalize_keyword(
            "  AI Semiconductor  "
        )
    )

    assert result == "AI Semiconductor"


def test_normalize_multiple_spaces():

    result = (
        KeywordMatchingService
        .normalize_keyword(
            "AI    Semiconductor"
        )
    )

    assert result == "AI Semiconductor"


def test_normalize_tabs_and_newlines():

    result = (
        KeywordMatchingService
        .normalize_keyword(
            "AI\t\nSemiconductor"
        )
    )

    assert result == "AI Semiconductor"


def test_normalize_non_string_value():

    result = (
        KeywordMatchingService
        .normalize_keyword(
            12345
        )
    )

    assert result == "12345"


# ==================================================
# Empty Keyword
# ==================================================


def test_is_empty_none():

    assert (
        KeywordMatchingService
        .is_empty(None)
        is True
    )


def test_is_empty_blank():

    assert (
        KeywordMatchingService
        .is_empty("   ")
        is True
    )


def test_is_empty_valid_keyword():

    assert (
        KeywordMatchingService
        .is_empty("AI")
        is False
    )


# ==================================================
# Case-insensitive Matching
# ==================================================


def test_matching_is_case_insensitive(
    service,
):

    assert service.matches(
        "AI Semiconductor",
        "ai semiconductor",
    )


def test_matching_uppercase_and_lowercase(
    service,
):

    assert service.matches(
        "AI",
        "ai",
    )


def test_matching_mixed_case(
    service,
):

    assert service.matches(
        "Ai SeMiCoNdUcToR",
        "aI sEmIcOnDuCtOr",
    )


# ==================================================
# Case-sensitive Matching
# ==================================================


def test_case_sensitive_matching_rejects_different_case(
    case_sensitive_service,
):

    assert not case_sensitive_service.matches(
        "AI",
        "ai",
    )


def test_case_sensitive_matching_accepts_same_case(
    case_sensitive_service,
):

    assert case_sensitive_service.matches(
        "AI",
        "AI",
    )


# ==================================================
# Whitespace Matching
# ==================================================


def test_matching_ignores_surrounding_spaces(
    service,
):

    assert service.matches(
        "  AI Semiconductor  ",
        "AI Semiconductor",
    )


def test_matching_ignores_multiple_spaces(
    service,
):

    assert service.matches(
        "AI   Semiconductor",
        "AI Semiconductor",
    )


def test_matching_ignores_tabs(
    service,
):

    assert service.matches(
        "AI\tSemiconductor",
        "AI Semiconductor",
    )


# ==================================================
# Exact Matching
# ==================================================


def test_exact_keyword_match(
    service,
):

    assert service.matches(
        "semiconductor",
        "semiconductor",
    )


def test_different_keyword_does_not_match(
    service,
):

    assert not service.matches(
        "semiconductor",
        "TSMC",
    )


def test_partial_keyword_does_not_match(
    service,
):

    assert not service.matches(
        "AI semiconductor",
        "AI",
    )


def test_extended_keyword_does_not_match(
    service,
):

    assert not service.matches(
        "AI",
        "AI semiconductor",
    )


# ==================================================
# Empty Keyword Matching
# ==================================================


def test_empty_target_does_not_match(
    service,
):

    assert not service.matches(
        "",
        "AI",
    )


def test_empty_source_does_not_match(
    service,
):

    assert not service.matches(
        "AI",
        "",
    )


def test_both_empty_do_not_match(
    service,
):

    assert not service.matches(
        "",
        "",
    )


def test_whitespace_only_target_does_not_match(
    service,
):

    assert not service.matches(
        "   ",
        "AI",
    )


def test_whitespace_only_source_does_not_match(
    service,
):

    assert not service.matches(
        "AI",
        "   ",
    )


# ==================================================
# Target Matching
# ==================================================


def test_matches_target(
    service,
):

    target = Target(
        name="AI Target",
        target_type="search",
        keyword="AI Semiconductor",
        search_provider="google_search",
    )

    assert service.matches_target(
        target,
        "ai semiconductor",
    )


def test_matches_target_rejects_different_keyword(
    service,
):

    target = Target(
        name="AI Target",
        target_type="search",
        keyword="AI Semiconductor",
        search_provider="google_search",
    )

    assert not service.matches_target(
        target,
        "TSMC",
    )


def test_matches_target_requires_keyword_attribute(
    service,
):

    class InvalidTarget:
        pass

    with pytest.raises(
        TypeError,
        match="keyword attribute",
    ):

        service.matches_target(
            InvalidTarget(),
            "AI",
        )


def test_matches_target_rejects_none(
    service,
):

    with pytest.raises(
        TypeError,
        match="target cannot be None",
    ):

        service.matches_target(
            None,
            "AI",
        )


# ==================================================
# Match Any
# ==================================================


def test_matches_any_finds_matching_keyword(
    service,
):

    assert service.matches_any(
        "semiconductor",
        [
            "AI",
            "semiconductor",
            "TSMC",
        ],
    )


def test_matches_any_returns_false_when_no_match(
    service,
):

    assert not service.matches_any(
        "semiconductor",
        [
            "AI",
            "TSMC",
            "Intel",
        ],
    )


def test_matches_any_is_case_insensitive(
    service,
):

    assert service.matches_any(
        "SEMICONDUCTOR",
        [
            "AI",
            "semiconductor",
        ],
    )


def test_matches_any_handles_none_source_list(
    service,
):

    assert not service.matches_any(
        "AI",
        None,
    )


def test_matches_any_handles_empty_source_list(
    service,
):

    assert not service.matches_any(
        "AI",
        [],
    )


# ==================================================
# Match All
# ==================================================


def test_matches_all_when_all_keywords_match(
    service,
):

    assert service.matches_all(
        "AI",
        [
            "AI",
            "ai",
            " AI ",
        ],
    )


def test_matches_all_returns_false_when_one_differs(
    service,
):

    assert not service.matches_all(
        "AI",
        [
            "AI",
            "TSMC",
        ],
    )


def test_matches_all_handles_none_source_list(
    service,
):

    assert not service.matches_all(
        "AI",
        None,
    )


def test_matches_all_handles_empty_source_list(
    service,
):

    assert not service.matches_all(
        "AI",
        [],
    )


# ==================================================
# Compare
# ==================================================


def test_compare_returns_match_result(
    service,
):

    result = service.compare(
        "AI Semiconductor",
        "ai semiconductor",
    )

    assert result["target_keyword"] == (
        "AI Semiconductor"
    )

    assert result["source_keyword"] == (
        "ai semiconductor"
    )

    assert result["normalized_target"] == (
        "ai semiconductor"
    )

    assert result["normalized_source"] == (
        "ai semiconductor"
    )

    assert result["matched"] is True


def test_compare_returns_non_match_result(
    service,
):

    result = service.compare(
        "AI",
        "TSMC",
    )

    assert result["matched"] is False


def test_compare_empty_keyword(
    service,
):

    result = service.compare(
        "",
        "AI",
    )

    assert result["matched"] is False


# ==================================================
# Service Configuration
# ==================================================


def test_default_service_is_case_insensitive():

    service = KeywordMatchingService()

    assert service.case_sensitive is False


def test_case_sensitive_configuration():

    service = KeywordMatchingService(
        case_sensitive=True
    )

    assert service.case_sensitive is True


def test_invalid_case_sensitive_configuration():

    with pytest.raises(
        TypeError,
        match="case_sensitive must be a boolean",
    ):

        KeywordMatchingService(
            case_sensitive="false"
        )


# ==================================================
# Public Convenience API
# ==================================================


def test_default_keyword_matching_service_exists():

    from services.keyword_matching_service import (
        default_keyword_matching_service,
    )

    assert (
        default_keyword_matching_service
        is not None
    )


def test_normalize_keyword_function():

    from services.keyword_matching_service import (
        normalize_keyword,
    )

    assert normalize_keyword(
        "  AI   Semiconductor  "
    ) == "AI Semiconductor"


def test_keywords_match_function():

    from services.keyword_matching_service import (
        keywords_match,
    )

    assert keywords_match(
        "AI",
        "ai",
    )


def test_keyword_matches_any_function():

    from services.keyword_matching_service import (
        keyword_matches_any,
    )

    assert keyword_matches_any(
        "AI",
        [
            "TSMC",
            "AI",
        ],
    )
