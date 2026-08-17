"""
services/ranking/freshness_score.py

AutoSearch V4

P2.6 Step 7

Freshness Score Calculator
"""

from datetime import (
    datetime,
    date,
    timezone
)


class FreshnessScoreCalculator:
    """
    Freshness Score Calculator

    負責計算 SearchIndex
    資料的新鮮程度。

    Score:

        <= 1 day       -> 10.0
        <= 7 days      -> 9.0
        <= 30 days     -> 8.0
        <= 90 days     -> 6.0
        <= 180 days    -> 4.0
        <= 365 days    -> 2.0
        > 365 days     -> 0.0
    """

    SCORE_MAX = 10.0

    def _get_published(self, search_index):
        """
        取得 SearchIndex.published。

        支援：

            datetime
            date
            ISO datetime string
            None
        """

        if search_index is None:
            return None

        published = getattr(
            search_index,
            "published",
            None
        )

        if published is None:
            return None

        if isinstance(
            published,
            datetime
        ):
            return published

        if isinstance(
            published,
            date
        ):
            return datetime.combine(
                published,
                datetime.min.time()
            )

        if isinstance(
            published,
            str
        ):

            value = published.strip()

            if not value:
                return None

            try:

                return datetime.fromisoformat(
                    value.replace(
                        "Z",
                        "+00:00"
                    )
                )

            except ValueError:

                return None

        return None

    def _normalize_datetime(
        self,
        value
    ):
        """
        將 datetime 正規化。

        移除 timezone 差異，
        避免 naive / aware datetime
        比較錯誤。
        """

        if value is None:
            return None

        if value.tzinfo is not None:

            return value.astimezone(
                timezone.utc
            ).replace(
                tzinfo=None
            )

        return value

    def _calculate_age_days(
        self,
        published,
        now=None
    ):
        """
        計算資料距今幾天。
        """

        published = self._normalize_datetime(
            published
        )

        if published is None:
            return None

        if now is None:

            now = datetime.now()

        now = self._normalize_datetime(
            now
        )

        if now < published:
            return 0.0

        delta = (
            now - published
        )

        return delta.total_seconds() / 86400

    def calculate(
        self,
        search_index,
        now=None
    ):
        """
        計算 Freshness Score。

        Parameters:

            search_index:
                SearchIndex object

            now:
                Optional datetime。
                主要提供 unit test 使用。

        Returns:

            float
        """

        published = self._get_published(
            search_index
        )

        if published is None:
            return 0.0

        age_days = self._calculate_age_days(
            published,
            now
        )

        if age_days is None:
            return 0.0

        if age_days <= 1:
            return 10.0

        if age_days <= 7:
            return 9.0

        if age_days <= 30:
            return 8.0

        if age_days <= 90:
            return 6.0

        if age_days <= 180:
            return 4.0

        if age_days <= 365:
            return 2.0

        return 0.0
