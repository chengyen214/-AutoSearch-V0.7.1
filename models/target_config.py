"""
models/target_config.py

AutoSearch V5

V5.1 P1.5

Target Configuration

用途：

    定義 User Target 的爬蟲相關設定。

設計：

    Target
        ↓
    TargetConfig
        ↓
    Existing V4 Crawl Pipeline

Target Configuration 目前負責：

    1. Configuration Definition
    2. Configuration Defaults
    3. Configuration Validation
    4. Configuration Normalization
    5. Configuration Dictionary

Target Configuration 不負責：

    - Crawler
    - Search Adapter
    - Parser
    - Article
    - Archive
    - Duplicate Detection
    - AI Analysis
    - Scheduling

重要：

    P1.5 只定義 Target 的執行設定。

    實際如何使用這些設定：

        Target
            ↓
        Target Pipeline
            ↓
        Existing V4 Crawl Pipeline

    後續 Pipeline Integration 再處理。
"""


class TargetConfig:
    """
    V5 Target Configuration。

    目前設定：

        max_results
        timeout
        search_enabled

    這些設定不直接執行 Crawler。
    """

    # ==================================
    # Defaults
    # ==================================

    DEFAULT_MAX_RESULTS = 20

    DEFAULT_TIMEOUT = 7

    DEFAULT_SEARCH_ENABLED = True

    # ==================================
    # Constructor
    # ==================================

    def __init__(
        self,
        max_results=None,
        timeout=None,
        search_enabled=None
    ):
        """
        建立 Target Configuration。
        """

        if max_results is None:

            max_results = (
                self.DEFAULT_MAX_RESULTS
            )

        if timeout is None:

            timeout = (
                self.DEFAULT_TIMEOUT
            )

        if search_enabled is None:

            search_enabled = (
                self.DEFAULT_SEARCH_ENABLED
            )

        self.max_results = max_results

        self.timeout = timeout

        self.search_enabled = search_enabled

        self.normalize()

    # ==================================
    # Validation
    # ==================================

    def validate(self):
        """
        驗證 Target Configuration。

        Returns
        -------

        bool

        Raises
        ------

        ValueError
            Configuration 無效。
        """

        # ----------------------------------
        # max_results
        # ----------------------------------

        if isinstance(
            self.max_results,
            bool
        ):

            raise ValueError(
                "max_results must be an integer"
            )

        if not isinstance(
            self.max_results,
            int
        ):

            raise ValueError(
                "max_results must be an integer"
            )

        if self.max_results <= 0:

            raise ValueError(
                "max_results must be greater than 0"
            )

        # ----------------------------------
        # timeout
        # ----------------------------------

        if isinstance(
            self.timeout,
            bool
        ):

            raise ValueError(
                "timeout must be a number"
            )

        if not isinstance(
            self.timeout,
            (int, float)
        ):

            raise ValueError(
                "timeout must be a number"
            )

        if self.timeout <= 0:

            raise ValueError(
                "timeout must be greater than 0"
            )

        # ----------------------------------
        # search_enabled
        # ----------------------------------

        if not isinstance(
            self.search_enabled,
            bool
        ):

            raise ValueError(
                "search_enabled must be a boolean"
            )

        return True

    # ==================================
    # Normalize
    # ==================================

    def normalize(self):
        """
        Normalize Target Configuration。

        Returns
        -------

        TargetConfig
            自己本身。
        """

        # max_results

        if isinstance(
            self.max_results,
            str
        ):

            value = self.max_results.strip()

            if value:

                try:

                    self.max_results = int(
                        value
                    )

                except ValueError:

                    pass

        # timeout

        if isinstance(
            self.timeout,
            str
        ):

            value = self.timeout.strip()

            if value:

                try:

                    self.timeout = float(
                        value
                    )

                except ValueError:

                    pass

        self.validate()

        return self

    # ==================================
    # Dictionary
    # ==================================

    def to_dict(self):
        """
        將 Configuration 轉成 Dictionary。
        """

        return {

            "max_results":
                self.max_results,

            "timeout":
                self.timeout,

            "search_enabled":
                self.search_enabled

        }

    # ==================================
    # Representation
    # ==================================

    def __repr__(self):

        return (

            "TargetConfig("

            f"max_results={self.max_results}, "

            f"timeout={self.timeout}, "

            f"search_enabled={self.search_enabled}"

            ")"

        )


# ==================================
# Public API
# ==================================

__all__ = [
    "TargetConfig",
]