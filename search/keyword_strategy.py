"""
search/keyword_strategy.py

AutoSearch V4

P4.7 Keyword / Language Source Strategy

功能:

1. 定義 Search Source Language
2. 管理不同 Source 的 Keyword Strategy
3. 提供統一 Keyword 取得介面
4. 支援:
       Google News
       TSMC
       Intel Newsroom
5. 未知 Source 使用 auto strategy
6. 保持既有 SearchAdapter Interface 不變

P4.7 架構:

User Keyword
    ↓
KeywordStrategy
    ↓
Source Language Strategy
    │
    ├── Google News
    │      └── auto
    │
    ├── TSMC
    │      └── zh
    │
    └── Intel Newsroom
           └── en

注意:

本模組不負責:

- Search
- HTTP Request
- HTML Download
- Parser
- Article
- Archive
- AI
- Database
"""


# ==================================================
#
# Source Language
#
# ==================================================


class SourceLanguage:
    """
    Search Source Language 定義。

    P4.7
    """

    AUTO = "auto"

    ZH = "zh"

    EN = "en"


# ==================================================
#
# Source Language Registry
#
# ==================================================


DEFAULT_SOURCE_LANGUAGES = {

    # ----------------------------------------------
    # Google News
    #
    # Google News 本身支援多語搜尋。
    # 保留原始 keyword。
    # ----------------------------------------------

    "google_news": (
        SourceLanguage.AUTO
    ),

    # ----------------------------------------------
    # TSMC
    #
    # TSMC Press Center
    # ----------------------------------------------

    "tsmc": (
        SourceLanguage.ZH
    ),

    # ----------------------------------------------
    # Intel Newsroom
    #
    # Intel 官方 Newsroom
    # ----------------------------------------------

    "intel": (
        SourceLanguage.EN
    ),

}


# ==================================================
#
# Keyword Strategy
#
# ==================================================


class KeywordStrategy:
    """
    P4.7 Keyword / Language Source Strategy。

    負責:

        1. Source Language Registry
        2. Keyword Normalization
        3. Source-specific Keyword Strategy

    不負責實際 Search。
    """

    def __init__(
        self,
        source_languages=None,
    ):
        """
        Parameters
        ----------

        source_languages:
            自訂 Source Language Registry。

        若未指定:

            使用 DEFAULT_SOURCE_LANGUAGES
        """

        if source_languages is None:

            source_languages = (
                DEFAULT_SOURCE_LANGUAGES.copy()
            )

        self.source_languages = (
            source_languages
        )

    # ==================================================
    #
    # Normalize Keyword
    #
    # ==================================================

    @staticmethod
    def normalize_keyword(
        keyword,
    ):
        """
        Normalize 使用者 Keyword。

        處理:

            None
            非字串
            前後空白
            多餘空白

        Returns
        -------

        str
        """

        if keyword is None:

            return ""

        if not isinstance(
            keyword,
            str,
        ):

            keyword = str(
                keyword
            )

        return " ".join(
            keyword.strip().split()
        )

    # ==================================================
    #
    # Get Source Language
    #
    # ==================================================

    def get_language(
        self,
        search_source,
    ):
        """
        取得 Search Source Language。

        未註冊 Source:

            auto
        """

        if not search_source:

            return SourceLanguage.AUTO

        language = (
            self.source_languages.get(
                search_source,
                SourceLanguage.AUTO,
            )
        )

        # ----------------------------------------------
        # Validate Language
        # ----------------------------------------------

        if language not in (
            SourceLanguage.AUTO,
            SourceLanguage.ZH,
            SourceLanguage.EN,
        ):

            return SourceLanguage.AUTO

        return language

    # ==================================================
    #
    # Get Keyword
    #
    # ==================================================

    def get_keyword(
        self,
        keyword,
        search_source,
    ):
        """
        取得指定 Search Source 使用的 Keyword。

        P4.7 第一階段:

            不自動翻譯 Keyword。

        Strategy 只負責:

            Keyword Normalize
            +
            Source Language Identity

        因此目前:

            auto → 原始 Keyword
            zh   → 原始 Keyword
            en   → 原始 Keyword

        後續若需要 Translation Strategy，
        可以在本模組擴充。

        Returns
        -------

        str
        """

        normalized_keyword = (
            self.normalize_keyword(
                keyword
            )
        )

        if not normalized_keyword:

            return ""

        # ----------------------------------------------
        # 取得 Source Language
        # ----------------------------------------------

        self.get_language(
            search_source
        )

        # ----------------------------------------------
        # P4.7 第一階段
        #
        # 不進行自動翻譯。
        #
        # ----------------------------------------------

        return normalized_keyword

    # ==================================================
    #
    # Build Search Context
    #
    # ==================================================

    def build_context(
        self,
        keyword,
        search_source,
    ):
        """
        建立 Search Source Keyword Context。

        Returns
        -------

        dict
        """

        normalized_keyword = (
            self.normalize_keyword(
                keyword
            )
        )

        language = (
            self.get_language(
                search_source
            )
        )

        source_keyword = (
            self.get_keyword(
                normalized_keyword,
                search_source,
            )
        )

        return {

            "keyword": normalized_keyword,

            "search_source": search_source,

            "language": language,

            "source_keyword": source_keyword,

        }


# ==================================================
#
# Default Strategy
#
# ==================================================


default_keyword_strategy = (
    KeywordStrategy()
)


# ==================================================
#
# Convenience Functions
#
# ==================================================


def get_source_language(
    search_source,
):
    """
    取得 Source Language。

    使用:

        get_source_language("tsmc")

    Returns:

        "zh"
    """

    return default_keyword_strategy.get_language(
        search_source
    )


def get_source_keyword(
    keyword,
    search_source,
):
    """
    取得 Source Keyword。

    使用:

        get_source_keyword(
            "IC semiconductor",
            "intel",
        )
    """

    return default_keyword_strategy.get_keyword(
        keyword,
        search_source,
    )


def build_keyword_context(
    keyword,
    search_source,
):
    """
    建立 Source Keyword Context。
    """

    return default_keyword_strategy.build_context(
        keyword,
        search_source,
    )


# ==================================================
#
# Export
#
# ==================================================


__all__ = [

    "SourceLanguage",

    "DEFAULT_SOURCE_LANGUAGES",

    "KeywordStrategy",

    "default_keyword_strategy",

    "get_source_language",

    "get_source_keyword",

    "build_keyword_context",

]
