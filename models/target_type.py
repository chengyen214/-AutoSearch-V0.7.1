"""
models/target_type.py

AutoSearch V5

V5.1 P1.3

Target Type Definition

用途：

    定義 V5 Target 支援的 Target Type。

目前支援：

    website
    rss
    api
    custom

設計：

    Target
        ↓
    Target Type
        ↓
    Existing V4 Crawl Pipeline

Target Type 不負責：

    - Crawler
    - Search Adapter
    - Parser
    - Article
    - Archive
    - Duplicate Detection
    - AI Analysis


重要：

    Target Type 目前只負責：

        1. Type Definition
        2. Type Validation
        3. Type Normalization
        4. Type Display Name

    實際 Target 執行邏輯：

        後續 P1.4 / P1.5 / Pipeline Integration
        再處理。
"""


class TargetType:
    """
    V5 Target Type Definition。

    使用字串作為 Database 儲存值，
    避免修改目前 targets.target_type
    的 varchar(50) Schema。
    """

    # ==================================
    # Target Types
    # ==================================

    WEBSITE = "website"

    RSS = "rss"

    API = "api"

    CUSTOM = "custom"

    # ==================================
    # All Types
    # ==================================

    ALL = (

        WEBSITE,

        RSS,

        API,

        CUSTOM

    )

    # ==================================
    # Validation
    # ==================================

    @classmethod
    def is_valid(
        cls,
        target_type
    ):
        """
        判斷 Target Type 是否有效。

        Parameters
        ----------

        target_type :
            Target Type 字串。

        Returns
        -------

        bool
        """

        if target_type is None:

            return False

        target_type = str(
            target_type
        ).strip().lower()

        return target_type in cls.ALL

    # ==================================
    # Normalize
    # ==================================

    @classmethod
    def normalize(
        cls,
        target_type
    ):
        """
        Normalize Target Type。

        例如：

            " WEBSITE "
                ↓
            "website"

            "RSS"
                ↓
            "rss"

        Invalid Type：

            ValueError
        """

        if target_type is None:

            raise ValueError(
                "target_type cannot be None"
            )

        normalized = str(
            target_type
        ).strip().lower()

        if not normalized:

            raise ValueError(
                "target_type cannot be empty"
            )

        if not cls.is_valid(
            normalized
        ):

            raise ValueError(
                "Unsupported target type: "
                f"{target_type}"
            )

        return normalized

    # ==================================
    # Display Name
    # ==================================

    @classmethod
    def display_name(
        cls,
        target_type
    ):
        """
        取得 Target Type 顯示名稱。
        """

        target_type = cls.normalize(
            target_type
        )

        names = {

            cls.WEBSITE:
                "Website",

            cls.RSS:
                "RSS",

            cls.API:
                "API",

            cls.CUSTOM:
                "Custom"

        }

        return names[
            target_type
        ]

    # ==================================
    # Is Website
    # ==================================

    @classmethod
    def is_website(
        cls,
        target_type
    ):
        """
        判斷是否為 Website Target。
        """

        return (
            cls.normalize(
                target_type
            )
            ==
            cls.WEBSITE
        )

    # ==================================
    # Is RSS
    # ==================================

    @classmethod
    def is_rss(
        cls,
        target_type
    ):
        """
        判斷是否為 RSS Target。
        """

        return (
            cls.normalize(
                target_type
            )
            ==
            cls.RSS
        )

    # ==================================
    # Is API
    # ==================================

    @classmethod
    def is_api(
        cls,
        target_type
    ):
        """
        判斷是否為 API Target。
        """

        return (
            cls.normalize(
                target_type
            )
            ==
            cls.API
        )

    # ==================================
    # Is Custom
    # ==================================

    @classmethod
    def is_custom(
        cls,
        target_type
    ):
        """
        判斷是否為 Custom Target。
        """

        return (
            cls.normalize(
                target_type
            )
            ==
            cls.CUSTOM
        )


# ==================================
# Public API
# ==================================

__all__ = [
    "TargetType",
]