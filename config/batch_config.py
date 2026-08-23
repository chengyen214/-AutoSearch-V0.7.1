"""
config/batch_config.py

AutoSearch V5

V5.6.2
Batch Configuration

用途：

    管理 Batch Runner 的批次設定。

目前：

    Batch Size

預設：

    20

V5.6.2 責任：

    BatchConfig
        ↓
    提供 Batch Size Configuration
        ↓
    BatchExecutionService
        ↓
    控制本次 Batch 執行數量

重要：

    BatchConfig 只提供設定。

    BatchExecutionService
    負責實際使用 Batch Size
    控制 Batch Execution。

    BatchJobService
    不負責 Batch Size 限制。

不負責：

    - Job Retrieval
    - Target Retrieval
    - Job Execution
    - Job Status
    - Source Resolution
    - Search Provider
    - Search API
    - Search Execution
    - SearchAdapter
    - Crawler
    - Parser
    - Archive
    - AI
"""


class BatchConfig:
    """
    V5.6.2 Batch Runner Configuration。

    目前只負責：

        batch_size

    預設：

        20

    設計原則：

        BatchConfig
            ↓
        Configuration

        BatchExecutionService
            ↓
        Execution Control
    """

    # ==================================================
    #
    # Default
    #
    # ==================================================

    DEFAULT_BATCH_SIZE = 20

    # ==================================================
    #
    # Constructor
    #
    # ==================================================

    def __init__(
        self,
        batch_size=None,
    ):
        """
        建立 Batch Configuration。

        Parameters
        ----------
        batch_size : int | None

            每一批最多處理的 Job 數量。

            None：

                使用 DEFAULT_BATCH_SIZE。
        """

        if batch_size is None:

            batch_size = (
                self.DEFAULT_BATCH_SIZE
            )

        # 使用 property setter，
        # 確保初始化時也經過 Validation。
        self.batch_size = (
            batch_size
        )

    # ==================================================
    #
    # Validation
    #
    # ==================================================

    @staticmethod
    def _validate_batch_size(
        batch_size,
    ):
        """
        驗證 Batch Size。

        條件：

            1. 必須為 int
            2. 不可為 bool
            3. 必須大於 0
        """

        # ----------------------------------------------
        # bool 必須排除
        #
        # Python：
        #
        #     isinstance(True, int) == True
        #
        # 因此必須單獨處理。
        # ----------------------------------------------

        if isinstance(
            batch_size,
            bool,
        ):

            raise TypeError(
                "batch_size must be an integer"
            )

        # ----------------------------------------------
        # Integer Validation
        # ----------------------------------------------

        if not isinstance(
            batch_size,
            int,
        ):

            raise TypeError(
                "batch_size must be an integer"
            )

        # ----------------------------------------------
        # Positive Validation
        # ----------------------------------------------

        if batch_size <= 0:

            raise ValueError(
                "batch_size must be greater than 0"
            )

    # ==================================================
    #
    # Batch Size Property
    #
    # ==================================================

    @property
    def batch_size(self):
        """
        取得目前 Batch Size。
        """

        return self._batch_size

    @batch_size.setter
    def batch_size(
        self,
        value,
    ):
        """
        更新 Batch Size。

        所有：

            config.batch_size = value

        都必須經過 Validation。
        """

        self._validate_batch_size(
            value
        )

        self._batch_size = value

    # ==================================================
    #
    # Setter API
    #
    # ==================================================

    def set_batch_size(
        self,
        batch_size,
    ):
        """
        更新 Batch Size。

        Validation：

            property setter
                ↓
            _validate_batch_size()
        """

        self.batch_size = (
            batch_size
        )

        return self.batch_size

    # ==================================================
    #
    # Getter API
    #
    # ==================================================

    def get_batch_size(self):
        """
        取得目前 Batch Size。
        """

        return self.batch_size

    # ==================================================
    #
    # Dictionary
    #
    # ==================================================

    def to_dict(self):
        """
        將設定轉換成 dictionary。

        Returns
        -------

        dict

            {
                "batch_size": 20
            }
        """

        return {
            "batch_size": self.batch_size,
        }

    # ==================================================
    #
    # Representation
    #
    # ==================================================

    def __repr__(
        self,
    ):
        """
        回傳 Configuration Representation。
        """

        return (
            "BatchConfig("
            f"batch_size={self.batch_size}"
            ")"
        )


# ==================================================
#
# Default Configuration
#
# ==================================================

DEFAULT_BATCH_CONFIG = (
    BatchConfig()
)


# ==================================================
#
# Public API
#
# ==================================================

__all__ = [
    "BatchConfig",
    "DEFAULT_BATCH_CONFIG",
]
