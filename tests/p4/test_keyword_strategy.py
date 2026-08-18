"""
tests/p4/test_keyword_strategy.py

AutoSearch V4

P4.7 Keyword / Language Source Strategy

測試:

1. Keyword Normalize
2. Source Language
3. Google News Strategy
4. TSMC Strategy
5. Intel Strategy
6. Unknown Source Strategy
7. Source Keyword
8. Keyword Context
9. Custom Source Registry
10. Invalid Language Fallback
"""


from search.keyword_strategy import (
    SourceLanguage,
    DEFAULT_SOURCE_LANGUAGES,
    KeywordStrategy,
    default_keyword_strategy,
    get_source_language,
    get_source_keyword,
    build_keyword_context,
)


# ==================================================
#
# Keyword Normalize
#
# ==================================================


def test_normalize_none():

    result = (
        KeywordStrategy.normalize_keyword(
            None
        )
    )

    assert result == ""


def test_normalize_empty_string():

    result = (
        KeywordStrategy.normalize_keyword(
            ""
        )
    )

    assert result == ""


def test_normalize_whitespace():

    result = (
        KeywordStrategy.normalize_keyword(
            "  IC semiconductor  "
        )
    )

    assert result == "IC semiconductor"


def test_normalize_multiple_spaces():

    result = (
        KeywordStrategy.normalize_keyword(
            "IC    semiconductor"
        )
    )

    assert result == "IC semiconductor"


def test_normalize_non_string():

    result = (
        KeywordStrategy.normalize_keyword(
            12345
        )
    )

    assert result == "12345"


# ==================================================
#
# Source Language
#
# ==================================================


def test_google_news_language():

    strategy = KeywordStrategy()

    assert (
        strategy.get_language(
            "google_news"
        )
        == SourceLanguage.AUTO
    )


def test_tsmc_language():

    strategy = KeywordStrategy()

    assert (
        strategy.get_language(
            "tsmc"
        )
        == SourceLanguage.ZH
    )


def test_intel_language():

    strategy = KeywordStrategy()

    assert (
        strategy.get_language(
            "intel"
        )
        == SourceLanguage.EN
    )


def test_unknown_source_language():

    strategy = KeywordStrategy()

    assert (
        strategy.get_language(
            "unknown_source"
        )
        == SourceLanguage.AUTO
    )


def test_empty_source_language():

    strategy = KeywordStrategy()

    assert (
        strategy.get_language(
            ""
        )
        == SourceLanguage.AUTO
    )


# ==================================================
#
# Default Registry
#
# ==================================================


def test_default_source_registry():

    assert (
        DEFAULT_SOURCE_LANGUAGES[
            "google_news"
        ]
        == SourceLanguage.AUTO
    )

    assert (
        DEFAULT_SOURCE_LANGUAGES[
            "tsmc"
        ]
        == SourceLanguage.ZH
    )

    assert (
        DEFAULT_SOURCE_LANGUAGES[
            "intel"
        ]
        == SourceLanguage.EN
    )


# ==================================================
#
# Source Keyword
#
# ==================================================


def test_google_news_keyword():

    strategy = KeywordStrategy()

    result = (
        strategy.get_keyword(
            "IC semiconductor",
            "google_news",
        )
    )

    assert result == "IC semiconductor"


def test_tsmc_keyword():

    strategy = KeywordStrategy()

    result = (
        strategy.get_keyword(
            "IC semiconductor",
            "tsmc",
        )
    )

    assert result == "IC semiconductor"


def test_intel_keyword():

    strategy = KeywordStrategy()

    result = (
        strategy.get_keyword(
            "IC semiconductor",
            "intel",
        )
    )

    assert result == "IC semiconductor"


def test_empty_keyword():

    strategy = KeywordStrategy()

    result = (
        strategy.get_keyword(
            "",
            "intel",
        )
    )

    assert result == ""


def test_none_keyword():

    strategy = KeywordStrategy()

    result = (
        strategy.get_keyword(
            None,
            "intel",
        )
    )

    assert result == ""


# ==================================================
#
# Keyword Context
#
# ==================================================


def test_google_news_context():

    strategy = KeywordStrategy()

    context = (
        strategy.build_context(
            "IC semiconductor",
            "google_news",
        )
    )

    assert (
        context["keyword"]
        == "IC semiconductor"
    )

    assert (
        context["search_source"]
        == "google_news"
    )

    assert (
        context["language"]
        == SourceLanguage.AUTO
    )

    assert (
        context["source_keyword"]
        == "IC semiconductor"
    )


def test_tsmc_context():

    strategy = KeywordStrategy()

    context = (
        strategy.build_context(
            "IC semiconductor",
            "tsmc",
        )
    )

    assert (
        context["language"]
        == SourceLanguage.ZH
    )

    assert (
        context["source_keyword"]
        == "IC semiconductor"
    )


def test_intel_context():

    strategy = KeywordStrategy()

    context = (
        strategy.build_context(
            "IC semiconductor",
            "intel",
        )
    )

    assert (
        context["language"]
        == SourceLanguage.EN
    )

    assert (
        context["source_keyword"]
        == "IC semiconductor"
    )


# ==================================================
#
# Custom Registry
#
# ==================================================


def test_custom_source_registry():

    strategy = KeywordStrategy(

        source_languages={

            "custom":
                SourceLanguage.EN,

        }

    )

    assert (
        strategy.get_language(
            "custom"
        )
        == SourceLanguage.EN
    )


# ==================================================
#
# Invalid Language
#
# ==================================================


def test_invalid_language_fallback():

    strategy = KeywordStrategy(

        source_languages={

            "invalid":
                "unknown",

        }

    )

    assert (
        strategy.get_language(
            "invalid"
        )
        == SourceLanguage.AUTO
    )


# ==================================================
#
# Convenience Functions
#
# ==================================================


def test_get_source_language():

    assert (
        get_source_language(
            "intel"
        )
        == SourceLanguage.EN
    )


def test_get_source_keyword():

    result = (
        get_source_keyword(
            "  IC    semiconductor  ",
            "intel",
        )
    )

    assert result == "IC semiconductor"


def test_build_keyword_context():

    context = (
        build_keyword_context(
            "IC semiconductor",
            "intel",
        )
    )

    assert context == {

        "keyword":
            "IC semiconductor",

        "search_source":
            "intel",

        "language":
            SourceLanguage.EN,

        "source_keyword":
            "IC semiconductor",

    }


# ==================================================
#
# Default Strategy
#
# ==================================================


def test_default_keyword_strategy():

    assert isinstance(
        default_keyword_strategy,
        KeywordStrategy,
    )