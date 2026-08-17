"""
services/ranking/ranking_score.py

AutoSearch V4

P2.6 Step 8

Ranking Score Calculator

Purpose:

    計算 SearchIndex / KnowledgeScore
    的 Ranking Score。

Responsibilities:

    1. 取得 ranking_score
    2. None 安全處理
    3. 數值轉換
    4. 限制 Score 範圍 0 ~ 10
"""


class RankingScoreCalculator:
    """
    Ranking Score Calculator

    負責取得 Knowledge 的
    Ranking Score。
    """

    SCORE_MIN = 0.0

    SCORE_MAX = 10.0

    # ==================================
    # Get Ranking Score
    # ==================================

    def _get_ranking_score(
        self,
        search_index
    ):
        """
        取得 SearchIndex.ranking_score。

        支援：

            int
            float
            numeric string
            None

        無效資料：

            回傳 0.0
        """

        if search_index is None:

            return 0.0

        value = getattr(
            search_index,
            "ranking_score",
            None
        )

        if value is None:

            return 0.0

        try:

            value = float(value)

        except (
            TypeError,
            ValueError
        ):

            return 0.0

        return value

    # ==================================
    # Calculate
    # ==================================

    def calculate(
        self,
        search_index
    ):
        """
        計算 Ranking Score。

        Score 範圍：

            0 ~ 10

        若超過範圍：

            > 10 → 10

            < 0  → 0
        """

        score = self._get_ranking_score(
            search_index
        )

        score = max(
            self.SCORE_MIN,
            score
        )

        score = min(
            self.SCORE_MAX,
            score
        )

        return round(
            score,
            2
        )