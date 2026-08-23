"""
models/target_status.py

AutoSearch V5

V5.1 P1.4

Target Status Definition

用途：

    定義 V5 Target 支援的 Target Status。

目前支援：

    active
    inactive

設計：

    Target
        ↓
    Target Status
        ↓
    Existing V4 Crawl Pipeline

Target Status 不負責：

    - Crawler
    - Search Adapter
    - Parser
    - Article
    - Archive
    - Duplicate Detection
    - AI Analysis
    - Scheduling


重要：

    Target Status 目前只負責：

        1. Status Definition
        2. Status Validation
        3. Status Normalization
        4. Status Display Name
        5. Status State Check

    實際 Target 執行邏輯：

        後續 Pipeline Integration
        再處理。
"""


class TargetStatus:
    """
    V5 Target Status Definition。

    使用字串作為 Database 儲存值，
    避免修改目前 targets.status
    的 varchar(30) Schema。
    """

    # ==================================
    # Target Status
    # ==================================

    ACTIVE = "active"

    INACTIVE = "inactive"

    # ==================================
    # All Status
    # ==================================

    ALL = (

        ACTIVE,

        INACTIVE

    )

    # ==================================
    # Validation
    # ==================================

    @classmethod
    def is_valid(
        cls,
        status
    ):
        """
        判斷 Target Status 是否有效。

        Parameters
        ----------

        status :
            Target Status 字串。

        Returns
        -------

        bool
        """

        if status is None:

            return False

        status = str(
            status
        ).strip().lower()

        return status in cls.ALL

    # ==================================
    # Normalize
    # ==================================

    @classmethod
    def normalize(
        cls,
        status
    ):
        """
        Normalize Target Status。

        例如：

            " ACTIVE "
                ↓
            "active"

            "INACTIVE"
                ↓
            "inactive"

        Invalid Status：

            ValueError
        """

        if status is None:

            raise ValueError(
                "status cannot be None"
            )

        normalized = str(
            status
        ).strip().lower()

        if not normalized:

            raise ValueError(
                "status cannot be empty"
            )

        if not cls.is_valid(
            normalized
        ):

            raise ValueError(
                "Unsupported target status: "
                f"{status}"
            )

        return normalized

    # ==================================
    # Display Name
    # ==================================

    @classmethod
    def display_name(
        cls,
        status
    ):
        """
        取得 Target Status 顯示名稱。
        """

        status = cls.normalize(
            status
        )

        names = {

            cls.ACTIVE:
                "Active",

            cls.INACTIVE:
                "Inactive"

        }

        return names[
            status
        ]

    # ==================================
    # Is Active
    # ==================================

    @classmethod
    def is_active(
        cls,
        status
    ):
        """
        判斷 Target 是否為 Active。
        """

        return (
            cls.normalize(
                status
            )
            ==
            cls.ACTIVE
        )

    # ==================================
    # Is Inactive
    # ==================================

    @classmethod
    def is_inactive(
        cls,
        status
    ):
        """
        判斷 Target 是否為 Inactive。
        """

        return (
            cls.normalize(
                status
            )
            ==
            cls.INACTIVE
        )


# ==================================
# Public API
# ==================================

__all__ = [
    "TargetStatus",
]