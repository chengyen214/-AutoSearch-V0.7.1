"""
services/keyword_matching_service.py

AutoSearch V5

V5.3 P3.7

Keyword Matching Service

用途：

    判斷 Target Keyword 是否符合 Source Keyword。

架構：

    Target
        ↓
    KeywordMatchingService
        ↓
    Keyword Match Result

負責：

    - Keyword Normalization
    - Exact Keyword Matching
    - Case-insensitive Matching
    - Whitespace Normalization
    - Empty Keyword Handling

不負責：

    - Search Provider
    - Search API
    - SearchAdapter
    - Website
    - HTTP Request
    - Crawler
    - Parser
    - Article
    - Database
    - Archive
    - AI
    - Translation

設計原則：

    P3.7 只回答：

        「Target Keyword 是否符合 Source Keyword？」

    不回答：

        「要去哪裡搜尋？」
        「怎麼搜尋？」
        「怎麼下載？」
"""


class KeywordMatchingService:
    """
    V5.3 P3.7 Keyword Matching Service。

    負責 Target Keyword 與 Source Keyword
    的標準化與匹配。

    此 Service 不執行實際搜尋。
    """

    # ==================================================
    # Constructor
    # ==================================================

    def __init__(
        self,
        case_sensitive=False,
    ):
        """
        建立 KeywordMatchingService。

        Parameters
        ----------
        case_sensitive : bool
            是否區分大小寫。

        預設：

            False

        因此：

            AI Semiconductor
            ai semiconductor

        會被視為相同 Keyword。
        """

        if not isinstance(
            case_sensitive,
            bool,
        ):
            raise TypeError(
                "case_sensitive must be a boolean"
            )

        self.case_sensitive = case_sensitive

    # ==================================================
    # Normalize Keyword
    # ==================================================

    @staticmethod
    def normalize_keyword(
        keyword,
    ):
        """
        Normalize Keyword。

        處理：

            - None
            - 非字串
            - 前後空白
            - 多餘空白

        Example
        -------

        "  AI   semiconductor  "

        →

        "AI semiconductor"

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
    # Normalize For Matching
    # ==================================================

    def normalize_for_matching(
        self,
        keyword,
    ):
        """
        建立實際用於 Matching 的 Keyword。

        流程：

            Normalize
                ↓
            Case Normalization
        """

        normalized = (
            self.normalize_keyword(
                keyword
            )
        )

        if not self.case_sensitive:
            normalized = normalized.casefold()

        return normalized

    # ==================================================
    # Is Empty
    # ==================================================

    @classmethod
    def is_empty(
        cls,
        keyword,
    ):
        """
        判斷 Keyword 是否為空。

        以下都視為空：

            None
            ""
            "   "
        """

        return (
            cls.normalize_keyword(
                keyword
            )
            == ""
        )

    # ==================================================
    # Match
    # ==================================================

    def matches(
        self,
        target_keyword,
        source_keyword,
    ):
        """
        判斷 Target Keyword 是否與 Source Keyword
        完全匹配。

        預設不區分大小寫。

        Example
        -------

        matches(
            "AI Semiconductor",
            "ai semiconductor",
        )

        →

        True
        """

        target = (
            self.normalize_for_matching(
                target_keyword
            )
        )

        source = (
            self.normalize_for_matching(
                source_keyword
            )
        )

        # ----------------------------------------------
        # Empty Keyword
        # ----------------------------------------------

        if not target:
            return False

        if not source:
            return False

        # ----------------------------------------------
        # Exact Match
        # ----------------------------------------------

        return target == source

    # ==================================================
    # Match Target
    # ==================================================

    def matches_target(
        self,
        target,
        source_keyword,
    ):
        """
        使用 Target Model 的 Keyword
        與 Source Keyword 進行匹配。

        此方法不負責 Target Validation。

        Target 必須具有：

            keyword

        屬性。
        """

        if target is None:
            raise TypeError(
                "target cannot be None"
            )

        if not hasattr(
            target,
            "keyword",
        ):
            raise TypeError(
                "target must have a keyword attribute"
            )

        return self.matches(
            target.keyword,
            source_keyword,
        )

    # ==================================================
    # Match Any
    # ==================================================

    def matches_any(
        self,
        target_keyword,
        source_keywords,
    ):
        """
        判斷 Target Keyword 是否符合
        任一 Source Keyword。

        Example
        -------

        Target：

            "semiconductor"

        Sources：

            [
                "AI",
                "semiconductor",
                "TSMC",
            ]

        →

        True
        """

        if source_keywords is None:
            return False

        target = (
            self.normalize_for_matching(
                target_keyword
            )
        )

        if not target:
            return False

        for source_keyword in source_keywords:

            source = (
                self.normalize_for_matching(
                    source_keyword
                )
            )

            if (
                source
                and target == source
            ):
                return True

        return False

    # ==================================================
    # Match All
    # ==================================================

    def matches_all(
        self,
        target_keyword,
        source_keywords,
    ):
        """
        判斷所有 Source Keywords
        是否都與 Target Keyword 相同。

        注意：

            空的 source_keywords
            回傳 False。
        """

        if source_keywords is None:
            return False

        source_keywords = list(
            source_keywords
        )

        if not source_keywords:
            return False

        target = (
            self.normalize_for_matching(
                target_keyword
            )
        )

        if not target:
            return False

        for source_keyword in source_keywords:

            source = (
                self.normalize_for_matching(
                    source_keyword
                )
            )

            if (
                not source
                or source != target
            ):
                return False

        return True

    # ==================================================
    # Compare
    # ==================================================

    def compare(
        self,
        target_keyword,
        source_keyword,
    ):
        """
        比較 Target Keyword 與 Source Keyword。

        Returns
        -------

        dict

        Example
        -------

        {
            "target_keyword": "AI Semiconductor",
            "source_keyword": "ai semiconductor",
            "normalized_target": "ai semiconductor",
            "normalized_source": "ai semiconductor",
            "matched": True
        }
        """

        normalized_target = (
            self.normalize_for_matching(
                target_keyword
            )
        )

        normalized_source = (
            self.normalize_for_matching(
                source_keyword
            )
        )

        matched = (
            bool(normalized_target)
            and bool(normalized_source)
            and normalized_target
            == normalized_source
        )

        return {
            "target_keyword": target_keyword,
            "source_keyword": source_keyword,
            "normalized_target": normalized_target,
            "normalized_source": normalized_source,
            "matched": matched,
        }


# ==================================================
# Default Service
# ==================================================

default_keyword_matching_service = (
    KeywordMatchingService()
)


# ==================================================
# Convenience Functions
# ==================================================

def normalize_keyword(
    keyword,
):
    """
    Normalize Keyword。
    """

    return (
        default_keyword_matching_service
        .normalize_keyword(
            keyword
        )
    )


def keywords_match(
    target_keyword,
    source_keyword,
):
    """
    判斷兩個 Keyword 是否匹配。
    """

    return (
        default_keyword_matching_service
        .matches(
            target_keyword,
            source_keyword,
        )
    )


def keyword_matches_any(
    target_keyword,
    source_keywords,
):
    """
    判斷 Target Keyword 是否符合
    任一 Source Keyword。
    """

    return (
        default_keyword_matching_service
        .matches_any(
            target_keyword,
            source_keywords,
        )
    )


# ==================================================
# Public API
# ==================================================

__all__ = [
    "KeywordMatchingService",
    "default_keyword_matching_service",
    "normalize_keyword",
    "keywords_match",
    "keyword_matches_any",
]