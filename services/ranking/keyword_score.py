"""
services/ranking/keyword_score.py

AutoSearch V4

P2.6 Step 2

Keyword Score Calculator
"""

import re


class KeywordScoreCalculator:
    """
    Keyword Score Calculator

    負責計算 Query 與 SearchIndex
    之間的 Keyword 相關性。
    """

    SCORE_MAX = 10.0

    def _tokenize_keywords(self, query):
        """
        將 Query 拆成 Keyword Token。
        """

        if not query:
            return []

        text = str(query).lower()

        tokens = re.findall(
            r"[^\W_]+",
            text,
            flags=re.UNICODE
        )

        return [
            token.strip()
            for token in tokens
            if token.strip()
        ]

    def _get_search_text(self, search_index):
        """
        取得 SearchIndex.search_text。
        """

        if search_index is None:
            return ""

        return str(
            getattr(
                search_index,
                "search_text",
                ""
            )
            or ""
        ).lower()

    def calculate(self, query, search_index):
        """
        計算 Keyword Score。

        Formula:

            matched_keywords
            ---------------- × 10
            total_keywords
        """

        keywords = self._tokenize_keywords(query)

        if not keywords:
            return 0.0

        search_text = self._get_search_text(
            search_index
        )

        if not search_text:
            return 0.0

        matched_count = 0

        for keyword in keywords:

            if keyword in search_text:
                matched_count += 1

        score = (
            matched_count
            / len(keywords)
        ) * self.SCORE_MAX

        return round(
            min(
                score,
                self.SCORE_MAX
            ),
            2
        )