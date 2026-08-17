"""
services/ranking/confidence_score.py

AutoSearch V4

P2.6 Step 6

Confidence Score Calculator
"""


class ConfidenceScoreCalculator:
    """
    Confidence Score Calculator

    負責取得 SearchIndex / Knowledge
    的 Confidence Score。

    Confidence：

        0.0 ~ 1.0

    Ranking Score：

        0.0 ~ 10.0

    Conversion:

        confidence * 10
    """

    SCORE_MAX = 10.0

    CONFIDENCE_MAX = 1.0


    def _get_confidence(
        self,
        search_index
    ):
        """
        取得 SearchIndex.confidence。

        支援：

            int
            float
            numeric string
            None

        回傳：

            0.0 ~ 1.0
        """

        if search_index is None:

            return 0.0


        confidence = getattr(

            search_index,

            "confidence",

            0

        )


        if confidence is None:

            return 0.0


        try:

            confidence = float(

                confidence

            )

        except (
            TypeError,
            ValueError
        ):

            return 0.0


        # ------------------------------
        # Clamp
        # ------------------------------

        confidence = max(

            0.0,

            min(

                confidence,

                self.CONFIDENCE_MAX

            )

        )


        return confidence


    def calculate(
        self,
        search_index
    ):
        """
        計算 Confidence Score。

        Formula:

            confidence × 10

        Examples:

            1.0  -> 10.0
            0.9  -> 9.0
            0.8  -> 8.0
            0.5  -> 5.0
            0.0  -> 0.0
        """

        confidence = self._get_confidence(

            search_index

        )


        score = (

            confidence

            * self.SCORE_MAX

        )


        return round(

            score,

            2

        )
