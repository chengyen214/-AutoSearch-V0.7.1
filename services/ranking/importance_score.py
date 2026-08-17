"""
services/ranking/importance_score.py

AutoSearch V4

P2.6 Step 5

Importance Score Calculator

Purpose:

    Convert KnowledgeScore.importance
    into Search Ranking Importance Score.

Score Range:

    0 ~ 10
"""


class ImportanceScoreCalculator:
    """
    Importance Score Calculator

    負責將 KnowledgeScore.importance
    轉換成 Search Ranking 使用的
    Importance Score。

    Search Ranking Score Range:

        0 ~ 10
    """

    SCORE_MIN = 0.0

    SCORE_MAX = 10.0

    def _get_importance(
        self,
        knowledge_score
    ):
        """
        取得 KnowledgeScore.importance。

        支援：

            KnowledgeScore object
            None

        Returns:

            float
        """

        if knowledge_score is None:

            return 0.0

        importance = getattr(

            knowledge_score,

            "importance",

            0

        )

        if importance is None:

            return 0.0

        try:

            return float(
                importance
            )

        except (
            TypeError,
            ValueError
        ):

            return 0.0

    def calculate(
        self,
        knowledge_score
    ):
        """
        計算 Importance Score。

        Formula:

            importance_score = importance

        Score Range:

            0 ~ 10

        超出範圍時：

            < 0  → 0
            > 10 → 10
        """

        importance = self._get_importance(

            knowledge_score

        )

        importance = max(

            self.SCORE_MIN,

            importance

        )

        importance = min(

            self.SCORE_MAX,

            importance

        )

        return round(

            importance,

            2

        )
